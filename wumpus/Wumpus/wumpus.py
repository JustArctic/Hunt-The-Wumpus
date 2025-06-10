import pygame
import random
import time
import sys

#===============================================================================
#                       Functions Area                                         =
#===============================================================================
def check_neighbor_rooms(pos, item_list):
    """ Checks each orthagonal cell next to pos for the requested item
    returns True as soon as the item is found.
    """
    exits = cave[pos]
    return any(item in cave[pos] for item in item_list)
        
def draw_room( pos, screen):
    """ Draws the room in the back buffer
    """
    x=0
    y=1
    exits = cave[player_pos]
    screen.fill( (0,0,0) ) #paint the background in black

    #draw the room circle in brown
    circle_radius = int ((SCREEN_WIDTH//2)*.75)
    pygame.draw.circle(screen, BROWN, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), circle_radius, 0)

    #next draw all exits from the room
    if exits[LEFT] > 0:
        left = 0
        top = SCREEN_HEIGHT//2-40
        pygame.draw.rect(screen, BROWN, ( (left,top), (SCREEN_WIDTH//4,80)), 0)
    if exits[RIGHT] > 0:
        #draw right exit
        left = SCREEN_WIDTH-(SCREEN_WIDTH//4)
        top = SCREEN_HEIGHT//2-40
        pygame.draw.rect(screen, BROWN, ((left,top), (SCREEN_WIDTH//4,80)), 0)
    if exits[UP] > 0:
        #draw top exit
        left = SCREEN_WIDTH//2-40
        top = 0
        pygame.draw.rect(screen, BROWN, ((left,top), (80,SCREEN_HEIGHT//4)), 0)
    if exits[DOWN] > 0 :
        #draw bottom exit
        left = SCREEN_WIDTH//2-40
        top = SCREEN_HEIGHT-(SCREEN_WIDTH//4)
        pygame.draw.rect(screen, BROWN, ((left,top), (80,SCREEN_HEIGHT//4)), 0)
        
    #find out if bats, pits or a wumpus is near
    bats_near = check_neighbor_rooms(player_pos, bats_list)
    pit_near = check_neighbor_rooms(player_pos, pits_list)
    wumpus_near = check_neighbor_rooms(player_pos, [wumpus_pos, [-1,-1]])
    
    #draw a blood circle if the Wumpus is nearby
    if wumpus_near == True:
        circle_radius = int ((SCREEN_WIDTH//2)*.5)
        pygame.draw.circle(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), circle_radius, 0)

    #draw the pit in black if it is present
    if player_pos in pits_list:
        circle_radius = int ((SCREEN_WIDTH//2)*.5)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), circle_radius, 0)
     
    #draw the player
    screen.blit(player_img,(SCREEN_WIDTH//2-player_img.get_width()//2,SCREEN_HEIGHT//2-player_img.get_height()//2))

    #draw the bat imag
    if player_pos in bats_list:
        screen.blit(bat_img,(SCREEN_WIDTH//2-bat_img.get_width()//2,SCREEN_HEIGHT//2-bat_img.get_height()//2))

    #draw the wumpus
    if player_pos == wumpus_pos:
        screen.blit(wumpus_img,(SCREEN_WIDTH//2-wumpus_img.get_width()//2,SCREEN_HEIGHT//2-wumpus_img.get_height()//2))

    #draw text
    y_text_pos = 0 #keeps track of the next y position on screen to draw text
    pos_text = font.render("POS:"+str(player_pos), 1, (0, 255, 64))
    screen.blit(pos_text,(0, 0))
    arrow_text = font.render("Arrows: "+str(num_arrows), 1, (0, 255, 64))
    y_text_pos = y_text_pos+pos_text.get_height()+10
    screen.blit(arrow_text,(0, y_text_pos))
    rock_text = font.render("Rocks: "+str(num_rocks), 1, (0, 255, 64))
    y_text_pos += rock_text.get_height() + 10
    screen.blit(rock_text,(0, y_text_pos))
    if bats_near == True:
        bat_text = font.render("You hear the squeaking of bats nearby", 1, (0, 255, 64))
        y_text_pos = y_text_pos+bat_text.get_height()+10
        screen.blit(bat_text,(0, y_text_pos))
    if pit_near == True:
        pit_text = font.render("You feel a draft nearby", 1, (0, 255, 64))
        y_text_pos = y_text_pos+pit_text.get_height()+10
        screen.blit(pit_text,(0, y_text_pos))

    if player_pos in bats_list: #if bats are here, go ahead and flip the display and wait a bit
        pygame.display.flip()
        time.sleep(2.0)

def draw_game_screen():
        screen.fill(BLACK)
    # Draw the room, player, rocks, bats, etc.
    # For example, draw player at player_pos, rocks at their positions
    # This depends on your game code

    # Example:
    # draw_player(player_pos)
    # draw_rocks(rocks_list)


def populate_cave():
    global player_pos, wumpus_pos

    #place the player
    player_pos = random.randint(1, 20)

    # place the wumpus
    place_wumpus()
    
    #place the bats
    for bat in range(0,NUM_BATS):
        place_bat()

    #place the pits
    for pit in range (0,NUM_PITS):
        place_pit()

    #place the arrows
    for arrow in range (0,NUM_ARROWS):
        place_arrow()

    #place the rocks
    for rock in range (0,NUM_ROCKS):
        place_rock()

    print ("Player at: "+str(player_pos))
    print ("Wumpus at: "+str(wumpus_pos))
    print ("Bats at:" + str(bats_list) )
    print ("Pits at:" + str(pits_list))
    print ("Arrows at:" +str(arrows_list))
    print ("Rocks at:" +str(rocks_list))

def place_wumpus():
    global player_pos, wumpus_pos
    
    wumpus_pos = player_pos
    while (wumpus_pos == player_pos):
        wumpus_pos = random.randint(0,20)

def place_bat():
   #place the bats
    bat_pos = player_pos
    while bat_pos == player_pos or (bat_pos in bats_list) or (bat_pos == wumpus_pos) or (bat_pos in pits_list):
        bat_pos = random.randint(1,20)
    bats_list.append(bat_pos)

def place_pit():
    pit_pos = player_pos
    while (pit_pos == player_pos) or (pit_pos in bats_list) or (pit_pos == wumpus_pos) or (pit_pos in pits_list):
        pit_pos = random.randint(1,20)
    pits_list.append(pit_pos)

def place_arrow():
    arrow_pos = player_pos
    while (arrow_pos == player_pos) or (arrow_pos in bats_list) or (arrow_pos == wumpus_pos) or (arrow_pos in pits_list):
        arrow_pos = random.randint(1,20)
    arrows_list.append(arrow_pos)

def place_rock():
    rock_pos = player_pos
    while (rock_pos == player_pos) or (rock_pos in bats_list) or (rock_pos == wumpus_pos) or (rock_pos in pits_list):
        rock_pos = random.randint(1,20)
    rocks_list.append(rock_pos)
    
def check_room(pos):
    global player_pos, screen, num_arrows
    
    #is there a Wumpus in the room?
    if player_pos == wumpus_pos:
        game_over("You were eaten by a WUMPUS!!!")

    #is there a pit?
    if player_pos in pits_list:
        game_over("You fell into a bottomless pit!!")

    #is there bats in the room?  If so move the player and the bats
    if player_pos in bats_list:
        print("Bats pick you up and place you elsewhere in the cave!")
        screen.fill(BLACK)
        bat_text = font.render("Bats pick you up and place you elsewhere in the cave!", 1, (0, 255, 64))
        textrect = bat_text.get_rect()
        textrect.centerx = screen.get_rect().centerx
        textrect.centery = screen.get_rect().centery
        screen.blit(bat_text,textrect)
        pygame.display.flip()
        time.sleep(2.5)
        
        #move the bats
        new_pos = player_pos
        
        while (new_pos == player_pos) or (new_pos in bats_list) or (new_pos == wumpus_pos) or (new_pos in pits_list):
            new_pos = random.randint(1,20)
        bats_list.remove(player_pos)   
        bats_list.append(new_pos)
        print ("bat at: "+str(new_pos))
                
        #now move the player
        new_pos = player_pos # set new_pos equal to the old os so the first test fails
        # Now place the player in a random location
        while (new_pos == player_pos) or (new_pos in bats_list) or (new_pos == wumpus_pos) or (new_pos in pits_list):
            new_pos = random.randint(1,20)
        player_pos = new_pos
        print ("player at:"+str(player_pos))

    #is there an arrow in the room?
    if player_pos in arrows_list:
        screen.fill(BLACK)
        text = font.render("You have found an arrow!", 1, (0, 255, 64))
        textrect = text.get_rect()
        textrect.centerx = screen.get_rect().centerx
        textrect.centery = screen.get_rect().centery
        screen.blit(text,textrect)
        pygame.display.flip()
        time.sleep(2.5)
        num_arrows +=1
        arrows_list.remove(player_pos)

    if player_pos in rocks_list:
        rocks_list.remove(player_pos)
        screen.fill(BLACK)  # or your background
        text = font.render("You have found a rock!", True, (0, 255, 64))
        textrect = text.get_rect(center=screen.get_rect().center)
        screen.blit(text, textrect)
        pygame.display.flip()
        time.sleep(2.5)
        
        # Now redraw the normal game state so message disappears
        draw_game_screen()  # <-- You need to define this function to redraw the game
        pygame.display.flip()




def reset_game():
    global num_arrows, num_rocks
    populate_cave()
    num_arrows = 1
    num_rocks = 1

def game_over(message):
    global screen
    time.sleep(1.0)
    screen.fill(RED)
    text=font.render(message, 1, (0, 255, 64))
    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    textrect.centery = screen.get_rect().centery
    screen.blit(text,textrect)
    pygame.display.flip()
    time.sleep(2.5)
    print (message)
    pygame.quit()
    sys.exit()

def move_wumpus():
    global wumpus_pos

    if mobile_wumpus == False or random.randint(1,100) > wumpus_move_chance:
        return
        
    exits = cave[wumpus_pos]
    
    for new_room in exits:
        if new_room == 0:
            continue
        elif new_room == player_pos:
            continue
        elif new_room in bats_list:
            continue
        elif new_room in pits_list:
            continue
        else:
            wumpus_pos = new_room
            break
            
    print ("Wumpus moved to:"+str(wumpus_pos))
                   
def shoot_arrow(direction):
    global num_arrows, player_pos

    hit = False
    
    if num_arrows == 0:
        return False
    num_arrows -= 1
    
    if wumpus_pos == cave[player_pos][direction]:
        hit = True

    if hit == True:
        game_over("Your aim was true and you have killed the Wumpus!")
        pygame.quit()
        sys.exit()
    else:    
        print ("Your arrow sails into the darkness, never to be seen again....")
        place_wumpus()
    if num_arrows == 0:
        game_over("You are out of arrows.  You have died!")
        pygame.quit()
        sys.exit()
        
def throw_rock(direction):
    global num_rocks

    if num_rocks == 0:
        return False
    print("No rocks left!")

    num_rocks -= 1
    next_room = cave[player_pos][direction]
    
    screen.fill(BLACK)
    if next_room == 0:
        text = font.render("You threw a rock into a wall!", 1, (255, 255, 255))
    elif next_room == wumpus_pos:
        text = font.render("You hear a low growl... the Wumpus is near!", 1, (255, 0, 0))
    elif next_room in bats_list:
        text = font.render("You hear frantic squeaking... bats!", 1, (200, 200, 0))
    elif next_room in pits_list:
        text = font.render("You hear the rock fall endlessly... a pit!", 1, (150, 150, 150))
    else:
        text = font.render("You hear a faint clink. The room is empty.", 1, (0, 255, 64))

    textrect = text.get_rect(center=screen.get_rect().center)
    screen.blit(text, textrect)
    pygame.display.flip()
    time.sleep(2.5)

def check_pygame_events():
    global player_pos
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.key ==pygame.K_LEFT:
             if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                shoot_arrow(LEFT)
             elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                throw_rock(LEFT)
             elif cave[player_pos][LEFT] > 0: 
                player_pos=cave[player_pos][LEFT]
                move_wumpus()
        elif event.key == pygame.K_RIGHT:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                shoot_arrow(RIGHT)
            elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                throw_rock(RIGHT)
            elif cave[player_pos][RIGHT] >0:
                player_pos = cave[player_pos][RIGHT]
                move_wumpus()
        elif event.key == pygame.K_UP:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                shoot_arrow(UP)
            elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                throw_rock(UP)
            elif cave[player_pos][UP] > 0:
                player_pos = cave[player_pos][UP]
                move_wumpus()
        elif event.key ==pygame.K_DOWN:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                shoot_arrow(DOWN)
            elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                throw_rock(DOWN)
            elif cave[player_pos][DOWN] > 0:
                player_pos = cave[player_pos][DOWN]
                move_wumpus()
      
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
    
#===============================================================================
#                       Gloabls and Constants area                             =
#===============================================================================
#Our screen width and height
SCREEN_WIDTH = SCREEN_HEIGHT= 1000

#number of bats, pits and arrows in the cave#load our three images
bat_img = pygame.image.load('images/bat.png')
player_img = pygame.image.load('images/player.png')
wumpus_img = pygame.image.load('images/wumpus.png')
arrow_img = pygame.image.load('images/arrow.png')
rock_img = pygame.image.load('images/rock.png')
#increase the number of bats and pits to make it harder
#increase the number of arrows to make it easier
NUM_BATS = 3
NUM_PITS = 3
NUM_ARROWS = 3
NUM_ROCKS = 1

player_pos = 0 #tracks where we are in the cave
wumpus_pos = 0 #tracks where the Wumpus is
num_arrows = 1 # Starting arrows
num_rocks = 1 #Starting rocks
mobile_wumpus = False #Set this to true to allow the wumpus to move
wumpus_move_chance = 50

#constants for directions
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

#color defintions
BROWN = 193,154,107
BLACK = 0,0,0
RED = 138,7,7

cave = {1: [0,8,2,5], 2: [0,10,3,1], 3: [0,12,4,2], 4: [0,14,5,3], 
    5:[0,6,1,4], 6: [5,0,7,15], 7: [0,17,8,6], 8: [1,0,9,7],
    9: [0,18,10,8], 10: [2,0,11,9], 11: [0,19,12,10], 12: [3,0,13,11], 
    13: [0,20,14,12], 14: [4,0,15,13], 15: [0,16,6,14], 16: [15,0,17,20],
    17: [7,0,18,16], 18: [9,0,19,17], 19: [11,0,20,18], 20: [13,0,16,19] }

bats_list = []
pits_list = []
arrows_list = []
rocks_list = []

#===============================================================================
#                       Initilizations area                                   =
#===============================================================================

# Game initialization
player_pos = (0, 0)
rocks_list = [(1, 1), (2, 2)]
num_rocks = 0

print_instructoions()
input("Press <ENTER> to begin.")
pygame.init()
screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE )
pygame.display.set_caption("Hunt the Wumpus")

#load our three images
bat_img = pygame.image.load('images/bat.png')
player_img = pygame.image.load('images/player.png')
wumpus_img = pygame.image.load('images/wumpus.png')
arrow_img = pygame.image.load('images/arrow.png')
rock_img = pygame.image.load('images/rock.png')

#setup our font
font = pygame.font.Font(None, 36)

#Get iniital game settings
reset_game()

#===============================================================================
#                       Main Game Loop                                         =
#===============================================================================
while True:
    check_pygame_events()     
    draw_room(player_pos, screen)
    pygame.display.flip()   
    check_room(player_pos)