########################################################################
#   Author: Nolan Y. / bbomb64 / Christopher D.                        #                                                                      #
#   Description: My goal is to recreate the New Super Mario Bros.      #
#                DS gamemode Mario vs Luigi. Even if it's not perfect, #
#                it'll be a fun challenge!                             #
########################################################################

# Enable/Disable DEBUG mode
DEBUG = True

# Enable/Disable Player 2
P2 = True

# Import things I might need
from pygame_functions import *
import sys
from level import *
from player import *
from cmap import *
from network import Network
import pickle

# Allows us to use another folder than the folder this file is located
sys.path.insert(1, "./Sprites")

#---------------------------------#
##########--BEGIN CLASSES--##########
  
##########--END CLASSES--##########
#---------------------------------#
##########--BEING FUNCTIONS--######
def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])

def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])
##########--END FUNCTIONS--########
#---------------------------------#
##########-Begin Main Code-########

# Load Level Data
levelchunk1 = []

# This recreates the collision map automatically
cmap = CMap("Cmap/1-1.cmap")
cmap.create_cmap("Levels/1-1.lvl")
level = Level("Levels/1-1.lvl")

# Define some constants
BLACK = (0, 0, 0)
WHITE  = (255, 255, 255)

# Setup the screen and other display stuff
# Note: WIDTH & HEIGHT are imported from player.py!
screen = screenSize(WIDTH, HEIGHT, None, None, False)

# Frame handler (used for any sprite animation)
frame = 0
superFrame = 0
nextFrame = clock()
n = Network()
# Create a player
mario = Player("Sprites/Mario/")
mm = player_movement()

if P2: #Experimental 
    luigi = Player("Sprites/Luigi/", [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT]\
                   , 1, 15, 100, 10, 20)
    lm = player_movement()
    players = [mario, luigi]
else:
    players = [mario]
# Load the Player's sprites
for player in players:
    # The powerup handler already creates the player sprite, so use this to initalize the players
    player.powerupHandler(0)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: sys.exit()
    mm.key = players[0].get_key()
    confirmed_controls = n.send(mm)
    players[0].keys = confirmed_controls[0].key
    players[1].keys = confirmed_controls[1].key

    if players[0].keys == []:
        players[0].keys = players[0].get_key()
    if players[1].keys == []:
        players[1].keys = players[0].keys

    for player in players:
        # Get player inputs
        # Turn inputs into movement
        player.RefineInput(player.keys, cmap, player.playerSprite, player.last_held_direction, frame, superFrame, level)

        # Calculate and update position
        player.calculatePosition()
        updated_position = player.check_collision(cmap)
        player.x = updated_position[0]
        player.y = updated_position[1]
        player.x_velocity = updated_position[2]
        player.y_velocity = updated_position[3]

        player.death()
        # Check for death

        # Debug
        if (DEBUG):
            if player.keys[pygame.K_0]:
                mario.powerupHandler(0)
                luigi.powerupHandler(0)

            if player.keys[pygame.K_1]:
                mario.powerupHandler(1)
                luigi.powerupHandler(1)
        
    # Limit the framerate to 60 FPS
    tick(60)

    #Render the screen
    screen.fill(WHITE)
    for tile in level.tiles:
        for w in range(int(tile.width / 16)):
            for h in range(int(tile.height / 16)):
                screen.blit(pygame.image.load(tile.tile_image), [tile.x + (w * 16), tile.y - (h * 16)])

    # Update the player's sprite location
    for player in players:
        moveSprite(player.playerSprite, player.x + player.draw_width, player.y + player.draw_height)

    updateDisplay()
    # Limits the frame rate of sprites (60 FPS walk cycle is bad)
    if clock() > nextFrame:
        frame = (frame+1)%2
        superFrame = (superFrame+1)%3
        nextFrame += 60
