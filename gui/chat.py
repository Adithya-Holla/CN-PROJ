import pygame
from gui.utils import TextBox, draw_text

class ChatPanel:
    def __init__(self, screen, colors, font, dimensions, max_messages=10):
        self.screen = screen
        self.colors = colors
        self.font = font
        self.width, self.height = dimensions
        self.messages = []
        self.max_messages = max_messages
        self.panel_rect = None  # Will be set during draw
        
        # Chat input box
        self.chat_box = TextBox(
            (0, 0, self.width - 60, 30),  # Position will be set in draw()
            font,
            {
                'normal': (240, 240, 240),
                'active': (255, 255, 255),
                'text': colors['text']
            },
            max_length=50
        )
        
        self.message_height = font.get_height() + 5
    
    def draw(self, x, y):
        if not self.panel_rect:
            self.panel_rect = pygame.Rect(x, y, self.width - 20, self.height)
        
        # Draw chat panel background with rounded corners
        pygame.draw.rect(self.screen, (240, 240, 245), self.panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.colors['panel'], self.panel_rect, 1, border_radius=8)
        
        # Draw messages
        message_area_height = self.height - 50  # Leave space for input box
        visible_messages = min(len(self.messages), int(message_area_height / self.message_height))
        start_idx = max(0, len(self.messages) - visible_messages)
        
        # Message area
        message_area = pygame.Rect(x + 5, y + 5, self.panel_rect.width - 10, message_area_height - 10)
        
        for i, message in enumerate(self.messages[start_idx:]):
            message_y = y + 10 + i * self.message_height
            
            # Determine if this is a player or opponent message
            if message.startswith("You:"):
                # Player message - right aligned with different color
                msg_parts = message.split(":", 1)
                if len(msg_parts) > 1:
                    sender, content = msg_parts
                    
                    # Draw player message with bubble
                    bubble_width = min(self.font.size(content)[0] + 20, message_area.width - 50)
                    bubble_rect = pygame.Rect(
                        message_area.right - bubble_width - 5,
                        message_y,
                        bubble_width,
                        self.message_height + 5
                    )
                    
                    # Bubble background
                    pygame.draw.rect(self.screen, self.colors['button'], bubble_rect, border_radius=8)
                    
                    # Message text
                    text_surface = self.font.render(content.strip(), True, self.colors['white'])
                    text_rect = text_surface.get_rect(midleft=(bubble_rect.left + 10, bubble_rect.centery))
                    self.screen.blit(text_surface, text_rect)
            else:
                # Opponent message - left aligned
                msg_parts = message.split(":", 1)
                if len(msg_parts) > 1:
                    sender, content = msg_parts
                    
                    # Draw sender name
                    sender_surface = pygame.font.SysFont('Arial', 14).render(sender, True, self.colors['header'])
                    self.screen.blit(sender_surface, (x + 10, message_y))
                    
                    # Draw opponent message with bubble
                    bubble_width = min(self.font.size(content)[0] + 20, message_area.width - 50)
                    bubble_rect = pygame.Rect(
                        x + 10,
                        message_y + sender_surface.get_height() + 2,
                        bubble_width,
                        self.message_height
                    )
                    
                    # Bubble background
                    pygame.draw.rect(self.screen, (220, 220, 225), bubble_rect, border_radius=8)
                    
                    # Message text
                    text_surface = self.font.render(content.strip(), True, self.colors['text'])
                    text_rect = text_surface.get_rect(midleft=(bubble_rect.left + 10, bubble_rect.centery))
                    self.screen.blit(text_surface, text_rect)
        
        # Draw bottom message divider
        pygame.draw.line(
            self.screen,
            self.colors['panel'],
            (x + 5, y + self.height - 45),
            (x + self.panel_rect.width - 5, y + self.height - 45),
            1
        )
        
        # Position and draw chat input box with rounded edges
        self.chat_box.rect.x = x + 5
        self.chat_box.rect.y = y + self.height - 40
        self.chat_box.rect.width = self.panel_rect.width - 60
        self.chat_box.update(pygame.time.get_ticks())
        self.chat_box.draw(self.screen)
        
        # Draw send button with better styling
        send_button_rect = pygame.Rect(
            x + self.panel_rect.width - 50,
            y + self.height - 40,
            45,
            30
        )
        
        # Button background
        pygame.draw.rect(self.screen, self.colors['button'], send_button_rect, border_radius=5)
        
        # Button text
        send_text = "Send"
        send_text_surface = pygame.font.SysFont('Arial', 14).render(send_text, True, self.colors['white'])
        send_text_rect = send_text_surface.get_rect(center=send_button_rect.center)
        self.screen.blit(send_text_surface, send_text_rect)
    
    def handle_click(self, mouse_pos):
        # Check if send button was clicked
        if hasattr(self, 'panel_rect') and self.panel_rect:
            send_button_rect = pygame.Rect(
                self.panel_rect.right - 50,
                self.panel_rect.bottom - 40,
                45,
                30
            )
            
            if send_button_rect.collidepoint(mouse_pos):
                return 'send'
        
        # Handle clicks on the chat box
        self.chat_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos, 'button': 1}))
        return None
    
    def handle_key(self, event):
        # Handle Enter key to send message
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.chat_box.active:
            return 'send'
        
        # Handle other key events for the chat box
        self.chat_box.handle_event(event)
        return None
    
    def send_message(self):
        message = self.chat_box.get_text().strip()
        if message:
            # The message will be sent by the client class
            # Clear the input box
            self.chat_box.clear()
            return message
        return None
    
    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def clear_messages(self):
        self.messages.clear() 