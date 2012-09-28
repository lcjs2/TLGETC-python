import copy
from BetterBot import *


 #GameState and capturing subroutines for BetterBot
searchDepth=4
 
def isCapturable(game,  i,  j,  colour): #Can a hypothetical move at i,j be captured? Returns True for illegal move
    gamecopy=copy.deepcopy(game)
    if gamecopy.move!=colour:
        gamecopy.makeMove(-1, -1,  True)
    if gamecopy.isLegalMove(i, j):
        gamecopy.makeMove(i, j,  True)
        capMoves = capturingMoves(gamecopy,  gamecopy.noOfGroups-1)
        if len(capMoves)>=1:
            return True
        else:
            return False
    else:
        return True
        
def capturingMoves(game,  group,  depth=searchDepth,  returnMoves=True): #returns list of moves that capture group with group number group. Call this one! Returns pass (only!) if can't escape.
    #Ladders are read out to the end, but depth determines how deep we search if we're not just reading atari. A depth of d aims to find anything which will remove the group
    #in d stones. We always return ladders, so effectively depth >= 2
    #returnMoves determines whether a full set of moves is returned, or just whether it's possible (allowing an early return)
    #Recursive calls from this function must pass depth-1!
    
    
    #assert game.groups[group].colour!=game.move,  'Calling capturingMoves to capture a group of my own colour! Group '+str(group)+' depth '+ str(depth) +' board '+str(game.board)
    #print(game.board)

    
    if game.groups[group].colour==game.move: #if target group is same colour as to move, insert pass
        gamecopy=copy.deepcopy(game)
        gamecopy.makeMove(-1, -1, True)
        game=gamecopy

    if returnMoves==True and canEscapeIn(game,  group,  depth-1)==False:
        return {(-1, -1)}
    
    capturingMoves=set()
    libs = game.touchingLiberties(group)
    if returnMoves==False and len(libs)==1:
        return True
    if len(libs)<=2:
        ladderMoves=isLadderable(game,  group,  returnMoves)
        if returnMoves==True and ladderMoves!=False:
            capturingMoves|=set(ladderMoves) #add whatever captures in a ladder (including capturing stones in atari)
        if returnMoves==False and ladderMoves==True:
            return True
    
    if depth==len(libs) and len(libs)>1: #don't bother if in atari - just return the capturing move
        movesToTry=libs
    if depth>len(libs) and len(libs)>1:
        movesToTry=possibleCapturingMoves(game,  group)
        
        for move in movesToTry:
            if game.isLegalMove(move[0], move[1]):
                gamecopy=copy.deepcopy(game)
                gamecopy.makeMove(move[0], move[1]) #Try that move, see if w can escape.
                if (move in libs) and (len(libs)==2): #ataris don't count as extra depth, because they have less branching
                    newdepth=depth-1
                else:
                    newdepth=depth-1
                if canEscapeIn(gamecopy,  group,  newdepth)==False:
                    if returnMoves==True:
                        capturingMoves.add(move)
                    else:
                        return True
    if returnMoves==False:
        assert len(capturingMoves)==0,  'In capturingMoves,  have returnMoves==False but capturingMoves list non-empty.'
        return False #if moves in capturingmoves list with this flag, should have returned there
    return capturingMoves

def canEscapeIn(game, group,  depth,  returnMoves=False): #returns set of escaping moves if group (to move) can survive (depth) more opponent stones
    #pass is only returned if liberties <=2 (seki, eye space filling) or if it has far too many liberties. Semeai will break here :(
    #print('Calling canEscapeIn,  ',  group,  ' depth ',  depth,  'board:')
    #print(game.board)
    if game.groups[group].liberties>depth: #obviously if it has too many liberties it will survive
        if returnMoves:
            return {(-1, -1)}
        else:
            return True
    
    if game.move!=game.groups[group].colour:
        gamecopy2=copy.deepcopy(game)
        gamecopy2.makeMove(-1, -1)
        game=gamecopy2
    
    movesToTry=possibleEscapingMoves(game,  group)
    escapingMoves=set()

    for move in movesToTry:  
        if game.isLegalMove(move[0], move[1]):
            gamecopy=copy.deepcopy(game)
            if move!=(-1, -1) and len(gamecopy.adjLiberties(move[0], move[1], [group]))>0: #if this escaping move merges with target group, change target group 
                newgroup=gamecopy.noOfGroups
            else:
                newgroup=group
            gamecopy.makeMove(move[0], move[1]) #Try that move, see if escaper can escape.
            a=capturingMoves(gamecopy,  newgroup,  depth, True) 
            if len(a)==0:
                if returnMoves:
                    escapingMoves|={move}
                else:
                    return True

    if returnMoves:
        return escapingMoves
    else:
        return False
    
def isLadderable(game,  group,  returnMoves=False): #returns True if group can be captured with constant ataris. Returns False if it can get more than two liberties.
    #returnMoves determines whether the successful liberties are returned, or just True/False (for recursion)
    
    #print('Calling isLadderable ',  group, '...')
    libs=game.touchingLiberties(group)
    assert len(libs)>0,  'Group '+str(group)+  ' has no liberties!'
    if len(libs)==1: #return immediately if target in atari
        if returnMoves==True:
            return libs
        else:
            return True
    if len(libs)>2:
        return False
    
    libs0legal=game.isLegalMove(libs[0][0],  libs[0][1])
    libs1legal=game.isLegalMove(libs[1][0],  libs[1][1])
    #print('...liberties ',  libs, '...')
    
    if libs0legal==False and libs1legal==False: #return false if neither liberty can be played
        #print('...returning False because neither is legal.')
        return False
    
    #Now we have exactly two liberties, possibly one illegal move. Possibly surrounding stones are in atari.
    touchingGroups=game.touchingGroups(group)    
    atariStones=0
    canCaptureHere=(-10, -10)
    for x in touchingGroups: #return False if atari-ing a group of two stones or longer, or two single stones
        if game.groups[x].liberties==1:
            if game.touchingLiberties(x)[0]==libs[0] or game.touchingLiberties(x)[0]==libs[1]:
                pass
            else:
                atariStones+=len(game.touchingStones(group,  x))
                canCaptureHere=game.touchingLiberties(x)[0]
    if atariStones>1: 
        #print('...returning False because more than two surrounding stones in atari.')
        return False

    atariFailsAfter0 = True #must declare them here; if nothing in atari, then they just stay as true
    atariFailsAfter1 = True
    if atariStones==1: #first, if escaper answers atari by capturing the one stone

        #print('...surrounding stone at ',  canCaptureHere, ' is in atari...')
        if libs0legal==True:
            gamecopy=copy.deepcopy(game)
            gamecopy.makeMove(libs[0][0],  libs[0][1]) #play liberty 0
            if gamecopy.isLegalMove(canCaptureHere[0],  canCaptureHere[1]):
                if group in gamecopy.adjGroups(canCaptureHere[0],  canCaptureHere[1]):
                    newGroupNumber=gamecopy.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy.makeMove(canCaptureHere[0],  canCaptureHere[1]) #gamecopy has lib 0 played, stone captured.
                atariFailsAfter0= isLadderable(gamecopy,  newGroupNumber) #if false, then can escape move 0 by capturing
            #print('...atariFailsAfter0: ', atariFailsAfter0, '...')
        if libs1legal==True:
            gamecopy=copy.deepcopy(game)
            gamecopy.makeMove(libs[1][0],  libs[1][1]) #play liberty 1
            if gamecopy.isLegalMove(canCaptureHere[0],  canCaptureHere[1]):
                if group in gamecopy.adjGroups(canCaptureHere[0],  canCaptureHere[1]):
                    newGroupNumber=gamecopy.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy.makeMove(canCaptureHere[0],  canCaptureHere[1]) #gamecopy has lib 1 played, stone captured.
                atariFailsAfter1= isLadderable(gamecopy,  newGroupNumber)
                #print('...atariFailsAfter1: ', atariFailsAfter1, '...')
        if (atariFailsAfter0==False or libs0legal==False) and (atariFailsAfter1==False or libs1legal==False): #if both libs are either illegal or fail after the capture
            #print('...returning False for ',  group, ' because capturing will escape.')
            return False
    
    
    
    #At this point we have exactly two liberties. Capturer is playing one, possibly self-atari. Escaper can't escape by capturing, so must either take the other or capture
    move0captures=False
    move1captures=False
    if libs0legal==True: #SAME CODE TWICE
        gamecopy=copy.deepcopy(game)
        gamecopy.makeMove(libs[0][0],  libs[0][1]) #make move 0
        libsOfCapturer=gamecopy.touchingLiberties(gamecopy.noOfGroups-1)
        capturingEscapes=False
        otherLibEscapes=False
        if len(libsOfCapturer)==1: #if playing that liberty was self-atari...
            gamecopy2 = copy.deepcopy(gamecopy)
            if gamecopy2.isLegalMove(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                if group in gamecopy2.adjGroups(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                    newGroupNumber=gamecopy2.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy2.makeMove(libsOfCapturer[0][0],  libsOfCapturer[0][1]) #...capture it and see if the result is ladderable
                capturingEscapes=not isLadderable(gamecopy2, newGroupNumber)
        if gamecopy.isLegalMove(libs[1][0],  libs[1][1]): #otherwise, escaper must play other liberty if possible, and see if that escapes
            gamecopy.makeMove(libs[1][0],  libs[1][1])
            otherLibEscapes=not isLadderable(gamecopy,  gamecopy.noOfGroups-1)
        if capturingEscapes==False and otherLibEscapes==False:
            move0captures=True
    if libs1legal==True and (move0captures==False or returnMoves==True): #SAME CODE TWICE
        gamecopy=copy.deepcopy(game)
        gamecopy.makeMove(libs[1][0],  libs[1][1]) #make move 1
        libsOfCapturer=gamecopy.touchingLiberties(gamecopy.noOfGroups-1)
        capturingEscapes=False
        otherLibEscapes=False
        if len(libsOfCapturer)==1:
            gamecopy2 = copy.deepcopy(gamecopy)
            if gamecopy2.isLegalMove(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                if group in gamecopy2.adjGroups(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                    newGroupNumber=gamecopy2.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy2.makeMove(libsOfCapturer[0][0],  libsOfCapturer[0][1])
                capturingEscapes=not isLadderable(gamecopy2,  newGroupNumber)
        if gamecopy.isLegalMove(libs[0][0],  libs[0][1]):
            gamecopy.makeMove(libs[0][0],  libs[0][1])
            otherLibEscapes=not isLadderable(gamecopy,  gamecopy.noOfGroups-1)
        if capturingEscapes==False and otherLibEscapes==False:
            move1captures=True
    #print('... returning ',  move0captures or move1captures, ' for ',  group, ' because move0captures ',  move0captures, ' and (if false) move1captures ',  move1captures)
    if returnMoves:
        moves=[]
        if (move0captures ==True and atariFailsAfter0==True and libs0legal):
            moves.append(libs[0])
        if (move1captures ==True and atariFailsAfter1==True and libs1legal):
            moves.append(libs[1])
        if moves==[]:
            return False
        else:
            return moves
    else:
        return move0captures or move1captures

def possibleCapturingMoves(game,  group): #returns moves that might capture group, including liberties. Put most promising first
    assert game.move!=game.groups[group].colour,  'Called capturingMoves with mismatched colours'
    possibles=[]
    for surroundingGroup in game.touchingGroups(group): #append connecting own stones in atari
        if game.groups[surroundingGroup].liberties==1:
            lib=game.touchingLiberties(surroundingGroup)[0]
            if game.isLegalMove(lib[0], lib[1]):
                possibles.append(lib)
    for x in game.touchingLiberties(group): #append removing a liberty
        if game.isLegalMove(x[0], x[1]):
            possibles.append(x)
    for x in game.diagTouchingLiberties(group): #append diagonal net-like moves
        if game.isLegalMove(x[0], x[1]):
            possibles.append(x)
    
    return condenseList(possibles)

def possibleEscapingMoves(game,  group): #returns possible moves to escape, most promising first, including liberties.
    assert game.move==game.groups[group].colour,  'Called escapingMoves with mismatched colours'
    possibles=[]
    for surroundingGroup in game.touchingGroups(group): #append atari or capture of surrounding stones. Only one of these so leave it at the front
        if game.groups[surroundingGroup].liberties<=2: #IMPLEMENT add all possible capturing moves if surrounding group has fewer or equal number of liberties.
            for lib in game.touchingLiberties(surroundingGroup):
                if game.isLegalMove(lib[0], lib[1]):
                    possibles.append(lib)
    libIncreasingPossibles=[]
    for x in game.touchingLiberties(group):
        if game.isLegalMove(x[0], x[1]):
            libIncreasingPossibles.append(x)
    libIncreasingPossibles.sort(key=game.lenResultingLibertiesFromTuple,  reverse=True)
    possibles.extend(libIncreasingPossibles)
    
    if game.groups[group].liberties>1: #only return diagonal moves if more than one liberty
        for x in game.diagTouchingLiberties(group):
            if game.isLegalMove(x[0], x[1]):
                possibles.append(x)
    return condenseList(possibles)
    
    if game.groups[group].liberties<=2: #put pass in last, and only if 2 or fewer liberties
        possibles.append((-1, -1))
