# Bangkok Taxi Driver Game - DSA Project

import pygame
import random
import networkx as nx
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bangkok Taxi Driver Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Graph Setup
locations = {
    'Home': (100, 100),
    'Siam': (300, 120),
    'Asok': (500, 100),
    'Chatuchak': (150, 300),
    'Silom': (400, 300),
    'Bang Na': (650, 400),
    'Victory Monument': (250, 500)
}

edges = [
    ('Home', 'Siam', 5),
    ('Siam', 'Asok', 4),
    ('Siam', 'Silom', 6),
    ('Home', 'Chatuchak', 7),
    ('Chatuchak', 'Victory Monument', 3),
    ('Silom', 'Bang Na', 5),
    ('Asok', 'Bang Na', 6),
    ('Victory Monument', 'Silom', 4)
]

G = nx.Graph()
for node in locations:
    G.add_node(node, pos=locations[node])
for edge in edges:
    G.add_edge(edge[0], edge[1], weight=edge[2])

# Taxi Setup
taxi_node = 'Chatuchak'  # Start at Chatuchak
target_node = None  # Target node for movement
taxi_progress = 0  # Progress along the edge (0 to 1)
taxi_pos = list(locations[taxi_node])
taxi_speed = 3

# Passenger Setup
class Passenger:
    def __init__(self):
        self.pickup, self.dropoff = random.sample(list(locations.keys()), 2)
        self.active = True

passenger = Passenger()

# Utility Functions
def draw_graph():
    win.fill(WHITE)
    for u, v in G.edges():
        pygame.draw.line(win, BLACK, locations[u], locations[v], 2)
    for node, pos in locations.items():
        color = BLUE
        if node == 'Chatuchak':
            color = GREEN
        elif node == passenger.pickup and passenger.active:
            color = RED
        elif node == passenger.dropoff and not passenger.active:
            color = YELLOW
        pygame.draw.circle(win, color, pos, 10)
        label = font.render(node, True, BLACK)
        win.blit(label, (pos[0] + 10, pos[1] - 10))

def draw_taxi():
    pygame.draw.rect(win, RED, (*taxi_pos, 20, 20))

def move_taxi_along_edge():
    global taxi_node, target_node, taxi_progress, taxi_pos
    if target_node:
        start_pos = locations[taxi_node]
        end_pos = locations[target_node]
        taxi_progress += taxi_speed / math.dist(start_pos, end_pos)
        if taxi_progress >= 1:
            taxi_node = target_node
            target_node = None
            taxi_progress = 0
        else:
            taxi_pos[0] = int(start_pos[0] + (end_pos[0] - start_pos[0]) * taxi_progress)
            taxi_pos[1] = int(start_pos[1] + (end_pos[1] - start_pos[1]) * taxi_progress)

def handle_taxi_movement(keys):
    global target_node
    if not target_node:  # Only allow movement if not already moving
        neighbors = list(G.neighbors(taxi_node))
        if keys[pygame.K_LEFT] and 'Home' in neighbors:
            target_node = 'Home'
        elif keys[pygame.K_RIGHT] and 'Bang Na' in neighbors:
            target_node = 'Bang Na'
        elif keys[pygame.K_UP] and 'Siam' in neighbors:
            target_node = 'Siam'
        elif keys[pygame.K_DOWN] and 'Victory Monument' in neighbors:
            target_node = 'Victory Monument'

# Font
font = pygame.font.SysFont(None, 24)

# Start Page
def start_page():
    win.fill(WHITE)
    title = font.render("Bangkok Taxi Driver Game", True, BLACK)
    instruction = font.render("Press SPACE to Start", True, BLACK)
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))
    win.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Game Loop
start_page()
run = True
picked_up = False
while run:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    handle_taxi_movement(keys)
    move_taxi_along_edge()

    # Check for pickup or dropoff
    if passenger.active and taxi_node == passenger.pickup:
        picked_up = True
        passenger.active = False
    elif picked_up and taxi_node == passenger.dropoff:
        picked_up = False
        passenger = Passenger()

    # Draw
    draw_graph()
    draw_taxi()
    pygame.display.update()

pygame.quit()
