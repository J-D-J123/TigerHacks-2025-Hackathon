import pygame
import sys
import json
import os

# --- Display ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

# --- Colors ---
WHITE = (245, 245, 245)
GRAY = (130, 130, 140)
ACCENT = (60, 180, 255)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
GOLD = (255, 215, 0)
BG1 = (18, 18, 28)
BG2 = (36, 30, 60)

# --- Fonts ---
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
        "icon": "🚀"
    },
    "fuel_capacity": {
        "name": "Fuel Capacity",
        "description": "More fuel for longer burns",
        "max_level": 5,
        "base_cost": 300,
        "cost_multiplier": 1.4,
        "icon": "⛽"
    },
    "structure": {
        "name": "Structure",
        "description": "Better durability and stability",
        "max_level": 5,
        "base_cost": 400,
        "cost_multiplier": 1.6,
        "icon": "🛡️"
    },
    "avionics": {
        "name": "Avionics",
        "description": "Improved guidance and control",
        "max_level": 5,
        "base_cost": 600,
        "cost_multiplier": 1.7,
        "icon": "📡"
    },
    "heat_shield": {
        "name": "Heat Shield",
        "description": "Better heat resistance",
        "max_level": 5,
        "base_cost": 350,
        "cost_multiplier": 1.5,
        "icon": "🔥"
    }
}

# --- Load or initialize store data ---
def load_store_data():
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r") as f:
            return json.load(f)
    return default_store.copy()

def save_store_data(data):
    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Calculate upgrade cost
def get_upgrade_cost(upgrade_key, current_level):
    upgrade = UPGRADES[upgrade_key]
    return int(upgrade["base_cost"] * (upgrade["cost_multiplier"] ** (current_level - 1)))

# Check if can afford upgrade
def can_afford(store_data, upgrade_key):
    current_level = store_data[upgrade_key]
    if current_level >= UPGRADES[upgrade_key]["max_level"]:
        return False
    cost = get_upgrade_cost(upgrade_key, current_level + 1)
    return store_data["credits"] >= cost

# Purchase upgrade
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

def open_store(screen):
    """Interactive store window for purchasing upgrades."""
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(FONT_NAME, 48)
    font = pygame.font.Font(FONT_NAME, 28)
    small_font = pygame.font.Font(FONT_NAME, 20)
    
    store_data = load_store_data()
    
    upgrade_keys = list(UPGRADES.keys())
    selected = 0
    
    message = ""
    message_timer = 0
    message_color = WHITE
    
    while True:
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_store_data(store_data)
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(upgrade_keys)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(upgrade_keys)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    success, msg = purchase_upgrade(store_data, upgrade_keys[selected])
                    message = msg
                    message_timer = 120  # 2 seconds at 60 FPS
                    message_color = GREEN if success else RED
                elif event.key == pygame.K_ESCAPE:
                    save_store_data(store_data)
                    return store_data
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if clicked on an upgrade button
                for i, key in enumerate(upgrade_keys):
                    button_rect = get_upgrade_button_rect(screen, i)
                    if button_rect.collidepoint(mx, my):
                        success, msg = purchase_upgrade(store_data, key)
                        message = msg
                        message_timer = 120
                        message_color = GREEN if success else RED
                        break
        
        # Update message timer
        if message_timer > 0:
            message_timer -= 1
        
        # Draw
        screen.fill(BG1)
        
        # Title
        title_surf = title_font.render("UPGRADE STORE", True, ACCENT)
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 30))
        
        # Credits display
        credits_surf = font.render(f"Credits: {store_data['credits']} 💰", True, GOLD)
        screen.blit(credits_surf, (screen.get_width() // 2 - credits_surf.get_width() // 2, 100))
        
        # Draw upgrades
        for i, key in enumerate(upgrade_keys):
            draw_upgrade_card(screen, font, small_font, store_data, key, i, selected, mx, my)
        
        # Message
        if message_timer > 0:
            msg_surf = font.render(message, True, message_color)
            screen.blit(msg_surf, (screen.get_width() // 2 - msg_surf.get_width() // 2, screen.get_height() - 100))
        
        # Instructions
        hint = small_font.render("ESC to return — SPACE/ENTER or CLICK to buy — Arrow keys to navigate", True, GRAY)
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, screen.get_height() - 40))
        
        pygame.display.flip()
        clock.tick(FPS)

def get_upgrade_button_rect(screen, idx):
    card_width = 850
    card_height = 60
    x = (screen.get_width() - card_width) // 2
    y = 160 + idx * 70
    return pygame.Rect(x, y, card_width, card_height)

def draw_upgrade_card(screen, font, small_font, store_data, upgrade_key, idx, selected_idx, mx, my):
    upgrade = UPGRADES[upgrade_key]
    current_level = store_data[upgrade_key]
    max_level = upgrade["max_level"]
    
    card_rect = get_upgrade_button_rect(screen, idx)
    is_hovered = card_rect.collidepoint(mx, my)
    is_selected = idx == selected_idx
    is_maxed = current_level >= max_level
    can_buy = can_afford(store_data, upgrade_key) and not is_maxed
    
    # Card background
    if is_selected or is_hovered:
        bg_color = (50, 50, 80)
    else:
        bg_color = BG2
    
    pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)
    
    # Border
    border_color = ACCENT if is_selected else GRAY
    pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)
    
    # Icon and name
    icon_text = small_font.render(upgrade["icon"], True, WHITE)
    screen.blit(icon_text, (card_rect.x + 15, card_rect.y + 8))
    
    name_surf = font.render(upgrade["name"], True, WHITE)
    screen.blit(name_surf, (card_rect.x + 60, card_rect.y + 8))
    
    # Level display
    level_text = f"Lv.{current_level}/{max_level}"
    level_surf = small_font.render(level_text, True, GOLD if current_level > 1 else GRAY)
    screen.blit(level_surf, (card_rect.x + 300, card_rect.y + 15))
    
    # Description
    desc_surf = small_font.render(upgrade["description"], True, GRAY)
    screen.blit(desc_surf, (card_rect.x + 60, card_rect.y + 35))
    
    # Buy button / status
    button_x = card_rect.right - 180
    button_y = card_rect.y + 10
    button_rect = pygame.Rect(button_x, button_y, 160, 40)
    
    if is_maxed:
        pygame.draw.rect(screen, (40, 40, 40), button_rect, border_radius=5)
        button_text = small_font.render("MAXED OUT", True, GRAY)
    elif can_buy:
        pygame.draw.rect(screen, GREEN, button_rect, border_radius=5)
        cost = get_upgrade_cost(upgrade_key, current_level + 1)
        button_text = small_font.render(f"Buy: {cost} 💰", True, WHITE)
    else:
        pygame.draw.rect(screen, (60, 40, 40), button_rect, border_radius=5)
        cost = get_upgrade_cost(upgrade_key, current_level + 1)
        button_text = small_font.render(f"{cost} 💰", True, RED)
    
    screen.blit(button_text, (button_x + 80 - button_text.get_width() // 2, button_y + 20 - button_text.get_height() // 2))

# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Spaceship Store")
    
    store_data = open_store(screen)
    print("Final store data:", store_data)
    
    pygame.quit()