# menu.py — Main Menu for Spaceship Launch Game + Retro Rocket integration

import pygame
import math
import sys
import os # Added for path operations
import random # Added for random image selection
from core import settings
from core.store import open_store  # Import the store function
from retro_rocket import start_game as launch_rocket_game  # import the real one safely

# --- Image and Background Management ---
IMAGE_FOLDER = "assets/loading_img/"
BACKGROUND_IMAGES = []
current_bg_image = None
# This will store the scaled image for the current screen size
current_scaled_bg = None 

def load_images():
    """Load all images from the specified folder."""
    global BACKGROUND_IMAGES
    BACKGROUND_IMAGES = []
    try:
        for filename in os.listdir(IMAGE_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                path = os.path.join(IMAGE_FOLDER, filename)
                # Load image once, keep original size
                image = pygame.image.load(path).convert() 
                BACKGROUND_IMAGES.append(image)
        if not BACKGROUND_IMAGES:
            print(f"Warning: No images found in {IMAGE_FOLDER}. Using solid background.")
    except FileNotFoundError:
        print(f"Error: Image folder {IMAGE_FOLDER} not found. Using solid background.")

def set_random_background(surface):
    """Randomly select a new background image and scale it to fit the screen."""
    global current_bg_image, current_scaled_bg
    
    if not BACKGROUND_IMAGES:
        current_bg_image = None
        current_scaled_bg = None
        return

    # Select a random image
    current_bg_image = random.choice(BACKGROUND_IMAGES)
    # Scale the image to fit the current surface size
    current_scaled_bg = scale_image_to_fit(current_bg_image, surface.get_size())

def scale_image_to_fit(image, target_size):
    """Scale an image to cover the target size while maintaining aspect ratio (cover)."""
    img_w, img_h = image.get_size()
    target_w, target_h = target_size
    
    # Calculate scale factor to cover the target area
    scale_factor = max(target_w / img_w, target_h / img_h)
    
    new_w = int(img_w * scale_factor)
    new_h = int(img_h * scale_factor)
    
    return pygame.transform.scale(image, (new_w, new_h))


def launch_retro_rocket():
    """Launches the rocket game and re-initializes Pygame for the menu."""
    pygame.quit()  # clean any leftover state
    launch_rocket_game()
    
    # --- Re-init Pygame for menu ---
    pygame.init()
    # Re-init screen and set a new random background
    global screen
    # Re-use the last size
    w, h = screen.get_size() 
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE) 
    pygame.display.set_caption(settings.WINDOW_TITLE)
    set_random_background(screen) # Set a new random background after returning

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
BG2 = settings.BG2 # Not used for image background, but kept for consistency

# --- Initialize image loading and set initial background ---
load_images()
set_random_background(screen)


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
    """Draws the current scaled background image or a solid color."""
    if current_scaled_bg:
        w, h = surface.get_size()
        img_w, img_h = current_scaled_bg.get_size()
        
        # Calculate offset to center the image (it will be larger than the screen)
        x_offset = (img_w - w) // 2
        y_offset = (img_h - h) // 2
        
        # Blit the centered, scaled image
        surface.blit(current_scaled_bg, (-x_offset, -y_offset))
        
        # Optional: Add a subtle overlay for better menu text visibility
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
    else:
        # Fallback to a solid background if no images are loaded
        surface.fill(BG1)


def render_menu(surface, selected_idx, mouse_idx):
    # ... (Rest of render_menu remains the same)
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
            # Reduced alpha for ACCENT background highlight over image
            pygame.draw.rect(surface, (*ACCENT, 120), bg_rect, border_radius=14) 

            sel_font = pygame.font.Font(FONT_NAME, int(menu_font.get_height() * 1.12))
            surf = sel_font.render(text, True, (10, 10, 20))
            rect = surf.get_rect(center=bg_rect.center)
        elif i == mouse_idx:
            surf = menu_font.render(text, True, ACCENT)
            rect = surf.get_rect(center=(w / 2, start_y + i * spacing))

        surface.blit(surf, rect)


def get_mouse_index(surface):
    # ... (This function remains the same as it handles menu interaction logic)
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
                # Re-scale the current background image on window resize
                w, h = event.w, event.h
                pygame.display.set_mode((w, h), pygame.RESIZABLE)
                
                # Check if we have an image before scaling
                if current_bg_image:
                    global current_scaled_bg
                    # Re-scale the original image to the new size
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

        # The image background drawing replaces the old screen.fill(BG1) and draw_background()
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