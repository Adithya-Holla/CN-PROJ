import pygame
import sys
from gui.menu import Menu

# Initialize pygame
pygame.init()

# Set up display
width, height = 1000, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Menu Test")

# Load fonts
font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 36)

# Set up colors
colors = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'text': (50, 50, 50),
    'button': (200, 200, 200),
    'button_hover': (180, 180, 180),
    'background': (240, 240, 240)
}

# Create menu
menu = Menu(screen, colors, font, title_font)

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                # Debug - print mouse position and button rect
                print(f"Mouse clicked at: {mouse_pos}")
                print(f"Find game button rect: {menu.find_game_button.rect}")
                print(f"Button clicked: {menu.find_game_button.rect.collidepoint(mouse_pos)}")
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    menu.find_game_button.update(mouse_pos)
    
    # Draw
    screen.fill(colors['background'])
    menu.draw_menu_screen()
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit() 