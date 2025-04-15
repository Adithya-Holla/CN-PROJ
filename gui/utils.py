import pygame

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

class Button:
    def __init__(self, rect, text, font, colors, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.colors = colors  # Should contain 'normal', 'hover', 'text'
        self.callback = callback
        self.hover = False
        self.outline_width = 2
        
        # Pre-render the text to improve performance
        self.text_surface = self.font.render(self.text, True, self.colors['text'])
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def draw(self, surface):
        # Draw button background
        color = self.colors['hover'] if self.hover else self.colors['normal']
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.colors['text'], self.rect, self.outline_width)
        
        # Draw button text
        surface.blit(self.text_surface, self.text_rect)
    
    def update(self, mouse_pos):
        # Update hover state
        prev_hover = self.hover
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Return True if hover state changed
        return prev_hover != self.hover
    
    def is_clicked(self, mouse_pos):
        # Simple method to check if the button was clicked
        clicked = self.rect.collidepoint(mouse_pos)
        print(f"Button clicked check: pos={mouse_pos}, rect={self.rect}, result={clicked}")
        return clicked
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.hover and self.callback:
                self.callback()
                return True
        return False


class TextBox:
    def __init__(self, rect, font, colors, max_length=20):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.colors = colors  # Should contain 'normal', 'active', 'text'
        self.text = ""
        self.active = False
        self.max_length = max_length
        self.cursor_visible = True
        self.cursor_timer = 0
        self.last_key_time = 0
        self.key_repeat_delay = 500  # ms
        self.key_repeat_interval = 50  # ms
    
    def draw(self, surface):
        # Draw textbox background
        color = self.colors['active'] if self.active else self.colors['normal']
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.colors['text'], self.rect, 2)
        
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, self.colors['text'])
            text_rect = text_surface.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
            surface.blit(text_surface, text_rect)
        
        # Draw cursor when active
        if self.active and self.cursor_visible:
            # Calculate cursor position
            if self.text:
                cursor_x = self.rect.x + 5 + self.font.size(self.text)[0]
            else:
                cursor_x = self.rect.x + 5
            
            # Draw cursor line
            pygame.draw.line(
                surface, 
                self.colors['text'],
                (cursor_x, self.rect.y + 5),
                (cursor_x, self.rect.y + self.rect.height - 5),
                2
            )
    
    def update(self, current_time):
        # Blink cursor every 500ms
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Toggle active state based on whether the click is inside the textbox
            prev_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            return prev_active != self.active
        
        if event.type == pygame.KEYDOWN and self.active:
            print(f"TextBox handling keydown: {event.key}")
            current_time = pygame.time.get_ticks()
            
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.last_key_time = current_time
                return True
                
            elif event.key == pygame.K_RETURN:
                # Only handle Enter in the input box
                return True
                
            elif len(self.text) < self.max_length:
                # Only add printable characters
                if event.unicode.isprintable():
                    self.text += event.unicode
                    print(f"Added character: '{event.unicode}' - Text is now: '{self.text}'")
                    self.last_key_time = current_time
                    return True
        
        return False
    
    def get_text(self):
        return self.text
    
    def set_text(self, text):
        self.text = text[:self.max_length]
    
    def clear(self):
        self.text = "" 