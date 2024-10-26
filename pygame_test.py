import os
import pygame
import time

# Set environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((320, 240))
pygame.mouse.set_visible(False)

# Define font and colors
font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)

try:
    while True:
        # Clear the screen
        screen.fill(black)
        
        # Generate dynamic content (e.g., current time)
        current_time = time.strftime("%H:%M:%S")
        text_surface = font.render(f"Time: {current_time}", True, white)
        
        # Blit the text onto the screen
        screen.blit(text_surface, (60, 100))
        
        # Update the display
        pygame.display.update()
        
        # Delay to control update rate
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up
    pygame.quit()
