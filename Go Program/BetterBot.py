import random
from drawBoard import * #for debugging - can get human move and debugDraw
from BetterBot_capturing import *



class BetterBot(object):
    def __init__(self):
        self.teams=[] #list of teams; ith entry is a team containing group i 
        self.connections=set() #connections between two groups. One for every pair of groups.
        self.interestingTeams=set() #Used for limiting the updating - basically all teams involving game.interestingGroups
        self.oldGameState=0
    
    def getName(self):
        return 'BetterBot'
    
    def getMove(self, game):
        if len(game.history)<=1:
            self.oldGameState = copy.deepcopy(game)
            self.updateConnectionsAndTeams(game)
        else:
            self.oldGameState.makeMove(game.history[len(game.history)-2][0], game.history[len(game.history)-2][1])
            self.updateConnectionsAndTeams(self.oldGameState)
            self.updateConnectionsAndTeams(game)
            self.oldGameState = copy.deepcopy(game)
            
        possibleMoves=set()#each elt is a tuple of: [move tuple; value; explanatory string for testing] (must be tuple, since list is not hashable so can't have set of lists)
        
        listOfTeams=self.setOfTeams(game)
        #generate moves that give teams space or take away space
        for team in listOfTeams:
            if team.colour==game.move: #if unsettled friendly team:
                a=self.possibleChangeInSpace(game,  team)
                if team.status==2:
                    for x in a:
                        possibleMoves.add((x[0], int((x[1]*3)/2),  str(int((x[1]*3)/2))+' for '+ x[2]+' (unsettled)'))
                else:
                    for x in a:
                        possibleMoves.add((x[0], x[1],  str(x[1])+' for '+ x[2]))
        
        #Begin loop through all moves
        for i in range(game.boardSize):
            for j in range(game.boardSize):
                
                if game.isLegalMove(i, j): #add points for not being too low
                    if i==2 or i==3 or i==game.boardSize-3 or i==game.boardSize-4:
                        possibleMoves.add(((i, j), 100, '100 for being in column 3 or 4'))
                    if j==2 or j==3 or j==game.boardSize-3 or j==game.boardSize-4:
                        possibleMoves.add(((i, j), 100, '100 for being in row 3 or 4'))
                    if (i>=1 and i<=game.boardSize-2) and (j>=1 and j<=game.boardSize-2):
                        possibleMoves.add(((i, j), 100, '100 for not first line'))
                
                    #Shape bonuses
                    if len(game.pattern3x3([[-1, 17, 17], [17, -1, 1], [17, 1, 1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), -10000, '-10000 for filling in eye'))
                    
                    if len(game.pattern3x3([[-1, 18, -1], [18, -1, 18], [-1, 18, -1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), -5000, '-5000 for self-atari'))
                
                    if len(game.pattern3x3([[-1, 1, -1], [2, -1,2], [-1, 1, -1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), 1500, '1500 for connecting through'))
                
                    if len(game.pattern3x3([[-1, 1, -1], [2, -1,2], [-3, -2, -1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), 1000, '1000 for pushing through'))
                    
                    if len(game.pattern5x5([[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -3, -1], [-1, 1, 2, 4, 2], [-1, -1, 1, 2, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 1000, '1000 for loss-free atari'))
                
                    if len(game.pattern5x5([[-1, -1, -1, -1, -1], [-1, -1, -2, -1, -1], [-1, 1, -1, -2, 16], [-1, 2, 1, -1, 16], [-1, -1, 2, -1, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 3000, '3000 for edge capture'))
                    
                    if len(game.pattern5x5([[-1, -1, -1, -1, -1], [-1, 4, 4, -1, -1], [2, 1, -1, -19, -1], [-1, 2, 4, -1, -1], [-1, -1, -1, -1, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 2000, '2000 for extend-from-hane'))
                    
                    if len(game.pattern3x3([[2, -2, -2], [-2, -1,-2], [-2, -2, -2]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), -4000, '-4000 for unsupported shoulder hit'))
                    
                    if len(game.pattern5x5([[-1, -1, -2, -1, -1], [2, 1, -2, -2, 16], [-2, 2, -1, -2, 16], [-1, -1, -2, -1, -1], [-1, -1, -1, -1, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), -7000, '-7000 for stupid 2nd line hane'))
                    
                    if len(game.pattern5x5([[-1, 4,4,4, -1], [4, 4, 4, 4, 4], [4, 4, -1, 4, 4], [4, 4, 4, 4, 4], [-1, 4,4,4, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 6000, '6000 for playing in empty space'))
                    
                    if len(game.pattern5x5([[-1, -1,-1,-1, -1], [-1, -1, -2, -1, -1], [-1, -2, -1, -2, -1], [-1, -1, 2, 1, 2], [-1, -1,-1,2, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), -6000, '-10000 for playing next to atari stone'))
        
        #generate moves that kill teams
        
        #generate moves that play in empty space
        
        #generate moves that capture stones/save stones
        for group in range(game.noOfGroups):
            if game.groups[group].merged==False:
                if game.groups[group].colour==game.move:
                    for x in game.groups[group].toEscape:
                        if x!=(-1, -1):
                            possibleMoves.add((x, 2000*game.groups[group].length, str(2000*game.groups[group].length)+' for saving group '+str(group)))
                else: #if enemy group
                    if (-1, -1) not in game.groups[group].toCapture:
                        for x in game.groups[group].toCapture:
                            possibleMoves.add((x, 2000*game.groups[group].length,  str(2000*game.groups[group].length)+' for capturing group '+str(group)))


        #Amalgamate possible move reasons
        amalgamatedMoves=[]
        while len(possibleMoves)>0:
            x = possibleMoves.pop()
            put=False
            for y in amalgamatedMoves:
                if x[0]==y[0]:
                    y[1]+=x[1]
                    y[2]+=', '+x[2]

                    put=True
            if put==False:
                amalgamatedMoves.append(list(x))
        
        
        #Pick randomly from moves with highest value
        amalgamatedMoves.sort(key=getPMValue)
        for x in amalgamatedMoves:
            if x[1]>=1000:
                print('Move ', x[0], '=', x[1], ': ', x[2])
        
        if len(amalgamatedMoves)==0:
            print('random move!')
            (i, j)=(-10, -10)
            while (game.isLegalMove(i, j))==False:
                (i, j)=(random.randrange(game.boardSize), random.randrange(game.boardSize))
                return (i, j)
        return amalgamatedMoves[len(amalgamatedMoves)-1][0]
    
 
    def recalculateControl(self, game, team): #Determine which points are controlled exclusively by team
        #sets team.controlledPoints to be the set of points undoubtably controlled by the team
        nearbyPoints=set()
        impassablePoints=set()
        taggedImpassables=set()
        colour=team.colour
        for group in team.groups:
            for (i, j) in game.groups[group].stones:
                nearbyPoints|=game.libertiesInEuclideanRadius(i, j, 4)
                impassablePoints|=game.pointsInTaxicabRadius(i, j, 1)
                taggedImpassables.add((i, j))
        
        enemyPoints=set()
        justAddedEnemyPoints=set()
        
        for a in range(team.left-4,  team.right+4+1):
            for b in range(team.top-4,  team.bottom+4+1):
                if game.isOnBoard(a, b) and game.board[a][b]>=0 and game.groups[game.board[a][b]].colour!=colour and ((-1, -1) not in game.groups[game.board[a][b]].toCapture):
                    justAddedEnemyPoints.add((a, b)) #add living enemy stones to justAddedEnemyStones
        
        for k in range(5):
            enemyPoints|=justAddedEnemyPoints
            newEnemyPoints=set()
            for (a, b) in justAddedEnemyPoints:
                for (c, d) in game.libertiesInTaxicabRadius(a, b, 1):
                    newEnemyPoints.add((c, d))
            newEnemyPoints-=enemyPoints
            taggedImpassables|=newEnemyPoints&impassablePoints
            newEnemyPoints-=impassablePoints
            justAddedEnemyPoints=newEnemyPoints
        enemyPoints|=justAddedEnemyPoints
        
        nearbyPoints-=enemyPoints
        nearbyPoints-=taggedImpassables
    
        team.controlledPoints = nearbyPoints


    
    
    def updateConnectionsAndTeams(self,  game): #creates and recalculates all connections, then call recalculateTeams
        #move is location of last played move
        
        #Update toCapture moves of all interesting groups
        for group in game.interestingGroups:
            game.groups[group].toCapture=capturingMoves(game,  group)
            #Then update toEscape moves for all interesting groups under threat
            if len(game.groups[group].toCapture)>0 and ((-1, -1) not in game.groups[group].toCapture):
                game.groups[group].toEscape=canEscapeIn(game,  group,  searchDepth,  True)
            else:
                game.groups[group].toEscape=set()
        
        #strip out connections involving at least one interestingGroup; remake those connections
        #also remove connections between merged groups.
        toRemove=set()
        for connection in self.connections:
                
            if (connection.group1 in game.justMergedGroups) or (connection.group2 in game.justMergedGroups) or (connection.group1 in game.interestingGroups) or (connection.group2 in game.interestingGroups) or (game.groups[connection.group1].merged==True) or (game.groups[connection.group2].merged==True):
                toRemove.add(connection)
        self.connections-=toRemove
        
        for group1 in range(game.noOfGroups):  #group1<group2?
            for group2 in range(game.noOfGroups):
                if group1 >= group2 or ((group1 not in game.interestingGroups) and (group2 not in game.interestingGroups)):
                    continue
                 
                if game.groups[group1].merged==False and game.groups[group2].merged==False and game.groups[group1].colour==game.groups[group2].colour:
                    x=connectionObj(group1,  group2,  game)
                    self.connections.add(x)
                    self.recalculateConnection(game, x)
                    
        
        self.interestingTeams=set()
        self.recalculateTeams(game)#now merge connected groups into teams
        
        for team in self.setOfTeams(game): #then recalculate life/death status of teams
            self.recalculateControl(game,  team)
            self.recalculateTeamStatus(game, team)
        
  
    def recalculateConnection(self, game,  connection): #recalculates the status of single connection 
        #ignore too far away
        a = max([game.groups[connection.group1].left - game.groups[connection.group2].right,game.groups[connection.group2].left - game.groups[connection.group1].right,  0])
        b= max([game.groups[connection.group1].top - game.groups[connection.group2].bottom,game.groups[connection.group2].top - game.groups[connection.group1].bottom,  0])
        if a+b>=9: #this just rules out large knight's move and two-space jump
            connection.status=0
            return
    
        libs1=set(game.touchingLiberties(connection.group1))
        libs2=set(game.touchingLiberties(connection.group2))
        sharedLibs=libs1&libs2
        touchingGroups1=set(game.touchingGroups(connection.group1))
        touchingGroups2=set(game.touchingGroups(connection.group2))
        cuttingGroups=touchingGroups1&touchingGroups2
        connection.halfConnections=set() #contains shared liberties and one stone from each capturable cutting groups
        connection.fullConnections=set()
        connection.toCut=set()
        connection.toConnect=set()
        
        for x in sharedLibs: #add a half connection for each shared liberty, unless opponent can't play there
            if isCapturable(game,  x[0],  x[1],  otherColour(connection.colour)):
                connection.fullConnections.add(x)
            else:
                connection.halfConnections.add(x)
        if len(connection.fullConnections)==0 and len(connection.halfConnections)<=1: #if necessary...
            for x in cuttingGroups: #...add half connection for capturable group, and... IMPLEMENT: full connection for dead group as long as it has fewer liberties 
                if (-1, -1) in game.groups[x].toCapture:
                    connection.fullConnections.add(game.groups[x].stones[0]) #add full connection for dead cutting stone
                elif len(game.groups[x].toCapture)>0:
                        connection.halfConnections.add(game.groups[x].stones[0]) #add a random stone from the group to halfconnections
            
        if len(connection.fullConnections)==0 and len(connection.halfConnections)==1: #If still no connection, look deeper
            (i, j)=connection.halfConnections.pop()
            if len(game.pattern3x3([[-1, 4, -1], [1, -1, 1], [-3, 4, -3]], i, j, connection.colour, {1, -1, 2, -2}, True))>0:
                connection.fullConnections.add((i, j)) #one-point jump, no peep, counts as full connection
            a=game.pattern3x3([[-1, 2, -1], [1, -1, 1], [-1, 4, -1]], i, j, connection.colour, {1, -1, 2, -2}, True)
            if len(a)==1: #one point jump with peep counts if both cutting points are individually capturable
                orientation=a.pop()
                gamecopy=copy.deepcopy(game)
                if gamecopy.move==connection.colour:
                    gamecopy.makeMove(-1, -1)
                gamecopy.makeMove(i, j)
                (x, y)=game.patternCoordinates(i, j, 1, 0, orientation)
                if gamecopy.isLegalMove(x, y):
                    gamecopy.makeMove(x, y)
                    (x_1, y_1)=gamecopy.patternCoordinates(i, j, 1, -1, orientation)
                    (x_2, y_2)=gamecopy.patternCoordinates(i, j, 1, -1, orientation)
                    if isCapturable(gamecopy, x_1, y_1, gamecopy.move) and isCapturable(gamecopy, x_2, y_2, gamecopy.move):
                        connection.fullConnections.add((i, j))
            
        if len(connection.fullConnections)==0 and len(connection.halfConnections)==0: #look for knight's move
            for (i, j) in (set(game.touchingLiberties(connection.group1))&set(game.touchingLiberties(connection.group2)))|(set(game.touchingLiberties(connection.group2))&set(game.touchingLiberties(connection.group1))):
                if len(game.pattern3x3([[-3, -3, -3], [1, -3, -3], [-3, -3, 1]], i, j, connection.colour))>0:
                    connection.fullConnections.add((i, j))
            
            
            
            
        #set status of connection
        if len(connection.halfConnections)>=2 or len(connection.fullConnections)>=1: #at least two possible connections, or a full one, makes connected
            connection.status=1
        elif len(connection.halfConnections)==1: #exactly one possible connection move
            for y in connection.halfConnections:
                connection.toCut.add(y)
                connection.toConnect.add(y)
            #where else to look for connecting moves? IMPLEMENT once captureMoves is more useful            
            connection.status=2
        else:
            connection.status=0
    
   
    def recalculateTeams(self, game): # given connections, group into teams. Recalculate control
        self.teams=[] #list of teams: pointer to the team of group i at index i. Many duplicates
        #Only update teams involving a group from game.interestingGroups
        
        
        for group in range(game.noOfGroups):
            if game.groups[group].merged==False:
                self.teams.append(team(game, group)) 
                #make one new team for every existent group
            else:
                self.teams.append('No team here - merged')
        
        for x in self.connections: #merge teams according to connections.
            team1=self.teams[x.group1]
            team2=self.teams[x.group2]
            if x.status==1: #if connected
                mergedTeam=self.mergeTeams(team1,  team2)
                for y in range(len(self.teams)):
                    if self.teams[y]==team1 or self.teams[y]==team2:
                        self.teams[y]=mergedTeam
                        
 
    def mergeTeams(self,  team1,  team2): #returns the merged team (used in recalculateTeams
        if team1==team2:
            return team1        
        team1.groups|=team2.groups
        team1.left=min(team1.left,  team2.left)
        team1.right=max(team1.right,  team2.right)
        team1.top=min(team1.top,  team2.top)
        team1.bottom=max(team1.bottom,  team2.bottom)
        return team1

    
    
    def recalculateTeamStatus(self,  game,  team): #recalculate life/death status of team.
        if len(team.controlledPoints)>7: #only return 1 for definitely alive
            #print('Team ',  team.name,  ' alive,  controlling ', len(team.controlledPoints), ' points')
            team.status=1
            return
        
        for group in team.groups: #can't be that dead if lots of liberties (!)
            if len(game.touchingLiberties(group))>5:
                #print('Team ', team.name, ' unsettled - group ', group,  'many liberties')
                team.status=2
                return
            if (-1, -1) in game.groups[group].toCapture:
                #print('Team ', team.name, ' dead - group ', group, ' cannot be saved, so team is dead')
                team.status=0
                return
        
        #print('Team ', team.name, ' unsettled.')
        team.status=2
        return
    
    
    
    def possibleChangeInSpace(self,  game,  team): #generates moves which expand the eye space of team or shrink it
        
        oldControlledPoints=team.controlledPoints
        possibleMoves=set()
        profitableMoves=set()
        for group in team.groups:
            for (i, j) in game.groups[group].stones:
                possibleMoves|=game.libertiesInTaxicabRadius(i, j, 2)
        for (i, j) in possibleMoves:        
            if game.isLegalMove(i, j):
                gamecopy=copy.deepcopy(game)
                gamecopy.makeMove(i, j)
                team.groups.add(gamecopy.noOfGroups-1)
                self.recalculateControl(gamecopy, team) 
                newControlledPoints=len(team.controlledPoints)
                team.groups.remove(gamecopy.noOfGroups-1)
                team.controlledPoints=oldControlledPoints
                profit=newControlledPoints-len(oldControlledPoints)
                if team.colour==game.move:
                    word='extra'
                else:
                    profit=-profit
                    word = 'less'
                if profit>0:
                    profitableMoves.add(((i, j), 1000*profit,  str(profit)+' '+word+' territory for team '+team.name))
            
        return profitableMoves
    
    
    
    
    def possibleConnections(self,  game,  team1,  team2):
        pass
    
    
    
    
    
    def setOfTeams(self, game): #returns duplicate-free set of team objects from game
        setTeams=set()
        for x in range(game.noOfGroups):
            if game.groups[x].merged==False:
                setTeams.add(self.teams[x])
        return setTeams
    
    
    
    
    
    
    
    
    
    
    
    
    def debugDraw(self,  game): #Draw useful data onto board
        if game.noOfGroups<=1:
            return
       

#PRINT CAPTURABILITY OF ALL GROUPS
#        for x in range(game.noOfGroups):
#            if game.groups[x].merged==False:
#                capmoves=game.groups[x].toCapture
#                if len(capmoves)==0:
#                    print('Group ', x, ' not capturable.')
#                else:
#                    print('Group ', x, ' capturable by: ', capmoves )
#                    print('...and can be saved with ', game.groups[x].toEscape)

#DRAW ON CONTROL
        listOfTeams=self.setOfTeams(game)
        
        statuses=['D', 'A', 'U']
        for x in listOfTeams:
            if x.status!=0:
                for (i, j) in x.controlledPoints:
                    pygame.draw.circle(DISPLAYSURF,x.colour,coordinates(i, j),10)
                    makeText(x.name, otherColour(x.colour), x.colour, coordinates(i,j)[0], coordinates(i,j)[1]-1, True)
            for group in x.groups:
                for stone in game.groups[group].stones:
                    if group in game.interestingGroups:
                        c='I'
                    else:
                        c='/'
                    makeText(x.name+c+statuses[x.status], otherColour(x.colour), x.colour, coordinates(stone[0],stone[1])[0], coordinates(stone[0], stone[1])[1]+8, True)
        
       # game.pattern5x5([[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1]], 4,4, game.move, {-4, -3, -2, -1, 1, 2, 3, 4}, False, [-1, -1, -1, -1],  True)

#Pattern matching test
#        target=[[16, 16, 16], [-1, 4, -1], [3, -1, 3]]
#        for i in range(game.boardSize):
#            for j in range(game.boardSize):
#                result=game.pattern3x3(target, i, j, BLACK, {-4, -3, -2, -1, 1, 2, 3, 4}, True)
#                if len(result)>0:
#                    print('At ', (i, j), ': ',result )
        
class team(object): #set of groups connected together by connections
    def __init__(self, game, firstGroup):
        self.colour=game.groups[firstGroup].colour
        self.groups={firstGroup} #group numbers involved in the team
        self.status=2 #0=dead, 1=alive, 2=unsettled. When in doubt, return "unsettled"
        self.controlledPoints=set() #set of points controlled by this team
        self.left=min(game.groups[firstGroup].stones[i][0] for i in range(game.groups[firstGroup].length)) #leftmost coordinate in all stones in this team
        self.right=max(game.groups[firstGroup].stones[i][0] for i in range(game.groups[firstGroup].length))#rightmost coordinate
        self.top=min(game.groups[firstGroup].stones[0][1] for i in range(game.groups[firstGroup].length))#top (remember this is a low number)!
        self.bottom=max(game.groups[firstGroup].stones[0][1] for i in range(game.groups[firstGroup].length))#bottom (high number)
        self.name=random.choice([ 'b', 'c', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z'])    
    
    def __str__(self):
        returnString='Team with groups '
        returnString+=str(self.groups)
        return returnString



class connectionObj(object): #a connection between two groups
    def __init__(self,  group1,  group2,  game): 
        self.group1=group1
        self.group2=group2
        self.colour=game.groups[group1].colour
        assert group1<group2,  'Calling connection with group1 >= group2'
        self.halfConnections={}
        self.fullConnections={}
        self.status=0 #0=not connected, 1=connected, 2=unsettled
        self.toConnect={}#if cut, threatens to connect; if unsettled, connects (not implemented)
        self.toCut={} #if connected, threaten to cut; if unsettled, cuts (not implemented)

    

    def __str__(self):
        returnString='Groups '+str(self.group1)+' and '+str(self.group2)+' are '
        if self.status==2:
            returnString+='cut at '
            for x in self.toCut:
                returnString+=str(x)
            returnString+= ' and connected at '
            for x in self.toConnect:
                returnString+=str(x)
        if self.status==1:
            returnString+='connected: half connections at '
            for x in self.halfConnections:
                returnString+=str(x)
            returnString+='; full connections at '
            for x in self.fullConnections:
                returnString+=str(x)
        if self.status==0:
            returnString+='not connected'
        return returnString
 
 
 
#other
def condenseList(list1): #returns a list with duplicates removed
    list2=[]
    for item in list1:
        if item in list2:
            pass
        else:
            list2.append(item)
    return list2
    
def otherColour(colour):
    if colour==BLACK:
        return WHITE
    else:
        return BLACK
        
def getPMValue(tuple): #Used in getMove
    return tuple[1]

