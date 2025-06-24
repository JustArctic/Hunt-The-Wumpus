import pygame
import random
import time
import sys

# --- Constants ---
SCREEN_WIDTH = SCREEN_HEIGHT = 1000
NUM_BATS = 2
NUM_PITS = 1
NUM_ARROWS = 3
NUM_ROCKS = 3

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

BROWN = (193, 154, 107)
BLACK = (0, 0, 0)
RED = (138, 7, 7)

# --- Cave Layout ---
cave = {
    1: [0, 8, 2, 5], 2: [0, 10, 3, 1], 3: [0, 12, 4, 2], 4: [0, 14, 5, 3],
    5: [0, 6, 1, 4], 6: [5, 0, 7, 15], 7: [0, 17, 8, 6], 8: [1, 0, 9, 7],
    9: [0, 18, 10, 8], 10: [2, 0, 11, 9], 11: [0, 19, 12, 10], 12: [3, 0, 13, 11],
    13: [0, 20, 14, 12], 14: [4, 0, 15, 13], 15: [0, 16, 6, 14], 16: [15, 0, 17, 20],
    17: [7, 0, 18, 16], 18: [9, 0, 19, 17], 19: [11, 0, 20, 18], 20: [13, 0, 16, 19]
}

# --- Game State Variables ---
player_pos = 0
wumpus_pos = 0
num_arrows = 1
num_rocks = 1
mobile_wumpus = True
wumpus_move_chance = 70
last_direction = UP  # Default facing direction

bats_list = []
pits_list = []
arrows_list = []
rocks_list = []

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
around you <SHIFT> key and an arrow key to fire your arrow, if you hit the Wumpus
you win.

If you are unsure where to move you can toss a rock to check if they are Bats, bottomless pits
or the Wumpus

Use the arrow keys to move.  Press the <SHIFT> key and an arrow key to
fire your arrow.
    '''
    )

# --- Initialize Pygame ---
print_instructoions()
input("Press <ENTER> to begin.")
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Hunt the Wumpus")
font = pygame.font.Font(None, 36)

# Load images
bat_img = pygame.image.load('images/bat.png')
player_img = pygame.image.load('images/player.png')
wumpus_img = pygame.image.load('images/wumpus.png')
arrow_img = pygame.image.load('images/arrow.png')
rock_img = pygame.image.load('images/rock.png')

# --- Helper Functions ---
def check_neighbor_rooms(pos, item_list):
    exits = cave[pos]
    return any(item in exits for item in item_list)

def draw_room(pos, screen):
    exits = cave[player_pos]
    screen.fill(BLACK)
    circle_radius = int((SCREEN_WIDTH // 2) * 0.75)
    pygame.draw.circle(screen, BROWN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), circle_radius)

    directions = [(LEFT, 0, SCREEN_HEIGHT//2-40, SCREEN_WIDTH//4, 80),
                  (RIGHT, SCREEN_WIDTH - SCREEN_WIDTH//4, SCREEN_HEIGHT//2-40, SCREEN_WIDTH//4, 80),
                  (UP, SCREEN_WIDTH//2-40, 0, 80, SCREEN_HEIGHT//4),
                  (DOWN, SCREEN_WIDTH//2-40, SCREEN_HEIGHT - SCREEN_WIDTH//4, 80, SCREEN_HEIGHT//4)]

    for dir, x, y, w, h in directions:
        if exits[dir] > 0:
            pygame.draw.rect(screen, BROWN, (x, y, w, h))

    if check_neighbor_rooms(player_pos, [wumpus_pos, [-1, -1]]):
        pygame.draw.circle(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), int((SCREEN_WIDTH//2)*.5))

    if player_pos in pits_list:
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), int((SCREEN_WIDTH//2)*.5))

    screen.blit(player_img, (SCREEN_WIDTH//2 - player_img.get_width()//2, SCREEN_HEIGHT//2 - player_img.get_height()//2))

    if player_pos in bats_list:
        screen.blit(bat_img, (SCREEN_WIDTH//2 - bat_img.get_width()//2, SCREEN_HEIGHT//2 - bat_img.get_height()//2))

    if player_pos == wumpus_pos:
        screen.blit(wumpus_img, (SCREEN_WIDTH//2 - wumpus_img.get_width()//2, SCREEN_HEIGHT//2 - wumpus_img.get_height()//2))

    y = 0
    for line in [
        f"POS: {player_pos}",
        f"Arrows: {num_arrows}",
        f"Rocks: {num_rocks}",
        "You hear the squeaking of bats nearby" if check_neighbor_rooms(player_pos, bats_list) else "",
        "You feel a draft nearby" if check_neighbor_rooms(player_pos, pits_list) else ""
    ]:
        if line:
            text = font.render(line, True, (0, 255, 64))
            screen.blit(text, (0, y))
            y += text.get_height() + 10

    if player_pos in bats_list:
        pygame.display.flip()
        time.sleep(2)

def check_room(pos):
    global player_pos, num_arrows, num_rocks

    if player_pos == wumpus_pos:
        game_over("You were eaten by a WUMPUS!!!")

    if player_pos in pits_list:
        game_over("You fell into a bottomless pit!!")

    if player_pos in bats_list:
        screen.fill(BLACK)
        message = "Bats pick you up and place you elsewhere in the cave!"
        text = font.render(message, True, (0, 255, 64))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        time.sleep(2.5)
        bats_list.remove(player_pos)
        new_bat_pos = random.choice([i for i in range(1, 21) if i != player_pos])
        bats_list.append(new_bat_pos)
        player_pos = random.choice([i for i in range(1, 21) if i != player_pos])

    if player_pos in arrows_list:
        show_message("You have found an arrow!")
        num_arrows += 1
        arrows_list.remove(player_pos)

    if player_pos in rocks_list:
        show_message("You have found a rock!")
        num_rocks += 1
        rocks_list.remove(player_pos)

def show_message(msg):
    screen.fill(BLACK)
    text = font.render(msg, True, (0, 255, 64))
    text_rect = text.get_rect(center=screen.get_rect().center)
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(2.5)

def shoot_arrow(direction):
    global num_arrows
    if num_arrows == 0:
        show_message("You have no arrows!")
        return

    num_arrows -= 1
    animate_projectile(arrow_img, direction)

    if wumpus_pos == cave[player_pos][direction]:
        game_over("Your aim was true and you have killed the Wumpus!")
    else:
        print("Your arrow sails into the darkness...")
        place_wumpus()
    if num_arrows == 0:
        show_message("You're out of arrows! The Wumpus begins to hunt you...")


def throw_rock(direction):
    global num_rocks
    messages = []

    if num_rocks == 0:
        messages.append("You have no rocks to throw!")
    else:
        num_rocks -= 1
        animate_projectile(rock_img, direction)

        target = cave[player_pos][direction]
        if wumpus_pos == target:
            messages.append("You hear a low growl... the Wumpus is near!")
        elif target in bats_list:
            messages.append("You hear frantic squeaking... bats!")
        elif target in pits_list:
            messages.append("You hear the rock fall endlessly... a pit!")
        else:
            messages.append("You hear a faint clink. The room is empty.")
        if num_rocks == 0:
            messages.append("You have no rocks left!")

    screen.fill(BLACK)
    y = 100
    for msg in messages:
        text = font.render(msg, True, (255, 255, 255))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, y))
        y += 50
    pygame.display.flip()
    time.sleep(2.5)

def move_wumpus():
    global wumpus_pos

    if num_arrows > 0:
        # Passive random movement if arrows still remain
        if not mobile_wumpus or random.randint(1, 100) > wumpus_move_chance:
            return
        neighbors = cave[wumpus_pos]
        random.shuffle(neighbors)
        for new_room in neighbors:
            if new_room and new_room != player_pos and new_room not in pits_list + bats_list:
                wumpus_pos = new_room
                return
    else:
        # Chase player aggressively
        if player_pos in cave[wumpus_pos]:
            wumpus_pos = player_pos  # Enters player's room
        else:
            # Move toward a neighboring room that's closer to the player
            neighbors = cave[wumpus_pos]
            best = None
            min_diff = 100
            for new_room in neighbors:
                if new_room and new_room not in pits_list + bats_list:
                    diff = abs(new_room - player_pos)
                    if diff < min_diff:
                        min_diff = diff
                        best = new_room
            if best:
                wumpus_pos = best

def game_over(message):
    while True:
        screen.fill(RED)
        text = font.render(message, True, (0, 255, 64))
        retry = font.render("Press [R] to Retry", True, (255, 255, 255))
        menu = font.render("Press [M] for Main Menu", True, (255, 255, 255))
        exit_msg = font.render("Press [Q] to Quit", True, (255, 255, 255))

        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, 200)))
        screen.blit(retry, (SCREEN_WIDTH//2 - retry.get_width()//2, 300))
        screen.blit(menu, (SCREEN_WIDTH//2 - menu.get_width()//2, 350))
        screen.blit(exit_msg, (SCREEN_WIDTH//2 - exit_msg.get_width()//2, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    return
                elif event.key == pygame.K_m:
                    main_menu()
                    reset_game()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def animate_projectile(image, direction, color=(0, 0, 0)):
    """Animate a projectile flying straight from the center in a cardinal direction."""
    x = SCREEN_WIDTH // 2
    y = SCREEN_HEIGHT // 2

    dx, dy = 0, 0
    speed = 15
    steps = 20  # Longer flight

    if direction == UP:
        dx, dy = 0, -speed
    elif direction == DOWN:
        dx, dy = 0, speed
    elif direction == LEFT:
        dx, dy = -speed, 0
    elif direction == RIGHT:
        dx, dy = speed, 0

    for _ in range(steps):
        draw_room(player_pos, screen)  # Re-render the base room
        x += dx
        y += dy
        screen.blit(image, (x - image.get_width() // 2, y - image.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(30)

# Global keybinds dict
keybinds = {
    "move_up": pygame.K_UP,
    "move_down": pygame.K_DOWN,
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "throw_rock": pygame.K_r,
    "shoot_arrow": pygame.K_a
}

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = 5
        self.color = (255, 200, 0)
        self.size = 30

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        # Keep inside screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.size))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.size))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

player = Player()

def main_menu():
    while True:
        screen.fill(BLACK)
        title = font.render("Hunt the Wumpus", True, (255, 255, 255))
        start = font.render("Press [S] to Start", True, (0, 255, 0))
        setting = font.render("Press [`] for Settings", True, (0, 0, 255))
        quit_game = font.render("Press [Q] to Quit", True, (255, 0, 0))

        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 250))
        screen.blit(setting, (SCREEN_WIDTH//2 - setting.get_width()//2, 300))
        screen.blit(quit_game, (SCREEN_WIDTH//2 - quit_game.get_width()//2, 350))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return  # Start game
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKQUOTE:
                    settings_menu()
                elif event.key == pygame.K_d:
                    difficulty_menu()


# Global keybinds dictionary
keybinds = {
    "move_up": pygame.K_UP,
    "move_down": pygame.K_DOWN,
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "throw_rock": pygame.K_r,
    "shoot_arrow": pygame.K_a
}

difficulty = font.render("Press [D] to Change Difficulty", True, (255, 255, 0))
screen.blit(difficulty, (SCREEN_WIDTH // 2 - difficulty.get_width() // 2, 325))


def settings_menu():
    global keybinds
    selected_action = None
    message = ""

    while True:
        screen.fill((30, 30, 30))
        title = font.render("Settings - Keybinds", True, (255, 255, 255))
        screen.blit(title, (200, 50))

        y = 150
        for idx, (action, key) in enumerate(keybinds.items(), start=1):
            action_text = f"[{idx}] {action.replace('_', ' ').title()}: {pygame.key.name(key)}"
            color = (255, 255, 0) if selected_action == action else (255, 255, 255)
            text_surface = font.render(action_text, True, color)
            screen.blit(text_surface, (200, y))
            y += 50

        instructions = font.render("Press 1-6 to rebind keys. Press [D] for difficulty. ESC to go back.", True, (150, 150, 150))
        screen.blit(instructions, (100, 500))

        if message:
            msg_surface = font.render(message, True, (0, 255, 0))
            screen.blit(msg_surface, (100, 450))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if selected_action:
                    keybinds[selected_action] = event.key
                    message = f"{selected_action.replace('_', ' ').title()} set to {pygame.key.name(event.key)}"
                    selected_action = None
                elif event.key == pygame.K_ESCAPE:
                    return
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
                elif event.key == pygame.K_d:
                    difficulty_menu()

def difficulty_menu():
    global NUM_BATS, NUM_PITS, NUM_ARROWS, NUM_ROCKS, wumpus_move_chance
    options = ["Easy", "Medium", "Hard"]
    values = {
        "Easy": (1, 1, 5, 5, 30),
        "Medium": (2, 1, 3, 3, 60),
        "Hard": (3, 2, 1, 1, 90)
    }
    selected = 0

    while True:
        screen.fill((10, 10, 10))
        title = font.render("Select Difficulty", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        back_msg = font.render("Press ESC to return", True, (100, 100, 100))
        screen.blit(back_msg, (SCREEN_WIDTH // 2 - back_msg.get_width() // 2, 450))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN: selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    NUM_BATS, NUM_PITS, NUM_ARROWS, NUM_ROCKS, wumpus_move_chance = values[options[selected]]
                    return
                elif event.key == pygame.K_ESCAPE:
                    return
                
def reset_game():
    global num_arrows, num_rocks
    num_arrows = 1
    num_rocks = 2
    populate_cave()

def populate_cave():
    global player_pos, wumpus_pos
    bats_list.clear()
    pits_list.clear()
    arrows_list.clear()
    rocks_list.clear()

    player_pos = random.randint(1, 20)
    place_wumpus()
    for _ in range(NUM_BATS): place_bat()
    for _ in range(NUM_PITS): place_pit()
    for _ in range(NUM_ARROWS): place_arrow()
    for _ in range(NUM_ROCKS): place_rock()

def place_wumpus():
    global wumpus_pos
    while True:
        wumpus_pos = random.randint(1, 20)
        if wumpus_pos != player_pos:
            break

def place_item(item_list):
    while True:
        pos = random.randint(1, 20)
        if pos != player_pos and pos != wumpus_pos and pos not in pits_list + bats_list + item_list:
            item_list.append(pos)
            break

def place_bat(): place_item(bats_list)
def place_pit(): place_item(pits_list)
def place_arrow(): place_item(arrows_list)
def place_rock(): place_item(rocks_list)

def get_action_from_key(key):
    for action, bound_key in keybinds.items():
        if key == bound_key:
            return action
    return None

def check_pygame_events():
    global player_pos, last_direction

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            action = get_action_from_key(event.key)

            if action in ["move_left", "move_right", "move_up", "move_down"]:
                if action == "move_left": direction = LEFT
                elif action == "move_right": direction = RIGHT
                elif action == "move_up": direction = UP
                elif action == "move_down": direction = DOWN

                last_direction = direction

                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    shoot_arrow(direction)
                elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                    throw_rock(direction)
                elif cave[player_pos][direction] > 0:
                    player_pos = cave[player_pos][direction]
                    move_wumpus()

            elif action == "throw_rock":
                direction = choose_direction("Choose direction to throw rock")
                if direction is not None:
                    throw_rock(direction)

            elif action == "shoot_arrow":
                direction = choose_direction("Choose direction to shoot arrow")
                if direction is not None:
                    shoot_arrow(direction)

def choose_direction(prompt):
    options = ["UP", "DOWN", "LEFT", "RIGHT"]
    directions = [UP, DOWN, LEFT, RIGHT]
    selected = 0

    while True:
        screen.fill(BLACK)
        title = font.render(prompt, True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected else (200, 200, 200)
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return directions[selected]
                elif event.key == pygame.K_ESCAPE:
                    return None

# --- Game Start ---
main_menu()
reset_game()

while True:
    check_pygame_events()
    draw_room(player_pos, screen)
    pygame.display.flip()
    check_room(player_pos)