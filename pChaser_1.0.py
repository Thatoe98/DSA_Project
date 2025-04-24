
import pygame
import random
import time
import heapq
from collections import deque
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module for sound

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chaser")  # Updated game title in window caption

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)
small_font = pygame.font.SysFont(None, 25)

# Snake settings
SNAKE_SIZE = 20
FPS = 10  # Increased FPS to make the game faster

# Game duration (in seconds)
GAME_DURATION = 60

# Load and resize power-up images
flash_image = pygame.image.load("flash.png")
flash_image = pygame.transform.scale(flash_image, (SNAKE_SIZE * 3, SNAKE_SIZE * 3))
snow_image = pygame.image.load("snow.jpg")  # Add snow power-up image
snow_image = pygame.transform.scale(snow_image, (SNAKE_SIZE * 2, SNAKE_SIZE * 2))  # Smaller size (2x2 blocks)

# Load and set up background music
try:
    pygame.mixer.music.load("game_music.mp3")
    pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    music_playing = True
except:
    print("Warning: Could not load background music file 'game_music.mp3'")
    music_playing = False

# Load sound effects
try:
    food_sound = pygame.mixer.Sound("pop.mp3")
    food_sound.set_volume(0.7)  # Set food sound volume to 70%
    has_food_sound = True
except:
    print("Warning: Could not load sound effect file 'pop.mp3'")
    has_food_sound = False

# Load RSU logo
try:
    rsu_logo = pygame.image.load("rsu_logo.png")
    rsu_logo = pygame.transform.scale(rsu_logo, (SNAKE_SIZE * 7, SNAKE_SIZE * 10))  # Size: 10x5 blocks
    logo_position = (WIDTH - SNAKE_SIZE * 10 - 10, 10)  # Top right with 10px margin
    has_logo = True
except:
    print("Warning: Could not load logo file 'rsu_logo.png'")
    has_logo = False

def draw_logo():
    """Draw the RSU logo in the top right corner if available"""
    if has_logo:
        screen.blit(rsu_logo, logo_position)

def draw_snake(snake_list, color, direction=None):  # Remove head_image and direction parameters
    for i, block in enumerate(snake_list):
        if i == len(snake_list) - 1:  # Head of the snake
            pygame.draw.rect(screen, WHITE, [block[0], block[1], SNAKE_SIZE, SNAKE_SIZE])  # White head
        else:
            pygame.draw.rect(screen, color, [block[0], block[1], SNAKE_SIZE, SNAKE_SIZE])

def display_message(msg, color, x, y):
    text = font.render(msg, True, color)
    screen.blit(text, [x, y])

# Bot pathfinding using Dijkstra's algorithm
def find_path_to_food(snake_head, food_pos, obstacles, grid_width, grid_height):
    # Convert positions to grid coordinates
    start = (snake_head[0] // SNAKE_SIZE, snake_head[1] // SNAKE_SIZE)
    goal = (food_pos[0] // SNAKE_SIZE, food_pos[1] // SNAKE_SIZE)
    
    # Create set of obstacles (snake bodies)
    obstacle_set = set((pos[0] // SNAKE_SIZE, pos[1] // SNAKE_SIZE) for pos in obstacles)
    
    # Queue for Dijkstra's algorithm
    queue = [(0, start, [])]  # (cost, position, path)
    visited = set()
    
    # Possible moves: up, right, down, left
    directions = [
        (0, -1),  # up
        (1, 0),   # right
        (0, 1),   # down
        (-1, 0)   # left
    ]
    
    while queue:
        cost, current, path = heapq.heappop(queue)
        
        # Convert to grid coordinates
        current_x, current_y = current
        
        # If we've reached the goal
        if current == goal:
            if not path:  # If path is empty, move in any valid direction
                for dx, dy in directions:
                    nx, ny = current_x + dx, current_y + dy
                    if 0 <= nx < grid_width and 0 <= ny < grid_height and (nx, ny) not in obstacle_set:
                        return (dx * SNAKE_SIZE, dy * SNAKE_SIZE)
            else:
                # Return the first step in the path
                first_step = path[0]
                dx = first_step[0] - start[0]
                dy = first_step[1] - start[1]
                return (dx * SNAKE_SIZE, dy * SNAKE_SIZE)
        
        # Skip if we've already visited this cell
        if current in visited:
            continue
            
        visited.add(current)
        
        # Check all adjacent cells
        for dx, dy in directions:
            nx, ny = current_x + dx, current_y + dy
            
            # Check if the new position is valid
            if 0 <= nx < grid_width and 0 <= ny < grid_height and (nx, ny) not in obstacle_set and (nx, ny) not in visited:
                # Calculate Manhattan distance to the goal as a heuristic
                h = abs(nx - goal[0]) + abs(ny - goal[1])
                new_cost = cost + 1 + h  # Cost so far + 1 step + heuristic
                
                # Add new position to the queue
                new_path = path + [(nx, ny)]
                heapq.heappush(queue, (new_cost, (nx, ny), new_path))
    
    # If no path found, move in a random valid direction
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = start[0] + dx, start[1] + dy
        if 0 <= nx < grid_width and 0 <= ny < grid_height and (nx, ny) not in obstacle_set:
            return (dx * SNAKE_SIZE, dy * SNAKE_SIZE)
            
    # If completely stuck, just try to go up
    return (0, -SNAKE_SIZE)

def show_intro_screen():
    """Display attractive introduction screen"""
    screen.fill(BLACK)
    intro_running = True
    alpha = 0  # For fade in effect
    start_time = time.time()
    
    # Initialize animated snakes for intro
    intro_red_snake = {
        'body': [[100, 300], [80, 300], [60, 300], [40, 300], [20, 300]],
        'direction': [SNAKE_SIZE, 0],
        'pos': [100, 300]
    }
    
    intro_blue_snake = {
        'body': [[700, 300], [720, 300], [740, 300], [760, 300], [780, 300]],
        'direction': [-SNAKE_SIZE, 0],
        'pos': [700, 300]
    }
    
    animation_timer = 0
    animation_speed = 0.15
    last_update = time.time()

    # Load or create title font
    title_font = pygame.font.SysFont("arial", 100, bold=True)
    subtitle_font = pygame.font.SysFont("arial", 40)
    
    while intro_running:
        current_time = time.time()
        delta_time = current_time - last_update
        animation_timer += delta_time
        
        screen.fill(BLACK)
        
        # Animate snakes
        if animation_timer >= animation_speed:
            # Update red snake position
            intro_red_snake['pos'][0] = (intro_red_snake['pos'][0] + intro_red_snake['direction'][0]) % WIDTH
            intro_red_snake['body'].append(list(intro_red_snake['pos']))
            intro_red_snake['body'].pop(0)
            
            # Update blue snake position
            intro_blue_snake['pos'][0] = (intro_blue_snake['pos'][0] + intro_blue_snake['direction'][0]) % WIDTH
            intro_blue_snake['body'].append(list(intro_blue_snake['pos']))
            intro_blue_snake['body'].pop(0)
            
            animation_timer = 0
        
        # Draw animated snakes
        draw_snake(intro_red_snake['body'], RED)
        draw_snake(intro_blue_snake['body'], BLUE)
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Draw title with glow effect
        title = "PYTHON CHASER"
        for offset in range(3, 0, -1):
            glow_surface = title_font.render(title, True, (50, 50, 100))
            screen.blit(glow_surface, (WIDTH//2 - glow_surface.get_width()//2 + offset, 
                                     HEIGHT//3 - offset))
        
        title_surface = title_font.render(title, True, WHITE)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, HEIGHT//3))
        
        # Draw subtitle with fade in
        if alpha < 255:
            alpha += 2
        
        subtitle = "Press SPACE to Start"
        subtitle_surface = subtitle_font.render(subtitle, True, WHITE)
        subtitle_surface.set_alpha(int(abs(math.sin(current_time * 2)) * 255))  # Pulsing effect
        screen.blit(subtitle_surface, 
                   (WIDTH//2 - subtitle_surface.get_width()//2, HEIGHT * 2//3))
        
        # Draw logo if available
        draw_logo()
        
        # Display version and controls
        version_text = small_font.render("Version 1.0", True, GRAY)
        screen.blit(version_text, (10, HEIGHT - 30))
        
        controls_text = small_font.render("M - Toggle Music | Q - Quit", True, GRAY)
        screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 30))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    intro_running = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_m:
                    global music_playing
                    if music_playing:
                        pygame.mixer.music.pause()
                        music_playing = False
                    else:
                        pygame.mixer.music.unpause()
                        music_playing = True
        
        pygame.display.update()
        last_update = current_time
        clock.tick(60)

def start_page():
    """Enhanced start page with animated snakes"""
    selected_timer = 60
    game_mode = None
    running = True
    
    # Initialize animated menu snakes with more segments
    red_snake = {
        'body': [[100, 200], [80, 200], [60, 200], [40, 200], [20, 200]],
        'direction': [SNAKE_SIZE, 0],
        'pos': [100, 200]
    }
    
    blue_snake = {
        'body': [[700, 400], [720, 400], [740, 400], [760, 400], [780, 400]],
        'direction': [-SNAKE_SIZE, 0],
        'pos': [700, 400]
    }
    
    animation_timer = 0
    animation_speed = 0.15
    last_update = time.time()
    
    while running:
        current_update = time.time()
        delta_time = current_update - last_update
        animation_timer += delta_time
        
        # Create gradient background
        screen.fill(BLACK)
        
        # Animate snakes
        if animation_timer >= animation_speed:
            # Move and update snakes...
            red_snake['pos'][0] = (red_snake['pos'][0] + red_snake['direction'][0]) % WIDTH
            red_snake['pos'][1] = (red_snake['pos'][1] + red_snake['direction'][1]) % HEIGHT
            red_snake['body'].append(list(red_snake['pos']))
            red_snake['body'].pop(0)
            
            blue_snake['pos'][0] = (blue_snake['pos'][0] + blue_snake['direction'][0]) % WIDTH
            blue_snake['pos'][1] = (blue_snake['pos'][1] + blue_snake['direction'][1]) % HEIGHT
            blue_snake['body'].append(list(blue_snake['pos']))
            blue_snake['body'].pop(0)
            
            animation_timer = 0

        # Draw animated snakes
        draw_snake(red_snake['body'], RED)
        draw_snake(blue_snake['body'], BLUE)

        # Create stylish semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((20, 20, 30))  # Dark blue-ish background
        screen.blit(overlay, (0, 0))

        if not game_mode:
            # Draw title with shadow effect
            title = "Select Game Mode"
            title_font = pygame.font.SysFont(None, 60)
            shadow = title_font.render(title, True, (50, 50, 50))
            text = title_font.render(title, True, WHITE)
            screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 2, 80 + 2))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 80))

            # Create modern looking mode buttons
            mode_buttons = [
                ("1. PVE", "Player vs Bot"),
                ("2. PVP", "Player vs Player")
            ]

            for idx, (mode, desc) in enumerate(mode_buttons):
                y_pos = HEIGHT//2 - 100 + idx * 120
                button_rect = pygame.Rect(WIDTH//2 - 200, y_pos, 400, 80)
                
                # Button hover effect
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (60, 60, 70), button_rect, 0, border_radius=15)
                    pygame.draw.rect(screen, (100, 100, 255), button_rect, 3, border_radius=15)
                else:
                    pygame.draw.rect(screen, (40, 40, 50), button_rect, 0, border_radius=15)
                    pygame.draw.rect(screen, GRAY, button_rect, 2, border_radius=15)

                # Mode text
                mode_text = font.render(mode, True, WHITE)
                screen.blit(mode_text, (button_rect.centerx - mode_text.get_width()//2, 
                                      button_rect.y + 15))
                
                # Description text
                desc_text = small_font.render(desc, True, GRAY)
                screen.blit(desc_text, (button_rect.centerx - desc_text.get_width()//2, 
                                       button_rect.y + 45))
        else:
            # Draw title with glow effect
            title = "Select Game Duration"
            title_font = pygame.font.SysFont(None, 70)
            
            # Glow effect
            glow = title_font.render(title, True, (30, 30, 100))
            screen.blit(glow, (WIDTH//2 - glow.get_width()//2 + 2, 80 + 2))  # Moved up slightly
            
            # Main title
            text = title_font.render(title, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 80))  # Moved up slightly

            # Timer selection buttons with centered positioning
            timer_options = [
                ("A. 1 Minute", "Quick Match", 60),
                ("B. 2 Minutes", "Standard Match", 120),
                ("C. 3 Minutes", "Extended Match", 180)
            ]

            # Center the entire button group vertically
            total_height = len(timer_options) * 70 + (len(timer_options) - 1) * 30  # Button height + spacing
            start_y = (HEIGHT - total_height) // 2 + 30  # Added offset to account for title

            for i, (text, desc, duration) in enumerate(timer_options):
                y_pos = start_y + i * (70 + 30)  # Button height (70) + spacing (30)
                
                # Center buttons horizontally
                button_rect = pygame.Rect(WIDTH//2 - 150, y_pos, 300, 70)
                
                # Hover effect
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (40, 40, 80), button_rect)
                    pygame.draw.rect(screen, (100, 100, 255), button_rect, 3, border_radius=10)
                else:
                    pygame.draw.rect(screen, (30, 30, 60), button_rect)
                    pygame.draw.rect(screen, GRAY, button_rect, 2, border_radius=10)

                # Timer text
                timer_text = font.render(text, True, WHITE)
                screen.blit(timer_text, (button_rect.centerx - timer_text.get_width()//2, 
                                       button_rect.y + 10))
                
                # Description text
                desc_text = small_font.render(desc, True, GRAY)
                screen.blit(desc_text, (button_rect.centerx - desc_text.get_width()//2, 
                                      button_rect.y + 40))

            # Move controls text to very bottom of screen
            controls_text = "Press M to Toggle Music | Press Q to Quit"
            controls = small_font.render(controls_text, True, (150, 150, 150))
            screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - 30))

        # Event handling and key checks remain the same
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_m:
                    global music_playing
                    if music_playing:
                        pygame.mixer.music.pause()
                        music_playing = False
                    else:
                        pygame.mixer.music.unpause()
                        music_playing = True
                
                if game_mode:
                    if event.key in [pygame.K_a, pygame.K_1]:
                        selected_timer = 60
                        running = False
                    elif event.key in [pygame.K_b, pygame.K_2]:
                        selected_timer = 120
                        running = False
                    elif event.key in [pygame.K_c, pygame.K_3]:
                        selected_timer = 180
                        running = False
                else:
                    if event.key == pygame.K_1:
                        game_mode = "PVE"
                    elif event.key == pygame.K_2:
                        game_mode = "PVP"

        pygame.display.update()
        last_update = current_update
        clock.tick(60)

    return selected_timer, game_mode

def display_end_screen(snake1_score, snake2_score, is_bot_game):
    """Display the end game screen with scores and wait for space to return to menu"""
    screen.fill(BLACK)
    
    # Display RSU logo
    draw_logo()
    
    player1_name = "Player 1"
    player2_name = "Bot" if is_bot_game else "Player 2"
    
    # Determine winner
    if snake1_score > snake2_score:
        display_message(f"{player1_name} Wins!", RED, WIDTH // 3, HEIGHT // 3)
    elif snake2_score > snake1_score:
        display_message(f"{player2_name} Wins!", BLUE if not is_bot_game else YELLOW, WIDTH // 3, HEIGHT // 3)
    else:
        display_message("It's a Tie!", WHITE, WIDTH // 3, HEIGHT // 3)
    
    # Sort scores to display in order
    players = [(player1_name, snake1_score, RED), (player2_name, snake2_score, BLUE if not is_bot_game else YELLOW)]
    players.sort(key=lambda x: x[1], reverse=True)
    
    # Display scores in order
    y_pos = HEIGHT // 2
    for i, (name, score, color) in enumerate(players, 1):
        display_message(f"{i}. {name}: {score}", color, WIDTH // 3, y_pos)
        y_pos += 40
    
    # Prompt to return to menu
    display_message("Press SPACE to return to main menu", WHITE, WIDTH // 4, HEIGHT - 100)
    # Add note about music toggle
    display_message("Press M to toggle music", WHITE, WIDTH // 4, HEIGHT - 60)
    pygame.display.update()
    
    # Wait for space key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True  # Return to main menu
    
    return False  # Should not reach here

def show_preparation_screen(is_bot_game):
    waiting = True
    
    # Font settings with more balanced sizes
    title_font = pygame.font.SysFont("arial", 36, bold=True)
    header_font = pygame.font.SysFont("arial", 33, bold=True)
    game_font = pygame.font.SysFont("consolas", 28)
    
    while waiting:
        screen.fill((15, 15, 35))
        
        # Title Box - Centered at top
        title = "Get Ready!"
        title_surface = title_font.render(title, True, WHITE)
        title_box = pygame.Rect(WIDTH//2 - 90, 20, 180, 50)  # Moved up slightly
        pygame.draw.rect(screen, (30, 30, 60), title_box, 0, 10)
        pygame.draw.rect(screen, (100, 100, 255), title_box, 2, 10)
        
        # Center title text in box
        title_x = title_box.centerx - title_surface.get_width()//2
        title_y = title_box.centery - title_surface.get_height()//2
        screen.blit(title_surface, (title_x, title_y))

        # Controls Box - Adjusted height for better fit
        controls_box = pygame.Rect(WIDTH//2 - 350, 90, 700, 280)
        pygame.draw.rect(screen, (30, 30, 60), controls_box, 0, 15)
        pygame.draw.rect(screen, (100, 100, 255), controls_box, 2, 15)
        
        # Controls Header
        header_text = header_font.render("Game Controls", True, WHITE)
        header_x = controls_box.centerx - header_text.get_width()//2
        header_y = controls_box.y + 15
        screen.blit(header_text, (header_x, header_y))

        if is_bot_game:
            # Player Box - Made smaller to fit
            player_box = pygame.Rect(controls_box.x + 40, controls_box.y + 60, 260, 190)
            pygame.draw.rect(screen, (40, 40, 70), player_box, 0, 10)
            pygame.draw.rect(screen, RED, player_box, 2, 10)

            # Bot Box - Made smaller to fit
            bot_box = pygame.Rect(controls_box.right - 300, controls_box.y + 60, 260, 190)
            pygame.draw.rect(screen, (40, 40, 70), bot_box, 0, 10)
            pygame.draw.rect(screen, YELLOW, bot_box, 2, 10)

            # Player Controls
            title_text = game_font.render("Player (Red)", True, RED)
            title_x = player_box.centerx - title_text.get_width()//2
            title_y = player_box.y + 20
            screen.blit(title_text, (title_x, title_y))

            controls = [
                ("W", "(Up)"),
                ("A", "(Left)"),
                ("S", "(Down)"),
                ("D", "(Right)")
            ]

            start_y = player_box.y + 60
            spacing = 30
            for i, (key, direction) in enumerate(controls):
                key_surface = game_font.render(key, True, WHITE)
                key_x = player_box.centerx - 50
                key_y = start_y + (i * spacing)
                screen.blit(key_surface, (key_x, key_y))
                
                dash_surface = game_font.render("-", True, WHITE)
                dash_x = player_box.centerx - 20
                screen.blit(dash_surface, (dash_x, key_y))
                
                dir_surface = game_font.render(direction, True, GRAY)
                dir_x = player_box.centerx + 10
                screen.blit(dir_surface, (dir_x, key_y))

            # Bot Info with explanation
            bot_info = [
                ("Bot (Yellow)", YELLOW),
                ("AI Controlled", WHITE),
                ("Finds Food", WHITE),
                ("Avoids Walls", WHITE),
                ("Auto Navigate", WHITE)
            ]

            # Display bot info with same spacing
            start_y = bot_box.y + 20
            for i, (text, color) in enumerate(bot_info):
                text_surface = game_font.render(text, True, color)
                text_x = bot_box.centerx - text_surface.get_width()//2
                text_y = start_y + (i * spacing)
                screen.blit(text_surface, (text_x, text_y))

        else:
            # PVP Mode - Similar adjustments for player boxes
            player1_box = pygame.Rect(controls_box.x + 40, controls_box.y + 60, 260, 190)
            pygame.draw.rect(screen, (40, 40, 70), player1_box, 0, 10)
            pygame.draw.rect(screen, RED, player1_box, 2, 10)

            player2_box = pygame.Rect(controls_box.right - 300, controls_box.y + 60, 260, 190)
            pygame.draw.rect(screen, (40, 40, 70), player2_box, 0, 10)
            pygame.draw.rect(screen, BLUE, player2_box, 2, 10)

            # Player 1 Controls
            title_text = game_font.render("Player 1 (Red)", True, RED)
            title_x = player1_box.centerx - title_text.get_width()//2
            title_y = player1_box.y + 20
            screen.blit(title_text, (title_x, title_y))

            p1_controls = [
                ("W", "(Up)"),
                ("A", "(Left)"),
                ("S", "(Down)"),
                ("D", "(Right)")
            ]

            start_y = player1_box.y + 60
            spacing = 30
            for i, (key, direction) in enumerate(p1_controls):
                key_surface = game_font.render(key, True, WHITE)
                key_x = player1_box.centerx - 50
                key_y = start_y + (i * spacing)
                screen.blit(key_surface, (key_x, key_y))
                
                dash_surface = game_font.render("-", True, WHITE)
                dash_x = player1_box.centerx - 20
                screen.blit(dash_surface, (dash_x, key_y))
                
                dir_surface = game_font.render(direction, True, GRAY)
                dir_x = player1_box.centerx + 10
                screen.blit(dir_surface, (dir_x, key_y))

            # Player 2 Controls
            title_text = game_font.render("Player 2 (Blue)", True, BLUE)
            title_x = player2_box.centerx - title_text.get_width()//2
            title_y = player2_box.y + 20
            screen.blit(title_text, (title_x, title_y))

            p2_controls = [
                ("↑", "(Up)"),
                ("←", "(Left)"),
                ("↓", "(Down)"),
                ("→", "(Right)")
            ]

            start_y = player2_box.y + 60
            for i, (key, direction) in enumerate(p2_controls):
                key_surface = game_font.render(key, True, WHITE)
                key_x = player2_box.centerx - 50
                key_y = start_y + (i * spacing)
                screen.blit(key_surface, (key_x, key_y))
                
                dash_surface = game_font.render("-", True, WHITE)
                dash_x = player2_box.centerx - 20
                screen.blit(dash_surface, (dash_x, key_y))
                
                dir_surface = game_font.render(direction, True, GRAY)
                dir_x = player2_box.centerx + 10
                screen.blit(dir_surface, (dir_x, key_y))

        # Power-ups Box with header
        powerup_box = pygame.Rect(WIDTH//2 - 300, controls_box.bottom + 20, 600, 100)
        pygame.draw.rect(screen, (30, 30, 60), powerup_box, 0, 10)
        pygame.draw.rect(screen, (100, 100, 255), powerup_box, 2, 10)

        # Power-ups Header
        powerup_header = header_font.render("Power-ups", True, WHITE)
        powerup_x = powerup_box.centerx - powerup_header.get_width()//2
        screen.blit(powerup_header, (powerup_x, powerup_box.y + 10))

        # Display power-ups with icons
        icon_size = 32
        padding = 20

        # Speed boost power-up
        speed_x = powerup_box.x + 50
        speed_y = powerup_box.centery + 5
        screen.blit(pygame.transform.scale(flash_image, (icon_size, icon_size)), (speed_x, speed_y))
        speed_text = game_font.render("Speed Boost (5s)", True, WHITE)
        screen.blit(speed_text, (speed_x + icon_size + 10, speed_y))

        # Freeze power-up
        freeze_x = powerup_box.centerx + 50
        freeze_y = powerup_box.centery + 5
        screen.blit(pygame.transform.scale(snow_image, (icon_size, icon_size)), (freeze_x, freeze_y))
        freeze_text = game_font.render("Freeze (3s)", True, WHITE)
        screen.blit(freeze_text, (freeze_x + icon_size + 10, freeze_y))

        # Press Space Box at bottom
        space_box = pygame.Rect(WIDTH//2 - 200, HEIGHT - 60, 400, 40)
        pygame.draw.rect(screen, (30, 30, 60), space_box, 0, 10)
        pygame.draw.rect(screen, (100, 100, 255), space_box, 2, 10)

        # Press Space Text with pulsing effect
        space_text = game_font.render("Press SPACE to Start", True, WHITE)
        space_alpha = abs(math.sin(time.time() * 2)) * 255
        space_text.set_alpha(int(space_alpha))
        screen.blit(space_text, (WIDTH//2 - space_text.get_width()//2, HEIGHT - 55))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_m:
                    global music_playing
                    if music_playing:
                        pygame.mixer.music.pause()
                        music_playing = False
                    else:
                        pygame.mixer.music.unpause()
                        music_playing = True

        pygame.display.update()
        clock.tick(60)

def game_loop(game_mode, game_duration):
    """Main game loop separated as a function to allow restarting"""
    is_bot_game = (game_mode == "PVE")

    # Show preparation screen
    show_preparation_screen(is_bot_game)

    # Player 1 (Red Snake)
    snake1_pos = [100, 50]
    snake1_body = [[100, 50], [80, 50]]  # Start with 2 blocks
    snake1_direction = 'RIGHT'
    snake1_change = [SNAKE_SIZE, 0]
    snake1_score = 0
    snake1_fps = FPS  # Individual FPS for Player 1
    snake1_speed_boost = 1.0  # Speed multiplier for snake 1
    snake1_last_move_time = 0  # Last time snake 1 moved
    snake1_frozen = False
    snake1_frozen_start_time = None

    # Player 2 (Blue Snake) / Bot
    snake2_pos = [700, 550]
    snake2_body = [[700, 550], [720, 550]]  # Start with 2 blocks
    snake2_direction = 'LEFT'
    snake2_change = [-SNAKE_SIZE, 0]
    snake2_score = 0
    snake2_fps = FPS  # Individual FPS for Player 2
    snake2_speed_boost = 1.0  # Speed multiplier for snake 2
    snake2_last_move_time = 0  # Last time snake 2 moved
    snake2_frozen = False
    snake2_frozen_start_time = None
    bot_decision_time = 0  # Time tracker for bot decisions
    bot_decision_interval = 0.1  # How often the bot makes decisions (in seconds)

    # Food
    food_pos = [random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE]
    food_spawn = True

    # Power-up variables
    flash_powerup_pos = None
    flash_powerup_active = False
    powerup_effect_start_time_1 = None
    powerup_effect_start_time_2 = None
    powerup_effect_active_1 = False
    powerup_effect_active_2 = False

    # Freeze power-up variables
    snow_powerup_pos = None
    snow_powerup_active = False
    snow_last_spawn_time = None

    # Game variables
    start_time = time.time()
    running = True

    while running:
        current_time = time.time()
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # Music toggle
                if event.key == pygame.K_m:
                    global music_playing
                    if music_playing:
                        pygame.mixer.music.pause()
                        music_playing = False
                    else:
                        pygame.mixer.music.unpause()
                        music_playing = True
                
                # Player 1 controls (WASD)
                if event.key == pygame.K_w and snake1_direction != 'DOWN':
                    snake1_direction = 'UP'
                    snake1_change = [0, -SNAKE_SIZE]
                elif event.key == pygame.K_s and snake1_direction != 'UP':
                    snake1_direction = 'DOWN'
                    snake1_change = [0, SNAKE_SIZE]
                elif event.key == pygame.K_a and snake1_direction != 'RIGHT':
                    snake1_direction = 'LEFT'
                    snake1_change = [-SNAKE_SIZE, 0]
                elif event.key == pygame.K_d and snake1_direction != 'LEFT':
                    snake1_direction = 'RIGHT'
                    snake1_change = [SNAKE_SIZE, 0]

                # Player 2 controls (Arrow keys) - Only if not a bot game
                if not is_bot_game:
                    if event.key == pygame.K_UP and snake2_direction != 'DOWN':
                        snake2_direction = 'UP'
                        snake2_change = [0, -SNAKE_SIZE]
                    elif event.key == pygame.K_DOWN and snake2_direction != 'UP':
                        snake2_direction = 'DOWN'
                        snake2_change = [0, SNAKE_SIZE]
                    elif event.key == pygame.K_LEFT and snake2_direction != 'RIGHT':
                        snake2_direction = 'LEFT'
                        snake2_change = [-SNAKE_SIZE, 0]
                    elif event.key == pygame.K_RIGHT and snake2_direction != 'LEFT':
                        snake2_direction = 'RIGHT'
                        snake2_change = [SNAKE_SIZE, 0]

        # Bot decision making (if in PVE mode)
        if is_bot_game and not snake2_frozen and current_time - bot_decision_time > bot_decision_interval:
            # Collect obstacles (both snake bodies minus the tail that will move)
            obstacles = snake1_body[:-1] + snake2_body[:-1]
            
            # Find path to food
            bot_change = find_path_to_food(snake2_pos, food_pos, obstacles, WIDTH // SNAKE_SIZE, HEIGHT // SNAKE_SIZE)
            
            # Update direction based on the next move
            if bot_change == (0, -SNAKE_SIZE) and snake2_direction != 'DOWN':
                snake2_direction = 'UP'
                snake2_change = [0, -SNAKE_SIZE]
            elif bot_change == (0, SNAKE_SIZE) and snake2_direction != 'UP':
                snake2_direction = 'DOWN'
                snake2_change = [0, SNAKE_SIZE]
            elif bot_change == (-SNAKE_SIZE, 0) and snake2_direction != 'RIGHT':
                snake2_direction = 'LEFT'
                snake2_change = [-SNAKE_SIZE, 0]
            elif bot_change == (SNAKE_SIZE, 0) and snake2_direction != 'LEFT':
                snake2_direction = 'RIGHT'
                snake2_change = [SNAKE_SIZE, 0]
                
            bot_decision_time = current_time

        # Check if either snake is frozen and update frozen status
        if snake1_frozen and current_time - snake1_frozen_start_time > 3:
            snake1_frozen = False
            
        if snake2_frozen and current_time - snake2_frozen_start_time > 3:
            snake2_frozen = False

        # Move snakes based on their individual timing, if not frozen
        if not snake1_frozen and current_time - snake1_last_move_time > (1.0 / (FPS * snake1_speed_boost)):
            # Update snake 1 position
            snake1_pos[0] += snake1_change[0]
            snake1_pos[1] += snake1_change[1]
            
            # Wrap around screen edges
            snake1_pos[0] %= WIDTH
            snake1_pos[1] %= HEIGHT
            
            # Update snake1 body
            snake1_body.append(list(snake1_pos))
            
            # Check if Player 1 eats the food
            if abs(snake1_pos[0] - food_pos[0]) < SNAKE_SIZE and abs(snake1_pos[1] - food_pos[1]) < SNAKE_SIZE:
                snake1_score += 1
                food_spawn = False
                # Play sound effect when food is eaten
                if has_food_sound:
                    food_sound.play()
            else:
                snake1_body.pop(0)
                
            snake1_last_move_time = current_time
        
        if not snake2_frozen and current_time - snake2_last_move_time > (1.0 / (FPS * snake2_speed_boost)):
            # Update snake 2 position
            snake2_pos[0] += snake2_change[0]
            snake2_pos[1] += snake2_change[1]
            
            # Wrap around screen edges
            snake2_pos[0] %= WIDTH
            snake2_pos[1] %= HEIGHT
            
            # Update snake2 body
            snake2_body.append(list(snake2_pos))
            
            # Check if Player 2 eats the food
            if abs(snake2_pos[0] - food_pos[0]) < SNAKE_SIZE and abs(snake2_pos[1] - food_pos[1]) < SNAKE_SIZE:
                snake2_score += 1
                food_spawn = False
                # Play sound effect when food is eaten
                if has_food_sound:
                    food_sound.play()
            else:
                snake2_body.pop(0)
                
            snake2_last_move_time = current_time

        # Respawn food
        if not food_spawn:
            food_pos = [random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                        random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE]
            food_spawn = True

        # Power-up logic
        elapsed_time = current_time - start_time

        # Spawn speed power-up after 10 seconds and every 5 seconds after it disappears
        if elapsed_time > 10 and not flash_powerup_active and not (powerup_effect_active_1 or powerup_effect_active_2):
            flash_powerup_pos = [random.randrange(1, (WIDTH // (SNAKE_SIZE * 3))) * SNAKE_SIZE * 3,
                           random.randrange(1, (HEIGHT // (SNAKE_SIZE * 3))) * SNAKE_SIZE * 3]
            flash_powerup_active = True

        # Spawn freeze power-up after 15 seconds and every 10 seconds after it disappears
        if elapsed_time > 15 and not snow_powerup_active and (snow_last_spawn_time is None or current_time - snow_last_spawn_time > 10):
            snow_powerup_pos = [random.randrange(1, (WIDTH // (SNAKE_SIZE * 3))) * SNAKE_SIZE * 3,
                         random.randrange(1, (HEIGHT // (SNAKE_SIZE * 3))) * SNAKE_SIZE * 3]
            snow_powerup_active = True
            
        # Check if a snake touches the speed power-up
        if flash_powerup_active:
            if (flash_powerup_pos[0] <= snake1_pos[0] < flash_powerup_pos[0] + SNAKE_SIZE * 3 and
                flash_powerup_pos[1] <= snake1_pos[1] < flash_powerup_pos[1] + SNAKE_SIZE * 3):
                flash_powerup_active = False
                powerup_effect_active_1 = True
                powerup_effect_start_time_1 = current_time
                snake1_speed_boost = 1.3  # Increase Player 1's speed by 30%
            elif (flash_powerup_pos[0] <= snake2_pos[0] < flash_powerup_pos[0] + SNAKE_SIZE * 3 and
                  flash_powerup_pos[1] <= snake2_pos[1] < flash_powerup_pos[1] + SNAKE_SIZE * 3):
                flash_powerup_active = False
                powerup_effect_active_2 = True
                powerup_effect_start_time_2 = current_time
                snake2_speed_boost = 1.3  # Increase Player 2's speed by 30%

        # Check if a snake touches the freeze power-up
        if snow_powerup_active:
            if (snow_powerup_pos[0] <= snake1_pos[0] < snow_powerup_pos[0] + SNAKE_SIZE * 3 and
                snow_powerup_pos[1] <= snake1_pos[1] < snow_powerup_pos[1] + SNAKE_SIZE * 3):
                snow_powerup_active = False
                snow_last_spawn_time = current_time
                snake2_frozen = True  # Freeze opponent (Player 2)
                snake2_frozen_start_time = current_time
            elif (snow_powerup_pos[0] <= snake2_pos[0] < snow_powerup_pos[0] + SNAKE_SIZE * 3 and
                  snow_powerup_pos[1] <= snake2_pos[1] < snow_powerup_pos[1] + SNAKE_SIZE * 3):
                snow_powerup_active = False
                snow_last_spawn_time = current_time
                snake1_frozen = True  # Freeze opponent (Player 1)
                snake1_frozen_start_time = current_time

        # End power-up effects
        # End power-up effect after 5 seconds for Player 1
        if powerup_effect_active_1 and current_time - powerup_effect_start_time_1 > 5:
            powerup_effect_active_1 = False
            snake1_speed_boost = 1.0  # Reset Player 1's speed to normal

        # End power-up effect after 5 seconds for Player 2
        if powerup_effect_active_2 and current_time - powerup_effect_start_time_2 > 5:
            powerup_effect_active_2 = False
            snake2_speed_boost = 1.0  # Reset Player 2's speed to normal

        # Draw power-ups
        if flash_powerup_active:
            screen.blit(flash_image, (flash_powerup_pos[0], flash_powerup_pos[1]))
            
        if snow_powerup_active:
            screen.blit(snow_image, (snow_powerup_pos[0], snow_powerup_pos[1]))

        # Draw food
        pygame.draw.rect(screen, GREEN, [food_pos[0], food_pos[1], SNAKE_SIZE, SNAKE_SIZE])

        # Draw snakes with original rectangle-based heads
        draw_snake(snake1_body, RED)
        draw_snake(snake2_body, BLUE if not is_bot_game else YELLOW)  # Make bot yellow to distinguish

        # Display scores and status effects
        player1_name = "Player 1"
        player2_name = "Player 2" if not is_bot_game else "Bot"
        
        display_message(f"{player1_name}: {snake1_score}", WHITE, 10, 10)
        if snake1_frozen:
            display_message("FROZEN!", WHITE, 10, 70)
        display_message(f"{player2_name}: {snake2_score}", WHITE, 10, 40)
        if snake2_frozen:
            display_message("FROZEN!", WHITE, 10, 100)

        # Display timer
        remaining_time = max(0, GAME_DURATION - int(elapsed_time))
        display_message(f"Time Left: {remaining_time}s", WHITE, WIDTH - 200, 10)

        # Check game duration
        if current_time - start_time >= game_duration:
            running = False

        pygame.display.update()
        
        # Fixed frame rate for rendering only
        clock.tick(60)

    # Return final scores
    return snake1_score, snake2_score, is_bot_game

def main():
    """Main function with game loop that can restart"""
    running = True
    
    # Show intro screen first
    show_intro_screen()
    
    while running:
        # Get game settings from start page
        game_duration, game_mode = start_page()
        
        # Run the game and get scores
        snake1_score, snake2_score, is_bot_game = game_loop(game_mode, game_duration)
        
        # Show end screen and check if we should return to menu
        continue_playing = display_end_screen(snake1_score, snake2_score, is_bot_game)
        
        if not continue_playing:
            running = False

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
