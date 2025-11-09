import pygame
import sys
import json
import os
import math

# --- Display ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# --- Colors ---
WHITE = (245, 245, 245)
GRAY = (130, 130, 140)
ACCENT = (60, 180, 255)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
GOLD = (255, 215, 0)
BG1 = (10, 10, 20)
BG2 = (25, 25, 40)
BG3 = (40, 35, 65)
NEON_BLUE = (0, 195, 255)
NEON_PURPLE = (180, 70, 255)

# --- Fonts ---
FONT_PATH = "assets/Coolvetica.otf"
FONT_NAME = None

# --- Store file ---
STORE_FILE = "store_data.json"

# --- Default store data ---
default_store = {
    "credits": 1000,
    "engines": 1,
    "fuel_capacity": 1,
    "structure": 1,
    "avionics": 1,
    "heat_shield": 1
}

# --- Upgrade definitions ---
UPGRADES = {
    "engines": {
        "name": "Engines",
        "description": "Increases thrust power",
        "max_level": 5,
        "base_cost": 500,
        "cost_multiplier": 1.5,
    },
    "fuel_capacity": {
        "name": "Fuel Capacity",
        "description": "More fuel for longer burns",
        "max_level": 5,
        "base_cost": 300,
        "cost_multiplier": 1.4,
    },
    "structure": {
        "name": "Structure",
        "description": "Better durability and stability",
        "max_level": 5,
        "base_cost": 400,
        "cost_multiplier": 1.6,
    },
    "avionics": {
        "name": "Avionics",
        "description": "Improved guidance and control",
        "max_level": 5,
        "base_cost": 600,
        "cost_multiplier": 1.7,
    },
    "heat_shield": {
        "name": "Heat Shield",
        "description": "Better heat resistance",
        "max_level": 5,
        "base_cost": 350,
        "cost_multiplier": 1.5,
    }
}

# --- Load or initialize store data ---
def load_store_data():
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r") as f:
                data = json.load(f)
            return migrate_store_data(data)
        except (json.JSONDecodeError, KeyError):
            return default_store.copy()
    return default_store.copy()

def migrate_store_data(data):
    """Migrate old store data to include all fields."""
    migrated_data = default_store.copy()
    for key in data:
        if key in migrated_data:
            migrated_data[key] = data[key]
    return migrated_data

def save_store_data(data):
    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Upgrade logic ---
def get_upgrade_cost(upgrade_key, current_level):
    upgrade = UPGRADES[upgrade_key]
    return int(upgrade["base_cost"] * (upgrade["cost_multiplier"] ** (current_level - 1)))

def can_afford(store_data, upgrade_key):
    current_level = store_data[upgrade_key]
    if current_level >= UPGRADES[upgrade_key]["max_level"]:
        return False
    cost = get_upgrade_cost(upgrade_key, current_level + 1)
    return store_data["credits"] >= cost

def purchase_upgrade(store_data, upgrade_key):
    current_level = store_data[upgrade_key]
    if current_level >= UPGRADES[upgrade_key]["max_level"]:
        return False, "Already at max level!"
    
    cost = get_upgrade_cost(upgrade_key, current_level + 1)
    if store_data["credits"] < cost:
        return False, "Not enough credits!"
    
    store_data["credits"] -= cost
    store_data[upgrade_key] += 1
    return True, "Upgrade purchased!"

# --- Drawing ---
def draw_gradient_background(screen):
    for y in range(screen.get_height()):
        r = int(10 + (y / screen.get_height()) * 15)
        g = int(10 + (y / screen.get_height()) * 10)
        b = int(20 + (y / screen.get_height()) * 45)
        pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))

def draw_stars(screen, time):
    for i in range(100):
        x = (i * 123) % screen.get_width()
        y = (i * 321) % screen.get_height()
        size = (math.sin(time * 0.5 + i) + 1) * 0.5 + 0.5
        brightness = 150 + int(100 * math.sin(time * 0.3 + i))
        pygame.draw.circle(screen, (brightness, brightness, brightness), (int(x), int(y)), int(size))

def draw_button(screen, rect, text, font, color, hover_color, is_hovered):
    button_color = hover_color if is_hovered else color
    pygame.draw.rect(screen, button_color, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def draw_progress_bar(screen, x, y, width, height, progress, color, bg_color):
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=height//2)
    if progress > 0:
        progress_width = max(10, int(width * progress))
        pygame.draw.rect(screen, color, (x, y, progress_width, height), border_radius=height//2)
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2, border_radius=height//2)

def draw_scroll_bar(screen, scroll_offset, max_scroll, visible_area_height, total_content_height):
    if max_scroll <= 0:
        return
    screen_width, screen_height = screen.get_size()
    bar_width = 12
    bar_x = screen_width - bar_width - 10
    bar_height = visible_area_height * (visible_area_height / total_content_height)
    bar_y = 10 + (scroll_offset / max_scroll) * (visible_area_height - bar_height)
    track_rect = pygame.Rect(bar_x, 10, bar_width, visible_area_height)
    pygame.draw.rect(screen, (60, 60, 80), track_rect, border_radius=6)
    thumb_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, NEON_BLUE, thumb_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, thumb_rect, 1, border_radius=6)

def draw_upgrade_card(screen, font, small_font, store_data, upgrade_key, idx, selected_idx, mx, my, scroll_offset):
    upgrade = UPGRADES[upgrade_key]
    current_level = store_data[upgrade_key]
    max_level = upgrade["max_level"]
    card_width = 900
    card_height = 80
    x = (screen.get_width() - card_width) // 2
    y = 180 + idx * 100 - scroll_offset
    if y + card_height < 0 or y > screen.get_height():
        return None
    card_rect = pygame.Rect(x, y, card_width, card_height)
    is_hovered = card_rect.collidepoint(mx, my)
    is_selected = idx == selected_idx
    is_maxed = current_level >= max_level
    can_buy = can_afford(store_data, upgrade_key) and not is_maxed
    bg_color = (50, 50, 80, 180) if is_selected or is_hovered else (30, 30, 50, 180)
    card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
    pygame.draw.rect(card_surface, bg_color, (0, 0, card_width, card_height), border_radius=12)
    border_color = NEON_BLUE if is_selected else (80, 80, 100)
    pygame.draw.rect(card_surface, border_color, (0, 0, card_width, card_height), 2, border_radius=12)
    screen.blit(card_surface, (x, y))
    name_surf = font.render(upgrade["name"], True, WHITE)
    screen.blit(name_surf, (x + 70, y + 15))
    level_text = f"Lv.{current_level}/{max_level}"
    level_surf = small_font.render(level_text, True, GOLD if current_level > 1 else GRAY)
    screen.blit(level_surf, (x + 70, y + 45))
    progress_width = 200
    progress = current_level / max_level
    draw_progress_bar(screen, x + 180, y + 50, progress_width, 8, progress, NEON_BLUE, BG2)
    desc_surf = small_font.render(upgrade["description"], True, GRAY)
    screen.blit(desc_surf, (x + 400, y + 30))
    button_x = x + card_width - 180
    button_y = y + 20
    button_rect = pygame.Rect(button_x, button_y, 160, 40)
    if is_maxed:
        button_color = (40, 40, 40)
        button_hover = (50, 50, 50)
        button_text = "MAXED OUT"
    elif can_buy:
        button_color = GREEN
        button_hover = (100, 220, 140)
        cost = get_upgrade_cost(upgrade_key, current_level + 1)
        button_text = f"Buy: {cost}"
    else:
        button_color = (60, 40, 40)
        button_hover = (70, 50, 50)
        cost = get_upgrade_cost(upgrade_key, current_level + 1)
        button_text = f"{cost}"
    button_hovered = button_rect.collidepoint(mx, my)
    draw_button(screen, button_rect, button_text, small_font, button_color, button_hover, button_hovered)
    return card_rect

def open_store(screen):
    clock = pygame.time.Clock()
    try:
        FONT_NAME = FONT_PATH if os.path.exists(FONT_PATH) else None
        title_font = pygame.font.Font(FONT_NAME, 48)
        font = pygame.font.Font(FONT_NAME, 28)
        small_font = pygame.font.Font(FONT_NAME, 20)
    except pygame.error:
        title_font = pygame.font.Font(None, 48)
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
    store_data = load_store_data()
    upgrade_keys = list(UPGRADES.keys())
    selected = 0
    message = ""
    message_timer = 0
    message_color = WHITE
    time = 0
    scroll_offset = 0
    scroll_speed = 30
    max_scroll = 0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        time += dt
        mx, my = pygame.mouse.get_pos()
        total_content_height = len(upgrade_keys) * 100
        visible_area_height = screen.get_height() - 180
        max_scroll = max(0, total_content_height - visible_area_height)
        
        if message_timer > 0:
            message_timer -= 1
        
        upgrades_tab_rect = pygame.Rect(screen.get_width() // 2 - 200, 120, 180, 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_store_data(store_data)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_store_data(store_data)
                return store_data
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - event.y * scroll_speed))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, key in enumerate(upgrade_keys):
                    card_width, card_height = 900, 80
                    x = (screen.get_width() - card_width) // 2
                    y = 180 + i * 100 - scroll_offset
                    if y + card_height >= 0 and y <= screen.get_height():
                        button_rect = pygame.Rect(x + card_width - 180, y + 20, 160, 40)
                        if button_rect.collidepoint(mx, my):
                            success, msg = purchase_upgrade(store_data, key)
                            message = msg
                            message_timer = 120
                            message_color = GREEN if success else RED
                            break
                        card_rect = pygame.Rect(x, y, card_width, card_height)
                        if card_rect.collidepoint(mx, my):
                            selected = i
        
        draw_gradient_background(screen)
        draw_stars(screen, time)
        title_surf = title_font.render("STORE", True, WHITE)
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 20))
        credits_surf = font.render(f"Credits: {store_data['credits']}", True, GOLD)
        screen.blit(credits_surf, (screen.get_width() // 2 - credits_surf.get_width() // 2, 80))
        
        for i, key in enumerate(upgrade_keys):
            draw_upgrade_card(screen, font, small_font, store_data, key, i, selected, mx, my, scroll_offset)
        
        if max_scroll > 0:
            draw_scroll_bar(screen, scroll_offset, max_scroll, visible_area_height, total_content_height)
        
        if message_timer > 0:
            msg_surf = font.render(message, True, message_color)
            screen.blit(msg_surf, (screen.get_width() // 2 - msg_surf.get_width() // 2, screen.get_height() - 60))
        
        pygame.display.flip()
