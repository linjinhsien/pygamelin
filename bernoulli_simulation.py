import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
GRAY = (200, 200, 200)

# Physics constants
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = 9.81  # m/s²

class Particle:
    def __init__(self, x, y, wind_speed, wind_angle, vertical_wind):
        self.x = x
        self.y = y
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
        
        # Update position
        self.x += vx * 0.1
        self.y += vy * 0.1
        
        # Calculate distance to ball
        dx = self.x - ball_pos[0]
        dy = self.y - ball_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # If close to the ball, adjust trajectory to flow around it
        if distance < ball_radius * 1.5:
            # Vector from particle to ball center
            norm = math.sqrt(dx*dx + dy*dy)
            if norm > 0:
                dx /= norm
                dy /= norm
                
                # Push particle away from ball
                deflection = (ball_radius * 1.5 - distance) * 0.2
                self.x += dx * deflection
                self.y += dy * deflection
                
                # Add some turbulence
                self.x += random.uniform(-0.5, 0.5)
                self.y += random.uniform(-0.5, 0.5)
        
        # Decrease life
        self.life -= 1
        
    def is_alive(self):
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT

class BernoulliSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("伯努利原理科学玩具 - Bernoulli Principle Simulation")
        self.clock = pygame.time.Clock()
        
        # Create a transparent surface for particles
        self.particle_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Simulation parameters
        self.wind_speed = 20  # m/s
        self.ball_radius = 50  # pixels
        self.ball_mass = 1.0  # kg
        self.wind_angle = 0  # degrees (0 = from left to right)
        self.vertical_wind = 0  # m/s
        
        # Ball position (initially centered)
        self.ball_pos = [WIDTH // 2, HEIGHT // 2]
        self.dragging = False
        
        # Particles for visualization
        self.particles = []
        
        # UI elements
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.show_info = True
        
        # Slider parameters
        self.sliders = {
            "wind_speed": {"value": self.wind_speed, "min": 0, "max": 50, "text": "風速 (m/s)"},
            "ball_radius": {"value": self.ball_radius, "min": 20, "max": 100, "text": "球體大小"},
            "ball_mass": {"value": self.ball_mass, "min": 0.1, "max": 2.0, "text": "球體質量 (kg)"},
            "wind_angle": {"value": self.wind_angle, "min": 0, "max": 360, "text": "風向角度 (°)"},
            "vertical_wind": {"value": self.vertical_wind, "min": -20, "max": 20, "text": "垂直風力 (m/s)"}
        }
        self.active_slider = None
        
    def generate_particles(self):
        # Add new particles from the left side
        if random.random() < 0.3:
            x = 0
            y = random.randint(0, HEIGHT)
            self.particles.append(Particle(x, y, self.wind_speed, self.wind_angle, self.vertical_wind))
            
        # Add particles from all sides based on wind angle
        angle_rad = math.radians(self.wind_angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        if random.random() < 0.3:
            if cos_angle < 0:  # Wind from right
                x = WIDTH
                y = random.randint(0, HEIGHT)
            elif cos_angle > 0:  # Wind from left
                x = 0
                y = random.randint(0, HEIGHT)
            elif sin_angle < 0:  # Wind from bottom
                x = random.randint(0, WIDTH)
                y = HEIGHT
            else:  # Wind from top
                x = random.randint(0, WIDTH)
                y = 0
                
            self.particles.append(Particle(x, y, self.wind_speed, self.wind_angle, self.vertical_wind))
    
    def calculate_lift(self):
        # Calculate lift using Bernoulli's principle
        # Simplified model: Lift = 0.5 * air_density * velocity^2 * area * lift_coefficient
        
        # Convert angle to radians
        angle_rad = math.radians(self.wind_angle)
        
        # Calculate effective velocity (including vertical component)
        vx = self.wind_speed * math.cos(angle_rad)
        vy = self.wind_speed * math.sin(angle_rad) + self.vertical_wind
        effective_velocity = math.sqrt(vx*vx + vy*vy)
        
        # Calculate projected area (simplified as circle)
        area = math.pi * (self.ball_radius/100)**2  # Convert pixels to meters (approximate)
        
        # Simplified lift coefficient based on Reynolds number
        lift_coefficient = 0.47  # Approximate for a sphere
        
        # Calculate pressure difference
        pressure_top = AIR_DENSITY * (effective_velocity**2) / 2
        pressure_bottom = pressure_top * 0.8  # Simplified pressure difference
        pressure_diff = pressure_top - pressure_bottom
        
        # Calculate lift force
        lift_force = pressure_diff * area
        
        # Calculate weight
        weight = self.ball_mass * GRAVITY
        
        # Net force (positive = upward)
        net_force = lift_force - weight
        
        return {
            "pressure_top": pressure_top,
            "pressure_bottom": pressure_bottom,
            "pressure_diff": pressure_diff,
            "lift_force": lift_force,
            "weight": weight,
            "net_force": net_force
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
            
        # Draw ball
        pygame.draw.circle(self.screen, color, self.ball_pos, self.ball_radius)
        pygame.draw.circle(self.screen, BLACK, self.ball_pos, self.ball_radius, 2)
        
        # Draw direction indicators
        angle_rad = math.radians(self.wind_angle)
        arrow_length = self.ball_radius * 0.8
        end_x = self.ball_pos[0] + arrow_length * math.cos(angle_rad)
        end_y = self.ball_pos[1] + arrow_length * math.sin(angle_rad)
        pygame.draw.line(self.screen, BLACK, self.ball_pos, (end_x, end_y), 3)
        
        # Draw vertical force indicator
        if abs(self.vertical_wind) > 0.1:
            vert_length = min(20, abs(self.vertical_wind)) * self.ball_radius / 20
            vert_sign = 1 if self.vertical_wind < 0 else -1  # Reverse for screen coordinates
            vert_end_y = self.ball_pos[1] + vert_sign * vert_length
            pygame.draw.line(self.screen, BLUE, 
                            (self.ball_pos[0], self.ball_pos[1]), 
                            (self.ball_pos[0], vert_end_y), 3)
    
    def draw_particles(self):
        # Clear the particle surface
        self.particle_surface.fill((0, 0, 0, 0))
        
        # Update and draw particles
        for particle in self.particles:
            particle.update(self.ball_pos, self.ball_radius)
            pygame.draw.circle(self.particle_surface, particle.color, 
                              (int(particle.x), int(particle.y)), particle.size)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        # Draw the particle surface
        self.screen.blit(self.particle_surface, (0, 0))
    
    def draw_ui(self):
        # Draw sliders
        y_offset = 20
        for key, slider in self.sliders.items():
            # Draw slider background
            slider_rect = pygame.Rect(20, y_offset, 200, 20)
            pygame.draw.rect(self.screen, GRAY, slider_rect)
            pygame.draw.rect(self.screen, BLACK, slider_rect, 1)
            
            # Calculate position for slider handle
            value_range = slider["max"] - slider["min"]
            handle_pos = 20 + int(200 * (slider["value"] - slider["min"]) / value_range)
            pygame.draw.rect(self.screen, BLACK, (handle_pos - 5, y_offset - 5, 10, 30))
            
            # Draw slider text
            value_text = f"{slider['text']}: {slider['value']:.1f}"
            text_surf = self.font.render(value_text, True, BLACK)
            self.screen.blit(text_surf, (230, y_offset))
            
            y_offset += 40
        
        # Draw force information
        forces = self.calculate_lift()
        info_x = WIDTH - 300
        info_y = 20
        
        info_texts = [
            f"上表面壓力: {forces['pressure_top']:.2f} Pa",
            f"下表面壓力: {forces['pressure_bottom']:.2f} Pa",
            f"壓力差: {forces['pressure_diff']:.2f} Pa",
            f"升力: {forces['lift_force']:.2f} N",
            f"重力: {forces['weight']:.2f} N",
            f"淨力: {forces['net_force']:.2f} N"
        ]
        
        for text in info_texts:
            text_surf = self.font.render(text, True, BLACK)
            self.screen.blit(text_surf, (info_x, info_y))
            info_y += 25
        
        # Draw information panel if enabled
        if self.show_info:
            self.draw_info_panel()
    
    def draw_info_panel(self):
        # Draw semi-transparent background
        info_surface = pygame.Surface((400, 300), pygame.SRCALPHA)
        info_surface.fill((240, 240, 240, 220))
        
        # Draw title
        title = self.title_font.render("伯努利原理", True, BLACK)
        info_surface.blit(title, (20, 20))
        
        # Draw explanation text
        explanation = [
            "伯努利原理說明流體速度增加時，壓力會下降。",
            "",
            "當空氣流過球體時，上表面的空氣流動較快，",
            "因此產生較低的壓力。下表面的空氣流動較慢，",
            "壓力較高，這種壓力差產生向上的升力。",
            "",
            "這個原理解釋了飛機機翼如何產生升力，以及",
            "許多其他流體動力學現象。",
            "",
            "按 'I' 鍵隱藏此信息"
        ]
        
        y_offset = 60
        for line in explanation:
            text_surf = self.font.render(line, True, BLACK)
            info_surface.blit(text_surf, (20, y_offset))
            y_offset += 25
        
        # Draw border
        pygame.draw.rect(info_surface, BLACK, (0, 0, 400, 300), 2)
        
        # Position in bottom right
        self.screen.blit(info_surface, (WIDTH - 420, HEIGHT - 320))
    
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
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking on ball
                    dx = event.pos[0] - self.ball_pos[0]
                    dy = event.pos[1] - self.ball_pos[1]
                    if dx*dx + dy*dy <= self.ball_radius*self.ball_radius:
                        self.dragging = True
                    
                    # Check if clicking on sliders
                    y_offset = 20
                    for key in self.sliders:
                        slider_rect = pygame.Rect(20, y_offset, 200, 20)
                        if slider_rect.collidepoint(event.pos):
                            self.active_slider = key
                            # Update slider value
                            self.update_slider(key, event.pos[0])
                        y_offset += 40
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.dragging = False
                    self.active_slider = None
            
            elif event.type == MOUSEMOTION:
                if self.dragging:
                    self.ball_pos[0] = event.pos[0]
                    self.ball_pos[1] = event.pos[1]
                
                if self.active_slider:
                    self.update_slider(self.active_slider, event.pos[0])
    
    def update_slider(self, key, x_pos):
        # Calculate new value based on slider position
        slider = self.sliders[key]
        value_range = slider["max"] - slider["min"]
        pos_ratio = max(0, min(1, (x_pos - 20) / 200))
        new_value = slider["min"] + pos_ratio * value_range
        
        # Update the value
        slider["value"] = new_value
        
        # Update the corresponding simulation parameter
        if key == "wind_speed":
            self.wind_speed = new_value
        elif key == "ball_radius":
            self.ball_radius = new_value
        elif key == "ball_mass":
            self.ball_mass = new_value
        elif key == "wind_angle":
            self.wind_angle = new_value
        elif key == "vertical_wind":
            self.vertical_wind = new_value
    
    def run(self):
        while True:
            # Handle events
            self.handle_events()
            
            # Generate new particles
            self.generate_particles()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_particles()
            self.draw_ball()
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    simulation = BernoulliSimulation()
    simulation.run()
