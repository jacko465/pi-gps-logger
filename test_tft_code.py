import os
import pygame

# Set environment variables
os.putenv('SDL_FBDEV', '/dev/fb1')
# os.putenv('SDL_VIDEODRIVER', 'fbcon')

# pygame.display.init()
# print(pygame.display.get_driver())

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((320, 240))  # PiTFT resolution
pygame.mouse.set_visible(False)

# Fill the screen with black
screen.fill((0, 0, 0))

# Draw a red circle in the center
pygame.draw.circle(screen, (255, 0, 0), (160, 120), 50)

# Update the display
pygame.display.flip()

# Wait for a few seconds
pygame.time.wait(5000)

# Quit Pygame
pygame.quit()