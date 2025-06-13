import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
TITLE_BAR_HEIGHT = 30
BUTTON_SIZE = 25
BUTTON_MARGIN = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TITLE_BAR_COLOR = (45, 45, 48)
BUTTON_HOVER_COLOR = (70, 70, 75)
CLOSE_BUTTON_COLOR = (196, 43, 28)
MINIMIZE_BUTTON_COLOR = (255, 189, 68)
MAXIMIZE_BUTTON_COLOR = (39, 174, 96)

class WindowControls:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.title_bar_rect = pygame.Rect(0, 0, width, TITLE_BAR_HEIGHT)
        self.is_maximized = False
        
        # Button positions (from right to left)
        button_y = (TITLE_BAR_HEIGHT - BUTTON_SIZE) // 2
        self.close_button = pygame.Rect(width - BUTTON_SIZE - BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.maximize_button = pygame.Rect(width - 2 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.minimize_button = pygame.Rect(width - 3 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
        
        self.hovered_button = None
    
    def update_size(self, width, height):
        self.width = width
        self.height = height
        self.title_bar_rect = pygame.Rect(0, 0, width, TITLE_BAR_HEIGHT)
        
        button_y = (TITLE_BAR_HEIGHT - BUTTON_SIZE) // 2
        self.close_button = pygame.Rect(width - BUTTON_SIZE - BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.maximize_button = pygame.Rect(width - 2 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.minimize_button = pygame.Rect(width - 3 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
    
    def handle_mouse_motion(self, pos):
        self.hovered_button = None
        if self.close_button.collidepoint(pos):
            self.hovered_button = "close"
        elif self.maximize_button.collidepoint(pos):
            self.hovered_button = "maximize"
        elif self.minimize_button.collidepoint(pos):
            self.hovered_button = "minimize"
    
    def handle_click(self, pos):
        if self.close_button.collidepoint(pos):
            return "close"
        elif self.maximize_button.collidepoint(pos):
            return "maximize"
        elif self.minimize_button.collidepoint(pos):
            return "minimize"
        elif self.title_bar_rect.collidepoint(pos):
            return "drag_start"
        return None
    
    def draw(self, screen, title="測試視窗控制"):
        # Draw title bar
        pygame.draw.rect(screen, TITLE_BAR_COLOR, self.title_bar_rect)
        
        # Draw title text
        font = pygame.font.SysFont(['Microsoft JhengHei', 'Arial'], 14)
        title_surface = font.render(title, True, WHITE)
        title_x = 10
        title_y = (TITLE_BAR_HEIGHT - title_surface.get_height()) // 2
        screen.blit(title_surface, (title_x, title_y))
        
        # Draw buttons
        self._draw_button(screen, self.close_button, "close", CLOSE_BUTTON_COLOR)
        self._draw_button(screen, self.maximize_button, "maximize", MAXIMIZE_BUTTON_COLOR)
        self._draw_button(screen, self.minimize_button, "minimize", MINIMIZE_BUTTON_COLOR)
    
    def _draw_button(self, screen, rect, button_type, base_color):
        # Button background
        color = BUTTON_HOVER_COLOR if self.hovered_button == button_type else base_color
        pygame.draw.rect(screen, color, rect, border_radius=3)
        
        # Button icon
        center_x = rect.centerx
        center_y = rect.centery
        icon_size = 8
        
        if button_type == "close":
            # X icon
            pygame.draw.line(screen, WHITE, 
                           (center_x - icon_size//2, center_y - icon_size//2),
                           (center_x + icon_size//2, center_y + icon_size//2), 2)
            pygame.draw.line(screen, WHITE,
                           (center_x + icon_size//2, center_y - icon_size//2),
                           (center_x - icon_size//2, center_y + icon_size//2), 2)
        elif button_type == "maximize":
            # Square icon
            pygame.draw.rect(screen, WHITE, 
                           (center_x - icon_size//2, center_y - icon_size//2, icon_size, icon_size), 2)
        elif button_type == "minimize":
            # Line icon
            pygame.draw.line(screen, WHITE,
                           (center_x - icon_size//2, center_y),
                           (center_x + icon_size//2, center_y), 2)

def main():
    # Set up display
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.NOFRAME)
    pygame.display.set_caption("視窗控制測試")
    clock = pygame.time.Clock()
    
    # Initialize window controls
    window_controls = WindowControls(WIDTH, HEIGHT)
    current_width, current_height = WIDTH, HEIGHT
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    action = window_controls.handle_click(event.pos)
                    if action == "close":
                        running = False
                    elif action == "minimize":
                        pygame.display.iconify()
                    elif action == "maximize":
                        if window_controls.is_maximized:
                            # Restore to normal size
                            current_width, current_height = WIDTH, HEIGHT
                            screen = pygame.display.set_mode((current_width, current_height), 
                                                           pygame.RESIZABLE | pygame.NOFRAME)
                            window_controls.update_size(current_width, current_height)
                            window_controls.is_maximized = False
                        else:
                            # Maximize window
                            info = pygame.display.Info()
                            current_width, current_height = info.current_w, info.current_h
                            screen = pygame.display.set_mode((current_width, current_height), 
                                                           pygame.RESIZABLE | pygame.NOFRAME)
                            window_controls.update_size(current_width, current_height)
                            window_controls.is_maximized = True
            
            elif event.type == pygame.MOUSEMOTION:
                window_controls.handle_mouse_motion(event.pos)
            
            elif event.type == pygame.VIDEORESIZE:
                current_width, current_height = event.w, event.h
                screen = pygame.display.set_mode((current_width, current_height), 
                                               pygame.RESIZABLE | pygame.NOFRAME)
                window_controls.update_size(current_width, current_height)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw title bar
        window_controls.draw(screen)
        
        # Draw some content
        font = pygame.font.SysFont(['Microsoft JhengHei', 'Arial'], 24)
        content_text = font.render("視窗控制測試 - 點擊右上角按鈕測試功能", True, BLACK)
        content_rect = content_text.get_rect(center=(current_width//2, current_height//2))
        screen.blit(content_text, content_rect)
        
        instruction_text = font.render("ESC 鍵退出", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(current_width//2, current_height//2 + 50))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
