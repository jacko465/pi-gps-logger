# from PIL import Image

# # Create a red image
# image = Image.new("RGB", (320, 240), "red")
# # image = Image.new("RGB", (320, 240), "green")

# # Write the image to the framebuffer
# with open("/dev/fb1", "wb") as fb:
#     fb.write(image.tobytes())



# from PIL import Image
# import numpy as np

# # Replace '/dev/fb1' with the appropriate framebuffer device if necessary
# fbdev = '/dev/fb1'

# # Check if the framebuffer device exists
# import os
# if not os.path.exists(fbdev):
#     print(f"Framebuffer device {fbdev} does not exist.")
#     exit()

# # Create a red image matching the PiTFT resolution (320x240)
# width, height = 320, 240
# image = Image.new("RGB", (width, height), "red")

# # Convert the image to raw bytes
# raw_data = image.tobytes()

# # Write the raw image data directly to the framebuffer
# try:
#     with open(fbdev, "wb") as fb:
#         fb.write(raw_data)
#     print(f"Successfully wrote to {fbdev}.")
# except PermissionError:
#     print(f"Permission denied when accessing {fbdev}. Try running the script with sudo.")
# except Exception as e:
#     print(f"An error occurred: {e}")

from PIL import Image, ImageDraw, ImageFont
import os

# Framebuffer device
fbdev = '/dev/fb1'  # Update if necessary

# Create an image with Pillow
width, height = 320, 240  # Adjust to your screen's resolution
image = Image.new('RGBA', (width, height), 'black')
draw = ImageDraw.Draw(image)

# Draw some text
font = ImageFont.load_default()
text = 'Hello, PiTFT!'
text_size = font.getbbox(text)

text_position = ((width - text_size[2]) // 2, (height - text_size[3]) // 2)
draw.text(text_position, text, font=font, fill='white')

# Write the image directly to the framebuffer
try:
    with open(fbdev, 'wb') as fb:
        fb.write(image.tobytes())
    print(f"Successfully wrote to {fbdev}.")
except PermissionError:
    print(f"Permission denied when accessing {fbdev}. Try running the script with sudo.")
except Exception as e:
    print(f"An error occurred: {e}")
