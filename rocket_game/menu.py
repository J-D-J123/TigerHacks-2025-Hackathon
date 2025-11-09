# menu.py — Main Menu for Spaceship Launch Game + Retro Rocket integration

import pygame
import json

from pathlib import Path
from core import settings
from core.store import open_store
from core.store import load_store_data 
from retro_rocket import start_game as launch_rocket_game

# --- Image and Background Management ---
BACKGROUND_IMG = "assets/loading_img/"
current_bg_image = None
current_scaled_bg = None


def load_images():
    """Load background images if they exist."""
    global current_bg_image, current_scaled_bg

    try:
        # Example: if you have a specific file like "background.png"
        image_path = BACKGROUND_IMG + "2.png"
        image = pygame.image.load(image_path)
        current_bg_image = image
        current_scaled_bg = scale_image_to_fit(image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    except Exception as e:
        print(f"Background image loading error {e}")


def scale_image_to_fit(image, target_size):
    img_w, img_h = image.get_size()
    target_w, target_h = target_size
    scale_factor = max(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale_factor)
    new_h = int(img_h * scale_factor)
    return pygame.transform.scale(image, (new_w, new_h))


def launch_retro_rocket():
    """Launches the rocket game and re-initializes Pygame for the menu."""
    launch_rocket_game()


def reset_game_data():
    """Resets progress and store data to zero instead of deleting files."""
    
    # ask user if they should reset the data 
    # tkMessageBox.showinfo(title="Warning", message="Hello, World!")

    # get current path 
    current_file = Path(__file__)
    base_dir = current_file.parent
    store_file = base_dir / "store_data.json"

    try:
        # Reset store data values
        if store_file.exists():
            with open(store_file, "r") as f:
                data = json.load(f)

            # Set every numeric value to zero
            for key in data:
                if isinstance(data[key], (int, float)):
                    data[key] = 0
                elif isinstance(data[key], dict):
                    for subkey in data[key]:
                        if isinstance(data[key][subkey], (int, float)):
                            data[key][subkey] = 0

            with open(store_file, "w") as f:
                json.dump(data, f, indent=4)

            print(f"Store data reset to zero: {store_file}")
        else:
            print(f"store_data.json not found at: {store_file}")

    except Exception as e:
        print(f"Error resetting game data: {e}")


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

# --- Menu configuration ---
OPTIONS = ["Start", "Store", "Settings", "Credits"]


def show_credits_popup(surface):
    popup_running = True
    font = pygame.font.Font(FONT_NAME, 26)
    small_font = pygame.font.Font(FONT_NAME, 18)
    title_text = font.render("Game Credits", True, WHITE)
    names_text = small_font.render("Joey Johnson, Amit Singh, Dev Tiwari", True, ACCENT)
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
        surface.blit(title_text, title_text.get_rect(center=(w / 2, h / 2 - 40)))
        surface.blit(names_text, names_text.get_rect(center=(w / 2, h / 2)))
        surface.blit(hint_text, hint_text.get_rect(center=(w / 2, h / 2 + 50)))
        pygame.display.flip()
        clock.tick(30)

# quit the game
def quit_game():
    pygame.quit()
    raise SystemExit 

OPTION_CALLBACKS = {
    "Start": launch_retro_rocket,
    "Store": lambda: open_store(screen),
    "Settings": lambda: settings.open_settings(screen),
    "Credits": lambda: show_credits_popup(screen),
    "Quit": quit_game,
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

    # --- Title ---
    title_font = pygame.font.Font(FONT_NAME, int(BASE_FONT_SIZE * 1.6))
    title_surf = title_font.render(TITLE, True, WHITE)
    title_rect = title_surf.get_rect(center=(w / 2, 0))
    title_rect.top = 40
    surface.blit(title_surf, title_rect)

    # --- Menu options ---
    menu_font = pygame.font.Font(FONT_NAME, max(18, int(BASE_FONT_SIZE * (w / 800))))
    spacing = menu_font.get_linesize() * 1.6
    total_h = spacing * len(OPTIONS)
    available_height = h - (title_rect.bottom + 20)
    start_y = title_rect.bottom + 20 + (available_height - total_h) / 2

    for i, option in enumerate(OPTIONS):
        # only blue when hovered
        color = ACCENT if i == mouse_idx else WHITE
        surf = menu_font.render(option, True, color)
        rect = surf.get_rect(center=(w / 2, start_y + i * spacing))
        surface.blit(surf, rect)



def get_mouse_index(surface):
    mx, my = pygame.mouse.get_pos()
    w, h = surface.get_size()
    title_font = pygame.font.Font(FONT_NAME, int(BASE_FONT_SIZE * 1.6))
    title_surf = title_font.render(TITLE, True, WHITE)
    title_rect = title_surf.get_rect(center=(w / 2, 0))
    title_top_margin = 40
    title_rect.top = title_top_margin

    menu_font = pygame.font.Font(FONT_NAME, max(18, int(BASE_FONT_SIZE * (w / 800))))
    spacing = menu_font.get_linesize() * 1.6
    total_h = spacing * len(OPTIONS)
    available_height = h - (title_rect.bottom + 20)
    start_y = title_rect.bottom + 20 + (available_height - total_h) / 2

    for i in range(len(OPTIONS)):
        item_y = start_y + i * spacing
        text_surf = menu_font.render(OPTIONS[i], True, WHITE)
        text_rect = text_surf.get_rect(center=(w / 2, item_y))
        hit_rect = pygame.Rect(
            text_rect.left - 20,
            text_rect.top - 5,
            text_rect.width + 40,
            text_rect.height + 10
        )
        if hit_rect.collidepoint(mx, my):
            return i
    return None


def main():

    store_data = load_store_data()
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
                mx, my = event.pos
                if 10 <= mx <= 90 and 10 <= my <= 40:
                    reset_game_data()
                else:
                    mi = get_mouse_index(screen)
                    if mi is not None:
                        OPTION_CALLBACKS.get(OPTIONS[mi], lambda: None)()

        mouse_idx = get_mouse_index(screen)
        draw_background(screen, t)
        render_menu(screen, selected, mouse_idx)

        # --- Draw Reset Button ---
        reset_font = pygame.font.Font(FONT_NAME, 20)
        reset_text = reset_font.render("Reset", True, WHITE)
        reset_rect = pygame.Rect(10, 10, 80, 30)
        # pygame.draw.rect(screen, (*ACCENT, 180), reset_rect, border_radius=6)
        screen.blit(reset_text, (reset_rect.x + 8, reset_rect.y + 5))

        # --- Draw credits Button --- 
        credits_font = pygame.font.Font(FONT_NAME, 20)
        credits_text = credits_font.render(f"Credits: {store_data['credits']}", True, (255, 215, 0))  # gold color
        credits_rect = credits_text.get_rect(topright=(screen.get_width() - 10, 10))
        screen.blit(credits_text, credits_rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
