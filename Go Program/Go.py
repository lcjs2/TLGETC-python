
########    Go.py    ########

#	main file

import pygame
import sys
import time
import random
import cProfile
from pygame.locals import *

#home made imports:
import gui
from gui import * 
from bots import *
from gameState import *

pygame.init()

def main():
    game=gameState()
    
    #set players
    players=[0, 0]
    players[0]=HumanBot()
    players[1]=HumanBot()

    
    #NB 14 characters is maximum name size
    game.blackName=players[0].getName()
    game.whiteName=players[1].getName()
    
    #draw game for first time
    gui.redraw(game,  players)
    #waitForKey()
    
    play(game, players)	
        
    gui.redraw(game,  players)
    print('Game Over')    
    waitForKey()
    sys.exit()


#Finally, run
if __name__=='__main__':
    #cProfile.run('main()')
    main()
