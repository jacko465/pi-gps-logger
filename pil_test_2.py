from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np

# Framebuffer device
fbdev = '/dev/fb1'  # Update if necessary

# Create an image with the correct mode
width, height = 320, 240  # Adjust to your screen's resolution
image = Image.new('RGB', (width, height), 'green')
draw = ImageDraw.Draw(image)

# Draw some text
font = ImageFont.load_default()
text = 'Hello, PiTFT!'
text_size = font.getbbox(text)
text_position = ((width - text_size[2]) // 2, (height - text_size[3]) // 2)
draw.text(text_position, text, font=font, fill='white')

# Convert the image to RGB565 format
def rgb_to_rgb565(image):
    arr = np.array(image)
    r = (arr[:,:,0] >> 3).astype(np.uint16)
    g = (arr[:,:,1] >> 2).astype(np.uint16)
    b = (arr[:,:,2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.flatten().astype('uint16').tobytes()

rgb565_data = rgb_to_rgb565(image)

# Write the image data to the framebuffer
try:
    with open(fbdev, 'wb') as fb:
        fb.write(rgb565_data)
    print(f"Successfully wrote to {fbdev}.")
except PermissionError:
    print(f"Permission denied when accessing {fbdev}. Try running the script with sudo.")
except Exception as e:
    print(f"An error occurred: {e}")
