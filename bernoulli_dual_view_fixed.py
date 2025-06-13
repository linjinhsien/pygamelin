import pygame
import math
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants - 修改預設大小為 800x600
WIDTH = 800
HEIGHT = 600
MIN_WIDTH = 800
MIN_HEIGHT = 600
FPS = 60

# Base dimensions for scaling
BASE_WIDTH = 1400
BASE_HEIGHT = 800

# Window control constants
TITLE_BAR_HEIGHT = 30
BUTTON_SIZE = 25
BUTTON_MARGIN = 5
LEFT_TOOLBAR_WIDTH = 200  # 減少工具列寬度以適應小視窗

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
GREEN = (50, 205, 50)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (25, 25, 112)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (64, 64, 64)
TITLE_BAR_COLOR = (45, 45, 48)
BUTTON_HOVER_COLOR = (70, 70, 75)
CLOSE_BUTTON_COLOR = (196, 43, 28)
MINIMIZE_BUTTON_COLOR = (255, 189, 68)
RESIZE_BUTTON_COLOR = (52, 152, 219)  # 藍色縮放按鈕

# Physics constants
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = 9.81  # m/s²
ATMOSPHERIC_PRESSURE = 101325  # Pa

class WindowControls:
    """Handle window control buttons and title bar"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.title_bar_rect = pygame.Rect(0, 0, width, TITLE_BAR_HEIGHT)
        self.is_minimized = False
        self.dragging_window = False
        self.drag_offset = (0, 0)
        
        # Button positions (from right to left) - 移除最大化，改為縮放
        button_y = (TITLE_BAR_HEIGHT - BUTTON_SIZE) // 2
        self.close_button = pygame.Rect(width - BUTTON_SIZE - BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.resize_button = pygame.Rect(width - 2 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.minimize_button = pygame.Rect(width - 3 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
        
        self.hovered_button = None
    
    def update_size(self, width, height):
        """Update button positions when window is resized"""
        self.width = width
        self.height = height
        self.title_bar_rect = pygame.Rect(0, 0, width, TITLE_BAR_HEIGHT)
        
        button_y = (TITLE_BAR_HEIGHT - BUTTON_SIZE) // 2
        self.close_button = pygame.Rect(width - BUTTON_SIZE - BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.resize_button = pygame.Rect(width - 2 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
        self.minimize_button = pygame.Rect(width - 3 * (BUTTON_SIZE + BUTTON_MARGIN), button_y, BUTTON_SIZE, BUTTON_SIZE)
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion for button hover effects"""
        self.hovered_button = None
        if self.close_button.collidepoint(pos):
            self.hovered_button = "close"
        elif self.resize_button.collidepoint(pos):
            self.hovered_button = "resize"
        elif self.minimize_button.collidepoint(pos):
            self.hovered_button = "minimize"
    
    def handle_click(self, pos):
        """Handle button clicks, returns action string or None"""
        if self.close_button.collidepoint(pos):
            return "close"
        elif self.resize_button.collidepoint(pos):
            return "resize"
        elif self.minimize_button.collidepoint(pos):
            return "minimize"
        elif self.title_bar_rect.collidepoint(pos):
            return "drag_start"
        return None
    
    def draw(self, screen, title="伯努利原理科學模擬 - 雙平面視圖"):
        """Draw the title bar and control buttons"""
        # Draw title bar
        pygame.draw.rect(screen, TITLE_BAR_COLOR, self.title_bar_rect)
        
        # Draw title text
        font = pygame.font.SysFont(['Noto Sans TC', 'Microsoft JhengHei', 'Segoe UI', 'Arial'], 12)
        title_surface = font.render(title, True, WHITE)
        title_x = 10
        title_y = (TITLE_BAR_HEIGHT - title_surface.get_height()) // 2
        screen.blit(title_surface, (title_x, title_y))
        
        # Draw buttons
        self._draw_button(screen, self.close_button, "close", CLOSE_BUTTON_COLOR)
        self._draw_button(screen, self.resize_button, "resize", RESIZE_BUTTON_COLOR)
        self._draw_button(screen, self.minimize_button, "minimize", MINIMIZE_BUTTON_COLOR)
    
    def _draw_button(self, screen, rect, button_type, base_color):
        """Draw individual control button"""
        # Button background
        color = BUTTON_HOVER_COLOR if self.hovered_button == button_type else base_color
        pygame.draw.rect(screen, color, rect, border_radius=3)
        
        # Button icon
        center_x = rect.centerx
        center_y = rect.centery
        icon_size = 6  # 減小圖示大小
        
        if button_type == "close":
            # X icon
            pygame.draw.line(screen, WHITE, 
                           (center_x - icon_size//2, center_y - icon_size//2),
                           (center_x + icon_size//2, center_y + icon_size//2), 2)
            pygame.draw.line(screen, WHITE,
                           (center_x + icon_size//2, center_y - icon_size//2),
                           (center_x - icon_size//2, center_y + icon_size//2), 2)
        elif button_type == "resize":
            # 縮放圖示 (雙向箭頭)
            pygame.draw.line(screen, WHITE,
                           (center_x - icon_size//2, center_y - icon_size//2),
                           (center_x + icon_size//2, center_y + icon_size//2), 2)
            pygame.draw.line(screen, WHITE,
                           (center_x + icon_size//2, center_y - icon_size//2),
                           (center_x - icon_size//2, center_y + icon_size//2), 2)
            # 箭頭頭部
            pygame.draw.line(screen, WHITE,
                           (center_x - icon_size//2, center_y - icon_size//2),
                           (center_x - icon_size//2 + 2, center_y - icon_size//2), 1)
            pygame.draw.line(screen, WHITE,
                           (center_x - icon_size//2, center_y - icon_size//2),
                           (center_x - icon_size//2, center_y - icon_size//2 + 2), 1)
        elif button_type == "minimize":
            # Line icon
            pygame.draw.line(screen, WHITE,
                           (center_x - icon_size//2, center_y),
                           (center_x + icon_size//2, center_y), 2)

class ResponsiveLayout:
    """Handle responsive layout calculations with left toolbar"""
    def __init__(self, width, height):
        self.update_layout(width, height)
    
    def update_layout(self, width, height):
        """Update layout based on current window size"""
        self.width = width
        self.height = height
        self.content_height = height - TITLE_BAR_HEIGHT
        self.content_width = width - LEFT_TOOLBAR_WIDTH  # 扣除左側工具列
        
        # Scaling factors - 修正縮放計算
        base_content_width = BASE_WIDTH - 250  # 原始設計的內容寬度
        self.scale_x = max(0.3, self.content_width / base_content_width)  # 設定最小縮放
        self.scale_y = max(0.3, self.content_height / BASE_HEIGHT)
        self.global_scale = min(self.scale_x, self.scale_y)
        
        # Layout calculations - 右側為雙視圖區域
        self.view_width = max(200, self.content_width // 2)  # 每個視圖的最小寬度
        
        # Font sizes based on scale
        self.base_font_size = max(8, int(12 * self.global_scale))
        self.title_font_size = max(10, int(self.base_font_size * 1.2))
        
        # UI element sizes
        self.slider_height = max(15, int(20 * self.global_scale))
        self.button_padding = max(3, int(5 * self.global_scale))
        self.panel_margin = max(3, int(5 * self.global_scale))
    
    def get_content_rect(self):
        """Get the main content area (right side, below title bar)"""
        return pygame.Rect(LEFT_TOOLBAR_WIDTH, TITLE_BAR_HEIGHT, self.content_width, self.content_height)
    
    def get_view_rects(self):
        """Get rectangles for left and right view panels"""
        left_view = pygame.Rect(LEFT_TOOLBAR_WIDTH, TITLE_BAR_HEIGHT, self.view_width, self.content_height)
        right_view = pygame.Rect(LEFT_TOOLBAR_WIDTH + self.view_width, TITLE_BAR_HEIGHT, 
                               self.view_width, self.content_height)
        return left_view, right_view
    
    def get_toolbar_rect(self):
        """Get rectangle for the left toolbar"""
        return pygame.Rect(0, TITLE_BAR_HEIGHT, LEFT_TOOLBAR_WIDTH, self.content_height)

class Particle:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.life = random.randint(200, 255)
        self.size = random.uniform(1, 2)  # 減小粒子大小
        self.color = random.choice([WHITE, LIGHT_BLUE, (200, 200, 255)])
        
    def update(self, wind_speed, wind_angle, wind_vertical, ball_pos, ball_radius, dt):
        # Convert wind angle to radians
        wind_rad = math.radians(wind_angle)
        wind_vec_x = math.cos(wind_rad)
        wind_vec_z = math.sin(wind_rad)
        
        # Calculate distance to ball
        dx = self.x - ball_pos[0]
        dy = self.y - ball_pos[1]
        dz = self.z - ball_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Wind field flow
        if distance > ball_radius + 20:
            # Far from ball - follow wind direction
            self.vx = wind_vec_x * wind_speed * 0.3
            self.vy = wind_vertical * 0.3
            self.vz = wind_vec_z * wind_speed * 0.3
            
            # Streamline curvature around ball
            if distance < ball_radius + 100:
                influence = (ball_radius + 100 - distance) / 100
                self.vy += (1 if dy > 0 else -1) * influence * wind_speed * 0.1
        else:
            # Flow around ball
            if distance > ball_radius:
                angle = math.atan2(dy, dx)
                self.vx = math.cos(angle + math.pi/2) * wind_speed * 0.3
                self.vy = math.sin(angle + math.pi/2) * wind_speed * 0.3
        
        # Update position
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.z += self.vz * dt * 60
        
        # Reset particles that go out of bounds
        if abs(self.x) > 400 or abs(self.y) > 300 or abs(self.z) > 200:  # 減小邊界
            self.reset_position(wind_vec_x, wind_vec_z)
        
        self.life = max(0, self.life - 1)
    
    def reset_position(self, wind_vec_x, wind_vec_z):
        """Reset particle position based on wind direction"""
        if wind_vec_x > 0:
            self.x = random.uniform(-400, -300)
        elif wind_vec_x < 0:
            self.x = random.uniform(300, 400)
        else:
            self.x = random.uniform(-400, 400)
            
        if wind_vec_z > 0:
            self.z = random.uniform(-200, -100)
        elif wind_vec_z < 0:
            self.z = random.uniform(100, 200)
        else:
            self.z = random.uniform(-200, 200)
            
        self.y = random.uniform(-150, 150)
        self.life = random.randint(200, 255)
        
    def is_alive(self):
        return self.life > 0
class BernoulliSimulation:
    def __init__(self):
        # Initialize window with responsive design - 預設 800x600
        self.current_width = WIDTH
        self.current_height = HEIGHT
        self.screen = pygame.display.set_mode((self.current_width, self.current_height), 
                                            pygame.RESIZABLE | pygame.NOFRAME)
        pygame.display.set_caption("伯努利原理科學模擬 - 雙平面視圖")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.window_controls = WindowControls(self.current_width, self.current_height)
        self.layout = ResponsiveLayout(self.current_width, self.current_height)
        
        # Ball properties - 修正初始位置計算
        content_height = self.current_height - TITLE_BAR_HEIGHT
        ground_level = content_height - 80  # 距離地面的高度
        self.ball_pos = [self.layout.view_width // 2, ground_level + TITLE_BAR_HEIGHT, 0]
        self.ball_radius = 20  # 減小初始半徑以適應小視窗
        self.ball_mass = 0.5  # kg
        self.ball_velocity = [0, 0, 0]  # [vx, vy, vz]
        
        # Wind properties
        self.wind_speed = 15  # 減小初始風速
        self.wind_angle = 0   # degrees
        self.wind_vertical = 0  # m/s
        self.vertical_thrust = 0  # Additional thrust force
        self.side_force_coefficient = 0.2  # Drag coefficient for side force
        
        # Physics state
        self.dragging = False
        self.active_view = None  # "xy" or "zx"
        self.drag_offset = [0, 0]
        
        # Wind visualization
        self.show_wind_vectors = True
        self.wind_arrow_length = 50  # 減小箭頭長度
        
        # Particles for wind visualization - 減少粒子數量
        self.particles = []
        self.particle_surface_xy = pygame.Surface((self.layout.view_width, self.layout.content_height), pygame.SRCALPHA)
        self.particle_surface_xz = pygame.Surface((self.layout.view_width, self.layout.content_height), pygame.SRCALPHA)
        
        for _ in range(150):  # 減少粒子數量
            x = random.uniform(-200, 200)
            y = random.uniform(-150, 150)
            z = random.uniform(-100, 100)
            self.particles.append(Particle(x, y, z))
        
        # Initialize fonts
        self.update_fonts()
        
        # Sliders (簡化標籤以適應小視窗)
        self.sliders = {
            "wind_speed": {"value": self.wind_speed, "min": -30, "max": 30, "text": "風速"},
            "wind_angle": {"value": self.wind_angle, "min": 0, "max": 360, "text": "風向"},
            "wind_vertical": {"value": self.wind_vertical, "min": -15, "max": 15, "text": "垂直風"},
            "ball_radius": {"value": self.ball_radius, "min": 15, "max": 40, "text": "球體大小"},
            "vertical_thrust": {"value": self.vertical_thrust, "min": -500, "max": 500, "text": "推力"},
            "side_force_coeff": {"value": self.side_force_coefficient, "min": 0, "max": 1.0, "text": "側向係數"}
        }
        self.active_slider = None
        
        # Physics data for display
        self.physics_data = {
            "top_pressure": ATMOSPHERIC_PRESSURE,
            "bottom_pressure": ATMOSPHERIC_PRESSURE,
            "pressure_diff": 0,
            "lift_force": 0,
            "side_force": 0,
            "front_force": 0
        }
        
        # Window resize options - 修正預設索引
        self.resize_options = [
            (800, 600, "小視窗"),
            (1024, 768, "中視窗"),
            (1280, 720, "大視窗"),
            (1400, 800, "標準大小"),
            (1600, 900, "超大視窗")
        ]
        self.current_resize_index = 0  # 預設為小視窗 (800x600)
    
    def update_fonts(self):
        """Update fonts based on current layout"""
        preferred_fonts = ['Noto Sans TC', 'Microsoft JhengHei', 'Segoe UI', 'Arial']
        self.font = pygame.font.SysFont(preferred_fonts, self.layout.base_font_size)
        self.title_font = pygame.font.SysFont(preferred_fonts, self.layout.title_font_size, bold=True)
    
    def resize_window(self, new_width, new_height):
        """Handle window resizing with minimum size constraints"""
        # Enforce minimum size
        new_width = max(MIN_WIDTH, new_width)
        new_height = max(MIN_HEIGHT, new_height)
        
        if new_width != self.current_width or new_height != self.current_height:
            self.current_width = new_width
            self.current_height = new_height
            
            # Update screen
            self.screen = pygame.display.set_mode((self.current_width, self.current_height), 
                                                pygame.RESIZABLE | pygame.NOFRAME)
            
            # Update components
            self.window_controls.update_size(self.current_width, self.current_height)
            self.layout.update_layout(self.current_width, self.current_height)
            
            # Update fonts
            self.update_fonts()
            
            # Resize particle surfaces
            self.particle_surface_xy = pygame.Surface((self.layout.view_width, self.layout.content_height), 
                                                    pygame.SRCALPHA)
            self.particle_surface_xz = pygame.Surface((self.layout.view_width, self.layout.content_height), 
                                                    pygame.SRCALPHA)
            
            # Adjust ball position if needed - 修正位置約束
            content_height = self.current_height - TITLE_BAR_HEIGHT
            max_x = self.layout.view_width - self.ball_radius
            max_y = content_height - self.ball_radius + TITLE_BAR_HEIGHT
            
            self.ball_pos[0] = max(self.ball_radius, min(self.ball_pos[0], max_x))
            self.ball_pos[1] = max(self.ball_radius + TITLE_BAR_HEIGHT, min(self.ball_pos[1], max_y))
    
    def cycle_window_size(self):
        """Cycle through predefined window sizes"""
        self.current_resize_index = (self.current_resize_index + 1) % len(self.resize_options)
        new_width, new_height, _ = self.resize_options[self.current_resize_index]
        self.resize_window(new_width, new_height)
    
    def calculate_bernoulli_effect(self):
        """Calculate Bernoulli effect with improved accuracy"""
        # Convert wind direction to vector
        wind_rad = math.radians(self.wind_angle)
        wind_x = self.wind_speed * math.cos(wind_rad)
        wind_z = self.wind_speed * math.sin(wind_rad)
        wind_y = self.wind_vertical
        
        # Calculate relative wind speed
        relative_wind_speed = math.sqrt(wind_x**2 + wind_y**2 + wind_z**2)
        
        # Ball properties
        ball_radius_m = self.ball_radius / 100.0  # Convert pixels to meters
        ball_area = math.pi * ball_radius_m**2
        ball_mass = (4/3) * math.pi * (ball_radius_m**3) * 500  # Assume density 500 kg/m³
        self.ball_mass = ball_mass
        
        # Only calculate lift if there's significant wind
        if relative_wind_speed > 0.5:  # Minimum wind threshold
            # Magnus effect and flow separation
            top_velocity = relative_wind_speed * 1.4
            bottom_velocity = relative_wind_speed * 0.8
            
            # Add angle factor for more realistic lift
            angle_factor = abs(math.sin(wind_rad)) * 0.3
            lift_coefficient = 0.5 * (1 + angle_factor)
            
            # Calculate pressure using Bernoulli equation
            top_pressure = ATMOSPHERIC_PRESSURE - 0.5 * AIR_DENSITY * top_velocity**2
            bottom_pressure = ATMOSPHERIC_PRESSURE - 0.5 * AIR_DENSITY * bottom_velocity**2
            
            pressure_difference = bottom_pressure - top_pressure
            
            # Calculate forces
            lift_force = pressure_difference * ball_area * lift_coefficient + self.vertical_thrust
            side_force = wind_x * AIR_DENSITY * ball_area * self.side_force_coefficient
            front_force = wind_z * AIR_DENSITY * ball_area * self.side_force_coefficient
        else:
            # No significant wind - no lift, only thrust
            top_pressure = ATMOSPHERIC_PRESSURE
            bottom_pressure = ATMOSPHERIC_PRESSURE
            pressure_difference = 0
            lift_force = self.vertical_thrust  # Only manual thrust
            side_force = 0
            front_force = 0
        
        # Update physics data
        self.physics_data.update({
            "top_pressure": top_pressure,
            "bottom_pressure": bottom_pressure,
            "pressure_diff": pressure_difference,
            "lift_force": lift_force,
            "side_force": side_force,
            "front_force": front_force,
            "ball_mass": ball_mass
        })
        
        return {
            "lift": lift_force,
            "side": side_force,
            "front": front_force,
            "ball_mass": ball_mass,
            "net_force": lift_force
        }
    
    def update_ball_physics(self, dt):
        """Update ball physics with proper 3D motion and gravity"""
        if self.dragging:
            return
        
        forces = self.calculate_bernoulli_effect()
        ball_mass = forces["ball_mass"]
        
        # Gravity affects all directions - primarily Y (downward) but also Z if tilted
        weight_y = ball_mass * GRAVITY  # Primary gravity downward
        weight_z = ball_mass * GRAVITY * 0.05  # Small Z-component gravity
        
        # Calculate net forces and accelerations
        net_force_y = forces["lift"] - weight_y  # Y direction (screen up/down)
        net_force_x = forces["side"]  # X direction (screen left/right)
        net_force_z = forces["front"] - weight_z  # Z direction (depth)
        
        acceleration_y = net_force_y / ball_mass if ball_mass > 0 else 0
        acceleration_x = net_force_x / ball_mass if ball_mass > 0 else 0
        acceleration_z = net_force_z / ball_mass if ball_mass > 0 else 0
        
        # Update velocities
        self.ball_velocity[1] += acceleration_y * dt * 30  # 減小加速度係數
        self.ball_velocity[0] += acceleration_x * dt * 30
        self.ball_velocity[2] += acceleration_z * dt * 30
        
        # Update positions
        self.ball_pos[1] += self.ball_velocity[1] * dt
        self.ball_pos[0] += self.ball_velocity[0] * dt
        self.ball_pos[2] += self.ball_velocity[2] * dt
        
        # Apply damping
        content_height = self.current_height - TITLE_BAR_HEIGHT
        ground_level = content_height - self.ball_radius - 30 + TITLE_BAR_HEIGHT
        
        if abs(self.ball_pos[1] - ground_level) < 10 and abs(self.ball_velocity[1]) < 5:
            # Strong damping near ground
            for i in range(3):
                self.ball_velocity[i] *= 0.9
        else:
            # Normal damping
            for i in range(3):
                self.ball_velocity[i] *= 0.98
        
        # Boundary constraints
        self.apply_boundary_constraints()
    
    def apply_boundary_constraints(self):
        """Apply boundary constraints to keep ball in view with proper physics"""
        content_height = self.current_height - TITLE_BAR_HEIGHT
        
        # Y boundaries (ground and ceiling) - adjusted for title bar
        ground_level = content_height - self.ball_radius - 30 + TITLE_BAR_HEIGHT
        ceiling_level = self.ball_radius + 30 + TITLE_BAR_HEIGHT
        
        if self.ball_pos[1] >= ground_level:
            self.ball_pos[1] = ground_level
            if abs(self.ball_velocity[1]) < 2:
                self.ball_velocity[1] = 0
            else:
                self.ball_velocity[1] = -abs(self.ball_velocity[1]) * 0.3
        elif self.ball_pos[1] <= ceiling_level:
            self.ball_pos[1] = ceiling_level
            self.ball_velocity[1] = abs(self.ball_velocity[1]) * 0.3
        
        # X boundaries (left and right walls)
        left_wall = self.ball_radius
        right_wall = self.layout.view_width - self.ball_radius
        
        if self.ball_pos[0] <= left_wall:
            self.ball_pos[0] = left_wall
            if abs(self.ball_velocity[0]) < 2:
                self.ball_velocity[0] = 0
            else:
                self.ball_velocity[0] = abs(self.ball_velocity[0]) * 0.3
        elif self.ball_pos[0] >= right_wall:
            self.ball_pos[0] = right_wall
            if abs(self.ball_velocity[0]) < 2:
                self.ball_velocity[0] = 0
            else:
                self.ball_velocity[0] = -abs(self.ball_velocity[0]) * 0.3
        
        # Z boundaries (front and back walls) - 修正Z邊界
        max_z = content_height // 4
        min_z = -content_height // 4
        ground_z = content_height // 6
        
        if self.ball_pos[2] >= max_z:
            self.ball_pos[2] = max_z
            if abs(self.ball_velocity[2]) < 2:
                self.ball_velocity[2] = 0
            else:
                self.ball_velocity[2] = -abs(self.ball_velocity[2]) * 0.3
        elif self.ball_pos[2] <= min_z:
            self.ball_pos[2] = min_z
            if abs(self.ball_velocity[2]) < 2:
                self.ball_velocity[2] = 0
            else:
                self.ball_velocity[2] = abs(self.ball_velocity[2]) * 0.3
        
        # Z方向地面約束
        if self.ball_pos[2] >= ground_z:
            self.ball_pos[2] = ground_z
            if abs(self.ball_velocity[2]) < 2:
                self.ball_velocity[2] = 0
            elif self.ball_velocity[2] > 0:
                self.ball_velocity[2] = -abs(self.ball_velocity[2]) * 0.3
    
    def get_ball_color(self):
        """Get ball color based on lift force"""
        forces = self.calculate_bernoulli_effect()
        weight = forces["ball_mass"] * GRAVITY
        
        if forces["lift"] > weight * 1.1:
            return GREEN  # Strong lift - rising
        elif forces["lift"] > weight * 0.9:
            return YELLOW  # Balanced
        else:
            return RED  # Falling (gravity dominates)
    
    def draw_particles(self):
        """Draw wind field particles on both views"""
        # Clear particle surfaces
        self.particle_surface_xy.fill((0, 0, 0, 0))
        self.particle_surface_xz.fill((0, 0, 0, 0))
        
        for particle in self.particles:
            if particle.is_alive():
                # XY view (left panel) - 修正縮放計算
                screen_x = int((particle.x + 200) * self.layout.scale_x)
                screen_y = int((particle.y + 150) * self.layout.scale_y)
                
                if 0 <= screen_x < self.layout.view_width and 0 <= screen_y < self.layout.content_height:
                    size = max(1, int(particle.size * self.layout.global_scale))
                    pygame.draw.circle(self.particle_surface_xy, particle.color, (screen_x, screen_y), size)
                
                # ZX view (right panel) - X horizontal, Z vertical with scaling
                screen_x_zx = int((particle.x + 200) * self.layout.scale_x)
                screen_y_zx = int((150 - particle.z) * self.layout.scale_y)
                
                if 0 <= screen_x_zx < self.layout.view_width and 0 <= screen_y_zx < self.layout.content_height:
                    size = max(1, int(particle.size * self.layout.global_scale))
                    pygame.draw.circle(self.particle_surface_xz, particle.color, (screen_x_zx, screen_y_zx), size)
        
        # Blit particle surfaces to main screen
        self.screen.blit(self.particle_surface_xy, (LEFT_TOOLBAR_WIDTH, TITLE_BAR_HEIGHT))
        self.screen.blit(self.particle_surface_xz, (LEFT_TOOLBAR_WIDTH + self.layout.view_width, TITLE_BAR_HEIGHT))
    
    def draw_ball(self):
        """Draw the ball on both XY and ZX views"""
        ball_color = self.get_ball_color()
        
        # XY view (left panel) - shows X and Y coordinates
        ball_x_xy = int(self.ball_pos[0] * self.layout.scale_x) + LEFT_TOOLBAR_WIDTH
        ball_y_xy = int((self.ball_pos[1] - TITLE_BAR_HEIGHT) * self.layout.scale_y) + TITLE_BAR_HEIGHT
        
        # Use scaled radius
        display_radius_xy = max(5, int(self.ball_radius * self.layout.global_scale))
        
        # Draw shadow with scaled offset
        shadow_offset = max(1, int(2 * self.layout.global_scale))
        pygame.draw.circle(self.screen, (50, 50, 50), 
                         (ball_x_xy + shadow_offset, ball_y_xy + shadow_offset), 
                         display_radius_xy)
        
        # Draw ball
        pygame.draw.circle(self.screen, ball_color, (ball_x_xy, ball_y_xy), display_radius_xy)
        pygame.draw.circle(self.screen, BLACK, (ball_x_xy, ball_y_xy), display_radius_xy, 
                         max(1, int(1 * self.layout.global_scale)))
        
        # Add highlight
        highlight_x = ball_x_xy - display_radius_xy // 3
        highlight_y = ball_y_xy - display_radius_xy // 3
        pygame.draw.circle(self.screen, WHITE, (highlight_x, highlight_y), 
                         max(1, display_radius_xy // 4))
        
        # ZX view (right panel) - shows X and Z coordinates
        ball_x_zx = int(self.ball_pos[0] * self.layout.scale_x) + LEFT_TOOLBAR_WIDTH + self.layout.view_width
        ball_y_zx = int((self.layout.content_height // 2 - self.ball_pos[2]) * self.layout.scale_y) + TITLE_BAR_HEIGHT
        
        # Use scaled radius
        display_radius_zx = max(5, int(self.ball_radius * self.layout.global_scale))
        
        # Draw shadow
        pygame.draw.circle(self.screen, (50, 50, 50), 
                         (ball_x_zx + shadow_offset, ball_y_zx + shadow_offset), 
                         display_radius_zx)
        
        # Draw ball
        pygame.draw.circle(self.screen, ball_color, (ball_x_zx, ball_y_zx), display_radius_zx)
        pygame.draw.circle(self.screen, BLACK, (ball_x_zx, ball_y_zx), display_radius_zx, 
                         max(1, int(1 * self.layout.global_scale)))
        
        # Add highlight
        highlight_x_zx = ball_x_zx - display_radius_zx // 3
        highlight_y_zx = ball_y_zx - display_radius_zx // 3
        pygame.draw.circle(self.screen, WHITE, (highlight_x_zx, highlight_y_zx), 
                         max(1, display_radius_zx // 4))
    
    def draw_left_toolbar(self):
        """Draw the left toolbar with controls and info"""
        toolbar_rect = self.layout.get_toolbar_rect()
        
        # Background
        pygame.draw.rect(self.screen, LIGHT_GRAY, toolbar_rect)
        pygame.draw.line(self.screen, BLACK, (LEFT_TOOLBAR_WIDTH, TITLE_BAR_HEIGHT), 
                        (LEFT_TOOLBAR_WIDTH, self.current_height), 1)
        
        # Title
        title = self.title_font.render("控制面板", True, BLACK)
        title_rect = title.get_rect(center=(LEFT_TOOLBAR_WIDTH // 2, TITLE_BAR_HEIGHT + 15))
        self.screen.blit(title, title_rect)
        
        # Draw sliders - 調整間距以適應小視窗
        y_offset = TITLE_BAR_HEIGHT + 35
        slider_width = LEFT_TOOLBAR_WIDTH - 15
        y_increment = max(45, int(self.layout.content_height * 0.08))  # 減小間距
        
        mouse_pos = pygame.mouse.get_pos()
        
        for key, slider in self.sliders.items():
            if y_offset + 30 < self.current_height - 120:  # 確保有空間顯示物理數據
                self.draw_slider(key, slider, LEFT_TOOLBAR_WIDTH // 2, slider_width, y_offset, mouse_pos)
                y_offset += y_increment
        
        # Draw physics info
        self.draw_physics_info_in_toolbar(y_offset + 10)
        
        # Draw window size info
        self.draw_window_size_info()
    
    def draw_slider(self, key, slider, center_x, slider_width, y_offset, mouse_pos):
        """Draw a horizontal slider in the left toolbar"""
        slider_length = slider_width
        slider_thickness = max(3, int(6 * self.layout.global_scale))
        slider_x = center_x - slider_length // 2
        slider_y = y_offset + 15
        
        # Slider track
        track_rect = pygame.Rect(slider_x, slider_y - slider_thickness // 2, 
                               slider_length, slider_thickness)
        pygame.draw.rect(self.screen, GRAY, track_rect, border_radius=max(1, int(3 * self.layout.global_scale)))
        
        # Slider fill
        value_range = slider["max"] - slider["min"]
        if value_range != 0:
            percent = (slider["value"] - slider["min"]) / value_range
        else:
            percent = 0
        selected_length = int(slider_length * percent)
        
        if selected_length > 0:
            fill_rect = pygame.Rect(slider_x, slider_y - slider_thickness // 2, 
                                  selected_length, slider_thickness)
            pygame.draw.rect(self.screen, BLUE, fill_rect, border_radius=max(1, int(3 * self.layout.global_scale)))
        
        # Slider handle
        handle_radius = max(4, int(8 * self.layout.global_scale))
        handle_center = (slider_x + selected_length, slider_y)
        
        # Check if mouse is hovering over handle
        hovering = (mouse_pos[0] - handle_center[0]) ** 2 + (mouse_pos[1] - handle_center[1]) ** 2 <= handle_radius ** 2
        handle_color = DARK_BLUE if hovering or self.active_slider == key else BLUE
        
        pygame.draw.circle(self.screen, handle_color, handle_center, handle_radius)
        pygame.draw.circle(self.screen, BLACK, handle_center, handle_radius, 1)
        
        # Slider label and value - 簡化顯示
        if key == "ball_radius":
            ball_mass = self.physics_data.get("ball_mass", 0.5)
            value_text = f"球體: {slider['value']:.0f}px"
            mass_text = f"質量: {ball_mass:.2f}kg"
            
            label_surf = self.font.render(value_text, True, BLACK)
            mass_surf = self.font.render(mass_text, True, BLACK)
            
            label_rect = label_surf.get_rect(center=(center_x, y_offset - 2))
            mass_rect = mass_surf.get_rect(center=(center_x, y_offset + 25))
            
            self.screen.blit(label_surf, label_rect)
            self.screen.blit(mass_surf, mass_rect)
        else:
            # 簡化標籤文字
            short_labels = {
                "wind_speed": f"風速: {slider['value']:.1f}",
                "wind_angle": f"風向: {slider['value']:.0f}°",
                "wind_vertical": f"垂直: {slider['value']:.1f}",
                "vertical_thrust": f"推力: {slider['value']:.0f}N",
                "side_force_coeff": f"側向: {slider['value']:.2f}"
            }
            
            value_text = short_labels.get(key, f"{slider['text']}: {slider['value']:.1f}")
            
            label_surf = self.font.render(value_text, True, BLACK)
            label_rect = label_surf.get_rect(center=(center_x, y_offset - 2))
            self.screen.blit(label_surf, label_rect)
    
    def draw_physics_info_in_toolbar(self, start_y):
        """Draw physics information in the left toolbar"""
        if start_y + 80 > self.current_height - 40:  # 檢查是否有足夠空間
            return
            
        info_title = self.font.render("物理數據", True, DARK_BLUE)
        title_rect = info_title.get_rect(center=(LEFT_TOOLBAR_WIDTH // 2, start_y))
        self.screen.blit(info_title, title_rect)
        
        y_pos = start_y + 18
        line_height = max(12, int(14 * self.layout.global_scale))
        
        # 簡化物理資訊顯示
        physics_info = [
            f"位置: ({self.ball_pos[0]:.0f},{self.ball_pos[1]:.0f},{self.ball_pos[2]:.0f})",
            f"升力: {self.physics_data['lift_force']:.1f}N",
            f"側力: {self.physics_data['side_force']:.1f}N"
        ]
        
        for info in physics_info:
            if y_pos + line_height < self.current_height - 40:
                text_surf = self.font.render(info, True, DARK_BLUE)
                text_rect = text_surf.get_rect(center=(LEFT_TOOLBAR_WIDTH // 2, y_pos))
                self.screen.blit(text_surf, text_rect)
                y_pos += line_height
    
    def draw_window_size_info(self):
        """Draw current window size info at bottom of toolbar"""
        current_size = self.resize_options[self.current_resize_index]
        size_text = f"{current_size[2]}"
        size_surf = self.font.render(size_text, True, BLACK)
        size_rect = size_surf.get_rect(center=(LEFT_TOOLBAR_WIDTH // 2, self.current_height - 25))
        self.screen.blit(size_surf, size_rect)
        
        # Instructions
        instruction_text = "點縮放按鈕切換"
        instruction_surf = self.font.render(instruction_text, True, GRAY)
        instruction_rect = instruction_surf.get_rect(center=(LEFT_TOOLBAR_WIDTH // 2, self.current_height - 10))
        self.screen.blit(instruction_surf, instruction_rect)
    
    def draw_ui(self):
        """Draw the complete UI with dual views and controls"""
        # Draw view separators
        line_width = max(1, int(2 * self.layout.global_scale))
        pygame.draw.line(self.screen, BLACK, 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, TITLE_BAR_HEIGHT), 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, self.current_height), line_width)
        
        # View labels - 簡化標籤
        xy_label = self.title_font.render("XY視圖", True, BLACK)
        self.screen.blit(xy_label, (LEFT_TOOLBAR_WIDTH + 5, TITLE_BAR_HEIGHT + 5))
        
        zx_label = self.title_font.render("XZ視圖", True, BLACK)
        self.screen.blit(zx_label, (LEFT_TOOLBAR_WIDTH + self.layout.view_width + 5, TITLE_BAR_HEIGHT + 5))
        
        # Draw coordinate axes and boundaries
        self.draw_boundaries()
        self.draw_axes()
        self.draw_wind_vectors()
        
        # Draw left toolbar
        self.draw_left_toolbar()
        
        # Draw instructions in right views
        self.draw_instructions()
    
    def draw_boundaries(self):
        """Draw ground and ceiling boundaries"""
        content_height = self.current_height - TITLE_BAR_HEIGHT
        ground_y = int(content_height - 30 * self.layout.scale_y) + TITLE_BAR_HEIGHT
        ceiling_y = int(30 * self.layout.scale_y) + TITLE_BAR_HEIGHT
        
        # Draw ground line on both views
        line_width = max(1, int(2 * self.layout.global_scale))
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (LEFT_TOOLBAR_WIDTH, ground_y), 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, ground_y), line_width)
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, ground_y), 
                        (self.current_width, ground_y), line_width)
        
        # Draw ceiling line on both views
        ceiling_line_width = max(1, int(1 * self.layout.global_scale))
        pygame.draw.line(self.screen, GRAY, 
                        (LEFT_TOOLBAR_WIDTH, ceiling_y), 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, ceiling_y), ceiling_line_width)
        pygame.draw.line(self.screen, GRAY, 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, ceiling_y), 
                        (self.current_width, ceiling_y), ceiling_line_width)
        
        # Z方向地面線 (在XZ視圖中顯示)
        z_ground_y = int((content_height // 2 + content_height // 6) * self.layout.scale_y) + TITLE_BAR_HEIGHT
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (LEFT_TOOLBAR_WIDTH + self.layout.view_width, z_ground_y), 
                        (self.current_width, z_ground_y), line_width)
    
    def draw_axes(self):
        """Draw coordinate axes on both views"""
        axes_length = max(20, int(30 * self.layout.global_scale))
        
        # XY view axes (bottom-left corner)
        origin_xy = (LEFT_TOOLBAR_WIDTH + max(15, int(20 * self.layout.global_scale)), 
                    int(self.current_height - 40 * self.layout.scale_y))
        
        # X axis (horizontal, red)
        line_width = max(1, int(1 * self.layout.global_scale))
        pygame.draw.line(self.screen, RED, origin_xy, 
                        (origin_xy[0] + axes_length, origin_xy[1]), line_width)
        x_label = self.font.render("X", True, RED)
        self.screen.blit(x_label, (origin_xy[0] + axes_length + 2, origin_xy[1] - 6))
        
        # Y axis (vertical, green)
        pygame.draw.line(self.screen, GREEN, origin_xy, 
                        (origin_xy[0], origin_xy[1] - axes_length), line_width)
        y_label = self.font.render("Y", True, GREEN)
        self.screen.blit(y_label, (origin_xy[0] - 8, origin_xy[1] - axes_length - 3))
        
        # ZX view axes (bottom-left corner of right panel)
        origin_zx = (LEFT_TOOLBAR_WIDTH + self.layout.view_width + max(15, int(20 * self.layout.global_scale)), 
                    int(self.current_height - 40 * self.layout.scale_y))
        
        # X axis (horizontal, red)
        pygame.draw.line(self.screen, RED, origin_zx, 
                        (origin_zx[0] + axes_length, origin_zx[1]), line_width)
        x_label_zx = self.font.render("X", True, RED)
        self.screen.blit(x_label_zx, (origin_zx[0] + axes_length + 2, origin_zx[1] - 6))
        
        # Z axis (vertical, blue)
        pygame.draw.line(self.screen, BLUE, origin_zx, 
                        (origin_zx[0], origin_zx[1] - axes_length), line_width)
        z_label = self.font.render("Z", True, BLUE)
        self.screen.blit(z_label, (origin_zx[0] - 8, origin_zx[1] - axes_length - 3))
    
    def draw_wind_vectors(self):
        """Draw wind speed and direction vectors"""
        if not self.show_wind_vectors:
            return
        
        # Calculate wind components
        wind_rad = math.radians(self.wind_angle)
        wind_x = self.wind_speed * math.cos(wind_rad)
        wind_z = self.wind_speed * math.sin(wind_rad)
        
        # Scale for display - 減小箭頭大小
        scale = 1.5
        arrow_x = wind_x * scale * self.layout.global_scale
        arrow_z = wind_z * scale * self.layout.global_scale
        arrow_y = self.wind_vertical * scale * self.layout.global_scale
        
        # XY view wind vector (left panel)
        center_xy = (LEFT_TOOLBAR_WIDTH + self.layout.view_width // 2, 
                    int(self.layout.content_height // 2 + TITLE_BAR_HEIGHT))
        
        # Draw wind vectors if significant
        if abs(arrow_x) > 2 * self.layout.global_scale:
            end_x = int(center_xy[0] + arrow_x)
            line_width = max(1, int(2 * self.layout.global_scale))
            pygame.draw.line(self.screen, RED, center_xy, (end_x, center_xy[1]), line_width)
            self.draw_arrow_head((end_x, center_xy[1]), arrow_x > 0, RED, horizontal=True)
        
        if abs(arrow_y) > 2 * self.layout.global_scale:
            end_y = int(center_xy[1] - arrow_y)
            line_width = max(1, int(2 * self.layout.global_scale))
            pygame.draw.line(self.screen, GREEN, center_xy, (center_xy[0], end_y), line_width)
            self.draw_arrow_head((center_xy[0], end_y), arrow_y > 0, GREEN, horizontal=False)
        
        # XZ view wind vector (right panel)
        center_xz = (LEFT_TOOLBAR_WIDTH + self.layout.view_width + self.layout.view_width // 2, 
                    int(self.layout.content_height // 2 + TITLE_BAR_HEIGHT))
        
        if abs(arrow_x) > 2 * self.layout.global_scale:
            end_x_xz = int(center_xz[0] + arrow_x)
            line_width = max(1, int(2 * self.layout.global_scale))
            pygame.draw.line(self.screen, RED, center_xz, (end_x_xz, center_xz[1]), line_width)
            self.draw_arrow_head((end_x_xz, center_xz[1]), arrow_x > 0, RED, horizontal=True)
        
        if abs(arrow_z) > 2 * self.layout.global_scale:
            end_z_xz = int(center_xz[1] - arrow_z)
            line_width = max(1, int(2 * self.layout.global_scale))
            pygame.draw.line(self.screen, BLUE, center_xz, (center_xz[0], end_z_xz), line_width)
            self.draw_arrow_head((center_xz[0], end_z_xz), arrow_z > 0, BLUE, horizontal=False)
    
    def draw_arrow_head(self, pos, pointing_right_or_up, color, horizontal=True):
        """Draw arrow head at the end of wind vector"""
        x, y = pos
        size = max(2, int(4 * self.layout.global_scale))
        
        if horizontal:
            if pointing_right_or_up:  # Pointing right
                points = [(x, y), (x - size, y - size//2), (x - size, y + size//2)]
            else:  # Pointing left
                points = [(x, y), (x + size, y - size//2), (x + size, y + size//2)]
        else:
            if pointing_right_or_up:  # Pointing up
                points = [(x, y), (x - size//2, y + size), (x + size//2, y + size)]
            else:  # Pointing down
                points = [(x, y), (x - size//2, y - size), (x + size//2, y - size)]
        
        pygame.draw.polygon(self.screen, color, points)
    
    def draw_instructions(self):
        """Draw instructions in the view areas"""
        instructions = [
            "🖱️ 拖拽球體",
            "🎛️ 左側控制",
            "🌬️ V鍵風速圖",
            "💡 🟢上升 🔴下降"
        ]
        
        y_pos = TITLE_BAR_HEIGHT + 25
        line_height = max(12, int(15 * self.layout.global_scale))
        for instruction in instructions:
            if y_pos + line_height < self.current_height - 50:
                text_surf = self.font.render(instruction, True, BLACK)
                # 在右側視圖顯示說明
                self.screen.blit(text_surf, (LEFT_TOOLBAR_WIDTH + self.layout.view_width + 5, y_pos))
                y_pos += line_height
    
    def handle_slider_interaction(self, pos):
        """Handle slider clicks and updates in left toolbar"""
        if pos[0] >= LEFT_TOOLBAR_WIDTH:  # Not in toolbar
            return False
        
        center_x = LEFT_TOOLBAR_WIDTH // 2
        slider_width = LEFT_TOOLBAR_WIDTH - 15
        y_offset = TITLE_BAR_HEIGHT + 35
        y_increment = max(45, int(self.layout.content_height * 0.08))
        
        for key in self.sliders:
            slider_rect = pygame.Rect(
                center_x - slider_width // 2,
                y_offset + 5,
                slider_width,
                25
            )
            
            if slider_rect.collidepoint(pos):
                self.active_slider = key
                self.update_slider_value(key, pos[0])
                return True
            
            y_offset += y_increment
            if y_offset + 30 >= self.current_height - 120:  # 避免超出範圍
                break
        
        return False
    
    def update_slider_value(self, key, mouse_x):
        """Update slider value based on mouse position"""
        center_x = LEFT_TOOLBAR_WIDTH // 2
        slider_width = LEFT_TOOLBAR_WIDTH - 15
        slider_x = center_x - slider_width // 2
        
        # Calculate position ratio
        ratio = max(0, min(1, (mouse_x - slider_x) / slider_width))
        
        slider = self.sliders[key]
        value_range = slider["max"] - slider["min"]
        new_value = slider["min"] + ratio * value_range
        
        # Update slider value
        slider["value"] = new_value
        
        # Update simulation parameters
        if key == "wind_speed":
            self.wind_speed = new_value
        elif key == "wind_angle":
            self.wind_angle = new_value
        elif key == "wind_vertical":
            self.wind_vertical = new_value
        elif key == "ball_radius":
            self.ball_radius = new_value
        elif key == "vertical_thrust":
            self.vertical_thrust = new_value
        elif key == "side_force_coeff":
            self.side_force_coefficient = new_value
    
    def handle_ball_interaction(self, pos, event_type):
        """Handle ball dragging in both views"""
        if event_type == "down":
            # Check XY view (left panel)
            if (LEFT_TOOLBAR_WIDTH <= pos[0] < LEFT_TOOLBAR_WIDTH + self.layout.view_width and 
                pos[1] > TITLE_BAR_HEIGHT):
                
                ball_screen_x = int(self.ball_pos[0] * self.layout.scale_x) + LEFT_TOOLBAR_WIDTH
                ball_screen_y = int((self.ball_pos[1] - TITLE_BAR_HEIGHT) * self.layout.scale_y) + TITLE_BAR_HEIGHT
                scaled_radius = max(5, int(self.ball_radius * self.layout.global_scale))
                
                ball_distance = math.sqrt((pos[0] - ball_screen_x)**2 + 
                                        (pos[1] - ball_screen_y)**2)
                if ball_distance <= scaled_radius + 5:  # 增加點擊容錯範圍
                    self.dragging = True
                    self.active_view = "xy"
                    self.drag_offset = [pos[0] - ball_screen_x, pos[1] - ball_screen_y]
                    self.ball_velocity = [0, 0, 0]  # Reset velocity
                    return True
            
            # Check ZX view (right panel)
            elif (pos[0] > LEFT_TOOLBAR_WIDTH + self.layout.view_width and pos[1] > TITLE_BAR_HEIGHT):
                zx_x = pos[0] - (LEFT_TOOLBAR_WIDTH + self.layout.view_width)
                ball_x_screen = int(self.ball_pos[0] * self.layout.scale_x)
                ball_z_screen = int((self.layout.content_height // 2 - self.ball_pos[2]) * self.layout.scale_y) + TITLE_BAR_HEIGHT
                scaled_radius = max(5, int(self.ball_radius * self.layout.global_scale))
                
                ball_distance = math.sqrt((zx_x - ball_x_screen)**2 + 
                                        (pos[1] - ball_z_screen)**2)
                if ball_distance <= scaled_radius + 5:  # 增加點擊容錯範圍
                    self.dragging = True
                    self.active_view = "zx"
                    self.drag_offset = [zx_x - ball_x_screen, pos[1] - ball_z_screen]
                    self.ball_velocity = [0, 0, 0]  # Reset velocity
                    return True
        
        elif event_type == "motion" and self.dragging:
            if self.active_view == "xy":
                # Update X and Y coordinates
                screen_x = pos[0] - self.drag_offset[0] - LEFT_TOOLBAR_WIDTH
                screen_y = pos[1] - self.drag_offset[1]
                
                # Convert screen coordinates back to ball coordinate space
                new_x = screen_x / self.layout.scale_x
                new_y = (screen_y - TITLE_BAR_HEIGHT) / self.layout.scale_y + TITLE_BAR_HEIGHT
                
                # Constrain to view bounds
                max_x = (self.layout.view_width / self.layout.scale_x) - self.ball_radius
                max_y = (self.layout.content_height / self.layout.scale_y) - self.ball_radius + TITLE_BAR_HEIGHT
                
                self.ball_pos[0] = max(self.ball_radius, min(max_x, new_x))
                self.ball_pos[1] = max(self.ball_radius + TITLE_BAR_HEIGHT, min(max_y, new_y))
            
            elif self.active_view == "zx":
                # Update X and Z coordinates
                zx_x = pos[0] - (LEFT_TOOLBAR_WIDTH + self.layout.view_width)
                screen_x = zx_x - self.drag_offset[0]
                screen_z_pos = pos[1] - self.drag_offset[1]
                
                # Convert back to ball coordinate space
                new_x = screen_x / self.layout.scale_x
                new_z = (self.layout.content_height // 2 / self.layout.scale_y - 
                        (screen_z_pos - TITLE_BAR_HEIGHT) / self.layout.scale_y)
                
                # Constrain to bounds
                max_x = (self.layout.view_width / self.layout.scale_x) - self.ball_radius
                max_z = self.layout.content_height // 4 / self.layout.scale_y
                
                self.ball_pos[0] = max(self.ball_radius, min(max_x, new_x))
                self.ball_pos[2] = max(-max_z, min(max_z, new_z))
        
        return False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Handle window control buttons first
                    action = self.window_controls.handle_click(event.pos)
                    if action == "close":
                        return False
                    elif action == "minimize":
                        pygame.display.iconify()
                        continue
                    elif action == "resize":
                        self.cycle_window_size()  # 循環切換視窗大小
                        continue
                    elif action == "drag_start":
                        self.window_controls.dragging_window = True
                        self.window_controls.drag_offset = event.pos
                        continue
                    
                    # Try ball interaction first
                    if not self.handle_ball_interaction(event.pos, "down"):
                        # Try slider interaction
                        self.handle_slider_interaction(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.active_view = None
                    self.active_slider = None
                    self.window_controls.dragging_window = False
            
            elif event.type == pygame.MOUSEMOTION:
                # Handle window control button hover effects
                self.window_controls.handle_mouse_motion(event.pos)
                
                # Handle window dragging (placeholder - would need platform-specific code)
                if self.window_controls.dragging_window:
                    pass  # Window dragging would be implemented here
                elif self.dragging:
                    self.handle_ball_interaction(event.pos, "motion")
                elif self.active_slider:
                    self.update_slider_value(self.active_slider, event.pos[0])
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self.show_wind_vectors = not self.show_wind_vectors
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.cycle_window_size()  # R鍵也可以切換視窗大小
            
            elif event.type == pygame.VIDEORESIZE:
                self.resize_window(event.w, event.h)
        
        return True
    
    def generate_particles(self):
        """Generate new particles to replace dead ones"""
        dead_count = sum(1 for p in self.particles if not p.is_alive())
        
        for _ in range(min(dead_count, 3)):  # Replace fewer particles each frame
            x = random.uniform(-200, 200)
            y = random.uniform(-150, 150)
            z = random.uniform(-100, 100)
            self.particles.append(Particle(x, y, z))
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def run(self):
        """Main simulation loop"""
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = min(0.1, (current_time - last_time) / 1000.0)
            last_time = current_time
            
            # Handle events
            running = self.handle_events()
            
            # Update physics
            self.update_ball_physics(dt)
            
            # Update particles
            for particle in self.particles:
                particle.update(self.wind_speed, self.wind_angle, self.wind_vertical,
                              self.ball_pos, self.ball_radius, dt)
            
            # Generate new particles
            self.generate_particles()
            
            # Draw everything
            self.screen.fill(WHITE)
            
            # Draw title bar first
            self.window_controls.draw(self.screen)
            
            # Draw view backgrounds
            left_view, right_view = self.layout.get_view_rects()
            
            pygame.draw.rect(self.screen, LIGHT_BLUE, left_view)
            pygame.draw.rect(self.screen, LIGHT_BLUE, right_view)
            
            # Draw particles and ball
            self.draw_particles()
            self.draw_ball()
            
            # Draw UI
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = BernoulliSimulation()
    simulation.run()
