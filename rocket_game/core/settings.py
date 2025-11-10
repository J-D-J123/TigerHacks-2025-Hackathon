import pygame
import sys
import json
import os

# --- Display ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
WINDOW_TITLE = "Spaceship Survival"

# --- Colors ---
WHITE = (245, 245, 245)
GRAY = (130, 130, 140)
# ACCENT = (60, 180, 255)
ACCENT = (201, 134, 0)
BG1 = (18, 18, 28)
BG2 = (36, 30, 60)
SLIDER_BG = (60, 60, 70)
SLIDER_FG = ACCENT

# --- Fonts ---
BASE_FONT_SIZE = 36
FONT_NAME = None

# --- Slider config ---
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 8
KNOB_RADIUS = 12

# --- Settings file ---
SETTINGS_FILE = "settings.json"

# --- Default settings ---
default_settings = {
    "music_volume": 0.5,
    "sfx_volume": 0.7,
}

# --- Load or initialize settings ---
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
else:
    data = default_settings.copy()

MUSIC_VOLUME = data.get("music_volume", 0.5)
SFX_VOLUME = data.get("sfx_volume", 0.7)


def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump({
            "music_volume": MUSIC_VOLUME,
            "sfx_volume": SFX_VOLUME,
        }, f, indent=4)


def open_settings(screen):
    """Interactive settings screen with sliders (keyboard + mouse)."""
    global MUSIC_VOLUME, SFX_VOLUME, GRAVITY, THRUST_POWER
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_NAME, 32)

    options = [
        {"label": "Music Volume", "value": lambda: MUSIC_VOLUME, "min": 0, "max": 1, "step": 0.01},
        {"label": "SFX Volume", "value": lambda: SFX_VOLUME, "min": 0, "max": 1, "step": 0.01},
    ]

    selected = 0
    dragging = None  # currently dragged slider

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    adjust_option(options[selected], -1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    adjust_option(options[selected], 1)
                elif event.key == pygame.K_ESCAPE:
                    save_settings()
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # check if mouse is over a slider knob
                for i, opt in enumerate(options):
                    slider_rect = get_slider_rect(screen, i)
                    knob_x = slider_rect.x + int(SLIDER_WIDTH * (opt["value"]() - opt["min"]) / (opt["max"] - opt["min"]))
                    knob_y = slider_rect.y + SLIDER_HEIGHT // 2
                    if (mx - knob_x) ** 2 + (my - knob_y) ** 2 <= KNOB_RADIUS ** 2:
                        dragging = i
                        break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = None

            if event.type == pygame.MOUSEMOTION and dragging is not None:
                # update the dragged slider
                opt = options[dragging]
                slider_rect = get_slider_rect(screen, dragging)
                pct = (mx - slider_rect.x) / SLIDER_WIDTH
                pct = max(0, min(1, pct))
                val = opt["min"] + pct * (opt["max"] - opt["min"])
                set_option(opt, val)

        screen.fill(BG1)
        draw_title(screen, font, "Settings")

        for i, opt in enumerate(options):
            draw_slider(screen, font, opt, i, selected)

        hint_font = pygame.font.Font(FONT_NAME, 20)
        hint = hint_font.render("ESC to return — Drag sliders with mouse or use arrows", True, GRAY)
        screen.blit(hint, (screen.get_width() // 2 - 250, screen.get_height() - 40))

        pygame.display.flip()
        clock.tick(FPS)


def draw_title(screen, font, title):
    title_surf = font.render(title, True, WHITE)
    rect = title_surf.get_rect(center=(screen.get_width() / 2, 80))
    screen.blit(title_surf, rect)


def get_slider_rect(screen, idx):
    y_offset = 180 + idx * 80
    return pygame.Rect(screen.get_width() // 2 - SLIDER_WIDTH // 2, y_offset, SLIDER_WIDTH, SLIDER_HEIGHT)


def draw_slider(screen, font, option, idx, selected_idx):
    y_offset = 180 + idx * 80
    label_color = ACCENT if idx == selected_idx else WHITE
    label = font.render(option["label"], True, label_color)
    screen.blit(label, (screen.get_width() // 2 - 150, y_offset - 30))

    slider_rect = get_slider_rect(screen, idx)
    pygame.draw.rect(screen, SLIDER_BG, slider_rect, border_radius=SLIDER_HEIGHT // 2)

    pct = (option["value"]() - option["min"]) / (option["max"] - option["min"])
    fg_rect = pygame.Rect(slider_rect.x, slider_rect.y, int(SLIDER_WIDTH * pct), SLIDER_HEIGHT)
    pygame.draw.rect(screen, SLIDER_FG, fg_rect, border_radius=SLIDER_HEIGHT // 2)

    knob_x = slider_rect.x + int(SLIDER_WIDTH * pct)
    knob_y = slider_rect.y + SLIDER_HEIGHT // 2
    pygame.draw.circle(screen, ACCENT, (knob_x, knob_y), KNOB_RADIUS)

    value_text = font.render(f"{option['value']():.2f}" if option['value']() % 1 else f"{int(option['value']())}", True, WHITE)
    screen.blit(value_text, (slider_rect.right + 20, y_offset - 10))


def adjust_option(option, direction):
    val = option["value"]() + option["step"] * direction
    val = max(option["min"], min(option["max"], val))
    set_option(option, val)


def set_option(option, val):
    global MUSIC_VOLUME, SFX_VOLUME
    if option["label"] == "Music Volume":
        MUSIC_VOLUME = val
    elif option["label"] == "SFX Volume":
        SFX_VOLUME = val
