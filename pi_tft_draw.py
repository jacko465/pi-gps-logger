import os
import pygame

os.putenv('SDL_FBDEV', '/dev/fb1')
# os.putenv('SDL_VIDEODRIVER', 'fbcon')

print("pygame init")
pygame.init()
print("screen init")
screen = pygame.display.set_mode((320, 240))
pygame.mouse.set_visible(False)

# Drawing a red circle
screen.fill((0, 0, 0))  # Clear screen with black
pygame.draw.circle(screen, (255, 0, 0), (160, 120), 50)
pygame.display.update()

# Keep the display open
print("entering holding loop")
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()