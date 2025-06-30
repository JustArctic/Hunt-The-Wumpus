# Import necessary libraries
import pygame       # Main game library for graphics and input
import random      # For random number generation (hazard placement, etc.)
import time        # For timing delays (message displays, etc.)
import sys         # For system functions like exit

# --- Constants ---
# Game window dimensions (square)
SCREEN_WIDTH = SCREEN_HEIGHT = 1000  

# Game configuration - number of hazards/items
NUM_BATS = 2       # Number of rooms with bats (teleport player)
NUM_PITS = 1       # Number of rooms with bottomless pits (instant death)
NUM_ARROWS = 3     # Number of extra arrows available in cave
NUM_ROCKS = 3      # Number of extra rocks available in cave

# Direction constants (matches indices in cave layout)
UP = 0    # Index for upward exit
DOWN = 1  # Index for downward exit  
LEFT = 2  # Index for left exit
RIGHT = 3 # Index for right exit

# Color definitions (RGB tuples)
BROWN = (193, 154, 107)  # Color for cave walls/paths
BLACK = (0, 0, 0)         # Background color
RED = (138, 7, 7)         # Warning color (Wumpus proximity)

# --- Cave Layout ---
# Dictionary representing the 20-room cave as a dodecahedron
# Format: {room_number: [up_exit, down_exit, left_exit, right_exit]}
# 0 indicates no exit in that direction
# Rooms are interconnected to form the cave structure
cave = {
    1: [0, 8, 2, 5], 2: [0, 10, 3, 1], 3: [0, 12, 4, 2], 4: [0, 14, 5, 3],
    5: [0, 6, 1, 4], 6: [5, 0, 7, 15], 7: [0, 17, 8, 6], 8: [1, 0, 9, 7],
    9: [0, 18, 10, 8], 10: [2, 0, 11, 9], 11: [0, 19, 12, 10], 12: [3, 0, 13, 11],
    13: [0, 20, 14, 12], 14: [4, 0, 15, 13], 15: [0, 16, 6, 14], 16: [15, 0, 17, 20],
    17: [7, 0, 18, 16], 18: [9, 0, 19, 17], 19: [11, 0, 20, 18], 20: [13, 0, 16, 19]
}

# --- Game State Variables ---
player_pos = 0          # Current room number (1-20) where player is located
wumpus_pos = 0          # Current room number where Wumpus is located
num_arrows = 1          # Player's current arrow count (starts with 1)
num_rocks = 1           # Player's current rock count (starts with 1)
mobile_wumpus = True    # Flag whether Wumpus can move between rooms
wumpus_move_chance = 70 # Percentage chance Wumpus moves each turn (when mobile)
last_direction = UP     # Tracks player's last facing direction (default up)

# Lists tracking rooms containing each type of hazard/item
bats_list = []    # Rooms containing bats
pits_list = []    # Rooms containing bottomless pits 
arrows_list = []  # Rooms containing arrow pickups
rocks_list = []   # Rooms containing rock pickups

def print_instructoions():
    print(
    '''
                             Hunt The Wumpus!
This is the game of "Hunt the Wumpus".  You have been cast into a
dark 20 room cave with a fearsome Wumpus. The cave is shaped like a 
dodachedron and the only way out is to kill the Wumpus.  To that end
you have a bow with one arrow. You might find more arrows from unlucky 
past Wumpus victims in the cave.  There are other dangers in the cave, 
specifcally bats and bottomless pits.

    * If you run out of arrows you die.
    * If you end up in the same room with the Wumpus you die.
    * If you fall into a bottomless pit you die.
    * If you end up in a room with bats they will pick you up
      and deposit you in a random location.

If you are near the Wumpus you will see the bloodstains on the walls.
If you are near bats you will hear them and if you are near a bottomless
pit you will feel the air flowing down it.

If you end up on a red spot the Wumpus will be in one of the following directions
around you <a> key and an selection screen to fire your arrow, if you hit the Wumpus
you win.

If you are unsure where to move you can toss a rock to check if they are Bats, bottomless pits
or the Wumpus by using the <r> key. 

    '''
    )

# --- Initialize Pygame ---
# Display game instructions and wait for player to start
print_instructoions()
input("Press <ENTER> to begin.")

# Initialize all pygame modules
pygame.init()

# Create game window with double buffering and hardware acceleration
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 
    pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("Hunt the Wumpus")  # Window title

# Create default font for text rendering (size 36)
font = pygame.font.Font(None, 36)

# --- Load Game Assets ---
# Load all image assets used in the game
bat_img = pygame.image.load('images/bat.png')      # Bat hazard image
player_img = pygame.image.load('images/player.png') # Player character image
wumpus_img = pygame.image.load('images/wumpus.png') # Wumpus enemy image
arrow_img = pygame.image.load('images/arrow.png')   # Arrow projectile image
rock_img = pygame.image.load('images/rock.png')     # Rock projectile image

# --- Helper Functions ---

def check_neighbor_rooms(pos, item_list):
    """Check if any adjacent rooms contain items from item_list"""
    exits = cave[pos]  # Get connected rooms from cave layout
    return any(item in exits for item in item_list)  # True if any match found

def draw_room(pos, screen):
    """
    Render the current game room with:
    - Background and exits
    - Player position
    - Any hazards/items present
    - Status information overlay
    """
    exits = cave[player_pos]  # Get exits for current room
    
    # Clear screen with black background
    screen.fill(BLACK)  
    
    # Draw main cave circle (room walls)
    circle_radius = int((SCREEN_WIDTH // 2) * 0.75)
    pygame.draw.circle(screen, BROWN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), circle_radius)

    # Define exit rectangles for each direction (left, right, up, down)
    directions = [
        (LEFT, 0, SCREEN_HEIGHT//2-40, SCREEN_WIDTH//4, 80),
        (RIGHT, SCREEN_WIDTH - SCREEN_WIDTH//4, SCREEN_HEIGHT//2-40, SCREEN_WIDTH//4, 80),
        (UP, SCREEN_WIDTH//2-40, 0, 80, SCREEN_HEIGHT//4),
        (DOWN, SCREEN_WIDTH//2-40, SCREEN_HEIGHT - SCREEN_WIDTH//4, 80, SCREEN_HEIGHT//4)
    ]

    # Draw each available exit path
    for dir, x, y, w, h in directions:
        if exits[dir] > 0:  # If exit exists in this direction
            pygame.draw.rect(screen, BROWN, (x, y, w, h))

    # Draw red warning circle if Wumpus is nearby
    if check_neighbor_rooms(player_pos, [wumpus_pos, [-1, -1]]):
        pygame.draw.circle(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), int((SCREEN_WIDTH//2)*.5))

    # Draw pit if player is in pit room (though they should die immediately)
    if player_pos in pits_list:
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), int((SCREEN_WIDTH//2)*.5))

    # Draw player at center of screen
    screen.blit(player_img, (SCREEN_WIDTH//2 - player_img.get_width()//2, SCREEN_HEIGHT//2 - player_img.get_height()//2))

    # Draw hazards if present in current room
    if player_pos in bats_list:
        screen.blit(bat_img, (SCREEN_WIDTH//2 - bat_img.get_width()//2, SCREEN_HEIGHT//2 - bat_img.get_height()//2))
    if player_pos == wumpus_pos:
        screen.blit(wumpus_img, (SCREEN_WIDTH//2 - wumpus_img.get_width()//2, SCREEN_HEIGHT//2 - wumpus_img.get_height()//2))

    # Draw status text overlay
    y = 0  # Starting y-position for text
    for line in [
        f"POS: {player_pos}",  # Current room number
        f"Arrows: {num_arrows}",  # Arrow count
        f"Rocks: {num_rocks}",  # Rock count
        "You hear the squeaking of bats nearby" if check_neighbor_rooms(player_pos, bats_list) else "",
        "You feel a draft nearby" if check_neighbor_rooms(player_pos, pits_list) else ""
    ]:
        if line:  # Only render non-empty lines
            text = font.render(line, True, (0, 255, 64))  # Green text
            screen.blit(text, (0, y))
            y += text.get_height() + 10  # Move down for next line

    # Special handling for bat encounter - pause to show before teleporting
    if player_pos in bats_list:
        pygame.display.flip()
        time.sleep(2)

def check_room(pos):
    """
    Check current room for hazards/items and handle consequences
    Modifies global game state
    """
    global player_pos, num_arrows, num_rocks

    # Death conditions
    if player_pos == wumpus_pos:
        game_over("You were eaten by a WUMPUS!!!")
    if player_pos in pits_list:
        game_over("You fell into a bottomless pit!!")

    # Bat encounter - teleport player
    if player_pos in bats_list:
        screen.fill(BLACK)
        message = "Bats pick you up and place you elsewhere in the cave!"
        text = font.render(message, True, (0, 255, 64))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        time.sleep(2.5)
        
        # Move bats and teleport player to safe room
        bats_list.remove(player_pos)
        new_bat_pos = random.choice([i for i in range(1, 21) if i != player_pos])
        bats_list.append(new_bat_pos)
        player_pos = random.choice([i for i in range(1, 21) if i != player_pos])

    # Arrow pickup
    if player_pos in arrows_list:
        show_message("You have found an arrow!")
        num_arrows += 1
        arrows_list.remove(player_pos)

    # Rock pickup
    if player_pos in rocks_list:
        show_message("You have found a rock!")
        num_rocks += 1
        rocks_list.remove(player_pos)

def show_message(msg):
    """Display a message to the player centered on a black screen for 2.5 seconds"""
    screen.fill(BLACK)  # Clear screen with black background
    # Render the message text in green (RGB: 0,255,64)
    text = font.render(msg, True, (0, 255, 64))
    # Center the text on screen
    text_rect = text.get_rect(center=screen.get_rect().center)
    screen.blit(text, text_rect)  # Draw text to screen
    pygame.display.flip()  # Update display
    time.sleep(2.5)  # Pause to allow reading

def shoot_arrow(direction):
    """Handle arrow shooting mechanics"""
    global num_arrows  # Need to modify arrow count
    
    # Check if player has arrows
    if num_arrows == 0:
        show_message("You have no arrows!")
        return

    # Deduct arrow and animate its flight
    num_arrows -= 1
    animate_projectile(arrow_img, direction)

    # Check if arrow hit the Wumpus
    if wumpus_pos == cave[player_pos][direction]:
        game_over("Your aim was true and you have killed the Wumpus!")
    else:
        print("Your arrow sails into the darkness...")
        place_wumpus()  # Wumpus may move after missed shot
        
        # Special warning when out of arrows
        if num_arrows == 0:
            show_message("You're out of arrows! The Wumpus begins to hunt you...")

def throw_rock(direction):
    """Handle rock throwing mechanics for scouting"""
    global num_rocks  # Need to modify rock count
    messages = []  # Stores feedback messages
    
    # Check if player has rocks
    if num_rocks == 0:
        messages.append("You have no rocks to throw!")
    else:
        # Deduct rock and animate its throw
        num_rocks -= 1
        animate_projectile(rock_img, direction)

        # Determine what's in the target room
        target = cave[player_pos][direction]
        if wumpus_pos == target:
            messages.append("You hear a low growl... the Wumpus is near!")
        elif target in bats_list:
            messages.append("You hear frantic squeaking... bats!")
        elif target in pits_list:
            messages.append("You hear the rock fall endlessly... a pit!")
        else:
            messages.append("You hear a faint clink. The room is empty.")
            
        # Warn if last rock was used
        if num_rocks == 0:
            messages.append("You have no rocks left!")

    # Display all messages
    screen.fill(BLACK)
    y = 100  # Starting y-position for first message
    for msg in messages:
        text = font.render(msg, True, (255, 255, 255))  # White text
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, y))
        y += 50  # Move down for next message
    pygame.display.flip()
    time.sleep(2.5)  # Pause to read messages

def move_wumpus():
    """Handle Wumpus movement AI"""
    global wumpus_pos
    
    # Behavior depends on whether player has arrows
    if num_arrows > 0:
        # Passive random movement mode
        if not mobile_wumpus or random.randint(1, 100) > wumpus_move_chance:
            return  # Chance to not move
            
        # Try to move to random adjacent safe room
        neighbors = cave[wumpus_pos]
        random.shuffle(neighbors)
        for new_room in neighbors:
            if new_room and new_room != player_pos and new_room not in pits_list + bats_list:
                wumpus_pos = new_room
                return
    else:
        # Aggressive chase mode when player is out of arrows
        if player_pos in cave[wumpus_pos]:
            wumpus_pos = player_pos  # Move directly to player if adjacent
        else:
            # Find closest safe room to player
            neighbors = cave[wumpus_pos]
            best = None
            min_diff = 100  # Large initial difference
            for new_room in neighbors:
                if new_room and new_room not in pits_list + bats_list:
                    diff = abs(new_room - player_pos)
                    if diff < min_diff:
                        min_diff = diff
                        best = new_room
            if best:
                wumpus_pos = best

def game_over(message):
    """Display game over screen with options to retry, menu or quit"""
    while True:  # Stay in game over loop until player chooses
        screen.fill(RED)  # Red background for game over
        
        # Render game over message and options
        text = font.render(message, True, (0, 255, 64))
        retry = font.render("Press [R] to Retry", True, (255, 255, 255))
        menu = font.render("Press [M] for Main Menu", True, (255, 255, 255))
        exit_msg = font.render("Press [Q] to Quit", True, (255, 255, 255))

        # Position and draw all text elements
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, 200)))
        screen.blit(retry, (SCREEN_WIDTH//2 - retry.get_width()//2, 300))
        screen.blit(menu, (SCREEN_WIDTH//2 - menu.get_width()//2, 350))
        screen.blit(exit_msg, (SCREEN_WIDTH//2 - exit_msg.get_width()//2, 400))
        pygame.display.flip()

        # Handle player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Retry
                    reset_game()
                    return
                elif event.key == pygame.K_m:  # Main menu
                    main_menu()
                    reset_game()
                    return
                elif event.key == pygame.K_q:  # Quit
                    pygame.quit()
                    sys.exit()

def animate_projectile(image, direction, color=(0, 0, 0)):
    """
    Animate a projectile (arrow/rock) flying in a straight line from center
    Args:
        image: pygame.Surface - The image to animate
        direction: int - Direction constant (UP/DOWN/LEFT/RIGHT)
        color: tuple - Background color during animation (default black)
    """
    # Start position at screen center
    x = SCREEN_WIDTH // 2
    y = SCREEN_HEIGHT // 2

    # Movement variables
    dx, dy = 0, 0  # Directional movement deltas
    speed = 15      # Pixels per frame movement speed
    steps = 20      # Number of animation frames (longer flight)

    # Set direction vector based on input direction
    if direction == UP:
        dx, dy = 0, -speed  # Move upward
    elif direction == DOWN:
        dx, dy = 0, speed   # Move downward
    elif direction == LEFT:
        dx, dy = -speed, 0  # Move left
    elif direction == RIGHT:
        dx, dy = speed, 0   # Move right

    # Animation loop
    for _ in range(steps):
        draw_room(player_pos, screen)  # Redraw background
        x += dx  # Update position
        y += dy
        # Draw projectile centered at new position
        screen.blit(image, (x - image.get_width() // 2, y - image.get_height() // 2))
        pygame.display.flip()  # Update display
        pygame.time.delay(30)   # Small delay for smooth animation

# Global keybind configuration dictionary
# Maps action names to pygame key constants
keybinds = {
    "move_up": pygame.K_UP,
    "move_down": pygame.K_DOWN,
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "throw_rock": pygame.K_r,  # 'R' for rock
    "shoot_arrow": pygame.K_a  # 'A' for arrow
}

class Player:
    """Player character class handling position and rendering"""
    def __init__(self):
        # Start at center of screen
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = 5        # Movement speed in pixels
        self.color = (255, 200, 0)  # Yellow-orange color
        self.size = 30        # Square side length

    def move(self, dx, dy):
        """Move player by dx,dy units while keeping within screen bounds"""
        self.x += dx * self.speed
        self.y += dy * self.speed
        # Clamp position to stay on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.size))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.size))

    def draw(self, surface):
        """Draw player as colored square on given surface"""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

# Create player instance
player = Player()

def main_menu():
    """Display main menu screen and handle navigation"""
    while True:
        screen.fill(BLACK)  # Clear screen
        
        # Render menu text options
        title = font.render("Hunt the Wumpus", True, (255, 255, 255))
        start = font.render("Press [S] to Start", True, (0, 255, 0))  # Green
        setting = font.render("Press [`] for Settings", True, (0, 0, 255))  # Blue
        quit_game = font.render("Press [Q] to Quit", True, (255, 0, 0))  # Red

        # Position and draw all text elements
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 250))
        screen.blit(setting, (SCREEN_WIDTH//2 - setting.get_width()//2, 300))
        screen.blit(quit_game, (SCREEN_WIDTH//2 - quit_game.get_width()//2, 350))

        pygame.display.flip()

        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # Start game
                    return  
                elif event.key == pygame.K_q:  # Quit
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKQUOTE:  # Settings
                    settings_menu()
                elif event.key == pygame.K_d:  # Difficulty
                    difficulty_menu()

def settings_menu():
    """Key rebinding configuration menu"""
    global keybinds
    selected_action = None  # Currently selected action to rebind
    message = ""  # Status message to display

    while True:
        screen.fill((30, 30, 30))  # Dark gray background
        title = font.render("Settings - Keybinds", True, (255, 255, 255))
        screen.blit(title, (200, 50))

        # Display all keybindings
        y = 150
        for idx, (action, key) in enumerate(keybinds.items(), start=1):
            # Format action text with current key
            action_text = f"[{idx}] {action.replace('_', ' ').title()}: {pygame.key.name(key)}"
            # Highlight selected action
            color = (255, 255, 0) if selected_action == action else (255, 255, 255)
            text_surface = font.render(action_text, True, color)
            screen.blit(text_surface, (200, y))
            y += 50

        # Help instructions
        instructions = font.render(
            "Press 1-6 to rebind keys. Press [D] for difficulty. ESC to go back.", 
            True, (150, 150, 150))
        screen.blit(instructions, (100, 500))

        # Display status message if exists
        if message:
            msg_surface = font.render(message, True, (0, 255, 0))
            screen.blit(msg_surface, (100, 450))

        pygame.display.flip()

        # Handle input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if selected_action:  # If waiting for new key
                    keybinds[selected_action] = event.key  # Update binding
                    message = f"{selected_action.replace('_', ' ').title()} set to {pygame.key.name(event.key)}"
                    selected_action = None
                elif event.key == pygame.K_ESCAPE:  # Return to previous menu
                    return
                # Number keys select actions 1-6
                elif event.key == pygame.K_1:
                    selected_action = "move_up"
                elif event.key == pygame.K_2:
                    selected_action = "move_down"
                elif event.key == pygame.K_3:
                    selected_action = "move_left"
                elif event.key == pygame.K_4:
                    selected_action = "move_right"
                elif event.key == pygame.K_5:
                    selected_action = "throw_rock"
                elif event.key == pygame.K_6:
                    selected_action = "shoot_arrow"
                elif event.key == pygame.K_d:  # Open difficulty menu
                    difficulty_menu()

def difficulty_menu():
    """Menu for selecting game difficulty level"""
    global NUM_BATS, NUM_PITS, NUM_ARROWS, NUM_ROCKS, wumpus_move_chance
    
    # Difficulty options and their configurations
    options = ["Easy", "Medium", "Hard"]
    values = {
        "Easy": (1, 1, 5, 5, 30),    # bats, pits, arrows, rocks, move_chance%
        "Medium": (2, 1, 3, 3, 60),   # bats, pits, arrows, rocks, move_chance%
        "Hard": (3, 2, 1, 1, 90)      # bats, pits, arrows, rocks, move_chance%
    }
    selected = 0  # Currently selected option index

    while True:
        screen.fill((10, 10, 10))  # Very dark background
        title = font.render("Select Difficulty", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Draw all difficulty options
        for i, option in enumerate(options):
            # Highlight selected option
            color = (0, 255, 0) if i == selected else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        # Return instructions
        back_msg = font.render("Press ESC to return", True, (100, 100, 100))
        screen.blit(back_msg, (SCREEN_WIDTH // 2 - back_msg.get_width() // 2, 450))

        pygame.display.flip()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Move selection up
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:  # Move selection down
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:  # Confirm selection
                    # Update game parameters based on difficulty
                    NUM_BATS, NUM_PITS, NUM_ARROWS, NUM_ROCKS, wumpus_move_chance = values[options[selected]]
                    return
                elif event.key == pygame.K_ESCAPE:  # Return without changes
                    return
                
def reset_game():
    """Reset game state to initial conditions"""
    global num_arrows, num_rocks
    num_arrows = 1  # Reset to starting arrow count
    num_rocks = 2   # Reset to starting rock count
    populate_cave()  # Regenerate cave layout and hazards

def populate_cave():
    """Initialize cave with random placement of player, wumpus, and items"""
    global player_pos, wumpus_pos
    # Clear all existing item/hazard lists
    bats_list.clear()
    pits_list.clear()
    arrows_list.clear()
    rocks_list.clear()

    # Place player in random room (1-20)
    player_pos = random.randint(1, 20)
    place_wumpus()  # Place wumpus (ensuring not in same room as player)
    
    # Place hazards and items according to current difficulty settings
    for _ in range(NUM_BATS): place_bat()
    for _ in range(NUM_PITS): place_pit()
    for _ in range(NUM_ARROWS): place_arrow()
    for _ in range(NUM_ROCKS): place_rock()

def place_wumpus():
    """Place the Wumpus in a random room not containing the player"""
    global wumpus_pos
    while True:
        wumpus_pos = random.randint(1, 20)
        if wumpus_pos != player_pos:  # Ensure wumpus doesn't spawn on player
            break

def place_item(item_list):
    """
    Generic function to place an item in a valid random room
    Args:
        item_list: The list to add the room number to (bats, pits, etc.)
    """
    while True:
        pos = random.randint(1, 20)  # Random room number
        # Check room is empty and not containing player/wumpus
        if (pos != player_pos and 
            pos != wumpus_pos and 
            pos not in pits_list + bats_list + item_list):
            item_list.append(pos)
            break

# Convenience functions for placing specific items
def place_bat(): place_item(bats_list)
def place_pit(): place_item(pits_list)
def place_arrow(): place_item(arrows_list)
def place_rock(): place_item(rocks_list)

def get_action_from_key(key):
    """Look up which action is bound to the given key"""
    for action, bound_key in keybinds.items():
        if key == bound_key:
            return action
    return None  # No action bound to this key

def check_pygame_events():
    """Handle all pygame events including player input"""
    global player_pos, last_direction

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Window close button
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:  # Key press events
            if event.key == pygame.K_ESCAPE:  # Quit on ESC
                pygame.quit()
                sys.exit()

            # Check if pressed key is bound to an action
            action = get_action_from_key(event.key)

            # Movement handling
            if action in ["move_left", "move_right", "move_up", "move_down"]:
                # Convert action to direction constant
                if action == "move_left": direction = LEFT
                elif action == "move_right": direction = RIGHT
                elif action == "move_up": direction = UP
                elif action == "move_down": direction = DOWN

                last_direction = direction  # Track facing direction

                # Check for modified movement (shoot/throw)
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Shift+move = shoot
                    shoot_arrow(direction)
                elif pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+move = throw
                    throw_rock(direction)
                # Normal movement if exit exists in that direction
                elif cave[player_pos][direction] > 0:
                    player_pos = cave[player_pos][direction]  # Move player
                    move_wumpus()  # Wumpus may move after player

            # Direct action keys
            elif action == "throw_rock":
                direction = choose_direction("Choose direction to throw rock")
                if direction is not None:  # If direction was selected
                    throw_rock(direction)
                    
            elif action == "shoot_arrow":
                direction = choose_direction("Choose direction to shoot arrow")
                if direction is not None:
                    shoot_arrow(direction)

def choose_direction(prompt):
    """Display directional choice menu and return selection"""
    options = ["UP", "DOWN", "LEFT", "RIGHT"]
    directions = [UP, DOWN, LEFT, RIGHT]  # Corresponding direction constants
    selected = 0  # Currently selected option index

    while True:
        screen.fill(BLACK)
        # Display prompt text
        title = font.render(prompt, True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        # Display all direction options
        for i, option in enumerate(options):
            # Highlight selected option in green
            color = (0, 255, 0) if i == selected else (200, 200, 200)
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i * 50))

        pygame.display.flip()

        # Handle menu navigation
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Move selection up
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:  # Move selection down
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:  # Confirm selection
                    return directions[selected]
                elif event.key == pygame.K_ESCAPE:  # Cancel
                    return None

# --- Game Start ---
main_menu()  # Show main menu first
reset_game()  # Initialize game state

# Main game loop
while True:
    check_pygame_events()  # Handle input
    draw_room(player_pos, screen)  # Render current room
    pygame.display.flip()  # Update display
    check_room(player_pos)  # Check for hazards/items in current room