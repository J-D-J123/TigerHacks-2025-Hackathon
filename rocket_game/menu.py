# menu.py — Main Menu for Spaceship Launch Game + Retro Rocket integration

import pygame
import math
import sys
from core import settings
from core.store import open_store  # Import the store function
from retro_rocket import start_game as launch_rocket_game  # import the real one safely

def launch_retro_rocket():
    pygame.quit()  # clean any leftover state
    launch_rocket_game()
    pygame.init()  # re-init Pygame for menu
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

pygame.init()

# --- Setup ---
FPS = settings.FPS
WIDTH, HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(settings.WINDOW_TITLE)
clock = pygame.time.Clock()
FONT_NAME = settings.FONT_NAME or pygame.font.get_default_font()
BASE_FONT_SIZE = settings.BASE_FONT_SIZE
TITLE = settings.WINDOW_TITLE

# --- Colors ---
WHITE = settings.WHITE
GRAY = settings.GRAY
ACCENT = settings.ACCENT
BG1 = settings.BG1
BG2 = settings.BG2

# --- Menu configuration ---
OPTIONS = ["Start", "Store", "Settings", "Credits", "Quit"]

OPTION_CALLBACKS = {
    "Start": launch_retro_rocket,
    "Store": lambda: open_store(screen),
    "Settings": lambda: settings.open_settings(screen),
    "Credits": lambda: print("Credits pressed"),
    "Quit": lambda: sys.exit(0),
}


def draw_background(surface, t):
    """Simple animated radial gradient-ish background."""
    w, h = surface.get_size()
    for i in range(6):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        radius = int(max(w, h) * (0.15 + 0.12 * i))
        cx = int(w * (0.5 + 0.02 * math.sin(t * 0.7 + i)))
        cy = int(h * (0.45 + 0.02 * math.cos(t * 0.9 + i)))
        color = (*BG2, max(10, 40 - 6 * i))
        pygame.draw.circle(s, color, (cx, cy), radius)
        surface.blit(s, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def render_menu(surface, selected_idx, mouse_idx):
    w, h = surface.get_size()
    # Title
    title_font = pygame.font.Font(FONT_NAME, int(BASE_FONT_SIZE * 1.6))
    title_surf = title_font.render(TITLE, True, WHITE)
    title_rect = title_surf.get_rect(center=(w / 2, h * 0.18))
    surface.blit(title_surf, title_rect)

    # Calculate menu layout based on window size
    menu_font = pygame.font.Font(FONT_NAME, max(18, int(BASE_FONT_SIZE * (w / 800))))
    spacing = menu_font.get_linesize() * 1.6
    total_h = spacing * len(OPTIONS)
    start_y = h / 2 - total_h / 2

    for i, option in enumerate(OPTIONS):
        text = option
        surf = menu_font.render(text, True, WHITE)
        rect = surf.get_rect(center=(w / 2, start_y + i * spacing))

        # Highlight logic
        if i == selected_idx:
            pad_x, pad_y = 18 * (w / 800), 8 * (h / 500)
            bg_rect = pygame.Rect(0, 0, rect.width + pad_x * 2, rect.height + pad_y * 2)
            bg_rect.center = rect.center
            pygame.draw.rect(surface, (*ACCENT, 80), bg_rect, border_radius=14)

            sel_font = pygame.font.Font(FONT_NAME, int(menu_font.get_height() * 1.12))
            surf = sel_font.render(text, True, (10, 10, 20))
            rect = surf.get_rect(center=bg_rect.center)
        elif i == mouse_idx:
            surf = menu_font.render(text, True, ACCENT)
            rect = surf.get_rect(center=(w / 2, start_y + i * spacing))

        surface.blit(surf, rect)


def get_mouse_index(surface):
    mx, my = pygame.mouse.get_pos()
    w, h = surface.get_size()
    menu_font = pygame.font.Font(FONT_NAME, max(18, int(BASE_FONT_SIZE * (w / 800))))
    spacing = menu_font.get_linesize() * 1.6
    total_h = spacing * len(OPTIONS)
    start_y = h / 2 - total_h / 2
    for i in range(len(OPTIONS)):
        rect = pygame.Rect(0, 0, w * 0.6, spacing)
        rect.center = (w / 2, start_y + i * spacing)
        if rect.collidepoint(mx, my):
            return i
    return None


def main():
    selected = 0
    t = 0.0

    while True:
        t += clock.get_time() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(OPTIONS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(OPTIONS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = OPTIONS[selected]
                    OPTION_CALLBACKS.get(choice, lambda: None)()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mi = get_mouse_index(screen)
                if mi is not None:
                    OPTION_CALLBACKS.get(OPTIONS[mi], lambda: None)()

        mouse_idx = get_mouse_index(screen)

        screen.fill(BG1)
        draw_background(screen, t)
        render_menu(screen, selected, mouse_idx)

        hint_font = pygame.font.Font(FONT_NAME, 14)
        hint = hint_font.render(
            "Use ↑ ↓ or W S to move — Enter to select — Resize window freely", True, GRAY
        )
        screen.blit(hint, (12, screen.get_height() - 26))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()