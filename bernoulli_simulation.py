import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Get display info for responsive design
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Constants - now responsive to screen size
WIDTH = min(int(SCREEN_WIDTH * 0.9), 1400)  # 90% of screen width, max 1400px
HEIGHT = min(int(SCREEN_HEIGHT * 0.9), 800)  # 90% of screen height, max 800px
VIEW_WIDTH = int(WIDTH * 0.4)  # 40% of window width for each view
FPS = 60
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
BLUE = (100, 160, 255)
RED = (255, 100, 100)
GREEN = (100, 220, 150)
YELLOW = (255, 230, 100)
GRAY = (220, 220, 230)
LIGHT_GRAY = (245, 245, 250)
DARK_GRAY = (180, 180, 200)
PANEL_BG = (250, 252, 255)
PANEL_SHADOW = (200, 210, 230)

# Physics constants
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = 9.81  # m/s²

class Particle:
    def __init__(self, x, y, z, wind_speed, wind_angle, vertical_wind):
        self.x = x
        self.y = y
        self.z = z  # Added z-coordinate
        self.size = random.randint(1, 3)
        self.color = (200, 200, 255, 150)  # RGBA
        self.wind_speed = wind_speed
        self.wind_angle = wind_angle
        self.vertical_wind = vertical_wind
        self.life = random.randint(50, 150)
        
    def update(self, ball_pos, ball_radius):
        # Convert angle to radians
        angle_rad = math.radians(self.wind_angle)
        
        # Calculate velocity components
        vx = self.wind_speed * math.cos(angle_rad)
        vy = self.wind_speed * math.sin(angle_rad) + self.vertical_wind
        vz = 0  # No z-component for wind by default
        
        # Update position
        self.x += vx * 0.1
        self.y += vy * 0.1
        self.z += vz * 0.1
        
        # Calculate distance to ball in 3D
        dx = self.x - ball_pos[0]
        dy = self.y - ball_pos[1]
        dz = self.z - ball_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # If close to the ball, adjust trajectory to flow around it
        if distance < ball_radius * 1.5:
            # Vector from particle to ball center
            norm = math.sqrt(dx*dx + dy*dy + dz*dz)
            if norm > 0:
                dx /= norm
                dy /= norm
                dz /= norm
                
                # Push particle away from ball
                deflection = (ball_radius * 1.5 - distance) * 0.2
                self.x += dx * deflection
                self.y += dy * deflection
                self.z += dz * deflection
                
                # Add some turbulence
                self.x += random.uniform(-0.5, 0.5)
                self.y += random.uniform(-0.5, 0.5)
                self.z += random.uniform(-0.5, 0.5)
        
        # Decrease life
        self.life -= 1
        
    def is_alive(self):
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT and -VIEW_WIDTH/2 <= self.z <= VIEW_WIDTH/2

class BernoulliSimulation:
    def __init__(self):
        # Set up display with responsive dimensions
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("伯努利原理科学玩具 - Bernoulli Principle Simulation")
        self.clock = pygame.time.Clock()
        
        # Store current window dimensions
        self.current_width = WIDTH
        self.current_height = HEIGHT
        self.current_view_width = VIEW_WIDTH
        self.middle_section_width = int(WIDTH * 0.2)  # 20% of width for middle section
        
        # Create transparent surfaces for particles in each view
        self.particle_surface_xy = pygame.Surface((VIEW_WIDTH, HEIGHT), pygame.SRCALPHA)
        self.particle_surface_xz = pygame.Surface((VIEW_WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Simulation parameters
        self.wind_speed = 20  # m/s
        self.ball_radius = int(HEIGHT * 0.07)  # Responsive ball size (7% of height)
        self.wind_angle = 0  # degrees (0 = from left to right)
        self.vertical_wind = 0  # m/s
        
        # Ball position (initially centered) - now with z-coordinate
        self.ball_pos = [VIEW_WIDTH // 2, HEIGHT // 2, 0]
        self.dragging = False
        self.active_view = None  # To track which view is being interacted with
        
        # Calculate ball mass based on radius (assuming constant density)
        # Using a simple formula: mass = density * volume = density * (4/3) * pi * r^3
        # For simplicity, we'll use a scale factor to convert radius to mass
        self.density_factor = 0.0008  # Adjusted to give reasonable mass values
        
        # Particles for visualization
        self.particles = []
        
        # UI elements
        # 優先使用 Noto Sans TC，否則用 Segoe UI 或 Arial
        preferred_fonts = ['Noto Sans TC', 'Segoe UI', 'Arial']
        self.font = pygame.font.SysFont(preferred_fonts, 18)
        self.title_font = pygame.font.SysFont(preferred_fonts, 28, bold=True)
        self.show_info = True
        self.info_collapsed = False  # 說明面板摺疊狀態
        
        # Slider parameters
        self.sliders = {
            "wind_speed": {"value": self.wind_speed, "min": -50, "max": 50, "text": "風速（右正左負，公尺/秒）"},
            "ball_radius": {"value": self.ball_radius, "min": 20, "max": 100, "text": "球體半徑/質量"},
            "wind_angle": {"value": self.wind_angle, "min": 0, "max": 360, "text": "風向角度（度）"},
            "vertical_wind": {"value": self.vertical_wind, "min": -20, "max": 20, "text": "垂直風速（公尺/秒）"},
            "vertical_thrust": {"value": 0.0, "min": -1000, "max": 1000, "text": "上升推力（N）"}
        }
        self.active_slider = None
        
        self.ball_vz = 0  # z方向速度
        
    def generate_particles(self):
        # Add new particles from different sides based on wind angle
        angle_rad = math.radians(self.wind_angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        if random.random() < 0.3:
            # Determine entry point based on wind direction
            if cos_angle < 0:  # Wind from right
                x = VIEW_WIDTH
                y = random.randint(0, HEIGHT)
            elif cos_angle > 0:  # Wind from left
                x = 0
                y = random.randint(0, HEIGHT)
            elif sin_angle < 0:  # Wind from bottom
                x = random.randint(0, VIEW_WIDTH)
                y = HEIGHT
            else:  # Wind from top
                x = random.randint(0, VIEW_WIDTH)
                y = 0
                
            # Random z position for 3D effect
            z = random.uniform(-VIEW_WIDTH/4, VIEW_WIDTH/4)
            
            self.particles.append(Particle(x, y, z, self.wind_speed, self.wind_angle, self.vertical_wind))
    
    def calculate_lift(self):
        # Calculate lift using Bernoulli's principle
        # Full model: P₁ + ½ρv₁² + ρgh₁ = P₂ + ½ρv₂² + ρgh₂
        
        # 風速可為正（右）或負（左），負值時風向反轉
        wind_speed = self.wind_speed
        wind_angle = self.wind_angle
        if wind_speed < 0:
            wind_speed = -wind_speed
            wind_angle = (wind_angle + 180) % 360
        angle_rad = math.radians(wind_angle)
        
        # Calculate effective velocity (including vertical component)
        vx = wind_speed * math.cos(angle_rad)
        vy = wind_speed * math.sin(angle_rad) + self.vertical_wind
        effective_velocity = math.sqrt(vx*vx + vy*vy)
        
        # Calculate projected area (simplified as circle)
        area = math.pi * (self.ball_radius/100)**2  # Convert pixels to meters (approximate)
        
        # 升力係數由滑桿控制
        lift_coefficient = 0.47  # 固定球體升力係數
        vertical_thrust = self.sliders["vertical_thrust"]["value"]
        
        # 伯努利方程計算
        # 假設球體上方流速較快，下方流速較慢
        # 上方流速 = 來流速度 + 加速效應
        velocity_top = effective_velocity * 1.5  # 上表面流速加快50%
        velocity_bottom = effective_velocity * 0.8  # 下表面流速減慢20%
        
        # 根據伯努利方程，P + ½ρv² + ρgh = 常數
        # 假設高度項相同，則壓力差由速度差決定
        pressure_top = AIR_DENSITY * (velocity_top**2) / 2
        pressure_bottom = AIR_DENSITY * (velocity_bottom**2) / 2
        
        # 壓力差（下表面壓力較大，上表面壓力較小）
        pressure_diff = pressure_bottom - pressure_top
        
        # Calculate lift force
        lift_force = pressure_diff * area
        
        # Calculate ball mass based on radius
        ball_mass = (4/3) * math.pi * (self.ball_radius/100)**3 * (1/self.density_factor)
        
        # Calculate weight
        weight = ball_mass * GRAVITY
        
        # Net force (positive = upward), 加入上升推力
        net_force = lift_force - weight + vertical_thrust
        
        return {
            "pressure_top": pressure_top,
            "pressure_bottom": pressure_bottom,
            "pressure_diff": pressure_diff,
            "velocity_top": velocity_top,
            "velocity_bottom": velocity_bottom,
            "lift_force": lift_force,
            "weight": weight,
            "net_force": net_force,
            "ball_mass": ball_mass,
            "vertical_thrust": vertical_thrust
        }
    
    def draw_ball(self):
        # Calculate forces
        forces = self.calculate_lift()
        net_force = forces["net_force"]
        
        # Determine ball color based on net force
        if net_force > 0.05:
            color = GREEN  # Rising
        elif net_force < -0.05:
            color = RED  # Falling
        else:
            color = YELLOW  # Balanced
        
        # 檢查是否正在拖動球體，若是則高亮
        highlight = self.dragging
        border_color = (0, 180, 255) if highlight else BLACK
        border_width = 5 if highlight else 2
        
        # Draw ball in XY view (left panel)
        pygame.draw.circle(self.screen, color, (self.ball_pos[0], self.ball_pos[1]), self.ball_radius)
        pygame.draw.circle(self.screen, border_color, (self.ball_pos[0], self.ball_pos[1]), self.ball_radius, border_width)
        
        # Draw ball in XZ view (right panel)
        xz_x = self.current_view_width + self.middle_section_width + self.ball_pos[0]  # Offset for right panel
        xz_y = self.current_height // 2 - self.ball_pos[2]  # Z-axis is vertical in XZ view
        pygame.draw.circle(self.screen, color, (xz_x, xz_y), self.ball_radius)
        pygame.draw.circle(self.screen, border_color, (xz_x, xz_y), self.ball_radius, border_width)
        
        # Draw direction indicators in XY view
        angle_rad = math.radians(self.wind_angle)
        arrow_length = self.ball_radius * 0.8
        end_x = self.ball_pos[0] + arrow_length * math.cos(angle_rad)
        end_y = self.ball_pos[1] + arrow_length * math.sin(angle_rad)
        pygame.draw.line(self.screen, BLACK, (self.ball_pos[0], self.ball_pos[1]), (end_x, end_y), 3)
        
        # Draw direction indicators in XZ view
        xz_end_x = xz_x + arrow_length * math.cos(angle_rad)
        xz_end_y = xz_y  # No vertical component in XZ view for wind angle
        pygame.draw.line(self.screen, BLACK, (xz_x, xz_y), (xz_end_x, xz_end_y), 3)
        
        # Draw vertical force indicator in XY view
        if abs(self.vertical_wind) > 0.1:
            vert_length = min(20, abs(self.vertical_wind)) * self.ball_radius / 20
            vert_sign = 1 if self.vertical_wind < 0 else -1  # Reverse for screen coordinates
            vert_end_y = self.ball_pos[1] + vert_sign * vert_length
            pygame.draw.line(self.screen, BLUE, 
                            (self.ball_pos[0], self.ball_pos[1]), 
                            (self.ball_pos[0], vert_end_y), 3)
    
    def draw_particles(self):
        # Clear the particle surfaces
        self.particle_surface_xy.fill((0, 0, 0, 0))
        self.particle_surface_xz.fill((0, 0, 0, 0))
        
        # Update and draw particles
        for particle in self.particles:
            particle.update(self.ball_pos, self.ball_radius)
            
            # Draw in XY view (left panel)
            pygame.draw.circle(self.particle_surface_xy, particle.color, 
                              (int(particle.x), int(particle.y)), particle.size)
            
            # Draw in XZ view (right panel)
            xz_x = particle.x
            xz_y = self.current_height // 2 - particle.z  # Z-axis is vertical in XZ view
            pygame.draw.circle(self.particle_surface_xz, particle.color, 
                              (int(xz_x), int(xz_y)), particle.size)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        # Draw the particle surfaces
        self.screen.blit(self.particle_surface_xy, (0, 0))
        self.screen.blit(self.particle_surface_xz, (self.current_view_width + self.middle_section_width, 0))
    
    def draw_ui(self):
        # Calculate responsive layout dimensions
        info_panel_width = int(self.current_view_width * 0.8)
        info_panel_height = int(self.current_height * 0.3)
        font_size = max(12, int(self.current_height / 50))
        
        # Draw view panels backgrounds and borders
        xy_panel = pygame.Rect(0, 0, self.current_view_width, self.current_height)
        xz_panel = pygame.Rect(self.current_view_width + self.middle_section_width, 0, 
                              self.current_view_width, self.current_height)
        shadow_offset = 8
        pygame.draw.rect(self.screen, PANEL_SHADOW, xy_panel.move(shadow_offset, shadow_offset), border_radius=18)
        pygame.draw.rect(self.screen, PANEL_SHADOW, xz_panel.move(shadow_offset, shadow_offset), border_radius=18)
        pygame.draw.rect(self.screen, PANEL_BG, xy_panel, border_radius=18)
        pygame.draw.rect(self.screen, PANEL_BG, xz_panel, border_radius=18)
        pygame.draw.rect(self.screen, BLACK, xy_panel, 2, border_radius=18)
        pygame.draw.rect(self.screen, BLACK, xz_panel, 2, border_radius=18)
        
        # Draw panel labels
        xy_label = self.title_font.render("XY 視圖 (側視圖)", True, BLUE)
        xz_label = self.title_font.render("XZ 視圖 (俯視圖)", True, BLUE)
        self.screen.blit(xy_label, (24, 18))
        self.screen.blit(xz_label, (self.current_view_width + self.middle_section_width + 24, 18))
        
        # Draw coordinate axes in XY view
        axes_length = int(self.current_height * 0.07)
        pygame.draw.line(self.screen, BLACK, (10, self.current_height - 30), 
                        (10 + axes_length, self.current_height - 30), 2)  # X-axis
        pygame.draw.line(self.screen, BLACK, (10, self.current_height - 30), 
                        (10, self.current_height - 30 - axes_length), 2)  # Y-axis
        x_label = self.font.render("X", True, BLACK)
        y_label = self.font.render("Y", True, BLACK)
        self.screen.blit(x_label, (10 + axes_length, self.current_height - 30))
        self.screen.blit(y_label, (10, self.current_height - 30 - axes_length))
        
        # Draw coordinate axes in XZ view
        pygame.draw.line(self.screen, BLACK, 
                        (self.current_view_width + self.middle_section_width + 10, self.current_height - 30), 
                        (self.current_view_width + self.middle_section_width + 10 + axes_length, self.current_height - 30), 2)  # X-axis
        pygame.draw.line(self.screen, BLACK, 
                        (self.current_view_width + self.middle_section_width + 10, self.current_height - 30), 
                        (self.current_view_width + self.middle_section_width + 10, self.current_height - 30 - axes_length), 2)  # Z-axis
        x_label = self.font.render("X", True, BLACK)
        z_label = self.font.render("Z", True, BLACK)
        self.screen.blit(x_label, (self.current_view_width + self.middle_section_width + 10 + axes_length, self.current_height - 30))
        self.screen.blit(z_label, (self.current_view_width + self.middle_section_width + 10, self.current_height - 30 - axes_length))
        
        # Draw sliders in the middle section
        middle_x = self.current_view_width + self.middle_section_width // 2
        slider_width = int(self.middle_section_width * 0.7)
        y_offset = int(self.current_height * 0.01)  # 更靠上
        slider_height = int(self.current_height * 0.16)  # 更小
        y_increment = int(self.current_height * 0.21)  # 更小
        
        # Draw middle section background
        middle_section = pygame.Rect(self.current_view_width, 0, self.middle_section_width, self.current_height)
        pygame.draw.rect(self.screen, PANEL_SHADOW, middle_section.move(shadow_offset, shadow_offset), border_radius=18)
        pygame.draw.rect(self.screen, PANEL_BG, middle_section, border_radius=18)
        pygame.draw.rect(self.screen, BLACK, middle_section, 1, border_radius=18)
        
        # Draw control panel title
        control_label = self.title_font.render("控制面板", True, BLACK)
        control_label_rect = control_label.get_rect(center=(middle_x, int(self.current_height * 0.05)))
        self.screen.blit(control_label, control_label_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        tooltip_text = None
        # 滑桿 Tooltip
        for key, slider in self.sliders.items():
            # 橫向滑桿設計
            slider_length = slider_width
            slider_thickness = 10
            slider_x = middle_x - slider_length // 2
            slider_y = y_offset + slider_height // 2
            # 滑桿底色
            pygame.draw.rect(self.screen, GRAY, (slider_x, slider_y - slider_thickness // 2, slider_length, slider_thickness), border_radius=6)
            # 已選部分主色
            value_range = slider["max"] - slider["min"]
            percent = (slider["value"] - slider["min"]) / value_range
            selected_length = int(slider_length * percent)
            pygame.draw.rect(self.screen, BLUE, (slider_x, slider_y - slider_thickness // 2, selected_length, slider_thickness), border_radius=6)
            # 圓形手把
            handle_radius = 14
            handle_center = (slider_x + selected_length, slider_y)
            # 檢查滑鼠是否懸停在手把上
            hovering = (mouse_pos[0] - handle_center[0]) ** 2 + (mouse_pos[1] - handle_center[1]) ** 2 <= handle_radius ** 2
            handle_color = (0, 180, 255) if hovering or self.active_slider == key else BLUE
            pygame.draw.circle(self.screen, handle_color, handle_center, handle_radius)
            pygame.draw.circle(self.screen, BLACK, handle_center, handle_radius, 2)
            # Tooltip 文字
            if hovering:
                if key == "wind_speed":
                    tooltip_text = "Wind Speed (m/s)"
                elif key == "ball_radius":
                    tooltip_text = "Ball Radius / Mass"
                elif key == "wind_angle":
                    tooltip_text = "Wind Angle (degree)"
                elif key == "vertical_wind":
                    tooltip_text = "Vertical Wind (m/s)"
            # Draw slider text
            if key == "ball_radius":
                ball_mass = (4/3) * math.pi * (slider["value"]/100)**3 * (1/self.density_factor)
                value_text = f"{slider['text']}: {slider['value']:.1f}"
                mass_text = f"質量: {ball_mass:.2f} kg"
                text_surf = self.font.render(value_text, True, BLACK)
                mass_surf = self.font.render(mass_text, True, BLACK)
                text_rect = text_surf.get_rect(center=(middle_x, y_offset + slider_height - 10))
                mass_rect = mass_surf.get_rect(center=(middle_x, y_offset + slider_height - 10 + self.font.get_height()))
                self.screen.blit(text_surf, text_rect)
                self.screen.blit(mass_surf, mass_rect)
            elif key == "vertical_thrust":
                value_text = f"{slider['text']}: {slider['value']:.1f}"
                text_surf = self.font.render(value_text, True, BLACK)
                text_rect = text_surf.get_rect(center=(middle_x, y_offset + slider_height - 10))
                self.screen.blit(text_surf, text_rect)
            else:
                value_text = f"{slider['text']}: {slider['value']:.1f}"
                text_surf = self.font.render(value_text, True, BLACK)
                text_rect = text_surf.get_rect(center=(middle_x, y_offset + slider_height - 10))
                self.screen.blit(text_surf, text_rect)
            y_offset += y_increment
        
        # Draw force information
        forces = self.calculate_lift()
        info_x = int(self.current_view_width * 0.05)
        info_y = int(self.current_height * 0.15)
        
        info_texts = [
            ("上表面壓力 (Pressure on Top)", BLACK),
            (f"  {forces['pressure_top']:.2f} Pa", BLACK),
            ("上表面流速 (Velocity on Top)", BLUE),
            (f"  {forces['velocity_top']:.2f} m/s", BLUE),
            ("下表面壓力 (Pressure on Bottom)", BLACK),
            (f"  {forces['pressure_bottom']:.2f} Pa", BLACK),
            ("下表面流速 (Velocity on Bottom)", BLUE),
            (f"  {forces['velocity_bottom']:.2f} m/s", BLUE),
            ("壓力差 (Pressure Difference)", BLUE),
            (f"  {forces['pressure_diff']:.2f} Pa", BLUE),
            ("升力 (Lift)", GREEN),
            (f"  {forces['lift_force']:.2f} N", GREEN),
            ("球體質量 (Ball Mass)", BLACK),
            (f"  {forces['ball_mass']:.2f} kg", BLACK),
            ("重力 (Weight)", RED),
            (f"  {forces['weight']:.2f} N", RED),
            ("淨力 (Net Force)", (0, 120, 255) if forces['net_force'] > 0 else RED),
            (f"  {forces['net_force']:.2f} N", (0, 120, 255) if forces['net_force'] > 0 else RED)
        ]
        
        # Draw semi-transparent background for info
        info_bg_width = int(self.current_view_width * 0.5)
        info_bg_height = len(info_texts) * (self.font.get_height() + 5) + 20
        info_bg = pygame.Surface((info_bg_width, info_bg_height), pygame.SRCALPHA)
        info_bg.fill((240, 240, 240, 200))
        self.screen.blit(info_bg, (info_x - 5, info_y - 5))
        
        for text, color in info_texts:
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (info_x + 10, info_y))
            info_y += self.font.get_height() + 8
        
        # Draw ball position information
        pos_x = self.current_width - int(self.current_view_width * 0.3)
        pos_y = self.current_height - int(self.current_height * 0.15)
        
        pos_texts = [
            ("球體位置:", BLUE),
            (f"X: {self.ball_pos[0]:.1f}", BLACK),
            (f"Y: {self.ball_pos[1]:.1f}", BLACK),
            (f"Z: {self.ball_pos[2]:.1f}", BLACK),
            (f"Z速度: {getattr(self, 'ball_vz', 0):.2f}", (80,80,80))
        ]
        
        # Draw semi-transparent background for position info
        pos_bg_width = int(self.current_view_width * 0.25)
        pos_bg_height = len(pos_texts) * (self.font.get_height() + 5) + 10
        pos_bg = pygame.Surface((pos_bg_width, pos_bg_height), pygame.SRCALPHA)
        pos_bg.fill((240, 240, 240, 200))
        self.screen.blit(pos_bg, (pos_x - 5, pos_y - pos_bg_height - 5))
        
        pos_y -= pos_bg_height
        for text, color in pos_texts:
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (pos_x + 6, pos_y))
            pos_y += self.font.get_height() + 6
        
        # Draw information panel if enabled
        if self.show_info:
            self.draw_info_panel()
        
        # 球體 Tooltip
        # XY view
        ball_hover = (mouse_pos[0] - self.ball_pos[0]) ** 2 + (mouse_pos[1] - self.ball_pos[1]) ** 2 <= self.ball_radius ** 2
        if ball_hover:
            tooltip_text = "Ball: Drag to move (XY view)"
        # XZ view
        xz_x = self.current_view_width + self.middle_section_width + self.ball_pos[0]
        xz_y = self.current_height // 2 - self.ball_pos[2]
        ball_hover_xz = (mouse_pos[0] - xz_x) ** 2 + (mouse_pos[1] - xz_y) ** 2 <= self.ball_radius ** 2
        if ball_hover_xz:
            tooltip_text = "Ball: Drag to move (XZ view)"
        # 資訊區 Tooltip
        info_panel_rect = pygame.Rect(info_x - 5, info_y - 5, info_bg_width, info_bg_height)
        if info_panel_rect.collidepoint(mouse_pos):
            tooltip_text = "Force and pressure information"
        # 顯示 Tooltip
        if tooltip_text:
            self.draw_tooltip(mouse_pos, tooltip_text)
    
    def draw_info_panel(self):
        # Calculate responsive panel size
        panel_width = int(self.current_view_width * 0.8)
        panel_height = int(self.current_height * 0.4)
        collapsed_height = 16  # 更細長
        
        # Draw semi-transparent background with shadow and rounded corners
        shadow_offset = 8
        info_shadow = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        info_shadow.fill((0, 0, 0, 0))
        pygame.draw.rect(info_shadow, PANEL_SHADOW + (120,), (shadow_offset, shadow_offset, panel_width - shadow_offset, panel_height - shadow_offset), border_radius=18)
        self.screen.blit(info_shadow, (self.current_view_width - panel_width - 20, self.current_height - panel_height - 20))
        info_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(info_surface, (250, 252, 255, 220), (0, 0, panel_width, panel_height), border_radius=18)
        pygame.draw.rect(info_surface, BLUE, (0, 0, panel_width, panel_height), 2, border_radius=18)
        
        # Draw title
        title = self.title_font.render("伯努利原理", True, BLUE)
        info_surface.blit(title, (28, 20))
        
        # 摺疊/展開按鈕
        btn_size = 28
        btn_rect = pygame.Rect(panel_width - btn_size - 12, 8, btn_size, btn_size)
        pygame.draw.rect(info_surface, (230, 240, 255), btn_rect, border_radius=8)
        pygame.draw.rect(info_surface, BLUE, btn_rect, 2, border_radius=8)
        # 畫+/-符號
        cx, cy = btn_rect.center
        if self.info_collapsed:
            # 畫+
            pygame.draw.line(info_surface, BLUE, (cx-7, cy), (cx+7, cy), 3)
            pygame.draw.line(info_surface, BLUE, (cx, cy-7), (cx, cy+7), 3)
        else:
            # 畫-
            pygame.draw.line(info_surface, BLUE, (cx-7, cy), (cx+7, cy), 3)
        # 當摺疊時只顯示一條橫條和按鈕
        if self.info_collapsed:
            bar_surface = pygame.Surface((panel_width, collapsed_height), pygame.SRCALPHA)
            pygame.draw.rect(bar_surface, (250, 252, 255, 220), (0, 0, panel_width, collapsed_height), border_radius=8)
            pygame.draw.rect(bar_surface, BLUE, (0, 0, panel_width, collapsed_height), 2, border_radius=8)
            # 畫小圖示（info圓圈）
            icon_radius = 7
            icon_center = (18, collapsed_height // 2)
            pygame.draw.circle(bar_surface, BLUE, icon_center, icon_radius, 2)
            pygame.draw.line(bar_surface, BLUE, (icon_center[0], icon_center[1]-3), (icon_center[0], icon_center[1]+2), 2)
            pygame.draw.circle(bar_surface, BLUE, (icon_center[0], icon_center[1]-4), 1)
            # 畫按鈕
            bar_surface.blit(info_surface.subsurface(btn_rect), btn_rect)
            self.screen.blit(bar_surface, (self.current_view_width - panel_width - 20, self.current_height - panel_height - 20))
            # Tooltip
            mouse_pos = pygame.mouse.get_pos()
            abs_btn_rect = btn_rect.move(self.current_view_width - panel_width - 20, self.current_height - panel_height - 20)
            if abs_btn_rect.collidepoint(mouse_pos):
                self.draw_tooltip(mouse_pos, "Click to expand (展開)")
            return
        
        # Draw explanation text
        line_height = self.font.get_height() + 5
        explanation = [
            "伯努利原理說明流體速度增加時，壓力會下降。",
            "",
            "伯努利方程式: P₁ + ½ρv₁² + ρgh₁ = P₂ + ½ρv₂² + ρgh₂",
            "",
            "當空氣流過球體時，上表面的空氣流動較快，",
            "因此產生較低的壓力。下表面的空氣流動較慢，",
            "壓力較高，這種壓力差產生向上的升力。",
            "",
            "這個原理解釋了飛機機翼如何產生升力，以及",
            "許多其他流體動力學現象。",
            "",
            "操作說明:",
            "- 按 'I' 鍵隱藏/顯示此信息",
            "- 按 'F' 鍵切換全屏模式",
            "- 在兩個視圖中拖動球體可改變其位置",
            "- 調整中間的滑桿來改變模擬參數"
        ]
        
        y_offset = 60
        for line in explanation:
            text_surf = self.font.render(line, True, BLACK)
            info_surface.blit(text_surf, (28, y_offset))
            y_offset += line_height
        
        # Position in bottom right of XY view
        self.screen.blit(info_surface, (self.current_view_width - panel_width - 20, 
                                       self.current_height - panel_height - 20))
        
        # Tooltip
        mouse_pos = pygame.mouse.get_pos()
        abs_btn_rect = btn_rect.move(self.current_view_width - panel_width - 20, self.current_height - panel_height - 20)
        if abs_btn_rect.collidepoint(mouse_pos):
            self.draw_tooltip(mouse_pos, "Click to collapse (摺疊)")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == KEYDOWN:
                if event.key == K_i:
                    self.show_info = not self.show_info
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_f:
                    # Toggle fullscreen
                    pygame.display.toggle_fullscreen()
            
            elif event.type == VIDEORESIZE:
                # Handle window resize event
                self.resize(event.w, event.h)
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # 摺疊/展開說明面板按鈕
                    panel_width = int(self.current_view_width * 0.8)
                    panel_height = int(self.current_height * 0.4)
                    btn_size = 28
                    btn_rect = pygame.Rect(panel_width - btn_size - 12, 8, btn_size, btn_size)
                    abs_btn_rect = btn_rect.move(self.current_view_width - panel_width - 20, self.current_height - panel_height - 20)
                    if abs_btn_rect.collidepoint(event.pos):
                        self.info_collapsed = not self.info_collapsed
                        return
                    # Check if clicking in XY view
                    if 0 <= event.pos[0] <= self.current_view_width:
                        # Check if clicking on ball in XY view
                        dx = event.pos[0] - self.ball_pos[0]
                        dy = event.pos[1] - self.ball_pos[1]
                        if dx*dx + dy*dy <= self.ball_radius*self.ball_radius:
                            self.dragging = True
                            self.active_view = "xy"
                    
                    # Check if clicking in XZ view
                    elif self.current_view_width + self.middle_section_width <= event.pos[0] <= self.current_width:
                        # Check if clicking on ball in XZ view
                        xz_x = event.pos[0] - (self.current_view_width + self.middle_section_width)
                        xz_z = self.current_height // 2 - event.pos[1]  # Convert y-coordinate to z
                        dx = xz_x - self.ball_pos[0]
                        dz = xz_z - self.ball_pos[2]
                        if dx*dx + dz*dz <= self.ball_radius*self.ball_radius:
                            self.dragging = True
                            self.active_view = "xz"
                    
                    # Check if clicking on sliders
                    middle_x = self.current_view_width + self.middle_section_width // 2
                    slider_width = int(self.middle_section_width * 0.7)
                    y_offset = int(self.current_height * 0.01)
                    slider_height = int(self.current_height * 0.16)
                    y_increment = int(self.current_height * 0.21)
                    
                    for key in self.sliders:
                        slider_rect = pygame.Rect(
                            middle_x - slider_width // 2, 
                            y_offset, 
                            slider_width, 
                            slider_height
                        )
                        if slider_rect.collidepoint(event.pos):
                            self.active_slider = key
                            # Update slider value
                            self.update_slider(key, event.pos[1], y_offset, slider_height)
                        y_offset += y_increment
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.dragging = False
                    self.active_view = None
                    self.active_slider = None
            
            elif event.type == MOUSEMOTION:
                if self.dragging:
                    if self.active_view == "xy":
                        # Update ball position in XY view
                        self.ball_pos[0] = min(max(event.pos[0], self.ball_radius), 
                                              self.current_view_width - self.ball_radius)
                        self.ball_pos[1] = min(max(event.pos[1], self.ball_radius), 
                                              self.current_height - self.ball_radius)
                    elif self.active_view == "xz":
                        # Update ball position in XZ view
                        self.ball_pos[0] = min(max(event.pos[0] - (self.current_view_width + self.middle_section_width), 
                                                  self.ball_radius), 
                                              self.current_view_width - self.ball_radius)
                        self.ball_pos[2] = self.current_height // 2 - event.pos[1]  # Convert y-coordinate to z
                
                if self.active_slider:
                    # Calculate slider positions dynamically
                    y_offset = int(self.current_height * 0.01)
                    slider_height = int(self.current_height * 0.16)
                    y_increment = int(self.current_height * 0.21)
                    
                    # Find the correct y_offset for the active slider
                    for key in self.sliders:
                        if key == self.active_slider:
                            break
                        y_offset += y_increment
                    
                    self.update_slider(self.active_slider, event.pos[1], y_offset, slider_height)
    
    def update_slider(self, key, y_pos, base_y, slider_height):
        """Update slider value based on mouse position"""
        # Calculate position ratio (inverted for vertical slider)
        pos_ratio = 1 - max(0, min(1, (y_pos - base_y) / slider_height))
        
        slider = self.sliders[key]
        value_range = slider["max"] - slider["min"]
        new_value = slider["min"] + pos_ratio * value_range
        
        # Update the value
        slider["value"] = new_value
        
        # Update the corresponding simulation parameter
        if key == "wind_speed":
            self.wind_speed = new_value
        elif key == "ball_radius":
            self.ball_radius = new_value
        elif key == "wind_angle":
            self.wind_angle = new_value
        elif key == "vertical_wind":
            self.vertical_wind = new_value
        elif key == "vertical_thrust":
            pass  # 直接用滑桿值即可
    
    def run(self):
        while True:
            # Handle events
            self.handle_events()
            
            # Generate new particles
            self.generate_particles()
            
            # 物理模擬：z方向運動
            forces = self.calculate_lift()
            ball_mass = forces["ball_mass"]
            net_force_z = forces["net_force"]
            # F=ma, 更新z速度與z座標
            acc_z = net_force_z / ball_mass if ball_mass > 0 else 0
            self.ball_vz += acc_z * 0.1  # 0.1為時間步長
            self.ball_pos[2] += self.ball_vz * 0.1
            # 簡單邊界條件，避免球體飛出視窗
            z_min = -self.current_view_width // 2 + self.ball_radius
            z_max = self.current_view_width // 2 - self.ball_radius
            if self.ball_pos[2] < z_min:
                self.ball_pos[2] = z_min
                self.ball_vz = 0
            if self.ball_pos[2] > z_max:
                self.ball_pos[2] = z_max
                self.ball_vz = 0
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_ui()
            self.draw_particles()
            self.draw_ball()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

    def resize(self, new_width, new_height):
        """Handle window resize events"""
        # Update window dimensions
        self.current_width = max(800, new_width)  # Minimum width
        self.current_height = max(600, new_height)  # Minimum height
        
        # Recalculate view widths
        self.current_view_width = int(self.current_width * 0.4)
        self.middle_section_width = int(self.current_width * 0.2)
        
        # Resize the screen
        self.screen = pygame.display.set_mode((self.current_width, self.current_height), pygame.RESIZABLE)
        
        # Resize particle surfaces
        self.particle_surface_xy = pygame.Surface((self.current_view_width, self.current_height), pygame.SRCALPHA)
        self.particle_surface_xz = pygame.Surface((self.current_view_width, self.current_height), pygame.SRCALPHA)
        
        # Adjust ball position if needed to keep it in view
        self.ball_pos[0] = min(self.ball_pos[0], self.current_view_width - self.ball_radius)
        self.ball_pos[1] = min(self.ball_pos[1], self.current_height - self.ball_radius)
        
        # Adjust font sizes based on screen dimensions
        base_font_size = max(12, int(self.current_height / 50))
        preferred_fonts = ['Noto Sans TC', 'Segoe UI', 'Arial']
        self.font = pygame.font.SysFont(preferred_fonts, base_font_size)
        self.title_font = pygame.font.SysFont(preferred_fonts, int(base_font_size * 1.5), bold=True)
        
        # Adjust ball radius to be proportional to screen size
        self.ball_radius = int(self.current_height * 0.07)  # 7% of height

    def draw_tooltip(self, pos, text):
        # Tooltip 半透明底色、圓角
        font = self.font
        padding = 8
        text_surf = font.render(text, True, BLACK)
        w, h = text_surf.get_size()
        tooltip_surf = pygame.Surface((w + 2 * padding, h + 2 * padding), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surf, (255, 255, 255, 230), (0, 0, w + 2 * padding, h + 2 * padding), border_radius=10)
        pygame.draw.rect(tooltip_surf, BLUE, (0, 0, w + 2 * padding, h + 2 * padding), 2, border_radius=10)
        tooltip_surf.blit(text_surf, (padding, padding))
        # 避免超出畫面
        x, y = pos
        if x + w + 2 * padding > self.current_width:
            x = self.current_width - w - 2 * padding - 10
        if y + h + 2 * padding > self.current_height:
            y = self.current_height - h - 2 * padding - 10
        self.screen.blit(tooltip_surf, (x + 12, y + 12))

if __name__ == "__main__":
    simulation = BernoulliSimulation()
    simulation.run()
