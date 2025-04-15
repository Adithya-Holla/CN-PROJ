import pygame
import time
import math
from gui.utils import Button, TextBox, draw_text

class Menu:
    def __init__(self, screen, colors, font, title_font):
        self.screen = screen
        self.colors = colors
        self.font = font
        self.title_font = title_font
        self.width, self.height = screen.get_size()
        
        # Login screen elements
        self.username_box = TextBox(
            (self.width // 2 - 150, self.height // 2 - 20, 300, 40),
            font,
            {
                'normal': (220, 220, 220),
                'active': (240, 240, 240),
                'text': colors['text']
            },
            max_length=15
        )
        
        # Activate the username box by default
        self.username_box.active = True
        
        self.login_button = Button(
            (self.width // 2 - 75, self.height // 2 + 40, 150, 40),
            "Connect",
            font,
            {
                'normal': colors['button'],
                'hover': colors['button_hover'],
                'text': colors['text']
            }
        )
        
        # Menu screen elements - make the button bigger and more prominent
        self.find_game_button = Button(
            (self.width // 2 - 150, self.height // 2 - 40, 300, 80),
            "FIND MATCH",
            title_font,
            {
                'normal': (50, 200, 50),    # Brighter green for normal state
                'hover': (30, 180, 30),     # Slightly darker green for hover
                'text': (255, 255, 255)     # White text
            }
        )
        
        # Status and game tracking
        self.status_message = ""
        self.find_game_clicked = False
    
    def draw_login_screen(self):
        # Draw background elements
        # Header bar
        pygame.draw.rect(self.screen, self.colors['header'], (0, 0, self.width, 80))
        
        # Draw title with shadow effect
        title_text = "CHESS ONLINE"
        # Shadow
        shadow_surface = self.title_font.render(title_text, True, (30, 30, 30))
        shadow_rect = shadow_surface.get_rect(center=(self.width // 2 + 2, 42))
        self.screen.blit(shadow_surface, shadow_rect)
        # Main text
        title_surface = self.title_font.render(title_text, True, self.colors['white'])
        title_rect = title_surface.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Draw login card background
        card_width, card_height = 400, 300
        card_x = self.width // 2 - card_width // 2
        card_y = self.height // 2 - card_height // 2
        
        # Card shadow
        pygame.draw.rect(self.screen, (200, 200, 200), 
                         (card_x + 5, card_y + 5, card_width, card_height), 
                         border_radius=10)
        
        # Card background
        pygame.draw.rect(self.screen, self.colors['white'], 
                         (card_x, card_y, card_width, card_height), 
                         border_radius=10)
        
        # Card border
        pygame.draw.rect(self.screen, self.colors['panel'], 
                         (card_x, card_y, card_width, card_height), 
                         2, border_radius=10)
        
        # Login subtitle
        subtitle_text = "Welcome! Enter your username to play"
        subtitle_surface = self.font.render(subtitle_text, True, self.colors['text'])
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, card_y + 50))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw username label
        label_text = "Username:"
        label_surface = self.font.render(label_text, True, self.colors['text'])
        self.screen.blit(label_surface, (card_x + 50, card_y + 100))
        
        # Reposition username box
        self.username_box.rect.x = card_x + 50
        self.username_box.rect.y = card_y + 130
        self.username_box.rect.width = 300
        
        # Draw username box
        self.username_box.update(pygame.time.get_ticks())
        self.username_box.draw(self.screen)
        
        # Reposition login button and make it more attractive
        self.login_button.rect.x = card_x + 125
        self.login_button.rect.y = card_y + 200
        self.login_button.rect.width = 150
        self.login_button.rect.height = 45
        
        # Recenter the button text
        self.login_button.text_rect = self.login_button.text_surface.get_rect(center=self.login_button.rect.center)
        
        # Draw login button
        mouse_pos = pygame.mouse.get_pos()
        self.login_button.update(mouse_pos)
        self.login_button.draw(self.screen)
        
        # Draw status message if any
        if self.status_message:
            # Choose color based on message content
            if "Connected" in self.status_message and "!" in self.status_message:
                msg_color = self.colors['success']
            elif "Failed" in self.status_message or "error" in self.status_message.lower():
                msg_color = self.colors['error']
            else:
                msg_color = self.colors['text']
                
            status_surface = self.font.render(self.status_message, True, msg_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, card_y + 260))
            self.screen.blit(status_surface, status_rect)
        
        # Footer
        pygame.draw.rect(self.screen, self.colors['panel'], (0, self.height - 40, self.width, 40))
        footer_text = "© 2023 Chess Online"
        footer_surface = pygame.font.SysFont('Arial', 14).render(footer_text, True, self.colors['text'])
        self.screen.blit(footer_surface, (self.width - footer_surface.get_width() - 10, self.height - 30))
    
    def draw_menu_screen(self, username=None):
        # Draw header bar with gradient effect
        header_rect = pygame.Rect(0, 0, self.width, 80)
        pygame.draw.rect(self.screen, self.colors['header'], header_rect)
        
        # Draw title with shadow effect
        title_text = "CHESS ONLINE"
        # Shadow
        shadow_surface = self.title_font.render(title_text, True, (30, 30, 30))
        shadow_rect = shadow_surface.get_rect(center=(self.width // 2 + 2, 42))
        self.screen.blit(shadow_surface, shadow_rect)
        # Main text
        title_surface = self.title_font.render(title_text, True, self.colors['white'])
        title_rect = title_surface.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Draw connection status indicator at top-right with improved styling
        status_text = "Connected to Server"
        status_surface = self.font.render(status_text, True, self.colors['success'])
        status_rect = status_surface.get_rect(midright=(self.width - 20, 40))
        
        # Status indicator circle with pulse effect
        pulse_size = 6 + (math.sin(pygame.time.get_ticks() / 500) + 1)
        pygame.draw.circle(self.screen, self.colors['success'], (status_rect.left - 15, status_rect.centery), pulse_size)
        
        self.screen.blit(status_surface, status_rect)
        
        # Draw main menu card with improved styling - SIMPLIFIED VERSION
        card_width, card_height = 500, 300
        card_x = self.width // 2 - card_width // 2
        card_y = self.height // 2 - card_height // 2
        
        # Card shadow
        pygame.draw.rect(self.screen, (180, 180, 180), 
                         (card_x + 8, card_y + 8, card_width, card_height), 
                         border_radius=15)
        
        # Card background with subtle gradient
        pygame.draw.rect(self.screen, (250, 250, 255), 
                         (card_x, card_y, card_width, card_height), 
                         border_radius=15)
        
        # Card border
        pygame.draw.rect(self.screen, self.colors['panel'], 
                         (card_x, card_y, card_width, card_height), 
                         2, border_radius=15)
        
        # Card title with better styling
        card_title = "Game Lobby"
        card_title_font = pygame.font.SysFont('Arial', 32, bold=True)
        card_title_surface = card_title_font.render(card_title, True, self.colors['header'])
        card_title_rect = card_title_surface.get_rect(midtop=(self.width // 2, card_y + 20))
        self.screen.blit(card_title_surface, card_title_rect)
        
        # Divider line below title
        pygame.draw.line(self.screen, self.colors['panel'],
                        (card_x + 50, card_y + 60),
                        (card_x + card_width - 50, card_y + 60),
                        1)
        
        # Welcome message with player name
        player_name = username or "Guest Player"
        welcome_text = f"Welcome, {player_name}!"
        welcome_surface = pygame.font.SysFont('Arial', 22).render(welcome_text, True, self.colors['text'])
        welcome_rect = welcome_surface.get_rect(center=(card_x + card_width // 2, card_y + 100))
        self.screen.blit(welcome_surface, welcome_rect)
        
        # Instructions
        instruction_text = "Ready to play? Click the button below to find an opponent"
        instruction_surface = pygame.font.SysFont('Arial', 16).render(instruction_text, True, self.colors['text'])
        instruction_rect = instruction_surface.get_rect(center=(card_x + card_width // 2, card_y + 130))
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Reposition and resize find game button to be more prominent
        self.find_game_button.rect.x = card_x + 100
        self.find_game_button.rect.y = card_y + 170
        self.find_game_button.rect.width = 300
        self.find_game_button.rect.height = 70
        
        # Update button text
        self.find_game_button.text = "FIND MATCH"
        self.find_game_button.text_surface = self.title_font.render(self.find_game_button.text, True, self.colors['white'])
        self.find_game_button.text_rect = self.find_game_button.text_surface.get_rect(center=self.find_game_button.rect.center)
        
        # Draw find game button with improved styling
        mouse_pos = pygame.mouse.get_pos()
        self.find_game_button.update(mouse_pos)
        
        # Add button shadow for 3D effect
        shadow_rect = pygame.Rect(
            self.find_game_button.rect.x + 3,
            self.find_game_button.rect.y + 3,
            self.find_game_button.rect.width,
            self.find_game_button.rect.height
        )
        pygame.draw.rect(self.screen, (30, 150, 30), shadow_rect, border_radius=10)
        
        self.find_game_button.draw(self.screen)
        
        # Draw status message with better styling
        if self.status_message:
            # Choose color based on message content
            if "Finding" in self.status_message or "Looking" in self.status_message:
                msg_color = self.colors['warning']
                # Draw animated waiting dots
                dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
                self.status_message = self.status_message.rstrip('.') + dots
                
                # Draw animated searching graphic
                center_x = card_x + card_width // 2
                center_y = card_y + 250
                radius = 15
                angle = (pygame.time.get_ticks() / 200) % (2 * 3.14159)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                pygame.draw.circle(self.screen, self.colors['warning'], (center_x, center_y), radius, 1)
                pygame.draw.circle(self.screen, self.colors['warning'], (int(x), int(y)), 5)
                
            elif "Found" in self.status_message:
                msg_color = self.colors['success']
            elif "Error" in self.status_message or "Failed" in self.status_message:
                msg_color = self.colors['error']
            else:
                msg_color = self.colors['text']
            
            # Draw status message with background
            status_bg = pygame.Rect(card_x + 50, card_y + 260, card_width - 100, 30)
            pygame.draw.rect(self.screen, (230, 230, 235), status_bg, border_radius=5)
            pygame.draw.rect(self.screen, self.colors['panel'], status_bg, 1, border_radius=5)
            
            status_surface = self.font.render(self.status_message, True, msg_color)
            status_rect = status_surface.get_rect(center=status_bg.center)
            self.screen.blit(status_surface, status_rect)
        
        # Footer
        footer_rect = pygame.Rect(0, self.height - 40, self.width, 40)
        pygame.draw.rect(self.screen, self.colors['panel'], footer_rect)
        
        # Left side - version info
        version_text = "Version 1.0.0"
        version_surface = pygame.font.SysFont('Arial', 14).render(version_text, True, self.colors['text'])
        self.screen.blit(version_surface, (10, self.height - 30))
        
        # Right side - copyright
        footer_text = "© 2023 Chess Online"
        footer_surface = pygame.font.SysFont('Arial', 14).render(footer_text, True, self.colors['text'])
        self.screen.blit(footer_surface, (self.width - footer_surface.get_width() - 10, self.height - 30))
    
    def set_status(self, message):
        self.status_message = message
    
    def handle_login_click(self, mouse_pos, client):
        # Update button hover state
        self.login_button.update(mouse_pos)
        
        # Handle username textbox click
        self.username_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos, 'button': 1}))
        
        # Check if login button was clicked
        if self.login_button.rect.collidepoint(mouse_pos):
            self.attempt_login(client)
    
    def attempt_login(self, client):
        username = self.username_box.get_text()
        if username:
            # Try to connect to server
            if client.connect_to_server(username):
                self.status_message = "Connected to server!"
                # Force client screen to menu after successful login
                client.current_screen = 'menu'
                print(f"Login successful, forced current_screen to: {client.current_screen}")
                return True
            else:
                self.status_message = "Failed to connect to server"
                return False
        else:
            self.status_message = "Please enter a username"
            return False
    
    def handle_menu_click(self, mouse_pos, client):
        # Print debug info about the find game button
        print(f"Mouse position: {mouse_pos}")
        print(f"Find game button rect: {self.find_game_button.rect}")
        print(f"Button collision check: {self.find_game_button.rect.collidepoint(mouse_pos)}")
        
        # Update button hover state
        hover_changed = self.find_game_button.update(mouse_pos)
        print(f"Button hover state: {self.find_game_button.hover}")
        
        # Get card dimensions for hit testing
        card_width, card_height = 500, 300
        card_x = self.width // 2 - card_width // 2
        card_y = self.height // 2 - card_height // 2
        
        # Check if find game button was clicked - use the Button's is_clicked method
        if self.find_game_button.is_clicked(mouse_pos):
            print("Find Game button clicked!")
            self.status_message = "Finding a game..."
            result = client.find_game()
            if result:
                self.find_game_clicked = True
                print("Find game request sent successfully")
            else:
                print("Failed to send find game request")
            return True
        else:
            print("Click was not on the Find Game button")
            
        return False
    
    def handle_login_key(self, event):
        # Handle textbox input
        if self.username_box.handle_event(event):
            # If Enter key was pressed, attempt login
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # This will be called by the client, which will pass itself
                return True
        return False 