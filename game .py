import pygame
import sys
import random
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rescue Ops 2D")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game states
MENU = 0
PLAYING = 1
SHOP = 2
PAUSED = 3
GAME_OVER = 4
VICTORY = 5
current_state = MENU

# Fonts
font_large = pygame.font.SysFont('Arial', 50)
font_medium = pygame.font.SysFont('Arial', 30)
font_small = pygame.font.SysFont('Arial', 20)

# Player settings
class Player:
    def __init__(self):
        self.reset()
        self.unlocked_characters = [0]  # Index of unlocked characters
        self.unlocked_weapons = [0]     # Index of unlocked weapons
        self.currency = 1000           # Starting in-game currency
        self.vip_currency = 0          # Currency bought with real money
        self.current_character = 0
        self.current_weapon = 0
        self.sensitivity = 1.0         # 0.5 for low, 1.0 for medium, 1.5 for high
        self.view_mode = "tpp"         # "tpp" or "fpp"
        
    def reset(self):
        self.health = 100
        self.position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.angle = 0
        self.ammo = 30
        self.score = 0
        self.level = 1
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            global current_state
            current_state = GAME_OVER
            
    def purchase_character(self, character_index):
        character = characters[character_index]
        if character["vip"] and self.vip_currency >= character["cost"]:
            self.vip_currency -= character["cost"]
            self.unlocked_characters.append(character_index)
            return True
        elif not character["vip"] and self.currency >= character["cost"]:
            self.currency -= character["cost"]
            self.unlocked_characters.append(character_index)
            return True
        return False
        
    def purchase_weapon(self, weapon_index):
        weapon = weapons[weapon_index]
        if weapon["vip"] and self.vip_currency >= weapon["cost"]:
            self.vip_currency -= weapon["cost"]
            self.unlocked_weapons.append(weapon_index)
            return True
        elif not weapon["vip"] and self.currency >= weapon["cost"]:
            self.currency -= weapon["cost"]
            self.unlocked_weapons.append(weapon_index)
            return True
        return False

# Game data
characters = [
    {"name": "Rookie", "cost": 0, "vip": False, "health": 100, "speed": 5, "color": BLUE},
    {"name": "Commando", "cost": 500, "vip": False, "health": 120, "speed": 6, "color": GREEN},
    {"name": "Elite", "cost": 70, "vip": True, "health": 150, "speed": 7, "color": RED},
    # ... add up to 50 characters
]

weapons = [
    {"name": "Pistol", "cost": 0, "vip": False, "damage": 20, "ammo": 12, "fire_rate": 0.5, "color": BLACK},
    {"name": "SMG", "cost": 200, "vip": False, "damage": 25, "ammo": 30, "fire_rate": 0.2, "color": (100, 100, 100)},
    {"name": "Assault Rifle", "cost": 50, "vip": True, "damage": 35, "ammo": 30, "fire_rate": 0.15, "color": (150, 75, 0)},
    # ... add more weapons
]

levels = [
    {"name": "Family Rescue", "enemies": 5, "environment": "house", "bg_color": (200, 200, 255)},
    {"name": "Apartment Siege", "enemies": 8, "environment": "apartment", "bg_color": (255, 200, 200)},
    # ... add up to 500 levels
]

# Enemy class
class Enemy:
    def __init__(self, level):
        self.health = 30 + level * 2
        self.damage = 10 + level
        self.speed = 2 + level * 0.1
        self.size = 30
        self.position = [
            random.choice([0, SCREEN_WIDTH]),
            random.randint(0, SCREEN_HEIGHT)
        ]
        self.color = (random.randint(150, 255), 0, 0)
        
    def update(self, player_pos):
        # Simple AI: move toward player
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            self.position[0] += (dx / dist) * self.speed
            self.position[1] += (dy / dist) * self.speed
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.size)

# Bullet class
class Bullet:
    def __init__(self, x, y, angle, damage):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.damage = damage
        self.lifetime = 60  # frames
        
    def update(self):
        self.x += self.speed * pygame.math.Vector2(1, 0).rotate(-self.angle).x
        self.y += self.speed * pygame.math.Vector2(1, 0).rotate(-self.angle).y
        self.lifetime -= 1
        return self.lifetime <= 0
        
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 5)

# Game objects
player = Player()
enemies = []
bullets = []
last_shot = 0
mpesa_number = "0715242363"

# Helper functions
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def show_menu():
    screen.fill(BLACK)
    
    # Title
    draw_text("RESCUE OPS", font_large, WHITE, SCREEN_WIDTH//2, 100)
    
    # Menu options
    draw_text("1. Start Game", font_medium, WHITE, SCREEN_WIDTH//2, 250)
    draw_text("2. Character Shop", font_medium, WHITE, SCREEN_WIDTH//2, 300)
    draw_text("3. Weapon Shop", font_medium, WHITE, SCREEN_WIDTH//2, 350)
    draw_text("4. Settings", font_medium, WHITE, SCREEN_WIDTH//2, 400)
    draw_text("5. Exit", font_medium, WHITE, SCREEN_WIDTH//2, 450)
    
    # Player info
    draw_text(f"Currency: {player.currency}", font_small, GREEN, SCREEN_WIDTH//2, 550)
    draw_text(f"VIP Points: {player.vip_currency}", font_small, YELLOW, SCREEN_WIDTH//2, 580)

def show_shop(shop_type):
    screen.fill(BLACK)
    items = characters if shop_type == "characters" else weapons
    
    # Title
    draw_text(f"{shop_type.upper()} SHOP", font_large, WHITE, SCREEN_WIDTH//2, 50)
    
    # Show items
    for i, item in enumerate(items):
        y_pos = 120 + i * 60
        color = GREEN if i in (player.unlocked_characters if shop_type == "characters" else player.unlocked_weapons) else WHITE
        vip_tag = " [VIP]" if item["vip"] else ""
        cost = f"Ksh.{item['cost']}" if item["vip"] else f"{item['cost']} coins"
        
        draw_text(f"{i+1}. {item['name']}{vip_tag} - {cost}", font_medium, color, SCREEN_WIDTH//2, y_pos)
        
        # Show stats
        if shop_type == "characters":
            stats = f"Health: {item['health']} | Speed: {item['speed']}"
        else:
            stats = f"Damage: {item['damage']} | Ammo: {item['ammo']} | Fire Rate: {item['fire_rate']}"
        
        draw_text(stats, font_small, color, SCREEN_WIDTH//2, y_pos + 25)
    
    # Back option
    draw_text("0. Back to Menu", font_medium, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)
    
    # Player info
    draw_text(f"Currency: {player.currency}", font_small, GREEN, 100, SCREEN_HEIGHT - 30)
    draw_text(f"VIP Points: {player.vip_currency}", font_small, YELLOW, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30)

def show_settings():
    screen.fill(BLACK)
    
    # Title
    draw_text("SETTINGS", font_large, WHITE, SCREEN_WIDTH//2, 100)
    
    # View mode
    draw_text(f"View Mode: {player.view_mode.upper()}", font_medium, WHITE, SCREEN_WIDTH//2, 200)
    draw_text("Press V to toggle", font_small, WHITE, SCREEN_WIDTH//2, 240)
    
    # Sensitivity
    draw_text(f"Sensitivity: {'High' if player.sensitivity == 1.5 else 'Medium' if player.sensitivity == 1.0 else 'Low'}", 
              font_medium, WHITE, SCREEN_WIDTH//2, 300)
    draw_text("Press 1 for Low, 2 for Medium, 3 for High", font_small, WHITE, SCREEN_WIDTH//2, 340)
    
    # MPESA Purchase
    draw_text("Add VIP Points via MPESA", font_medium, YELLOW, SCREEN_WIDTH//2, 400)
    draw_text("Press 7 for Ksh.70 (100 VIP)", font_small, WHITE, SCREEN_WIDTH//2, 440)
    draw_text("Press 5 for Ksh.500 (750 VIP)", font_small, WHITE, SCREEN_WIDTH//2, 470)
    draw_text("Press 1 for Ksh.1000 (1500 VIP)", font_small, WHITE, SCREEN_WIDTH//2, 500)
    
    # Back option
    draw_text("0. Back to Menu", font_medium, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)

def init_level():
    global enemies
    enemies = []
    for _ in range(levels[player.level-1]["enemies"]):
        enemies.append(Enemy(player.level))

def draw_game():
    # Background based on level
    screen.fill(levels[player.level-1]["bg_color"])
    
    # Draw environment (simplified)
    if levels[player.level-1]["environment"] == "house":
        pygame.draw.rect(screen, (139, 69, 19), (100, 100, 300, 200))  # House
    elif levels[player.level-1]["environment"] == "apartment":
        pygame.draw.rect(screen, (169, 169, 169), (100, 100, 200, 400))  # Apartment
    
    # Draw player
    if player.view_mode == "tpp":
        # Third person view - show player character
        pygame.draw.circle(screen, characters[player.current_character]["color"], 
                          (int(player.position[0]), int(player.position[1])), 20)
        
        # Draw a line indicating direction
        end_x = player.position[0] + 30 * pygame.math.Vector2(1, 0).rotate(-player.angle).x
        end_y = player.position[1] + 30 * pygame.math.Vector2(1, 0).rotate(-player.angle).y
        pygame.draw.line(screen, BLACK, player.position, (end_x, end_y), 2)
    else:
        # First person view - just show crosshair
        pygame.draw.line(screen, RED, (SCREEN_WIDTH//2 - 20, SCREEN_HEIGHT//2), 
                         (SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2), 2)
        pygame.draw.line(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20), 
                         (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20), 2)
    
    # Draw enemies
    for enemy in enemies:
        enemy.draw()
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw()
    
    # HUD
    draw_text(f"Health: {player.health}", font_small, RED, 100, 20)
    draw_text(f"Ammo: {player.ammo}/{weapons[player.current_weapon]['ammo']}", font_small, BLACK, 100, 50)
    draw_text(f"Level: {player.level} - {levels[player.level-1]['name']}", font_small, BLACK, SCREEN_WIDTH//2, 20)
    draw_text(f"Score: {player.score}", font_small, BLACK, SCREEN_WIDTH - 100, 20)

def handle_mpesa_purchase(amount, vip_points):
    print(f"Initiating MPESA payment of Ksh.{amount} to {mpesa_number}")
    # In a real game, this would trigger the STK push
    # For this demo, we'll just add the VIP points
    player.vip_currency += vip_points
    return True

# Main game loop
clock = pygame.time.Clock()
init_level()

running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Menu navigation
        if current_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_state = PLAYING
                    player.reset()
                    init_level()
                elif event.key == pygame.K_2:
                    current_state = SHOP
                    shop_type = "characters"
                elif event.key == pygame.K_3:
                    current_state = SHOP
                    shop_type = "weapons"
                elif event.key == pygame.K_4:
                    current_state = SETTINGS
                elif event.key == pygame.K_5:
                    running = False
        
        # Shop navigation
        elif current_state == SHOP:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    current_state = MENU
                elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    item_index = event.key - pygame.K_1
                    items = characters if shop_type == "characters" else weapons
                    if item_index < len(items):
                        if item_index in (player.unlocked_characters if shop_type == "characters" else player.unlocked_weapons):
                            # Select item
                            if shop_type == "characters":
                                player.current_character = item_index
                            else:
                                player.current_weapon = item_index
                        else:
                            # Try to purchase
                            if shop_type == "characters":
                                if not player.purchase_character(item_index):
                                    print("Not enough currency!")
                            else:
                                if not player.purchase_weapon(item_index):
                                    print("Not enough currency!")
        
        # Settings
        elif current_state == SETTINGS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    current_state = MENU
                elif event.key == pygame.K_v:
                    player.view_mode = "fpp" if player.view_mode == "tpp" else "tpp"
                elif event.key == pygame.K_1:
                    player.sensitivity = 0.5  # Low
                elif event.key == pygame.K_2:
                    player.sensitivity = 1.0  # Medium
                elif event.key == pygame.K_3:
                    player.sensitivity = 1.5  # High
                elif event.key == pygame.K_7:
                    handle_mpesa_purchase(70, 100)
                elif event.key == pygame.K_5:
                    handle_mpesa_purchase(500, 750)
                elif event.key == pygame.K_1 and pygame.KMOD_SHIFT:  # Actually need to handle this differently
                    handle_mpesa_purchase(1000, 1500)
        
        # Game over/victory
        elif current_state in (GAME_OVER, VICTORY):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    current_state = MENU
                elif event.key == pygame.K_q:
                    running = False
    
    # Game logic
    if current_state == PLAYING:
        # Player movement
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]:
            move_vector.y -= 1
        if keys[pygame.K_s]:
            move_vector.y += 1
        if keys[pygame.K_a]:
            move_vector.x -= 1
        if keys[pygame.K_d]:
            move_vector.x += 1
            
        if move_vector.length() > 0:
            move_vector = move_vector.normalize() * characters[player.current_character]["speed"] * player.sensitivity
            player.position[0] += move_vector.x
            player.position[1] += move_vector.y
            
            # Boundary checking
            player.position[0] = max(0, min(SCREEN_WIDTH, player.position[0]))
            player.position[1] = max(0, min(SCREEN_HEIGHT, player.position[1]))
        
        # Player rotation (aiming)
        if player.view_mode == "tpp":
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player.position[0]
            dy = mouse_y - player.position[1]
            player.angle = pygame.math.Vector2(dx, dy).angle_to((1, 0))
        
        # Shooting
        if pygame.mouse.get_pressed()[0] and player.ammo > 0:
            current_time = pygame.time.get_ticks()
            if current_time - last_shot > weapons[player.current_weapon]["fire_rate"] * 1000:
                last_shot = current_time
                player.ammo -= 1
                
                if player.view_mode == "fpp":
                    # Shoot straight ahead in FPP
                    angle = 0
                else:
                    # Use calculated angle in TPP
                    angle = player.angle
                
                bullets.append(Bullet(player.position[0], player.position[1], angle, weapons[player.current_weapon]["damage"]))
        
        # Reload
        if keys[pygame.K_r]:
            player.ammo = weapons[player.current_weapon]["ammo"]
        
        # Update bullets
        bullets = [bullet for bullet in bullets if not bullet.update()]
        
        # Update enemies
        for enemy in enemies:
            enemy.update(player.position)
            
            # Check enemy-player collision
            dist = ((enemy.position[0] - player.position[0])**2 + 
                    (enemy.position[1] - player.position[1])**2)**0.5
            if dist < 20 + enemy.size:
                player.take_damage(enemy.damage / 10)  # Continuous damage
        
        # Check bullet-enemy collisions
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                dist = ((bullet.x - enemy.position[0])**2 + 
                        (bullet.y - enemy.position[1])**2)**0.5
                if dist < enemy.size:
                    enemy.health -= bullet.damage
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        player.score += 100
                        player.ammo += 5  # Ammo pickup
                    break
        
        # Level progression
        if len(enemies) == 0:
            player.level += 1
            if player.level > len(levels):
                current_state = VICTORY
            else:
                init_level()
    
    # Drawing
    if current_state == MENU:
        show_menu()
    elif current_state == SHOP:
        show_shop(shop_type)
    elif current_state == SETTINGS:
        show_settings()
    elif current_state == PLAYING:
        draw_game()
    elif current_state == GAME_OVER:
        screen.fill(BLACK)
        draw_text("GAME OVER", font_large, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)
        draw_text(f"Score: {player.score}", font_medium, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)
        draw_text("Press R to return to menu", font_small, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70)
    elif current_state == VICTORY:
        screen.fill(BLACK)
        draw_text("MISSION COMPLETE!", font_large, GREEN, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)
        draw_text(f"Final Score: {player.score}", font_medium, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)
        draw_text("Press R to return to menu", font_small, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()