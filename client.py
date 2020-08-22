########################################################################
#   Author: Nolan Y. / bbomb64 / Christopher D.                        #                                                                      #
#   Description: My goal is to recreate the New Super Mario Bros.      #
#                DS gamemode Mario vs Luigi. Even if it's not perfect, #
#                it'll be a fun challenge!                             #
########################################################################

##########--Begin System Level Stuff--##########

# Import things I might need
import os
from raylibpy import *
from level import *
from player import *
from cmap import *

# Get the program's directory (used for relative pathing)
dirname = os.path.dirname(__file__)

##########--End System Level Stuff--##########


#---------------------------------#


##########--BEGIN CLASSES--##########
class Camerat(object):
    def __init__(self):
        # Sets the camera position to player 0, originally planned to use a tuple for x and y but abandoned that
        self.camera = game.players[0].position[0]
        # Moving frames are used to control View position
        self.moving_frames = 0

        # Need to add y movement

    # Moves the View box (camera) around a player
    def move_view(self,player):
        # Defines when to stop adding onto the moving frames
        if self.moving_frames > 14:
            self.moving_frames = 14
        if self.moving_frames < -26:
            self.moving_frames = -26

        if self.moving_frames == 0:
            # Sets the camera to the middle of the screen
            tempX, tempY = player.position
            self.camera = tempX - 112
        else:
            # Moves the camera with the player
            tempX, tempY = player.position
            self.camera = tempX - 112 + (2 * self.moving_frames)

        # Defines the boundaries of how far the camera can go from the player, with the center being - 112
        if self.camera > player.position[0] - 84:
            self.camera = player.position[0] - 84
        elif self.camera < player.position[0] - 246:
            self.camera = player.position[0] - 246


class Game(object):
    def __init__(self):
        self.players = []

    def gameIntro(self):
        screen_width = 800
        screen_height = 450

        init_window(screen_width, screen_height, "MvsL Recoded - Title Screen")

        intro = True

        while intro:
            begin_drawing()
            clear_background(RAYWHITE)
            draw_text('Press "A" to start!', 200, 200, 20, LIGHTGRAY)
            end_drawing()

            if is_key_down(KEY_A):
                intro = False
            
            # Run the game if the title screen is cleared
            if intro == False:
                close_window()
                self.gameLoop()

    def gameLoop(self):

        # Setup the screen and other display stuff
        screen_width = 256
        screen_height = 192
        init_window(screen_width, screen_height, "MvsL Recoded - In Game")

        inGame = True

        # This creates the collision map and the camera collision map from the level file automatically
        #TODO: Fix relative path for 1-1.lvl file (to run, you'll need the entire file path)
        cmap = CMap(dirname + "Cmap/1-1.cmap")
        cmap.create_cmap(dirname + "/Levels/1-1.lvl")
        cmap.create_camera_map(dirname + "/Levels/1-1.lvl")
        level = Level(dirname + "/Levels/1-1.lvl")

        # Frame handler (used for any sprite animation)
        frame = 0
        superFrame = 0
        nextFrame = get_time()

        # Create a player
        mario = Player(dirname + "/Sprites/Mario/")

        if P2: #Experimental 
            luigi = Player(dirname + "/Sprites/Luigi/", [KEY_W, KEY_S, KEY_A, KEY_D, KEY_Q, KEY_LEFT_SHIFT]\
                        , 1, 10, 20)
            self.players = [mario, luigi]
        else:
            self.players = [mario]

        # Start up the camera
        old_x = self.players[0].position[0]
        View = Camerat()
        view = [View.camera,192,False,False]
        camera = Camera2D()
        camera.offset = Vector2(0, 0)
        camera.target = Vector2(mario.position[0] + 20, mario.position[1] + 20)
        camera.rotation = 0.0
        camera.zoom = 1.0

        print(camera.__class__, Camera2D.__class__)

        # Load the Player's sprites
        for player in self.players:
            # The powerup handler already creates the player sprite, so use this to initalize the players
            player.powerupHandler(0)

        while inGame:

            # Create bounding box for the player sprites
            for player in self.players:
                player.frame_rec = Rectangle(0.0, 0.0, player.playerSprite.width/10, player.playerSprite.height)

            # Get player inputs
            for player in self.players:
                # Turn inputs into movement
                player.RefineInput(cmap, player.playerSprite, player.last_held_direction, frame, superFrame, level)        
            
                # Calculate and update player position
                player.calculatePosition(10, cmap)
                updated_position = player.check_collision(cmap)
                player.position = (updated_position[0], updated_position[1])
                player.velocity = (updated_position[2], updated_position[3])

                # Check for death
                player.death()

            # Debug
                if (DEBUG):
                    # Make the Bros. Small
                    if is_key_down(KEY_ZERO):
                        mario.powerupHandler(0)
                        luigi.powerupHandler(0)

                    # Make both Bros. Super
                    if is_key_down(KEY_ONE):
                        mario.powerupHandler(1)
                        luigi.powerupHandler(1)
                    
                    # Make Mario Fire Mario
                    if is_key_down(KEY_TWO):
                        mario.powerupHandler(2)

                    # Return to the title screen
                    if is_key_down(KEY_NINE):
                        self.clearGame()

            # Detect if player moved
            if round(self.players[0].position[0]) > old_x:
                # If player moved to the right, try to move the View a bit
                View.moving_frames += .5
            elif round(self.players[0].position[0]) < old_x:
                # If player moved to the left, try to move the View a bit
                View.moving_frames -= .5

            # Used to detect a change in x between each frame to control View
            old_x = round(self.players[0].position[0])
            # Store the old camera view position to use in camera movement
            old_view = View.camera
            # Update the View to check if it is ok later
            View.move_view(self.players[0])
            # Prevents the camera from going too far left, which breaks everything I have done
            if View.camera <= 16:
                # "34" is a placeholder variable until I add Camera movement on the "Y" axis
                view = [16, 34, True,True]
            elif cmap.check_camera_box(round(old_view), 192, 256,
                                       192) == 1:
                # Set to True to prevent any unnecessary camera safe position checks, which causes massive lag
                view[2] = True
                view[3] = True
            else:
                # Set to False to prevent any unnecessary camera safe position checks, which causes massive lag
                view[2] = False
                view[3] = False
                # If the camera hasnt been set to a safe position, set it to a safe position
            if view[2] == False:
                view = cmap.nearest_good_x_camera_pos(round(old_view), 192, 256, 192)

            #Update the camera


            # Limit the framerate to 60 FPS
            set_target_fps(60)

            #Render the screen
            begin_drawing()
            begin_mode2d(camera)
            clear_background(RAYWHITE)

            for tile in level.tiles:
                for w in range(int((tile.width) / 16)):
                    for h in range(int(tile.height / 16)):
                        # (Image to load, [(left coord of tile * width) - View, (bottom coord of tile - height)])
                        draw_texture(tile.tile_image, tile.x + (w * 16)- view[0], tile.y + (h * 16), RAYWHITE)


            # Update the player's sprite location
            for player in self.players:
                #(Player Sprite, (player x + width offset - View), (player y + height offset))
                tempX = player.position[0] - view[0]
                tempY = player.position[1]

                tempX += player.draw_width
                tempY += player.draw_height

                tempPosition = Vector2(tempX, tempY)

                draw_texture_rec(player.playerSprite, player.frame_rec, tempPosition, RAYWHITE)
            end_mode2d()
            end_drawing()

            # Limits the frame rate of sprites (60 FPS walk cycle is bad)
            if get_time() > nextFrame:
                frame = (frame+1)%2
                superFrame = (superFrame+1)%3
                nextFrame += 60

    def clearGame(self):
        # Remove all player sprites 
        for player in self.players:
            unload_texture(player.playerSprite)
        # Remove all players from the player list
        self.players.clear()

        # Load the title screen
        self.gameIntro()

##########--END CLASSES--##########


#---------------------------------#


##########--BEGIN FUNCTIONS--######


##########--END FUNCTIONS--########


#---------------------------------#


##########-Begin Main Code-########

# Enable/Disable DEBUG mode
DEBUG = True

# Enable/Disable Player 2
P2 = True

# Define some constants
BLACK = (0, 0, 0)
WHITE  = (255, 255, 255)


# Initialize the game to the title screen

game = Game()

game.gameIntro()

###########-End Main Code-#########