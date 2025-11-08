"""
File for pypixel package.
Provides synchronous and asynchronous clients for controlling LED matrix.
"""

import asyncio
import logging
from typing import Optional
from bleak import BleakClient

from .lib.transport.send_plan import send_plan
from .lib.transport.ack_manager import AckManager
from .commands import COMMANDS

logger = logging.getLogger(__name__)

NOTIFY_UUID = "0000fa03-0000-1000-8000-00805f9b34fb"

def _create_async_method(command_name: str, command_func):
    """Create an async method for a command.
    
    Args:
        command_name: Name of the command
        command_func: The command function from COMMANDS
    
    Returns:
        An async method that can be added to AsyncClient
    """
    async def method(self, *args, **kwargs):
        await self._ensure_connected()
        
        if not self._client or not self._ack_mgr:
            raise RuntimeError("Client or AckManager not initialized")
        
        # Build the SendPlan
        plan = command_func(*args, **kwargs)
        
        # Send the plan
        await send_plan(self._client, plan, self._ack_mgr)
        logger.info(f"Command '{command_name}' executed successfully")
    
    # Preserve the original function's metadata for better introspection
    method.__name__ = command_name
    method.__doc__ = command_func.__doc__
    
    return method


class AsyncClient:
    """Asynchronous client for controlling the LED matrix via BLE."""
    
    def __init__(self, address: str):
        """Initialize the AsyncClient.
        
        Args:
            address: Bluetooth device address (e.g., "1D:6B:5E:B5:A5:54")
        """
        self._address = address
        self._client: Optional[BleakClient] = None
        self._ack_mgr: Optional[AckManager] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to the BLE device."""
        if self._connected:
            logger.warning("Already connected")
            return
        
        self._client = BleakClient(self._address)
        await self._client.connect()
        self._connected = True
        logger.info(f"Connected to {self._address}")
        
        # Enable notify-based ACKs
        self._ack_mgr = AckManager()
        try:
            await self._client.start_notify(NOTIFY_UUID, self._ack_mgr.make_notify_handler())
        except Exception as e:
            logger.warning(f"Failed to enable notifications on {NOTIFY_UUID}: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        if not self._connected:
            logger.warning("Not connected")
            return
        
        try:
            if self._client:
                await self._client.stop_notify(NOTIFY_UUID)
        except Exception as e:
            logger.debug(f"Error stopping notifications: {e}")
        
        if self._client:
            await self._client.disconnect()
        
        self._connected = False
        self._client = None
        self._ack_mgr = None
        logger.info("Disconnected")
    
    async def _ensure_connected(self) -> None:
        """Ensure the client is connected."""
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() first")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Dynamically add command methods to AsyncClient
for cmd_name, cmd_func in COMMANDS.items():
    setattr(AsyncClient, cmd_name, _create_async_method(cmd_name, cmd_func))

class Client:
    """Synchronous client for controlling the LED matrix via BLE.
    
    This is a synchronous wrapper around AsyncClient that handles the event loop
    automatically for simpler usage in non-async code.
    """
    
    def __init__(self, address: str):
        """Initialize the Client.
        
        Args:
            address: Bluetooth device address (e.g., "1D:6B:5E:B5:A5:54")
        """
        self._async_client = AsyncClient(address)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread = None
        self._setup_loop()
    
    def _setup_loop(self):
        """Set up a persistent event loop in a separate thread."""
        import threading
        
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=start_loop, args=(self._loop,), daemon=True)
        self._loop_thread.start()
    
    def _run_async(self, coro):
        """Run an async coroutine synchronously using the persistent loop."""
        if self._loop is None:
            raise RuntimeError("Event loop not initialized")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
    
    def __getattr__(self, name: str):
        """Delegate attribute access to async client, wrapping coroutines.
        
        This allows automatic synchronous wrapping of all async methods without
        explicit redefinition, reducing code duplication.
        """
        attr = getattr(self._async_client, name)
        
        # If it's a coroutine function, wrap it to run synchronously
        if asyncio.iscoroutinefunction(attr):
            def sync_wrapper(*args, **kwargs):
                return self._run_async(attr(*args, **kwargs))
            # Preserve function metadata for better IDE support
            sync_wrapper.__name__ = name
            sync_wrapper.__doc__ = attr.__doc__
            return sync_wrapper
        
        # Otherwise return the attribute as-is
        return attr
    
    def _cleanup_loop(self):
        """Clean up the event loop."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            if self._async_client._connected:
                self.disconnect()
        except Exception:
            pass
        self._cleanup_loop()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
