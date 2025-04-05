import pygame
import time
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
            "FIND GAME",
            title_font,
            {
                'normal': (50, 200, 50),    # Brighter green for normal state
                'hover': (30, 180, 30),     # Slightly darker green for hover
                'text': (255, 255, 255)     # White text
            }
        )
        
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
    
    def draw_menu_screen(self):
        # Draw header bar
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
        
        # Draw connection status indicator at top-right
        status_text = "Connected to Server"
        status_surface = self.font.render(status_text, True, self.colors['success'])
        status_rect = status_surface.get_rect(center=(self.width - 120, 40))
        
        # Status indicator circle
        pygame.draw.circle(self.screen, self.colors['success'], (self.width - 220, 40), 8)
        
        self.screen.blit(status_surface, status_rect)
        
        # Draw main menu card
        card_width, card_height = 500, 350
        card_x = self.width // 2 - card_width // 2
        card_y = self.height // 2 - card_height // 2 + 20
        
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
        
        # Card title
        card_title = "Game Lobby"
        card_title_surface = pygame.font.SysFont('Arial', 28).render(card_title, True, self.colors['header'])
        card_title_rect = card_title_surface.get_rect(center=(self.width // 2, card_y + 30))
        self.screen.blit(card_title_surface, card_title_rect)
        
        # Card subtitle
        subtitle_text = "Click below to find an opponent"
        subtitle_surface = self.font.render(subtitle_text, True, self.colors['text'])
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, card_y + 70))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Reposition find game button
        self.find_game_button.rect.x = self.width // 2 - 175
        self.find_game_button.rect.y = card_y + 120 
        self.find_game_button.rect.width = 350
        self.find_game_button.rect.height = 100
        
        # Recenter the button text
        self.find_game_button.text_rect = self.find_game_button.text_surface.get_rect(center=self.find_game_button.rect.center)
        
        # Draw find game button
        mouse_pos = pygame.mouse.get_pos()
        self.find_game_button.update(mouse_pos)
        self.find_game_button.draw(self.screen)
        
        # Draw status message if any
        if self.status_message:
            # Choose color based on message content
            if "Finding" in self.status_message or "Looking" in self.status_message:
                msg_color = self.colors['warning']
                # Draw animated waiting dots
                dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
                self.status_message = self.status_message.rstrip('.') + dots
            elif "Found" in self.status_message:
                msg_color = self.colors['success']
            elif "Error" in self.status_message or "Failed" in self.status_message:
                msg_color = self.colors['error']
            else:
                msg_color = self.colors['text']
                
            status_surface = self.font.render(self.status_message, True, msg_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, card_y + 250))
            self.screen.blit(status_surface, status_rect)
        
        # Additional instructions
        if not self.find_game_clicked:
            # Draw box with game instructions
            pygame.draw.rect(self.screen, (245, 245, 245), 
                             (card_x + 75, card_y + 250, 350, 70), 
                             border_radius=5)
            pygame.draw.rect(self.screen, self.colors['panel'], 
                             (card_x + 75, card_y + 250, 350, 70), 
                             1, border_radius=5)
            
            help_text1 = "Ready to play? Click the button to start matchmaking"
            help_text2 = "You'll be paired with another player automatically"
            help_surface1 = pygame.font.SysFont('Arial', 16).render(help_text1, True, self.colors['text'])
            help_surface2 = pygame.font.SysFont('Arial', 16).render(help_text2, True, self.colors['text'])
            
            self.screen.blit(help_surface1, (card_x + 85, card_y + 260))
            self.screen.blit(help_surface2, (card_x + 85, card_y + 290))
        
        # Footer
        pygame.draw.rect(self.screen, self.colors['panel'], (0, self.height - 40, self.width, 40))
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
        else:
            print("Click was not on the Find Game button")
    
    def handle_login_key(self, event):
        # Handle textbox input
        if self.username_box.handle_event(event):
            # If Enter key was pressed, attempt login
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # This will be called by the client, which will pass itself
                return True
        return False 