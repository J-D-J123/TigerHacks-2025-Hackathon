"""
retro_rocket.py
Optimized retro rocket game with clean UI
"""

import pygame
import math
import random
import json
from pathlib import Path

# Constants
SCREEN_W, SCREEN_H = 960, 640
FPS = 60
MAX_METEORS, MAX_BULLETS = 18, 40
SHIP_RADIUS, BULLET_SPEED, BULLET_LIFE = 12, 420.0, 1.0
THRUST, DRAG = 220.0, 0.98
NEAR_MISS_RADIUS, NEAR_MISS_POINTS, NEAR_MISS_COOLDOWN = 50.0, 25, 1.0
CREDITS_CONVERSION_RATE = 5
SAVE_FILE = "save.json"

# Colors
BLACK, WHITE = (8, 10, 20), (240, 240, 240)
YELLOW, RED, GRAY = (255, 220, 80), (220, 70, 70), (120, 120, 120)
GREEN, ORANGE = (80, 200, 120), (255, 165, 0)
JARVIS_BLUE, JARVIS_TEXT = (0, 120, 255, 180), (200, 230, 255)

# Utility Functions
def wrap_pos(x, y):
    return x % SCREEN_W, y % SCREEN_H

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    words, lines, current_line = text.split(' '), [], []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line: lines.append(' '.join(current_line))
            current_line = [word]
    if current_line: lines.append(' '.join(current_line))
    return lines

def load_save():
    try:
        p = Path(SAVE_FILE)
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return {"highscore": data.get("highscore", 0), "credits": data.get("credits", 0)}
    except Exception: pass
    return {"highscore": 0, "credits": 0}

def save_save(state):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"highscore": state.get("highscore", 0), "credits": state.get("credits", 0)}, f, indent=2)
    except Exception as e: print("Failed to save:", e)

def points_to_credits(points): return points // CREDITS_CONVERSION_RATE

# Game Classes
class Bullet:
    __slots__ = ("x", "y", "vx", "vy", "life", "alive")
    def __init__(self): self.alive = False
    def spawn(self, x, y, vx, vy):
        self.alive, self.x, self.y, self.vx, self.vy, self.life = True, x, y, vx, vy, BULLET_LIFE
    def update(self, dt):
        if not self.alive: return
        self.life -= dt
        if self.life <= 0: self.alive = False
        else: self.x, self.y = wrap_pos(self.x + self.vx * dt, self.y + self.vy * dt)
    def draw(self, surf):
        if self.alive: pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), 3)

class Meteor:
    __slots__ = ("x", "y", "vx", "vy", "r", "alive", "last_near_miss", "health", "max_health", "crack_level")
    def __init__(self): self.alive = False
    def spawn(self):
        edge, pad = random.choice([0, 1, 2, 3]), 30
        self.x = [-pad, SCREEN_W + pad, random.uniform(0, SCREEN_W), random.uniform(0, SCREEN_W)][edge]
        self.y = [random.uniform(0, SCREEN_H), random.uniform(0, SCREEN_H), -pad, SCREEN_H + pad][edge]
        ang, speed = random.uniform(0, 2 * math.pi), random.uniform(20.0, 120.0)
        self.vx, self.vy = math.cos(ang) * speed, math.sin(ang) * speed
        self.r = random.uniform(12.0, 42.0)
        self.max_health = 1 if self.r < 20 else 2 if self.r < 30 else 3
        self.health, self.crack_level, self.last_near_miss = self.max_health, 0, -NEAR_MISS_COOLDOWN
        self.alive = True
    def take_damage(self):
        self.health -= 1
        self.crack_level = 0 if self.health / self.max_health > 0.66 else 1 if self.health / self.max_health > 0.33 else 2
        if self.health <= 0: self.alive = False; return True
        return False
    def update(self, dt):
        if self.alive: self.x, self.y = wrap_pos(self.x + self.vx * dt, self.y + self.vy * dt); self.last_near_miss += dt
    def draw(self, surf):
        if not self.alive: return
        points = [(self.x + math.cos(a) * self.r * random.uniform(0.75, 1.15), 
                   self.y + math.sin(a) * self.r * random.uniform(0.75, 1.15)) for a in (i/10 * math.tau for i in range(10))]
        pygame.draw.polygon(surf, GRAY, points)
        if self.crack_level > 0:
            for _ in range(self.crack_level * 2 + 2):
                start_a, end_a = random.uniform(0, 2 * math.pi), random.uniform(-0.5, 0.5)
                start = (self.x + math.cos(start_a) * random.uniform(0, self.r * 0.3), 
                         self.y + math.sin(start_a) * random.uniform(0, self.r * 0.3))
                end = (self.x + math.cos(start_a + end_a) * self.r * random.uniform(0.7, 1.0),
                       self.y + math.sin(start_a + end_a) * self.r * random.uniform(0.7, 1.0))
                pygame.draw.line(surf, (60, 60, 80), (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), 2)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), 2)

class NearMissEffect:
    __slots__ = ("x", "y", "life", "alive", "points")
    def __init__(self): self.alive = False
    def spawn(self, x, y, points): self.alive, self.x, self.y, self.life, self.points = True, x, y, 1.5, points
    def update(self, dt):
        if self.alive: 
            self.life -= dt; self.y -= 40 * dt
            if self.life <= 0: self.alive = False
    def draw(self, surf):
        if not self.alive: return
        alpha, font_size = min(255, int(self.life * 255)), max(16, int(surf.get_width() * 0.018))
        text_surf = pygame.font.SysFont("Consolas", font_size, bold=True).render(f"+{self.points} NEAR MISS!", True, ORANGE)
        s = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA); s.blit(text_surf, (0, 0)); s.set_alpha(alpha)
        surf.blit(s, (int(self.x - text_surf.get_width() / 2), int(self.y)))

class Ship:
    __slots__ = ("x", "y", "vx", "vy", "angle", "alive", "lives", "score", "thrusting")
    def __init__(self): self.reset()
    def reset(self):
        self.x, self.y, self.vx, self.vy = SCREEN_W * 0.5, SCREEN_H * 0.5, 0.0, 0.0
        self.angle, self.alive, self.lives, self.score, self.thrusting = -math.pi / 2.0, True, 3, 0, False
    def update(self, dt):
        self.vx *= pow(DRAG, dt * 60.0); self.vy *= pow(DRAG, dt * 60.0)
        self.x, self.y = wrap_pos(self.x + self.vx * dt, self.y + self.vy * dt)
    def draw(self, surf):
        s, ca, sa = SHIP_RADIUS, math.cos(self.angle), math.sin(self.angle)
        points = [(self.x + px * ca - py * sa, self.y + px * sa + py * ca) for px, py in [(s, 0), (-s * 0.6, s * 0.6), (-s * 0.6, -s * 0.6)]]
        pygame.draw.polygon(surf, GREEN, points)
        if self.thrusting:
            pygame.draw.polygon(surf, YELLOW, [
                (self.x + (-s * 0.8) * ca - 6 * sa, self.y + (-s * 0.8) * sa + 6 * ca),
                (self.x + (-s * 1.6) * ca, self.y + (-s * 1.6) * sa),
                (self.x + (-s * 0.8) * ca + 6 * sa, self.y + (-s * 0.8) * sa - 6 * ca)])

# Main Game
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Retro Rocket")
        self.clock = pygame.time.Clock()
        self.update_font_sizes()
        self.ship = Ship()
        self.bullets = [Bullet() for _ in range(MAX_BULLETS)]
        self.meteors = [Meteor() for _ in range(MAX_METEORS)]
        self.near_miss_effects = [NearMissEffect() for _ in range(10)]
        self.spawn_timer, self.running, self.paused, self.state = 0.0, True, False, "menu"
        save_data = load_save()
        self.highscore, self.credits = save_data.get("highscore", 0), save_data.get("credits", 0)
        self.last_shot, self.shot_cooldown, self.should_return_to_menu = 0.0, 0.14, False

    def update_font_sizes(self):
        screen_width = self.screen.get_width()
        self.base_font_size = max(14, int(screen_width * 0.018))
        self.big_font_size = max(20, int(screen_width * 0.035))
        self.font = pygame.font.SysFont("Consolas", self.base_font_size)
        self.bigfont = pygame.font.SysFont("Consolas", self.big_font_size, bold=True)

    def reset_for_play(self):
        self.ship.reset()
        for obj in self.bullets + self.meteors + self.near_miss_effects: obj.alive = False
        self.spawn_timer, self.state, self.paused, self.should_return_to_menu = 0.0, "playing", False, False

    def return_to_menu(self):
        self.credits += points_to_credits(self.ship.score)
        save_save({"highscore": self.highscore, "credits": self.credits})
        self.should_return_to_menu = True

    def spawn_meteor(self):
        for m in self.meteors:
            if not m.alive: m.spawn(); return

    def fire_bullet(self):
        for b in self.bullets:
            if not b.alive:
                ax, ay = math.cos(self.ship.angle), math.sin(self.ship.angle)
                b.spawn(self.ship.x + ax * (SHIP_RADIUS + 6), self.ship.y + ay * (SHIP_RADIUS + 6),
                        self.ship.vx + ax * BULLET_SPEED, self.ship.vy + ay * BULLET_SPEED)
                break

    def spawn_near_miss_effect(self, x, y, points):
        for effect in self.near_miss_effects:
            if not effect.alive: effect.spawn(x, y, points); break

    def handle_input(self, dt):
        if self.state != "playing": return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.ship.angle -= 3.5 * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.ship.angle += 3.5 * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ax, ay = math.cos(self.ship.angle) * THRUST, math.sin(self.ship.angle) * THRUST
            self.ship.vx += ax * dt; self.ship.vy += ay * dt; self.ship.thrusting = True
        else: self.ship.thrusting = False

    def update(self, dt):
        if self.state in ["menu", "gameover"] or self.paused: return
        
        # Update objects
        self.ship.update(dt)
        for obj in self.bullets + self.meteors + self.near_miss_effects: obj.update(dt)

        # Bullet vs meteor collision
        for b in self.bullets:
            if not b.alive: continue
            for m in self.meteors:
                if m.alive and (b.x - m.x)**2 + (b.y - m.y)**2 <= (3 + m.r)**2:
                    b.alive = False
                    if m.take_damage():
                        gained = int(m.r * 2)
                        self.ship.score += gained
                        if self.ship.score > self.highscore: self.highscore = self.ship.score
                    break

        # Ship collision and near misses
        for m in self.meteors:
            if not m.alive: continue
            dx, dy = self.ship.x - m.x, self.ship.y - m.y
            dist_sq = dx*dx + dy*dy
            collision_dist = SHIP_RADIUS + m.r
            
            if dist_sq <= collision_dist**2:  # Collision
                m.alive = False
                self.ship.lives -= 1
                self.ship.x, self.ship.y = SCREEN_W * 0.5, SCREEN_H * 0.5
                self.ship.vx = self.ship.vy = 0.0
                self.ship.angle, self.ship.thrusting = -math.pi / 2, False
                if self.ship.lives <= 0: self.ship.alive = False; self.state = "gameover"
            
            elif dist_sq <= NEAR_MISS_RADIUS**2 and m.last_near_miss >= NEAR_MISS_COOLDOWN:  # Near miss
                self.ship.score += NEAR_MISS_POINTS
                if self.ship.score > self.highscore: self.highscore = self.ship.score
                self.spawn_near_miss_effect((self.ship.x + m.x) / 2, (self.ship.y + m.y) / 2, NEAR_MISS_POINTS)
                m.last_near_miss = 0.0

        # Spawn meteors
        self.spawn_timer += dt
        if self.spawn_timer >= 0.6:
            self.spawn_timer = 0
            if sum(1 for m in self.meteors if m.alive) < MAX_METEORS and random.random() < 0.85:
                self.spawn_meteor()

    def draw_hud(self):
        """Draw HUD without blue backgrounds"""
        self.update_font_sizes()
        screen_width = self.screen.get_width()
        
        # Draw text directly on screen (no background panels)
        self.screen.blit(self.font.render(f"SCORE: {self.ship.score}", True, JARVIS_TEXT), (20, 15))
        self.screen.blit(self.font.render(f"HIGH: {self.highscore}", True, JARVIS_TEXT), (20, 15 + self.base_font_size + 5))
        self.screen.blit(self.font.render(f"CREDITS: {self.credits}", True, JARVIS_TEXT), (20, 15 + (self.base_font_size + 5) * 2))
        self.screen.blit(self.font.render(f"LIVES: {self.ship.lives}", True, JARVIS_TEXT), (screen_width - 120, 15))
        
        # Draw ship icons for lives
        ship_size = max(6, int(screen_width * 0.006))
        for i in range(self.ship.lives):
            x = screen_width - 40 - i * (ship_size * 2)
            y = 15 + self.base_font_size + 10
            pygame.draw.polygon(self.screen, JARVIS_TEXT, 
                              [(x, y), (x + ship_size, y + ship_size), (x, y + ship_size * 2)])

    def draw_jarvis_panel(self, lines, center_y, big=False):
        """Draw instructional text with blue background"""
        self.update_font_sizes()
        font = self.bigfont if big else self.font
        
        # Wrap text
        max_width = int(self.screen.get_width() * 0.8)
        padding = max(20, int(self.screen.get_width() * 0.02))
        available_width = max_width - (padding * 2)
        
        wrapped_lines = []
        for line in lines:
            if line == "": wrapped_lines.append("")
            else: wrapped_lines.extend(wrap_text(line, font, available_width))
        
        # Calculate panel size
        line_heights = [font.size(line)[1] if line else int(font.get_height() * 0.5) for line in wrapped_lines]
        spacing = max(8, int(self.screen.get_height() * 0.012))
        total_height = sum(line_heights) + (len(wrapped_lines) - 1) * spacing
        
        max_line_width = max((font.size(line)[0] for line in wrapped_lines if line), default=0)
        panel_width = min(max_width, max_line_width + (padding * 2))
        panel_height = total_height + padding
        
        # Create and draw panel
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        corner_radius = max(15, int(self.screen.get_width() * 0.015))
        pygame.draw.rect(panel, JARVIS_BLUE, (0, 0, panel_width, panel_height), border_radius=corner_radius)
        
        # Draw text
        y = padding // 2
        for i, line in enumerate(wrapped_lines):
            if line:
                text_surf = font.render(line, True, JARVIS_TEXT)
                text_rect = text_surf.get_rect(center=(panel_width // 2, y + line_heights[i] // 2))
                panel.blit(text_surf, text_rect)
            y += line_heights[i] + (spacing if i < len(wrapped_lines) - 1 else 0)
        
        self.screen.blit(panel, panel.get_rect(center=(self.screen.get_width() // 2, center_y)))

    def render(self):
        self.screen.fill(BLACK)
        
        # Draw game objects
        for obj in self.meteors + self.bullets: obj.draw(self.screen)
        if self.ship.alive: self.ship.draw(self.screen)
        for effect in self.near_miss_effects: effect.draw(self.screen)
        
        self.draw_hud()

        # Draw instructional panels with blue backgrounds
        if self.state == "menu":
            self.draw_jarvis_panel([
                "RETRO ROCKET", "", "Press Enter to Start",
                "Arrow keys OR WASD to steer", "Space to shoot",
                f"Near misses: +{NEAR_MISS_POINTS} points!", f"Credits: {self.credits}", "",
                "Big meteors take multiple hits!"], self.screen.get_height() // 2 - 40, big=True)
        elif self.paused:
            self.draw_jarvis_panel(["PAUSED", "", "Press P to resume"], self.screen.get_height() // 2, big=True)
        elif self.state == "gameover":
            credits_earned = points_to_credits(self.ship.score)
            self.draw_jarvis_panel([
                "GAME OVER", f"Score: {self.ship.score}", f"Credits earned: {credits_earned}", "",
                "Press Enter to Play Again", "Press M for Main Menu"], self.screen.get_height() // 2, big=True)

        pygame.display.flip()

    def run(self):
        while self.running and not self.should_return_to_menu:
            dt = self.clock.tick(FPS) / 1000.0
            current_time = pygame.time.get_ticks() / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.update_font_sizes()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.state in ["playing", "gameover"]:
                        self.return_to_menu()
                    elif event.key == pygame.K_RETURN and self.state in ["menu", "gameover"]:
                        self.reset_for_play()
                    elif event.key == pygame.K_m and self.state == "gameover":
                        self.return_to_menu()
                    elif event.key == pygame.K_p and self.state == "playing":
                        self.paused = not self.paused
                    elif (event.key == pygame.K_SPACE and self.state == "playing" and not self.paused and 
                          current_time - self.last_shot >= self.shot_cooldown):
                        self.fire_bullet(); self.last_shot = current_time
                    elif event.key == pygame.K_r and self.state == "gameover":
                        self.reset_for_play()

            self.handle_input(dt)
            self.update(dt)
            self.render()

        if not self.should_return_to_menu:
            save_save({"highscore": self.highscore, "credits": self.credits})
            pygame.quit()

def start_game():
    Game().run()

if __name__ == "__main__":
    start_game()