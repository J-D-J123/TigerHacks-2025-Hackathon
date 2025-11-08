"""
retro_rocket.py
A simple retro 2D rocket game using Pygame.
- Save/Load high score in save.json
- Controls: Left/Right rotate, Up thrust, Space shoot, P pause, Enter start/restart, Esc quit
"""

import pygame
import math
import random
import json
import os
from pathlib import Path

# --------------------------
# Config / constants
# --------------------------
SCREEN_W = 960
SCREEN_H = 640
FPS = 60

MAX_METEORS = 18
MAX_BULLETS = 40

SHIP_RADIUS = 12
BULLET_SPEED = 420.0
BULLET_LIFE = 1.6  # seconds
THRUST = 220.0
DRAG = 0.98

SAVE_FILE = "save.json"

# Colors
BLACK = (8, 10, 20)
WHITE = (240, 240, 240)
YELLOW = (255, 220, 80)
RED = (220, 70, 70)
GRAY = (120, 120, 120)
GREEN = (80, 200, 120)


# --------------------------
# Utility helpers
# --------------------------
def clamp(v, lo, hi):
    return max(lo, min(v, hi))


def wrap_pos(x, y):
    if x < 0:
        x += SCREEN_W
    if x >= SCREEN_W:
        x -= SCREEN_W
    if y < 0:
        y += SCREEN_H
    if y >= SCREEN_H:
        y -= SCREEN_H
    return x, y


def vec_length(x, y):
    return math.hypot(x, y)


# --------------------------
# Save / load highscore
# --------------------------
def load_save():
    try:
        p = Path(SAVE_FILE)
        if not p.exists():
            return {"highscore": 0}
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return {"highscore": int(data.get("highscore", 0))}
    except Exception:
        return {"highscore": 0}


def save_save(state):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"highscore": int(state.get("highscore", 0))}, f, indent=2)
    except Exception as e:
        print("Failed to save:", e)


# --------------------------
# Game classes
# --------------------------
class Bullet:
    __slots__ = ("x", "y", "vx", "vy", "life", "alive")

    def __init__(self):
        self.alive = False
        self.x = self.y = self.vx = self.vy = 0.0
        self.life = 0.0

    def spawn(self, x, y, vx, vy):
        self.alive = True
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = BULLET_LIFE

    def update(self, dt):
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x, self.y = wrap_pos(self.x, self.y)

    def draw(self, surf):
        if not self.alive:
            return
        r = 2
        pygame.draw.rect(surf, YELLOW, (int(self.x) - r, int(self.y) - r, r * 2, r * 2))


class Meteor:
    __slots__ = ("x", "y", "vx", "vy", "r", "alive")

    def __init__(self):
        self.alive = False

    def spawn(self):
        self.alive = True
        # spawn outside screen edges
        edge = random.choice([0, 1, 2, 3])  # 0 left,1 right,2 top,3 bottom
        pad = 30
        if edge == 0:
            self.x = -pad
            self.y = random.uniform(0, SCREEN_H)
        elif edge == 1:
            self.x = SCREEN_W + pad
            self.y = random.uniform(0, SCREEN_H)
        elif edge == 2:
            self.x = random.uniform(0, SCREEN_W)
            self.y = -pad
        else:
            self.x = random.uniform(0, SCREEN_W)
            self.y = SCREEN_H + pad

        ang = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20.0, 120.0)
        self.vx = math.cos(ang) * speed
        self.vy = math.sin(ang) * speed
        self.r = random.uniform(12.0, 42.0)

    def update(self, dt):
        if not self.alive:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x, self.y = wrap_pos(self.x, self.y)

    def draw(self, surf):
        if not self.alive:
            return
        # simple polygon meteor
        points = []
        segs = 10
        for i in range(segs):
            a = (i / segs) * math.tau
            rr = self.r * random.uniform(0.75, 1.15)
            points.append((self.x + math.cos(a) * rr, self.y + math.sin(a) * rr))
        pygame.draw.polygon(surf, GRAY, points)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), 2)


class Ship:
    __slots__ = ("x", "y", "vx", "vy", "angle", "alive", "lives", "score", "thrusting")

    def __init__(self):
        self.x = SCREEN_W * 0.5
        self.y = SCREEN_H * 0.5
        self.vx = 0.0
        self.vy = 0.0
        self.angle = -math.pi / 2.0  # pointing up
        self.alive = True
        self.lives = 3
        self.score = 0
        self.thrusting = False

    def reset(self):
        self.x = SCREEN_W * 0.5
        self.y = SCREEN_H * 0.5
        self.vx = self.vy = 0.0
        self.angle = -math.pi / 2.0
        self.alive = True
        self.lives = 3
        self.score = 0
        self.thrusting = False

    def update(self, dt):
        # apply drag
        self.vx *= pow(DRAG, dt * 60.0)
        self.vy *= pow(DRAG, dt * 60.0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x, self.y = wrap_pos(self.x, self.y)

    def draw(self, surf):
        # triangle ship
        s = SHIP_RADIUS
        ca = math.cos(self.angle)
        sa = math.sin(self.angle)
        # ship local points
        p1 = (s, 0)
        p2 = (-s * 0.6, s * 0.6)
        p3 = (-s * 0.6, -s * 0.6)

        def rot(px, py):
            return (self.x + px * ca - py * sa, self.y + px * sa + py * ca)

        v1 = rot(*p1)
        v2 = rot(*p2)
        v3 = rot(*p3)
        pygame.draw.polygon(surf, GREEN, [v1, v2, v3])
        if self.thrusting:
            # draw thrust flame
            pygame.draw.polygon(
                surf,
                YELLOW,
                [
                    (self.x + (-s * 0.8) * ca - 6 * sa, self.y + (-s * 0.8) * sa + 6 * ca),
                    (self.x + (-s * 1.6) * ca, self.y + (-s * 1.6) * sa),
                    (self.x + (-s * 0.8) * ca + 6 * sa, self.y + (-s * 0.8) * sa - 6 * ca),
                ],
            )


# --------------------------
# Main Game
# --------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Retro Rocket")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 20)
        self.bigfont = pygame.font.SysFont("Consolas", 46, bold=True)

        self.ship = Ship()
        self.bullets = [Bullet() for _ in range(MAX_BULLETS)]
        self.meteors = [Meteor() for _ in range(MAX_METEORS)]
        self.spawn_timer = 0.0
        self.running = True
        self.paused = False
        self.state = "menu"  # menu, playing, gameover
        self.highscore = load_save().get("highscore", 0)
        self.last_shot = 0.0
        self.shot_cooldown = 0.14

    def reset_for_play(self):
        self.ship.reset()
        for b in self.bullets:
            b.alive = False
        for m in self.meteors:
            m.alive = False
        self.spawn_timer = 0.0
        self.state = "playing"
        self.paused = False

    def spawn_meteor(self):
        for m in self.meteors:
            if not m.alive:
                m.spawn()
                return

    def fire_bullet(self):
        for b in self.bullets:
            if not b.alive:
                ax = math.cos(self.ship.angle)
                ay = math.sin(self.ship.angle)
                bx = self.ship.x + ax * (SHIP_RADIUS + 6)
                by = self.ship.y + ay * (SHIP_RADIUS + 6)
                b.spawn(
                    bx,
                    by,
                    self.ship.vx + ax * BULLET_SPEED,
                    self.ship.vy + ay * BULLET_SPEED,
                )
                break

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        if self.state != "playing":
            return
        if keys[pygame.K_LEFT]:
            self.ship.angle -= 3.5 * dt
        if keys[pygame.K_RIGHT]:
            self.ship.angle += 3.5 * dt
        if keys[pygame.K_UP]:
            ax = math.cos(self.ship.angle) * THRUST
            ay = math.sin(self.ship.angle) * THRUST
            self.ship.vx += ax * dt
            self.ship.vy += ay * dt
            self.ship.thrusting = True
        else:
            self.ship.thrusting = False

    def update(self, dt):
        if self.state == "menu" or self.state == "gameover":
            return
        if self.paused:
            return

        self.ship.update(dt)
        for b in self.bullets:
            b.update(dt)
        for m in self.meteors:
            if m.alive:
                m.update(dt)

        # bullet vs meteor
        for b in self.bullets:
            if not b.alive:
                continue
            for m in self.meteors:
                if not m.alive:
                    continue
                dx = b.x - m.x
                dy = b.y - m.y
                if dx * dx + dy * dy <= (2.5 + m.r) ** 2:
                    b.alive = False
                    m.alive = False
                    gained = int(m.r * 2)
                    self.ship.score += gained
                    if self.ship.score > self.highscore:
                        self.highscore = self.ship.score
                        save_save({"highscore": self.highscore})
                    break

        # ship vs meteor
        for m in self.meteors:
            if not m.alive:
                continue
            dx = self.ship.x - m.x
            dy = self.ship.y - m.y
            if dx * dx + dy * dy <= (SHIP_RADIUS + m.r) ** 2:
                m.alive = False
                self.ship.lives -= 1
                self.ship.x = SCREEN_W * 0.5
                self.ship.y = SCREEN_H * 0.5
                self.ship.vx = self.ship.vy = 0.0
                self.ship.angle = -math.pi / 2
                self.ship.thrusting = False
                if self.ship.lives <= 0:
                    self.ship.alive = False
                    self.state = "gameover"
                break

        # spawn meteors
        self.spawn_timer += dt
        if self.spawn_timer >= 0.6:
            self.spawn_timer = 0
            active = sum(1 for m in self.meteors if m.alive)
            if active < MAX_METEORS and random.random() < 0.85:
                self.spawn_meteor()

    def draw_hud(self):
        score_surf = self.font.render(f"SCORE: {self.ship.score}", True, WHITE)
        self.screen.blit(score_surf, (8, 8))
        high_surf = self.font.render(f"HIGH: {self.highscore}", True, GRAY)
        self.screen.blit(high_surf, (8, 32))
        for i in range(self.ship.lives):
            x = SCREEN_W - 20 - i * 20
            y = 12
            pygame.draw.polygon(self.screen, RED, [(x, y), (x + 8, y + 6), (x, y + 12)])

    def draw_center_text(self, lines, y_offset=0, big=False):
        font = self.bigfont if big else self.font
        total_h = sum(font.size(line)[1] + 6 for line in lines)
        y = SCREEN_H * 0.5 - total_h * 0.5 + y_offset
        for line in lines:
            surf = font.render(line, True, WHITE)
            rect = surf.get_rect(center=(SCREEN_W * 0.5, y + surf.get_height() * 0.5))
            self.screen.blit(surf, rect)
            y += surf.get_height() + 6

    def render(self):
        self.screen.fill(BLACK)

        for m in self.meteors:
            if m.alive:
                m.draw(self.screen)
        for b in self.bullets:
            if b.alive:
                b.draw(self.screen)
        if self.ship.alive:
            self.ship.draw(self.screen)

        self.draw_hud()

        if self.state == "menu":
            self.draw_center_text(
                [
                    "RETRO ROCKET",
                    "",
                    "Press Enter to Start",
                    "Arrow keys to steer, Space to shoot",
                ],
                y_offset=-40,
                big=True,
            )
        elif self.paused:
            self.draw_center_text(["PAUSED", "", "Press P to resume"], big=True)
        elif self.state == "gameover":
            self.draw_center_text(
                ["GAME OVER", f"Score: {self.ship.score}", "", "Press Enter to Restart"],
                big=True,
            )

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_RETURN:
                        if self.state in ("menu", "gameover"):
                            self.reset_for_play()
                    elif event.key == pygame.K_p:
                        if self.state == "playing":
                            self.paused = not self.paused
                    elif event.key == pygame.K_SPACE:
                        if (
                            self.state == "playing"
                            and not self.paused
                            and self.clock.get_time() / 1000.0 - self.last_shot
                            >= self.shot_cooldown
                        ):
                            self.fire_bullet()
                            self.last_shot = pygame.time.get_ticks() / 1000.0
                    elif event.key == pygame.K_r:
                        if self.state == "gameover":
                            self.reset_for_play()

            self.handle_input(dt)
            self.update(dt)
            self.render()

        save_save({"highscore": self.highscore})
        pygame.quit()


# --------------------------
# Main entry
# --------------------------
def start_game():
    Game().run()


if __name__ == "__main__":
    start_game()
