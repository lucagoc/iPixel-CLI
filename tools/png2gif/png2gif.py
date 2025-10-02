import os
from PIL import Image

def png_to_gif(input_folder, output_file, duration=100, loop=0):
    """
    Converts a sequence of PNG images to an animated GIF.

    :param input_folder: Folder containing PNG images
    :param output_file: Output GIF file name
    :param duration: Duration of each image in milliseconds (100ms by default)
    :param loop: Number of loops (0 for infinite loop)
    """
    # List all PNG images in the folder
    images = [f for f in os.listdir(input_folder) if f.endswith(".png")]
    
    if not images:
        print("No PNG images found in the folder.")
        return

    # Sort images by name (useful if they are numbered)
    images.sort()

    # Load images with Pillow
    frames = [Image.open(os.path.join(input_folder, img)) for img in images]

    # Save as animated GIF
    frames[0].save(
        output_file,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop
    )
    print(f"GIF created successfully: {output_file}")

if __name__ == "__main__":
    
    # Parameters
    input_folder = "input_images"
    output_file = "output_animation.gif"
    duration = 500
    loop = 0

    # Create GIF
    png_to_gif(input_folder, output_file, duration, loop)
