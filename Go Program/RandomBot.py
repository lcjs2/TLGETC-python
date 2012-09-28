import random
class RandomBot(object):
    def __init__(self):
        pass
    
    def getName(self):
        return 'RandomBot v'+str(random.randrange(1, 10))+'.'+str(random.randrange(0, 10))
    
    def getMove(self,  game):
        possibles=[]
        for i in range(0,game.boardSize):
            for j in range(0,game.boardSize):
                if game.isLegalMove(i,j):
                    possibles.append((i,j))
        if len(possibles)==0:
            return (-1,-1) 
        
        return random.choice(possibles)
