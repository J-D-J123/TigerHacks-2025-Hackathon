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
FONT_PATH = "assets/Coolvetica.otf" # Define the path to your custom font
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
    "heat_shield": 1,
    "battle_pass_level": 1,
    "battle_pass_xp": 0,
    "battle_pass_premium": False
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

# --- Battle Pass ---
BATTLE_PASS_LEVELS = 50
BATTLE_PASS_XP_PER_LEVEL = 1000

# Battle Pass rewards - (free, premium)
BATTLE_PASS_REWARDS = {
    1: (100, 300),  # (credits_free, credits_premium)
    5: (None, "special_skin_1"),
    10: (200, 500),
    15: (None, "special_skin_2"),
    20: (300, 700),
    25: ("emote_1", "emote_1_premium"),
    30: (400, 900),
    35: (None, "special_skin_3"),
    40: (500, 1100),
    45: ("emote_2", "emote_2_premium"),
    50: (1000, "legendary_skin")
}

# --- Load or initialize store data ---
def load_store_data():
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r") as f:
                data = json.load(f)
            
            # Migrate old save data to include new battle pass fields
            return migrate_store_data(data)
        except (json.JSONDecodeError, KeyError):
            # If file is corrupted, create new default data
            return default_store.copy()
    return default_store.copy()

def migrate_store_data(data):
    """Migrate old store data to include new battle pass fields"""
    # Ensure all default fields exist
    migrated_data = default_store.copy()
    
    # Copy existing values from old data
    for key in data:
        if key in migrated_data:
            migrated_data[key] = data[key]
    
    # Add battle pass fields if they don't exist
    if 'battle_pass_level' not in data:
        migrated_data['battle_pass_level'] = 1
    if 'battle_pass_xp' not in data:
        migrated_data['battle_pass_xp'] = 0
    if 'battle_pass_premium' not in data:
        migrated_data['battle_pass_premium'] = False
    
    return migrated_data

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

# Add XP to battle pass
def add_battle_pass_xp(store_data, xp):
    # Ensure battle pass fields exist
    if 'battle_pass_level' not in store_data:
        store_data['battle_pass_level'] = 1
    if 'battle_pass_xp' not in store_data:
        store_data['battle_pass_xp'] = 0
    
    store_data["battle_pass_xp"] += xp
    new_level = min(BATTLE_PASS_LEVELS, store_data["battle_pass_level"] + store_data["battle_pass_xp"] // BATTLE_PASS_XP_PER_LEVEL)
    levels_gained = new_level - store_data["battle_pass_level"]
    store_data["battle_pass_level"] = new_level
    store_data["battle_pass_xp"] %= BATTLE_PASS_XP_PER_LEVEL
    return levels_gained

# Purchase premium battle pass
def purchase_premium_battle_pass(store_data):
    # Ensure battle pass fields exist
    if 'battle_pass_premium' not in store_data:
        store_data['battle_pass_premium'] = False
    
    if store_data["battle_pass_premium"]:
        return False, "Already have premium battle pass!"
    
    # Premium Battle Pass cost
    PREMIUM_COST = 1500
    if store_data["credits"] < PREMIUM_COST:
        return False, f"Not enough credits! Needs {PREMIUM_COST} 💰"
    
    store_data["credits"] -= PREMIUM_COST
    store_data["battle_pass_premium"] = True
    return True, "Premium battle pass purchased!"

# Draw gradient background - FIXED to cover entire screen
def draw_gradient_background(screen):
    # Fill the entire screen with the gradient
    for y in range(screen.get_height()):
        # Create a gradient from dark blue to purple
        r = int(10 + (y / screen.get_height()) * 15)
        g = int(10 + (y / screen.get_height()) * 10)
        b = int(20 + (y / screen.get_height()) * 45)
        pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))

# Draw animated stars - FIXED to cover entire screen
def draw_stars(screen, time):
    for i in range(100):
        x = (i * 123) % screen.get_width()
        y = (i * 321) % screen.get_height()
        size = (math.sin(time * 0.5 + i) + 1) * 0.5 + 0.5
        brightness = 150 + int(100 * math.sin(time * 0.3 + i))
        pygame.draw.circle(screen, (brightness, brightness, brightness), (int(x), int(y)), int(size))

# Draw button with hover effect
def draw_button(screen, rect, text, font, color, hover_color, is_hovered):
    button_color = hover_color if is_hovered else color
    pygame.draw.rect(screen, button_color, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
    return rect

# Draw progress bar
def draw_progress_bar(screen, x, y, width, height, progress, color, bg_color):
    # Background
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=height//2)
    
    # Progress
    if progress > 0:
        progress_width = max(10, int(width * progress))
        pygame.draw.rect(screen, color, (x, y, progress_width, height), border_radius=height//2)
    
    # Border
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2, border_radius=height//2)

# Draw upgrade card with modern design
def draw_upgrade_card(screen, font, small_font, store_data, upgrade_key, idx, selected_idx, mx, my):
    upgrade = UPGRADES[upgrade_key]
    current_level = store_data[upgrade_key]
    max_level = upgrade["max_level"]
    
    card_width = 900
    card_height = 80
    x = (screen.get_width() - card_width) // 2
    y = 180 + idx * 100
    
    card_rect = pygame.Rect(x, y, card_width, card_height)
    is_hovered = card_rect.collidepoint(mx, my)
    is_selected = idx == selected_idx
    is_maxed = current_level >= max_level
    can_buy = can_afford(store_data, upgrade_key) and not is_maxed
    
    # Card background with gradient
    if is_selected or is_hovered:
        bg_color = (50, 50, 80, 180)
    else:
        bg_color = (30, 30, 50, 180)
    
    # Create a surface for the card with alpha
    card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
    pygame.draw.rect(card_surface, bg_color, (0, 0, card_width, card_height), border_radius=12)
    
    # Add a subtle border
    border_color = NEON_BLUE if is_selected else (80, 80, 100)
    pygame.draw.rect(card_surface, border_color, (0, 0, card_width, card_height), 2, border_radius=12)
    
    # Blit the card surface
    screen.blit(card_surface, (x, y))
    
    # Icon and name
    # The icon is an emoji, which may not render correctly with a custom font that doesn't include it.
    # It's kept as-is but be aware of potential rendering issues for non-standard characters.
    try:
        icon_text = small_font.render(upgrade["icon"], True, WHITE)
        screen.blit(icon_text, (x + 20, y + 20))
    except pygame.error:
        # Fallback if the font doesn't support the emoji
        pass
    
    name_surf = font.render(upgrade["name"], True, WHITE)
    screen.blit(name_surf, (x + 70, y + 15))
    
    # Level display with progress bar
    level_text = f"Lv.{current_level}/{max_level}"
    level_surf = small_font.render(level_text, True, GOLD if current_level > 1 else GRAY)
    screen.blit(level_surf, (x + 70, y + 45))
    
    # Progress bar for level
    progress_width = 200
    progress = current_level / max_level
    draw_progress_bar(screen, x + 180, y + 50, progress_width, 8, progress, NEON_BLUE, BG2)
    
    # Description
    desc_surf = small_font.render(upgrade["description"], True, GRAY)
    screen.blit(desc_surf, (x + 400, y + 30))
    
    # Buy button / status
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
        button_text = f"Buy: {cost} 💰"
    else:
        button_color = (60, 40, 40)
        button_hover = (70, 50, 50)
        cost = get_upgrade_cost(upgrade_key, current_level + 1)
        button_text = f"{cost} 💰"
    
    button_hovered = button_rect.collidepoint(mx, my)
    draw_button(screen, button_rect, button_text, small_font, button_color, button_hover, button_hovered)
    
    return card_rect

# Draw battle pass section
def draw_battle_pass(screen, font, small_font, store_data, mx, my):
    # Ensure battle pass fields exist
    if 'battle_pass_level' not in store_data:
        store_data['battle_pass_level'] = 1
    if 'battle_pass_xp' not in store_data:
        store_data['battle_pass_xp'] = 0
    if 'battle_pass_premium' not in store_data:
        store_data['battle_pass_premium'] = False
    
    # Battle pass header
    header_rect = pygame.Rect(50, 180, screen.get_width() - 100, 120) # Adjusted Y and height for better layout
    pygame.draw.rect(screen, BG3, header_rect, border_radius=12)
    pygame.draw.rect(screen, NEON_PURPLE, header_rect, 2, border_radius=12)
    
    title = font.render("BATTLE PASS", True, WHITE)
    screen.blit(title, (header_rect.centerx - title.get_width() // 2, header_rect.y + 10))
    
    # Level and XP
    level_text = f"Level {store_data['battle_pass_level']}/{BATTLE_PASS_LEVELS}"
    level_surf = small_font.render(level_text, True, GOLD)
    screen.blit(level_surf, (header_rect.centerx - level_surf.get_width() // 2, header_rect.y + 40))
    
    # XP progress bar
    xp_progress = store_data['battle_pass_xp'] / BATTLE_PASS_XP_PER_LEVEL
    draw_progress_bar(screen, header_rect.x + 50, header_rect.y + 70, header_rect.width - 100, 20, 
                      xp_progress, NEON_PURPLE, BG2)
    
    xp_text = f"{store_data['battle_pass_xp']}/{BATTLE_PASS_XP_PER_LEVEL} XP"
    xp_surf = small_font.render(xp_text, True, WHITE)
    screen.blit(xp_surf, (header_rect.centerx - xp_surf.get_width() // 2, header_rect.y + 72))
    
    # Premium status
    premium_status = "PREMIUM ACTIVE" if store_data["battle_pass_premium"] else "FREE TRACK"
    premium_color = GOLD if store_data["battle_pass_premium"] else GRAY
    premium_surf = small_font.render(premium_status, True, premium_color)
    screen.blit(premium_surf, (header_rect.right - premium_surf.get_width() - 20, header_rect.y + 15))
    
    # Buy premium button (if not already premium)
    premium_button = None
    if not store_data["battle_pass_premium"]:
        premium_button = pygame.Rect(header_rect.right - 180, header_rect.y + 40, 160, 30)
        premium_hovered = premium_button.collidepoint(mx, my)
        draw_button(screen, premium_button, "UPGRADE: 1500 💰", small_font, NEON_PURPLE, (200, 100, 255), premium_hovered)
    
    return premium_button

# Draw battle pass rewards
def draw_battle_pass_rewards(screen, font, small_font, store_data):
    # Ensure battle pass fields exist
    if 'battle_pass_level' not in store_data:
        store_data['battle_pass_level'] = 1
    
    current_level = store_data['battle_pass_level']
    
    # Rewards container
    rewards_rect = pygame.Rect(50, 320, screen.get_width() - 100, 300)
    pygame.draw.rect(screen, BG2, rewards_rect, border_radius=12)
    pygame.draw.rect(screen, NEON_BLUE, rewards_rect, 2, border_radius=12)
    
    title = font.render("UPCOMING REWARDS", True, WHITE)
    screen.blit(title, (rewards_rect.centerx - title.get_width() // 2, rewards_rect.y + 10))

    y_offset = rewards_rect.y + 50
    
    # Display up to 4 upcoming levels
    upcoming_levels = sorted([lvl for lvl in BATTLE_PASS_REWARDS.keys() if lvl > current_level])[:4]
    
    if not upcoming_levels:
        max_level_surf = font.render("ALL REWARDS EARNED!", True, GOLD)
        screen.blit(max_level_surf, (rewards_rect.centerx - max_level_surf.get_width() // 2, y_offset + 50))
        return

    for next_level in upcoming_levels:
        reward_free, reward_premium = BATTLE_PASS_REWARDS.get(next_level, (50, 100))

        level_text = f"Level {next_level}:"
        level_surf = small_font.render(level_text, True, GOLD)
        screen.blit(level_surf, (rewards_rect.x + 20, y_offset))
        
        # Free reward
        if reward_free:
            reward_type = f"{reward_free} 💰" if isinstance(reward_free, int) else reward_free
            free_text = f"Free: {reward_type}"
        else:
            free_text = "Free: (No Reward)"
        
        free_surf = small_font.render(free_text, True, GRAY)
        screen.blit(free_surf, (rewards_rect.x + 180, y_offset))
        
        # Premium reward
        if reward_premium:
            reward_type = f"{reward_premium} 💰" if isinstance(reward_premium, int) else reward_premium
            premium_text = f"Premium: {reward_type}"
        else:
            premium_text = "Premium: (No Reward)"
            
        premium_color = GOLD if store_data.get("battle_pass_premium", False) else NEON_PURPLE
        premium_surf = small_font.render(premium_text, True, premium_color)
        screen.blit(premium_surf, (rewards_rect.x + 450, y_offset))
        
        y_offset += 50
        
        # Separator for clarity
        if next_level != upcoming_levels[-1]:
             pygame.draw.line(screen, BG3, (rewards_rect.x + 10, y_offset - 5), (rewards_rect.right - 10, y_offset - 5), 1)

def open_store(screen):
    """Interactive store window for purchasing upgrades."""
    clock = pygame.time.Clock()
    
    # Font setup with Coolvetica.otf
    try:
        if not os.path.exists(FONT_PATH):
            print(f"Warning: Font file not found at {FONT_PATH}. Using default Pygame font.")
            FONT_NAME = None # Fallback to default
        else:
            FONT_NAME = FONT_PATH
            
        # Load fonts using the set FONT_NAME (or None for default)
        title_font = pygame.font.Font(FONT_NAME, 48)
        font = pygame.font.Font(FONT_NAME, 28)
        small_font = pygame.font.Font(FONT_NAME, 20)
        
    except pygame.error as e:
        print(f"Error loading font: {e}. Falling back to default Pygame font.")
        title_font = pygame.font.Font(None, 48)
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
    store_data = load_store_data()
    
    upgrade_keys = list(UPGRADES.keys())
    selected = 0
    
    message = ""
    message_timer = 0
    message_color = WHITE
    
    # Animation variables
    time = 0
    
    # Tab system
    current_tab = "upgrades"  # "upgrades" or "battle_pass"
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        time += dt
        mx, my = pygame.mouse.get_pos()
        
        # Update message timer
        if message_timer > 0:
            message_timer -= 1
        
        # Define tab button rectangles for event handling
        upgrades_tab_rect = pygame.Rect(screen.get_width() // 2 - 200, 120, 180, 40)
        battle_pass_tab_rect = pygame.Rect(screen.get_width() // 2 + 20, 120, 180, 40)
        
        # Get premium button rect for event handling
        premium_button_rect = None
        if current_tab == "battle_pass" and not store_data.get("battle_pass_premium", False):
            # Calculate rect manually since draw_battle_pass returns the rect
            header_rect = pygame.Rect(50, 180, screen.get_width() - 100, 120)
            premium_button_rect = pygame.Rect(header_rect.right - 180, header_rect.y + 40, 160, 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_store_data(store_data)
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_store_data(store_data)
                    return store_data
                
                # Tab switching
                if event.key == pygame.K_1:
                    current_tab = "upgrades"
                elif event.key == pygame.K_2:
                    current_tab = "battle_pass"
                    
                if current_tab == "upgrades":
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        selected = (selected + 1) % len(upgrade_keys)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        selected = (selected - 1) % len(upgrade_keys)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        success, msg = purchase_upgrade(store_data, upgrade_keys[selected])
                        message = msg
                        message_timer = 120  # 2 seconds at 60 FPS
                        message_color = GREEN if success else RED
                
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Tab clicks
                if upgrades_tab_rect.collidepoint(mx, my):
                    current_tab = "upgrades"
                elif battle_pass_tab_rect.collidepoint(mx, my):
                    current_tab = "battle_pass"
                
                if current_tab == "upgrades":
                    # Check if clicked on an upgrade button
                    for i, key in enumerate(upgrade_keys):
                        # Calculate the buy button's rect for the current upgrade card
                        card_width = 900
                        card_height = 80
                        x = (screen.get_width() - card_width) // 2
                        y = 180 + i * 100
                        button_rect = pygame.Rect(x + card_width - 180, y + 20, 160, 40)
                        
                        if button_rect.collidepoint(mx, my):
                            success, msg = purchase_upgrade(store_data, key)
                            message = msg
                            message_timer = 120
                            message_color = GREEN if success else RED
                            break
                        
                        # Also handle clicking anywhere on the card to select it
                        card_rect = pygame.Rect(x, y, card_width, card_height)
                        if card_rect.collidepoint(mx, my):
                            selected = i

                elif current_tab == "battle_pass":
                    # Check if clicked on premium battle pass button
                    if premium_button_rect and premium_button_rect.collidepoint(mx, my):
                        success, msg = purchase_premium_battle_pass(store_data)
                        message = msg
                        message_timer = 120
                        message_color = GREEN if success else RED
        
        # Draw - FIXED: Background now covers entire screen
        draw_gradient_background(screen)
        draw_stars(screen, time)
        
        # Title and credits
        title_surf = title_font.render("SPACESHIP STORE", True, WHITE) # Slightly changed title
        screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, 20))
        
        credits_surf = font.render(f"Credits: {store_data['credits']} 💰", True, GOLD)
        screen.blit(credits_surf, (screen.get_width() // 2 - credits_surf.get_width() // 2, 80))
        
        # Tab buttons (defined earlier for event handling)
        upgrades_hovered = upgrades_tab_rect.collidepoint(mx, my)
        battle_pass_hovered = battle_pass_tab_rect.collidepoint(mx, my)
        
        # Draw tabs
        upgrades_color = NEON_BLUE if current_tab == "upgrades" else BG3
        battle_pass_color = NEON_PURPLE if current_tab == "battle_pass" else BG3
        
        draw_button(screen, upgrades_tab_rect, "UPGRADES [1]", font, upgrades_color, (70, 200, 255), upgrades_hovered)
        draw_button(screen, battle_pass_tab_rect, "BATTLE PASS [2]", font, battle_pass_color, (200, 100, 255), battle_pass_hovered)
        
        # Draw content based on current tab
        if current_tab == "upgrades":
            # Draw upgrades
            for i, key in enumerate(upgrade_keys):
                draw_upgrade_card(screen, font, small_font, store_data, key, i, selected, mx, my)
        elif current_tab == "battle_pass":
            # Draw battle pass
            draw_battle_pass(screen, font, small_font, store_data, mx, my)
            draw_battle_pass_rewards(screen, font, small_font, store_data)
        
        # Message
        if message_timer > 0:
            msg_surf = font.render(message, True, message_color)
            screen.blit(msg_surf, (screen.get_width() // 2 - msg_surf.get_width() // 2, screen.get_height() - 100))
        
        # Instructions
        hint_text = "ESC to return — SPACE/ENTER or CLICK buy to upgrade — Arrow keys to navigate upgrades — 1/2 or CLICK tabs to switch"
        hint = small_font.render(hint_text, True, GRAY)
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, screen.get_height() - 40))
        
        pygame.display.flip()

def get_upgrade_button_rect(screen, idx):
    # This function is not used in the final loop logic for button detection, but is kept for completeness/old code reference.
    # Button detection is now done inline in the main loop to handle the specific buy button rect.
    card_width = 900
    card_height = 80
    x = (screen.get_width() - card_width) // 2
    y = 180 + idx * 100
    # Returns the entire card rect now, but the original intent was the button.
    # The actual buy button is at: pygame.Rect(x + card_width - 180, y + 20, 160, 40)
    return pygame.Rect(x, y, card_width, card_height) 

