# menu.py — Main Menu for Spaceship Launch Game + Retro Rocket integration

import pygame
import math
import sys
import os
import random
from core import settings
from core.store import open_store
from retro_rocket import start_game as launch_rocket_game

# --- Image and Background Management ---
IMAGE_FOLDER = "assets/loading_img/"
BACKGROUND_IMAGES = []
current_bg_image = None
current_scaled_bg = None

def load_images():
    global BACKGROUND_IMAGES
    BACKGROUND_IMAGES = []
    try:
        for filename in os.listdir(IMAGE_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                path = os.path.join(IMAGE_FOLDER, filename)
                image = pygame.image.load(path).convert()
                BACKGROUND_IMAGES.append(image)
        if not BACKGROUND_IMAGES:
            print(f"Warning: No images found in {IMAGE_FOLDER}. Using solid background.")
    except FileNotFoundError:
        print(f"Error: Image folder {IMAGE_FOLDER} not found. Using solid background.")

def set_random_background(surface):
    global current_bg_image, current_scaled_bg
    if not BACKGROUND_IMAGES:
        current_bg_image = None
        current_scaled_bg = None
        return
    current_bg_image = random.choice(BACKGROUND_IMAGES)
    current_scaled_bg = scale_image_to_fit(current_bg_image, surface.get_size())

def scale_image_to_fit(image, target_size):
    img_w, img_h = image.get_size()
    target_w, target_h = target_size
    scale_factor = max(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale_factor)
    new_h = int(img_h * scale_factor)
    return pygame.transform.scale(image, (new_w, new_h))

def launch_retro_rocket():
    pygame.quit()
    launch_rocket_game()
    pygame.init()
    global screen
    w, h = screen.get_size()
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    pygame.display.set_caption(settings.WINDOW_TITLE)
    set_random_background(screen)

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

# --- Initialize image loading ---
load_images()
set_random_background(screen)

# --- Menu configuration ---
OPTIONS = ["Start", "Store", "Settings", "Credits", "Quit"]

def show_credits_popup(surface):
    popup_running = True
    font = pygame.font.Font(FONT_NAME, 26)
    small_font = pygame.font.Font(FONT_NAME, 18)
    title_text = font.render("Game Credits", True, WHITE)
    names_text = small_font.render("Joey Johnson, Amit Sing, Dev Tiwari", True, ACCENT)
    hint_text = small_font.render("Click anywhere or press any key to close", True, GRAY)
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    while popup_running:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                popup_running = False
        draw_background(surface, 0)
        surface.blit(overlay, (0, 0))
        w, h = surface.get_size()
        surface.blit(title_text, title_text.get_rect(center=(w/2, h/2 - 40)))
        surface.blit(names_text, names_text.get_rect(center=(w/2, h/2)))
        surface.blit(hint_text, hint_text.get_rect(center=(w/2, h/2 + 50)))
        pygame.display.flip()
        clock.tick(30)

OPTION_CALLBACKS = {
    "Start": launch_retro_rocket,
    "Store": lambda: open_store(screen),
    "Settings": lambda: settings.open_settings(screen),
    "Credits": lambda: show_credits_popup(screen),
    "Quit": lambda: sys.exit(0),
}

def draw_background(surface, t):
    if current_scaled_bg:
        w, h = surface.get_size()
        img_w, img_h = current_scaled_bg.get_size()
        x_offset = (img_w - w) // 2
        y_offset = (img_h - h) // 2
        surface.blit(current_scaled_bg, (-x_offset, -y_offset))
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))
    else:
        surface.fill(BG1)

def render_menu(surface, selected_idx, mouse_idx):
    w, h = surface.get_size()
    title_font = pygame.font.Font(FONT_NAME, int(BASE_FONT_SIZE * 1.6))
    title_surf = title_font.render(TITLE, True, WHITE)
    title_rect = title_surf.get_rect(center=(w / 2, 0))
    title_rect.top = 40
    surface.blit(title_surf, title_rect)
    menu_font = pygame.font.Font(FONT_NAME, max(18, int(BASE_FONT_SIZE * (w / 800))))
    spacing = menu_font.get_linesize() * 1.6
    total_h = spacing * len(OPTIONS)
    available_height = h - (title_rect.bottom + 20)
    start_y = title_rect.bottom + 20 + (available_height - total_h) / 2
    for i, option in enumerate(OPTIONS):
        surf = menu_font.render(option, True, WHITE)
        rect = surf.get_rect(center=(w / 2, start_y + i * spacing))
        if i == selected_idx:
            pad_x, pad_y = 18 * (w / 800), 8 * (h / 500)
            bg_rect = pygame.Rect(0, 0, rect.width + pad_x * 2, rect.height + pad_y * 2)
            bg_rect.center = rect.center
            pygame.draw.rect(surface, (*ACCENT, 120), bg_rect, border_radius=14)
            sel_font = pygame.font.Font(FONT_NAME, int(menu_font.get_height() * 1.12))
            surf = sel_font.render(option, True, (10, 10, 20))
            rect = surf.get_rect(center=bg_rect.center)
        elif i == mouse_idx:
            surf = menu_font.render(option, True, ACCENT)
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
                w, h = event.w, event.h
                pygame.display.set_mode((w, h), pygame.RESIZABLE)
                if current_bg_image:
                    global current_scaled_bg
                    current_scaled_bg = scale_image_to_fit(current_bg_image, (w, h))
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
        draw_background(screen, t)
        render_menu(screen, selected, mouse_idx)
        hint_font = pygame.font.Font(FONT_NAME, 14)
        hint = hint_font.render("Use ↑ ↓ or W S to move — Enter to select — Resize window freely", True, GRAY)
        screen.blit(hint, (12, screen.get_height() - 26))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
