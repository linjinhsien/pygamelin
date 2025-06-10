import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1400
HEIGHT = 800
FPS = 60
VIEW_WIDTH = 400  # Width for 3D visualization

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

# Physics constants (matching HTML version)
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = 9.81  # m/s²
ATMOSPHERIC_PRESSURE = 101325  # Pa

class Particle:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.life = random.randint(200, 255)
        self.size = random.uniform(1, 3)
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
        if abs(self.x) > 800 or abs(self.y) > 600 or abs(self.z) > 400:
            self.reset_position(wind_vec_x, wind_vec_z)
        
        self.life = max(0, self.life - 1)
    
    def reset_position(self, wind_vec_x, wind_vec_z):
        """Reset particle position based on wind direction"""
        if wind_vec_x > 0:
            self.x = random.uniform(-800, -600)
        elif wind_vec_x < 0:
            self.x = random.uniform(600, 800)
        else:
            self.x = random.uniform(-800, 800)
            
        if wind_vec_z > 0:
            self.z = random.uniform(-400, -200)
        elif wind_vec_z < 0:
            self.z = random.uniform(200, 400)
        else:
            self.z = random.uniform(-400, 400)
            
        self.y = random.uniform(-300, 300)
        self.life = random.randint(200, 255)
        
    def is_alive(self):
        return self.life > 0

class BernoulliSimulation:
    def __init__(self):
        # Set up display with responsive dimensions
        self.current_width = WIDTH
        self.current_height = HEIGHT
        self.screen = pygame.display.set_mode((self.current_width, self.current_height), pygame.RESIZABLE)
        pygame.display.set_caption("伯努利原理科學模擬 - 雙平面視圖")
        self.clock = pygame.time.Clock()
        
        # Layout calculations
        self.middle_section_width = int(self.current_width * 0.25)
        self.current_view_width = (self.current_width - self.middle_section_width) // 2
        
        # Ball properties - 預設位置在地面上方
        ground_level = self.current_height - 100
        self.ball_pos = [self.current_view_width // 2, ground_level, 0]  # [x, y, z] - 開始在地面附近
        self.ball_radius = 30
        self.ball_mass = 0.5  # kg
        self.ball_velocity = [0, 0, 0]  # [vx, vy, vz]
        
        # Wind properties
        self.wind_speed = 20  # m/s
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
        self.wind_arrow_length = 100
        
        # Particles for wind visualization
        self.particles = []
        self.particle_surface_xy = pygame.Surface((self.current_view_width, self.current_height), pygame.SRCALPHA)
        self.particle_surface_xz = pygame.Surface((self.current_view_width, self.current_height), pygame.SRCALPHA)
        
        for _ in range(300):
            x = random.uniform(-400, 400)
            y = random.uniform(-300, 300)
            z = random.uniform(-200, 200)
            self.particles.append(Particle(x, y, z))
        
        # UI
        base_font_size = max(12, int(self.current_height / 50))
        preferred_fonts = ['Noto Sans TC', 'Microsoft JhengHei', 'Segoe UI', 'Arial']
        self.font = pygame.font.SysFont(preferred_fonts, base_font_size)
        self.title_font = pygame.font.SysFont(preferred_fonts, int(base_font_size * 1.5), bold=True)
        
        # Sliders (保留原本的中文標籤)
        self.sliders = {
            "wind_speed": {"value": self.wind_speed, "min": -50, "max": 50, "text": "風速（右正左負，公尺/秒）"},
            "wind_angle": {"value": self.wind_angle, "min": 0, "max": 360, "text": "風向角度（度）"},
            "wind_vertical": {"value": self.wind_vertical, "min": -20, "max": 20, "text": "垂直風力（公尺/秒）"},
            "ball_radius": {"value": self.ball_radius, "min": 20, "max": 80, "text": "球體半徑/質量"},
            "vertical_thrust": {"value": self.vertical_thrust, "min": -1000, "max": 1000, "text": "上升推力（N）"},
            "side_force_coeff": {"value": self.side_force_coefficient, "min": 0, "max": 1.0, "text": "側向力係數"}
        }
        self.active_slider = None
        
        # Physics data for display (保留中文標籤)
        self.physics_data = {
            "top_pressure": ATMOSPHERIC_PRESSURE,
            "bottom_pressure": ATMOSPHERIC_PRESSURE,
            "pressure_diff": 0,
            "lift_force": 0,
            "side_force": 0,
            "front_force": 0
        }
        
        # Info panel state
        self.info_collapsed = False
    
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
            side_force = wind_x * AIR_DENSITY * ball_area * self.side_force_coefficient  # 使用可控制的係數
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
        """Update ball physics with proper 3D motion and gravity in all directions"""
        if self.dragging:
            return
        
        forces = self.calculate_bernoulli_effect()
        ball_mass = forces["ball_mass"]
        
        # Gravity affects all directions - primarily Y (downward) but also Z if tilted
        weight_y = ball_mass * GRAVITY  # Primary gravity downward
        weight_z = ball_mass * GRAVITY * 0.05  # Small Z-component gravity (reduced)
        
        # Calculate net forces and accelerations
        net_force_y = forces["lift"] - weight_y  # Y direction (screen up/down)
        net_force_x = forces["side"]  # X direction (screen left/right)
        net_force_z = forces["front"] - weight_z  # Z direction (depth) - also affected by gravity
        
        acceleration_y = net_force_y / ball_mass if ball_mass > 0 else 0
        acceleration_x = net_force_x / ball_mass if ball_mass > 0 else 0
        acceleration_z = net_force_z / ball_mass if ball_mass > 0 else 0
        
        # Update velocities (Y acceleration is positive downward in screen coordinates)
        self.ball_velocity[1] += acceleration_y * dt * 50  # Gravity pulls down (positive Y)
        self.ball_velocity[0] += acceleration_x * dt * 50
        self.ball_velocity[2] += acceleration_z * dt * 50  # Z also affected by gravity
        
        # Update positions
        self.ball_pos[1] += self.ball_velocity[1] * dt
        self.ball_pos[0] += self.ball_velocity[0] * dt
        self.ball_pos[2] += self.ball_velocity[2] * dt
        
        # Apply stronger damping when ball is near ground and moving slowly
        ground_level = self.current_height - self.ball_radius - 50
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
        # Y boundaries (ground and ceiling)
        ground_level = self.current_height - self.ball_radius - 50  # Leave space for ground
        ceiling_level = self.ball_radius + 50  # Leave space from top
        
        if self.ball_pos[1] >= ground_level:
            self.ball_pos[1] = ground_level
            # Stop bouncing if velocity is very small (ball settles on ground)
            if abs(self.ball_velocity[1]) < 2:
                self.ball_velocity[1] = 0
            else:
                self.ball_velocity[1] = -abs(self.ball_velocity[1]) * 0.3  # Bounce with energy loss
        elif self.ball_pos[1] <= ceiling_level:
            self.ball_pos[1] = ceiling_level
            self.ball_velocity[1] = abs(self.ball_velocity[1]) * 0.3  # Bounce with energy loss
        
        # X boundaries (left and right walls)
        left_wall = self.ball_radius
        right_wall = self.current_view_width - self.ball_radius
        
        if self.ball_pos[0] <= left_wall:
            self.ball_pos[0] = left_wall
            if abs(self.ball_velocity[0]) < 2:
                self.ball_velocity[0] = 0
            else:
                self.ball_velocity[0] = abs(self.ball_velocity[0]) * 0.3  # Bounce
        elif self.ball_pos[0] >= right_wall:
            self.ball_pos[0] = right_wall
            if abs(self.ball_velocity[0]) < 2:
                self.ball_velocity[0] = 0
            else:
                self.ball_velocity[0] = -abs(self.ball_velocity[0]) * 0.3  # Bounce
        
        # Z boundaries (front and back walls) - 也有地面效果
        max_z = self.current_height // 3
        min_z = -self.current_height // 3
        ground_z = self.current_height // 4  # Z方向的地面位置
        
        if self.ball_pos[2] >= max_z:
            self.ball_pos[2] = max_z
            if abs(self.ball_velocity[2]) < 2:
                self.ball_velocity[2] = 0
            else:
                self.ball_velocity[2] = -abs(self.ball_velocity[2]) * 0.3  # Bounce
        elif self.ball_pos[2] <= min_z:
            self.ball_pos[2] = min_z
            if abs(self.ball_velocity[2]) < 2:
                self.ball_velocity[2] = 0
            else:
                self.ball_velocity[2] = abs(self.ball_velocity[2]) * 0.3  # Bounce
        
        # Z方向地面約束 - 球體會掉落到Z方向的地面
        if self.ball_pos[2] >= ground_z:
            self.ball_pos[2] = ground_z
            if abs(self.ball_velocity[2]) < 2:
                self.ball_velocity[2] = 0  # Stop small movements
            elif self.ball_velocity[2] > 0:
                self.ball_velocity[2] = -abs(self.ball_velocity[2]) * 0.3  # 反彈
    
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
                alpha = int(particle.life * 0.8)
                color = (*particle.color, alpha)
                
                # XY view (left panel)
                screen_x = int(particle.x + self.current_view_width // 2)
                screen_y = int(particle.y + self.current_height // 2)
                
                if 0 <= screen_x < self.current_view_width and 0 <= screen_y < self.current_height:
                    size = max(1, int(particle.size))
                    pygame.draw.circle(self.particle_surface_xy, particle.color, (screen_x, screen_y), size)
                
                # ZX view (right panel) - X horizontal, Z vertical
                screen_x_zx = int(particle.x + self.current_view_width // 2)
                screen_y_zx = int(self.current_height // 2 - particle.z)
                
                if 0 <= screen_x_zx < self.current_view_width and 0 <= screen_y_zx < self.current_height:
                    size = max(1, int(particle.size))
                    pygame.draw.circle(self.particle_surface_xz, particle.color, (screen_x_zx, screen_y_zx), size)
        
        # Blit particle surfaces to main screen
        self.screen.blit(self.particle_surface_xy, (0, 0))
        self.screen.blit(self.particle_surface_xz, (self.current_view_width + self.middle_section_width, 0))
    
    def draw_ball(self):
        """Draw the ball on both XY and ZX views"""
        ball_color = self.get_ball_color()
        
        # XY view (left panel) - shows X and Y coordinates
        ball_x_xy = int(self.ball_pos[0])
        ball_y_xy = int(self.ball_pos[1])
        
        # Use consistent radius for both views
        display_radius_xy = int(self.ball_radius)
        
        # Draw shadow
        shadow_offset = 3
        pygame.draw.circle(self.screen, (50, 50, 50), 
                         (ball_x_xy + shadow_offset, ball_y_xy + shadow_offset), 
                         display_radius_xy)
        
        # Draw ball
        pygame.draw.circle(self.screen, ball_color, (ball_x_xy, ball_y_xy), display_radius_xy)
        pygame.draw.circle(self.screen, BLACK, (ball_x_xy, ball_y_xy), display_radius_xy, 2)
        
        # Add highlight
        highlight_x = ball_x_xy - display_radius_xy // 3
        highlight_y = ball_y_xy - display_radius_xy // 3
        pygame.draw.circle(self.screen, WHITE, (highlight_x, highlight_y), display_radius_xy // 4)
        
        # ZX view (right panel) - shows X and Z coordinates (X horizontal, Z vertical)
        ball_x_zx = int(self.ball_pos[0]) + self.current_view_width + self.middle_section_width
        ball_y_zx = int(self.current_height // 2 - self.ball_pos[2])
        
        # Use consistent radius for both views
        display_radius_zx = int(self.ball_radius)
        
        # Draw shadow
        pygame.draw.circle(self.screen, (50, 50, 50), 
                         (ball_x_zx + shadow_offset, ball_y_zx + shadow_offset), 
                         display_radius_zx)
        
        # Draw ball
        pygame.draw.circle(self.screen, ball_color, (ball_x_zx, ball_y_zx), display_radius_zx)
        pygame.draw.circle(self.screen, BLACK, (ball_x_zx, ball_y_zx), display_radius_zx, 2)
        
        # Add highlight
        highlight_x_zx = ball_x_zx - display_radius_zx // 3
        highlight_y_zx = ball_y_zx - display_radius_zx // 3
        pygame.draw.circle(self.screen, WHITE, (highlight_x_zx, highlight_y_zx), display_radius_zx // 4)
    
    def draw_ui(self):
        """Draw the complete UI with dual views and controls"""
        # Draw view separators
        pygame.draw.line(self.screen, BLACK, 
                        (self.current_view_width, 0), 
                        (self.current_view_width, self.current_height), 3)
        pygame.draw.line(self.screen, BLACK, 
                        (self.current_view_width + self.middle_section_width, 0), 
                        (self.current_view_width + self.middle_section_width, self.current_height), 3)
        
        # View labels
        xy_label = self.title_font.render("XY 平面視圖", True, BLACK)
        self.screen.blit(xy_label, (10, 10))
        
        zx_label = self.title_font.render("XZ 平面視圖", True, BLACK)
        self.screen.blit(zx_label, (self.current_view_width + self.middle_section_width + 10, 10))
        
        # Draw coordinate axes
        self.draw_boundaries()
        self.draw_axes()
        self.draw_wind_vectors()
        
        # Draw control panel
        self.draw_control_panel()
        
        # Draw physics information
        self.draw_physics_info()
        
        # Draw instructions
        self.draw_instructions()
    
    def draw_wind_vectors(self):
        """Draw wind speed and direction vectors"""
        if not self.show_wind_vectors:
            return
        
        # Calculate wind components
        wind_rad = math.radians(self.wind_angle)
        wind_x = self.wind_speed * math.cos(wind_rad)
        wind_z = self.wind_speed * math.sin(wind_rad)
        
        # Scale for display
        scale = 3
        arrow_x = wind_x * scale
        arrow_z = wind_z * scale
        arrow_y = self.wind_vertical * scale
        
        # XY view wind vector (left panel)
        center_xy = (self.current_view_width // 2, self.current_height // 2)
        
        # Horizontal wind component (X direction)
        if abs(arrow_x) > 5:
            end_x = center_xy[0] + arrow_x
            pygame.draw.line(self.screen, RED, center_xy, (end_x, center_xy[1]), 4)
            # Arrow head
            self.draw_arrow_head((end_x, center_xy[1]), arrow_x > 0, RED, horizontal=True)
            # Wind speed label
            wind_label = self.font.render(f"風速X: {wind_x:.1f} m/s", True, RED)
            self.screen.blit(wind_label, (center_xy[0] + 10, center_xy[1] - 40))
        
        # Vertical wind component (Y direction)
        if abs(arrow_y) > 5:
            end_y = center_xy[1] - arrow_y  # Negative because screen Y is inverted
            pygame.draw.line(self.screen, GREEN, center_xy, (center_xy[0], end_y), 4)
            # Arrow head
            self.draw_arrow_head((center_xy[0], end_y), arrow_y > 0, GREEN, horizontal=False)
            # Wind speed label
            wind_label = self.font.render(f"風速Y: {self.wind_vertical:.1f} m/s", True, GREEN)
            self.screen.blit(wind_label, (center_xy[0] + 10, center_xy[1] - 20))
        
        # XZ view wind vector (right panel)
        center_xz = (self.current_view_width + self.middle_section_width + self.current_view_width // 2, 
                     self.current_height // 2)
        
        # X direction (horizontal in XZ view)
        if abs(arrow_x) > 5:
            end_x_xz = center_xz[0] + arrow_x
            pygame.draw.line(self.screen, RED, center_xz, (end_x_xz, center_xz[1]), 4)
            # Arrow head
            self.draw_arrow_head((end_x_xz, center_xz[1]), arrow_x > 0, RED, horizontal=True)
        
        # Z direction (vertical in XZ view)
        if abs(arrow_z) > 5:
            end_z_xz = center_xz[1] - arrow_z  # Negative because screen Y is inverted
            pygame.draw.line(self.screen, BLUE, center_xz, (center_xz[0], end_z_xz), 4)
            # Arrow head
            self.draw_arrow_head((center_xz[0], end_z_xz), arrow_z > 0, BLUE, horizontal=False)
            # Wind speed label
            wind_label = self.font.render(f"風速Z: {wind_z:.1f} m/s", True, BLUE)
            self.screen.blit(wind_label, (center_xz[0] + 10, center_xz[1] - 20))
        
        # Total wind speed display
        total_wind = math.sqrt(wind_x**2 + wind_z**2 + self.wind_vertical**2)
        total_label = self.font.render(f"總風速: {total_wind:.1f} m/s", True, BLACK)
        self.screen.blit(total_label, (10, self.current_height - 30))
    
    def draw_arrow_head(self, pos, pointing_right_or_up, color, horizontal=True):
        """Draw arrow head at the end of wind vector"""
        x, y = pos
        size = 8
        
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
    def draw_boundaries(self):
        """Draw ground and ceiling boundaries"""
        ground_y = self.current_height - 50
        ceiling_y = 50
        
        # Draw ground line on both views
        pygame.draw.line(self.screen, (139, 69, 19), (0, ground_y), (self.current_view_width, ground_y), 3)
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (self.current_view_width + self.middle_section_width, ground_y), 
                        (self.current_width, ground_y), 3)
        
        # Draw ceiling line on both views
        pygame.draw.line(self.screen, GRAY, (0, ceiling_y), (self.current_view_width, ceiling_y), 2)
        pygame.draw.line(self.screen, GRAY, 
                        (self.current_view_width + self.middle_section_width, ceiling_y), 
                        (self.current_width, ceiling_y), 2)
        
        # Z方向地面線 (在XZ視圖中顯示)
        z_ground_y = self.current_height // 2 + self.current_height // 4
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (self.current_view_width + self.middle_section_width, z_ground_y), 
                        (self.current_width, z_ground_y), 3)
        
        # Ground labels
        ground_label = self.font.render("地面", True, (139, 69, 19))
        self.screen.blit(ground_label, (10, ground_y + 5))
        self.screen.blit(ground_label, (self.current_view_width + self.middle_section_width + 10, ground_y + 5))
        
        # Z方向地面標籤
        z_ground_label = self.font.render("Z地面", True, (139, 69, 19))
        self.screen.blit(z_ground_label, (self.current_view_width + self.middle_section_width + 10, z_ground_y + 5))
    
    def draw_axes(self):
        """Draw coordinate axes on both views"""
        axes_length = 50
        axes_color = DARK_BLUE
        
        # XY view axes (bottom-left corner)
        origin_xy = (30, self.current_height - 80)
        
        # X axis (horizontal, red)
        pygame.draw.line(self.screen, RED, origin_xy, 
                        (origin_xy[0] + axes_length, origin_xy[1]), 3)
        x_label = self.font.render("X", True, RED)
        self.screen.blit(x_label, (origin_xy[0] + axes_length + 5, origin_xy[1] - 10))
        
        # Y axis (vertical, green)
        pygame.draw.line(self.screen, GREEN, origin_xy, 
                        (origin_xy[0], origin_xy[1] - axes_length), 3)
        y_label = self.font.render("Y", True, GREEN)
        self.screen.blit(y_label, (origin_xy[0] - 15, origin_xy[1] - axes_length - 5))
        
        # ZX view axes (bottom-left corner of right panel) - X horizontal, Z vertical
        origin_zx = (self.current_view_width + self.middle_section_width + 30, self.current_height - 80)
        
        # X axis (horizontal, red)
        pygame.draw.line(self.screen, RED, origin_zx, 
                        (origin_zx[0] + axes_length, origin_zx[1]), 3)
        x_label_zx = self.font.render("X", True, RED)
        self.screen.blit(x_label_zx, (origin_zx[0] + axes_length + 5, origin_zx[1] - 10))
        
        # Z axis (vertical, blue)
        pygame.draw.line(self.screen, BLUE, origin_zx, 
                        (origin_zx[0], origin_zx[1] - axes_length), 3)
        z_label = self.font.render("Z", True, BLUE)
        self.screen.blit(z_label, (origin_zx[0] - 15, origin_zx[1] - axes_length - 5))
    
    def draw_control_panel(self):
        """Draw the control panel in the middle section"""
        # Background
        panel_rect = pygame.Rect(self.current_view_width, 0, self.middle_section_width, self.current_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        
        # Title
        title = self.title_font.render("控制面板", True, BLACK)
        title_rect = title.get_rect(center=(self.current_view_width + self.middle_section_width // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Draw sliders
        middle_x = self.current_view_width + self.middle_section_width // 2
        slider_width = int(self.middle_section_width * 0.8)
        y_offset = 70
        slider_height = int(self.current_height * 0.12)
        y_increment = int(self.current_height * 0.15)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for key, slider in self.sliders.items():
            self.draw_slider(key, slider, middle_x, slider_width, y_offset, mouse_pos)
            y_offset += y_increment
    
    def draw_slider(self, key, slider, middle_x, slider_width, y_offset, mouse_pos):
        """Draw a horizontal slider"""
        slider_length = slider_width
        slider_thickness = 8
        slider_x = middle_x - slider_length // 2
        slider_y = y_offset + 20
        
        # Slider track
        track_rect = pygame.Rect(slider_x, slider_y - slider_thickness // 2, 
                               slider_length, slider_thickness)
        pygame.draw.rect(self.screen, GRAY, track_rect, border_radius=4)
        
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
            pygame.draw.rect(self.screen, BLUE, fill_rect, border_radius=4)
        
        # Slider handle
        handle_radius = 12
        handle_center = (slider_x + selected_length, slider_y)
        
        # Check if mouse is hovering over handle
        hovering = (mouse_pos[0] - handle_center[0]) ** 2 + (mouse_pos[1] - handle_center[1]) ** 2 <= handle_radius ** 2
        handle_color = DARK_BLUE if hovering or self.active_slider == key else BLUE
        
        pygame.draw.circle(self.screen, handle_color, handle_center, handle_radius)
        pygame.draw.circle(self.screen, BLACK, handle_center, handle_radius, 2)
        
        # Slider label and value
        if key == "ball_radius":
            ball_mass = self.physics_data.get("ball_mass", 0.5)
            value_text = f"{slider['text']}: {slider['value']:.0f}px"
            mass_text = f"質量: {ball_mass:.2f} kg"
            
            label_surf = self.font.render(value_text, True, BLACK)
            mass_surf = self.font.render(mass_text, True, BLACK)
            
            label_rect = label_surf.get_rect(center=(middle_x, y_offset - 5))
            mass_rect = mass_surf.get_rect(center=(middle_x, y_offset + 45))
            
            self.screen.blit(label_surf, label_rect)
            self.screen.blit(mass_surf, mass_rect)
        else:
            value_text = f"{slider['text']}: {slider['value']:.1f}"
            if key == "wind_angle":
                value_text += "°"
            elif "wind" in key or "thrust" in key:
                if "thrust" in key:
                    value_text = f"{slider['text']}: {slider['value']:.0f}"
                value_text += " " + ("N" if "thrust" in key else "m/s")
            
            label_surf = self.font.render(value_text, True, BLACK)
            label_rect = label_surf.get_rect(center=(middle_x, y_offset - 5))
            self.screen.blit(label_surf, label_rect)
    
    def draw_physics_info(self):
        """Draw physics information panel"""
        info_x = self.current_view_width + 10
        info_y = self.current_height - 200
        info_width = self.middle_section_width - 20
        info_height = 180
        
        # Background
        info_rect = pygame.Rect(info_x, info_y, info_width, info_height)
        pygame.draw.rect(self.screen, WHITE, info_rect)
        pygame.draw.rect(self.screen, BLACK, info_rect, 2)
        
        # Title
        title = self.font.render("物理數據", True, BLACK)
        self.screen.blit(title, (info_x + 10, info_y + 5))
        
        # Physics data
        y_pos = info_y + 30
        line_height = 20
        
        physics_info = [
            f"球體位置: ({self.ball_pos[0]:.0f}, {self.ball_pos[1]:.0f}, {self.ball_pos[2]:.0f})",
            f"球體速度: ({self.ball_velocity[0]:.1f}, {self.ball_velocity[1]:.1f}, {self.ball_velocity[2]:.1f})",
            f"上方壓力: {self.physics_data['top_pressure']/1000:.1f} kPa",
            f"下方壓力: {self.physics_data['bottom_pressure']/1000:.1f} kPa",
            f"壓力差: {self.physics_data['pressure_diff']/1000:.2f} kPa",
            f"升力: {self.physics_data['lift_force']:.2f} N",
            f"側向力: {self.physics_data['side_force']:.2f} N",
            f"球體質量: {self.physics_data.get('ball_mass', 0.5):.2f} kg"
        ]
        
        for info in physics_info:
            if y_pos + line_height < info_y + info_height - 5:
                text_surf = self.font.render(info, True, DARK_BLUE)
                self.screen.blit(text_surf, (info_x + 10, y_pos))
                y_pos += line_height
    
    def draw_instructions(self):
        """Draw instructions panel"""
        inst_x = 10
        inst_y = 50
        inst_width = self.current_view_width - 20
        inst_height = 120
        
        # Semi-transparent background
        inst_surface = pygame.Surface((inst_width, inst_height), pygame.SRCALPHA)
        pygame.draw.rect(inst_surface, (255, 255, 255, 200), (0, 0, inst_width, inst_height), border_radius=10)
        pygame.draw.rect(inst_surface, BLACK, (0, 0, inst_width, inst_height), 2, border_radius=10)
        self.screen.blit(inst_surface, (inst_x, inst_y))
        
        # Instructions text
        instructions = [
            "🖱️ 拖拽球體: 在任一視圖中點擊並拖拽球體",
            "🎛️ 調整參數: 使用右側滑桿控制風力和球體屬性",
            "📊 觀察數據: 右下角顯示即時物理數據",
            "🌪️ 伯努利原理: P + ½ρv² + ρgh = 常數",
            "💡 顏色含義: 🟢上升 🟡平衡 🔴下降",
            "🌬️ 按 V 鍵切換風速圖顯示"
        ]
        
        y_pos = inst_y + 10
        for instruction in instructions:
            text_surf = self.font.render(instruction, True, BLACK)
            self.screen.blit(text_surf, (inst_x + 10, y_pos))
            y_pos += 20
    
    def handle_slider_interaction(self, pos):
        """Handle slider clicks and updates"""
        if pos[0] < self.current_view_width or pos[0] > self.current_view_width + self.middle_section_width:
            return False
        
        middle_x = self.current_view_width + self.middle_section_width // 2
        slider_width = int(self.middle_section_width * 0.8)
        y_offset = 70
        y_increment = int(self.current_height * 0.15)
        
        for key in self.sliders:
            slider_rect = pygame.Rect(
                middle_x - slider_width // 2,
                y_offset + 10,
                slider_width,
                30
            )
            
            if slider_rect.collidepoint(pos):
                self.active_slider = key
                self.update_slider_value(key, pos[0])
                return True
            
            y_offset += y_increment
        
        return False
    
    def update_slider_value(self, key, mouse_x):
        """Update slider value based on mouse position"""
        middle_x = self.current_view_width + self.middle_section_width // 2
        slider_width = int(self.middle_section_width * 0.8)
        slider_x = middle_x - slider_width // 2
        
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
            if pos[0] < self.current_view_width:
                ball_distance = math.sqrt((pos[0] - self.ball_pos[0])**2 + 
                                        (pos[1] - self.ball_pos[1])**2)
                if ball_distance <= self.ball_radius:
                    self.dragging = True
                    self.active_view = "xy"
                    self.drag_offset = [pos[0] - self.ball_pos[0], pos[1] - self.ball_pos[1]]
                    self.ball_velocity = [0, 0, 0]  # Reset velocity
                    return True
            
            # Check ZX view (right panel) - X horizontal, Z vertical
            elif pos[0] > self.current_view_width + self.middle_section_width:
                zx_x = pos[0] - (self.current_view_width + self.middle_section_width)
                ball_x_screen = self.ball_pos[0]
                ball_z_screen = self.current_height // 2 - self.ball_pos[2]
                
                ball_distance = math.sqrt((zx_x - ball_x_screen)**2 + 
                                        (pos[1] - ball_z_screen)**2)
                if ball_distance <= self.ball_radius:
                    self.dragging = True
                    self.active_view = "zx"
                    self.drag_offset = [zx_x - ball_x_screen, pos[1] - ball_z_screen]
                    self.ball_velocity = [0, 0, 0]  # Reset velocity
                    return True
        
        elif event_type == "motion" and self.dragging:
            if self.active_view == "xy":
                # Update X and Y coordinates
                new_x = pos[0] - self.drag_offset[0]
                new_y = pos[1] - self.drag_offset[1]
                
                # Constrain to view bounds
                self.ball_pos[0] = max(self.ball_radius, 
                                     min(self.current_view_width - self.ball_radius, new_x))
                self.ball_pos[1] = max(self.ball_radius, 
                                     min(self.current_height - self.ball_radius, new_y))
            
            elif self.active_view == "zx":
                # Update X and Z coordinates (X horizontal, Z vertical)
                zx_x = pos[0] - (self.current_view_width + self.middle_section_width)
                new_x = zx_x - self.drag_offset[0]
                new_z = (self.current_height // 2 - pos[1]) + self.drag_offset[1]
                
                # Constrain to bounds
                self.ball_pos[0] = max(self.ball_radius, 
                                     min(self.current_view_width - self.ball_radius, new_x))
                self.ball_pos[2] = max(-self.current_height // 3, 
                                     min(self.current_height // 3, new_z))
        
        return False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Try ball interaction first
                    if not self.handle_ball_interaction(event.pos, "down"):
                        # Try slider interaction
                        self.handle_slider_interaction(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.active_view = None
                    self.active_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.handle_ball_interaction(event.pos, "motion")
                elif self.active_slider:
                    self.update_slider_value(self.active_slider, event.pos[0])
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self.show_wind_vectors = not self.show_wind_vectors
            
            elif event.type == pygame.VIDEORESIZE:
                self.current_width = max(800, event.w)
                self.current_height = max(600, event.h)
                self.middle_section_width = int(self.current_width * 0.25)
                self.current_view_width = (self.current_width - self.middle_section_width) // 2
                
                # Resize screen
                self.screen = pygame.display.set_mode((self.current_width, self.current_height), 
                                                    pygame.RESIZABLE)
                
                # Resize particle surfaces
                self.particle_surface_xy = pygame.Surface((self.current_view_width, self.current_height), 
                                                        pygame.SRCALPHA)
                self.particle_surface_xz = pygame.Surface((self.current_view_width, self.current_height), 
                                                        pygame.SRCALPHA)
                
                # Adjust ball position if needed
                self.ball_pos[0] = min(self.ball_pos[0], self.current_view_width - self.ball_radius)
                self.ball_pos[1] = min(self.ball_pos[1], self.current_height - self.ball_radius)
                
                # Update fonts
                base_font_size = max(12, int(self.current_height / 50))
                preferred_fonts = ['Noto Sans TC', 'Microsoft JhengHei', 'Segoe UI', 'Arial']
                self.font = pygame.font.SysFont(preferred_fonts, base_font_size)
                self.title_font = pygame.font.SysFont(preferred_fonts, int(base_font_size * 1.5), bold=True)
        
        return True
    
    def generate_particles(self):
        """Generate new particles to replace dead ones"""
        dead_count = sum(1 for p in self.particles if not p.is_alive())
        
        for _ in range(min(dead_count, 5)):  # Replace a few each frame
            x = random.uniform(-400, 400)
            y = random.uniform(-300, 300)
            z = random.uniform(-200, 200)
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
            
            # Draw view backgrounds
            xy_rect = pygame.Rect(0, 0, self.current_view_width, self.current_height)
            zx_rect = pygame.Rect(self.current_view_width + self.middle_section_width, 0, 
                                self.current_view_width, self.current_height)
            
            pygame.draw.rect(self.screen, LIGHT_BLUE, xy_rect)
            pygame.draw.rect(self.screen, LIGHT_BLUE, zx_rect)
            
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
