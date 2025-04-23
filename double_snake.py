import pygame
import random
import time
import os
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Double Snake Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)
small_font = pygame.font.SysFont(None, 25)

# Snake settings
SNAKE_SIZE = 20
FPS = 10  # Increased FPS to make the game faster

# Game duration (in seconds)
GAME_DURATION = 60

# High scores file path
HIGH_SCORES_FILE = os.path.join(os.path.dirname(__file__), "high_scores.json")

# Remove image loading and resizing
# red_snake_head = pygame.image.load("red_snake.png")
# red_snake_head = pygame.transform.scale(red_snake_head, (SNAKE_SIZE, SNAKE_SIZE))
# yellow_snake_head = pygame.image.load("yellow_snake.png")
# yellow_snake_head = pygame.transform.scale(yellow_snake_head, (SNAKE_SIZE, SNAKE_SIZE))

# Load and resize power-up images
flash_image = pygame.image.load("flash.png")
flash_image = pygame.transform.scale(flash_image, (SNAKE_SIZE * 3, SNAKE_SIZE * 3))
snow_image = pygame.image.load("snow.jpg")  # Add snow power-up image
snow_image = pygame.transform.scale(snow_image, (SNAKE_SIZE * 2, SNAKE_SIZE * 2))  # Smaller size (2x2 blocks)

def draw_snake(snake_list, color, direction=None):  # Remove head_image and direction parameters
    for i, block in enumerate(snake_list):
        if i == len(snake_list) - 1:  # Head of the snake
            pygame.draw.rect(screen, WHITE, [block[0], block[1], SNAKE_SIZE, SNAKE_SIZE])  # White head
        else:
            pygame.draw.rect(screen, color, [block[0], block[1], SNAKE_SIZE, SNAKE_SIZE])

def display_message(msg, color, x, y):
    text = font.render(msg, True, color)
    screen.blit(text, [x, y])

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.active = False
        self.txt_surface = font.render(text, True, WHITE)
        self.max_length = 12  # Max name length

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable
                self.active = True
            else:
                self.active = False
            # Change the current color
            self.color = RED if self.active else WHITE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True  # Signal that Enter was pressed
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Only add character if below max length
                    if len(self.text) < self.max_length and event.unicode.isprintable():
                        self.text += event.unicode
                # Re-render the text
                self.txt_surface = font.render(self.text, True, WHITE)
        return False

    def draw(self, screen):
        # Draw the text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Draw the rect
        pygame.draw.rect(screen, self.color, self.rect, 2)

def save_high_score(player1_name, player2_name, player1_score, player2_score):
    # Load existing high scores
    high_scores = []
    if os.path.exists(HIGH_SCORES_FILE):
        try:
            with open(HIGH_SCORES_FILE, 'r') as file:
                high_scores = json.load(file)
        except:
            high_scores = []
    
    # Add new scores
    high_scores.append({"name": player1_name, "score": player1_score})
    high_scores.append({"name": player2_name, "score": player2_score})
    
    # Sort by score (highest first)
    high_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Keep only top 10 scores
    high_scores = high_scores[:10]
    
    # Save to file
    with open(HIGH_SCORES_FILE, 'w') as file:
        json.dump(high_scores, file)
    
    return high_scores

def display_high_scores(screen):
    high_scores = []
    if os.path.exists(HIGH_SCORES_FILE):
        try:
            with open(HIGH_SCORES_FILE, 'r') as file:
                high_scores = json.load(file)
        except:
            high_scores = []
    
    screen.fill(BLACK)
    display_message("HIGH SCORES", WHITE, WIDTH // 3, 50)
    
    y_pos = 120
    for i, score in enumerate(high_scores[:10], 1):
        player_name = score["name"] if "name" in score else "Unknown"
        player_score = score["score"]
        display_message(f"{i}. {player_name}: {player_score}", WHITE, WIDTH // 3, y_pos)
        y_pos += 40
    
    display_message("Press any key to quit", WHITE, WIDTH // 3, HEIGHT - 50)
    pygame.display.update()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                waiting = False

def start_page():
    selected_timer = 60  # Default timer (1 minute)
    running = True
    
    # Create input boxes for player names
    player1_input = InputBox(WIDTH // 4 + 200, HEIGHT // 4 + 40, 200, 32, "Player 1")
    player2_input = InputBox(WIDTH // 4 + 200, HEIGHT // 4 + 80, 200, 32, "Player 2")
    player1_name = "Player 1"
    player2_name = "Player 2"
    
    # Input box state
    current_step = "names"  # "names" or "timer"
    player1_confirmed = False
    player2_confirmed = False
    
    # Make player1 input active by default
    player1_input.active = True
    player1_input.color = RED

    while running:
        screen.fill(BLACK)

        # Display welcome message
        display_message("Welcome to Snake Race!!!", WHITE, WIDTH // 4, HEIGHT // 6)

        if current_step == "names":
            # Display name input fields
            display_message("Enter Player Names:", WHITE, WIDTH // 4, HEIGHT // 4)
            display_message("Player 1 (Red):", RED, WIDTH // 4, HEIGHT // 4 + 40)
            display_message("Player 2 (Blue):", BLUE, WIDTH // 4, HEIGHT // 4 + 80)
            
            # Draw input boxes
            player1_input.draw(screen)
            player2_input.draw(screen)
            
            # Display continue instruction and status
            display_message("Click on name box to edit, press Tab to switch", WHITE, WIDTH // 4, HEIGHT // 2)
            display_message("Press Enter when done with both names", WHITE, WIDTH // 4, HEIGHT // 2 + 40)
            
            # Show which names are confirmed
            if player1_confirmed:
                display_message("✓", GREEN, WIDTH // 4 + 180, HEIGHT // 4 + 40)
            if player2_confirmed:
                display_message("✓", GREEN, WIDTH // 4 + 180, HEIGHT // 4 + 80)
        else:
            # Display rules
            display_message("Rules:", WHITE, WIDTH // 4, HEIGHT // 4)
            display_message(f"{player1_name} (Red): Use W/A/S/D to move", RED, WIDTH // 4, HEIGHT // 4 + 40)
            display_message(f"{player2_name} (Blue): Use Arrow Keys to move", BLUE, WIDTH // 4, HEIGHT // 4 + 80)
            display_message("Eat the green food to score points!", GREEN, WIDTH // 4, HEIGHT // 4 + 120)

            # Display timer selection
            display_message("Select Timer:", WHITE, WIDTH // 4, HEIGHT // 2)
            display_message("1. 1 Minute", WHITE, WIDTH // 4, HEIGHT // 2 + 40)
            display_message("2. 2 Minutes", WHITE, WIDTH // 4, HEIGHT // 2 + 80)
            display_message("3. 3 Minutes", WHITE, WIDTH // 4, HEIGHT // 2 + 120)

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if current_step == "names":
                # Handle Tab key to switch between input boxes
                if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    if player1_input.active:
                        player1_input.active = False
                        player2_input.active = True
                        player1_input.color = WHITE
                        player2_input.color = RED
                    else:
                        player1_input.active = True
                        player2_input.active = False
                        player1_input.color = RED
                        player2_input.color = WHITE
                
                # Handle Enter key to confirm names and move to next screen
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if player1_input.active:
                        player1_name = player1_input.text if player1_input.text else "Player 1"
                        player1_confirmed = True
                        # Switch to player 2 input if not confirmed yet
                        if not player2_confirmed:
                            player1_input.active = False
                            player2_input.active = True
                            player1_input.color = WHITE
                            player2_input.color = RED
                    elif player2_input.active:
                        player2_name = player2_input.text if player2_input.text else "Player 2"
                        player2_confirmed = True
                        # Switch to player 1 input if not confirmed yet
                        if not player1_confirmed:
                            player1_input.active = True
                            player2_input.active = False
                            player1_input.color = RED
                            player2_input.color = WHITE
                    
                    # If both names are confirmed, move to timer selection
                    if player1_confirmed and player2_confirmed:
                        current_step = "timer"
                
                # Handle input box events (clicks, typing)
                player1_clicked = player1_input.handle_event(event)
                player2_clicked = player2_input.handle_event(event)
                
                # If Space key pressed, use default names and move to timer
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    current_step = "timer"
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_timer = 60  # 1 minute
                        running = False
                    elif event.key == pygame.K_2:
                        selected_timer = 120  # 2 minutes
                        running = False
                    elif event.key == pygame.K_3:
                        selected_timer = 180  # 3 minutes
                        running = False

    # Return both timer and player names
    return selected_timer, player1_name, player2_name

def main():
    global GAME_DURATION  # Declare GAME_DURATION as global
    GAME_DURATION, player1_name, player2_name = start_page()  # Get selected timer and player names

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

    # Player 2 (Blue Snake)
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
                running = False
            if event.type == pygame.KEYDOWN:
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

                # Player 2 controls (Arrow keys)
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
        draw_snake(snake2_body, BLUE)

        # Display scores and status effects
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
        if elapsed_time >= GAME_DURATION:
            running = False

        pygame.display.update()
        
        # Fixed frame rate for rendering only
        clock.tick(60)

    # Game over screen
    screen.fill(BLACK)
    if snake1_score > snake2_score:
        display_message(f"{player1_name} Wins!", RED, WIDTH // 3, HEIGHT // 3)
    elif snake2_score > snake1_score:
        display_message(f"{player2_name} Wins!", BLUE, WIDTH // 3, HEIGHT // 3)
    else:
        display_message("It's a Tie!", WHITE, WIDTH // 3, HEIGHT // 3)
    display_message(f"Final Scores - {player1_name}: {snake1_score}, {player2_name}: {snake2_score}", WHITE, WIDTH // 6, HEIGHT // 2)
    pygame.display.update()
    time.sleep(5)
    
    # Save high scores and display them
    high_scores = save_high_score(player1_name, player2_name, snake1_score, snake2_score)
    display_high_scores(screen)

    pygame.quit()

if __name__ == "__main__":
    main()
