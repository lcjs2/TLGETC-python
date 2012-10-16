
########   constants    ########

import pygame

pygame.init()

#Global Constants:
BLACK=(0, 0, 0)
WHITE=(255, 255, 255)

#drawBoard Constants
boardColour = (230,200,130)
panelColour = (180,180,180)
boardWidth=600
panelWidth=200
margin=50

font = pygame.font.Font(pygame.font.match_font('couriernew',  'timesnewroman',  'arial'), 14)
fontSmall = pygame.font.Font(pygame.font.match_font('couriernew',  'timesnewroman',  'arial'), 10)

DISPLAYSURF = pygame.display.set_mode((boardWidth+panelWidth, boardWidth))
pygame.display.set_caption('The Little Go Engine That Could')


