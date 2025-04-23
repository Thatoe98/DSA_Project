import pygame
import random
import time
import heapq
from collections import deque

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

def start_page():
    selected_timer = 60  # Default timer (1 minute)
    game_mode = None  # "PVP" or "PVE"
    running = True
    
    while running:
        screen.fill(BLACK)

        # Display welcome message with new game name
        display_message("Welcome to Python Chaser!!!", WHITE, WIDTH // 4, HEIGHT // 6)

        # Display RSU logo
        draw_logo()

        # Display mode selection
        display_message("Select Game Mode:", WHITE, WIDTH // 4, HEIGHT // 3)
        display_message("1. Player vs Bot", WHITE, WIDTH // 4, HEIGHT // 3 + 50)
        display_message("2. Player vs Player", WHITE, WIDTH // 4, HEIGHT // 3 + 100)
        
        # Display timer selection (only shown after game mode is selected)
        if game_mode:
            display_message("Select Timer:", WHITE, WIDTH // 4, HEIGHT // 2 + 50)
            display_message("A. 1 Minute", WHITE, WIDTH // 4, HEIGHT // 2 + 100)
            display_message("B. 2 Minutes", WHITE, WIDTH // 4, HEIGHT // 2 + 150)
            display_message("C. 3 Minutes", WHITE, WIDTH // 4, HEIGHT // 2 + 200)
        
        # Move quit option to bottom of page
        display_message("Press Q to Quit Game", RED, WIDTH // 4, HEIGHT - 60)

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN:
                # Add quit option with 'Q' key
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                
                # Add music toggle with 'M' key
                if event.key == pygame.K_m:
                    global music_playing
                    if music_playing:
                        pygame.mixer.music.pause()
                        music_playing = False
                    else:
                        pygame.mixer.music.unpause()
                        music_playing = True
                
                if not game_mode:
                    # Game mode selection
                    if event.key == pygame.K_1:
                        game_mode = "PVE"  # Player vs Bot
                    elif event.key == pygame.K_2:
                        game_mode = "PVP"  # Player vs Player
                else:
                    # Timer selection
                    if event.key == pygame.K_a:
                        selected_timer = 60  # 1 minute
                        running = False
                    elif event.key == pygame.K_b:
                        selected_timer = 120  # 2 minutes
                        running = False
                    elif event.key == pygame.K_c:
                        selected_timer = 180  # 3 minutes
                        running = False

    # Return timer and game mode
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
    """Display controls and game information for 10 seconds before game starts"""
    screen.fill(BLACK)
    
    # Display RSU logo
    draw_logo()
    
    # Title
    display_message("Get Ready!", WHITE, WIDTH // 3, 60)
    
    # Controls section
    display_message("Controls:", WHITE, 100, 120)
    display_message("Player 1 (Red):", RED, 100, 160)
    display_message("W - Up", WHITE, 120, 190)
    display_message("A - Left", WHITE, 120, 220)
    display_message("S - Down", WHITE, 120, 250)
    display_message("D - Right", WHITE, 120, 280)
    
    if not is_bot_game:
        display_message("Player 2 (Blue):", BLUE, 400, 160)
        display_message("↑ - Up", WHITE, 420, 190)
        display_message("← - Left", WHITE, 420, 220)
        display_message("↓ - Down", WHITE, 420, 250)
        display_message("→ - Right", WHITE, 420, 280)
    else:
        display_message("Bot (Yellow):", YELLOW, 400, 160)
        display_message("Automated AI using", WHITE, 420, 220)
        display_message("pathfinding algorithm", WHITE, 420, 250)
    
    # Power-ups section
    display_message("Power-ups:", WHITE, 100, 340)
    # Draw power-up examples
    screen.blit(pygame.transform.scale(flash_image, (30, 30)), (120, 380))
    display_message("Speed boost (30% faster for 5s)", WHITE, 170, 380)
    
    screen.blit(pygame.transform.scale(snow_image, (30, 30)), (120, 420))
    display_message("Freeze opponent (for 3s)", WHITE, 170, 420)
    
    # Add music control information
    display_message("Press M to toggle music on/off", WHITE, WIDTH // 4, HEIGHT - 120)
    
    # Countdown
    start_time = time.time()
    countdown_duration = 10  # 10 seconds preparation time
    
    while time.time() - start_time < countdown_duration:
        # Redraw the logo (it might be covered by countdown updates)
        draw_logo()
        
        # Calculate remaining time
        remaining = countdown_duration - int(time.time() - start_time)
        
        # Clear the previous countdown text area
        pygame.draw.rect(screen, BLACK, [WIDTH // 2 - 50, HEIGHT - 100, 100, 50])
        
        # Display countdown
        display_message(f"Starting in: {remaining}s", WHITE, WIDTH // 3, HEIGHT - 80)
        
        # Update display
        pygame.display.update()
        
        # Check if user wants to skip countdown
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return  # Skip countdown if space is pressed
        
        # Control frame rate
        clock.tick(30)

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
    
    while running:
        # Get game settings from start page
        game_duration, game_mode = start_page()
        
        # Run the game and get scores
        snake1_score, snake2_score, is_bot_game = game_loop(game_mode, game_duration)
        
        # Show end screen and check if we should return to menu
        continue_playing = display_end_screen(snake1_score, snake2_score, is_bot_game)
        
        if not continue_playing:
            running = False

    # Stop music when exiting
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
