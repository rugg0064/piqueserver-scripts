from piqueserver.config import config
from piqueserver.commands import command, admin, player_only, target_player
from piqueserver import map
from pyspades.common import Vertex3
from pyspades.world import Grenade
from pyspades import contained as loaders
from math import ceil, sqrt, pi, sin, cos, exp
from random import random
from time import time

nukeErrorMessage = "Invalid Input, provide coordinate (eg: C3) and region (eg: NE for northeast)"

sectionConfig = config.section('nuke')
radius = sectionConfig.option('explosionRadius', default = 10).get()
maximumRadius = sectionConfig.option('maximumExplosionRadius', default = 50).get()
fallOff = sectionConfig.option('fallOff', default = 0.0025).get() #Used in the mathematical expression for making a curve for how far the blast should go
propogationTime = sectionConfig.option('propogationTime', default = 2.5).get()
upHeight = sectionConfig.option('upHeight', default = 8).get()
downHeight = sectionConfig.option('downHeight', default = 2).get()
grenadeAmount = sectionConfig.option('grenadeAmount', default = 400).get()
teamSuccessCD = sectionConfig.option('teamSuccessCooldown', default = 30).get()
playerSuccessCD = sectionConfig.option('playerSuccessCooldown', default = 30).get()
teamCD = sectionConfig.option('teamCooldown', default = 5).get()
playerCD = sectionConfig.option('playerCooldown', default = 5).get()

friendly_fire = config.option('friendly_fire', default = True).get()

@command('nukes')
@target_player
@player_only
def nukes(connection, player):
    connection.send_chat("%s has %d nukes." %(player.name, player.nukesAvailable))
@admin
@command('givenuke', 'gn')
@target_player
def givenuke(connection, player):
    """
    Gives a nuke to target player
    /givenuke *<player>*
    """
    player.nukesAvailable = player.nukesAvailable+1
    try:
        connection.send_chat_notice("You have given %s a nuke." %player.name)
    except AttributeError as ex:
        print("%s has been given a nuke, but there was a %s error" %(player.name, type(ex)))
    player.send_chat_notice("%s has given you a nuke." %connection.name)

@command('nuke', 'n')
@player_only
def nuke(connection, *args):
    """
    Drops a devastating nuke that destroys building and kills many people
    /nuke <Coordinate> *<Region>*
    """
    if(connection.nukesAvailable>0):
        if(len(args)>=1):
            if(len(args[0])==2):
                horizontal = ord(args[0][0].lower())-97
                aimPosX = (horizontal*64) + 32
                vertical = ord(args[0][1]) - 49
                aimPosY = (vertical*64) + 32
                accuracy = 32
                if(horizontal in range(0,9) and vertical in range(0,9)): 
                    if(len(args)==2):
                        if(len(args[1])>=1):
                            input = args[1].lower()
                            if(args[1][0].lower() in "neswc"):
                                accuracy=16
                                input = args[1][0].lower()
                                if(input=="n"):
                                    aimPosY-=16
                                elif(input=="s"):
                                    aimPosY+=16
                                elif(input=="e") and len(args[1])==1:
                                    aimPosX+=16
                                elif(input=="w" and len(args[1])==1):
                                    aimPosX-=16
                                if(len(args[1])==2):
                                    input = args[1][1].lower()
                                    if(input in "ew"):
                                        if(input=="e"):
                                            aimPosX+=16
                                        elif(input=="w"):
                                            aimPosX-=16
                                        verticalDirection = ["north", "south"]["ns".find(args[1][0].lower())]
                                        horizontalDirection = ["east", "west"]["ew".find(args[1][1].lower())]
                                        connection.send_chat_notice("Nuking %s%s of %s%s" %(verticalDirection, horizontalDirection, chr(horizontal + 97).upper(), str(vertical+1)))
                                    else:
                                        #error
                                        connection.send_chat_error(nukeErrorMessage)
                                        return
                                else:
                                    direction = ["north", "east", "south", "west", "center"]["neswc".find(args[1][0].lower())]
                                    connection.send_chat_notice("Nuking %s of %s%s" %(direction, chr(horizontal + 97).upper(), str(vertical+1)))
                            else:
                                #error
                                connection.send_chat_error(nukeErrorMessage)
                                return
                        else:
                            #error
                            connection.send_chat_error(nukeErrorMessage)
                            return
                    else:
                        connection.send_chat_notice("Nuking coordinate %s%s" %(chr(horizontal + 97).upper(), str(vertical+1)))
                else:
                    #error
                    connection.send_chat_error(nukeErrorMessage)
                    return
            else:
                #error
                connection.send_chat_error(nukeErrorMessage)
                return
        else:
            #error
            connection.send_chat_error(nukeErrorMessage)
            return
    else:
        connection.send_chat_error("You do not have a nuke available")
        return
    
    personalSuccessTimeLeft = playerSuccessCD-(time()-connection.personalSuccessNukeTime)
    teamSuccessTimeLeft = teamSuccessCD-(time()-(connection.protocol.team1SuccessNukeTime if connection.team.id==0 else connection.protocol.team2SuccessNukeTime))
    
    personalTimeLeft = playerCD-(time()-connection.personalNukeTime)
    teamTimeLeft = teamCD-(time()-(connection.protocol.team1NukeTime if connection.team.id==0 else connection.protocol.team2NukeTime))
    if(personalSuccessTimeLeft>0):
        connection.send_chat_error("Your nuke is on cooldown for another %s seconds" %(round(personalSuccessTimeLeft,1)))
        return
    elif(teamSuccessTimeLeft>0):
        connection.send_chat_error("Your nuke is on a team cooldown for another %s seconds" %(round(teamSuccessTimeLeft,1)))
        return
    elif(personalTimeLeft>0):
        connection.send_chat_error("Your nuke is on cooldown for another %s seconds" %(round(personalTimeLeft,1)))
        return
    elif(teamTimeLeft>0):
        connection.send_chat_error("Your nuke is on a team cooldown for another %s seconds" %(round(teamTimeLeft,1)))
        return
        

        
    mapData = connection.protocol.map

    block_action = loaders.BlockAction()
    block_action.value = 3
    block_action.player_id = 31
    
    
    centerPosition = [aimPosX, aimPosY, None]
    randomDegrees = random() * 360
    randomRadius = accuracy * random()
    centerPosition[0] += (randomRadius * cos(randomDegrees))
    centerPosition[1] += (randomRadius * sin(randomDegrees))
    centerPosition[2] = mapData.get_z(centerPosition[0], centerPosition[1])
    
    for x in range(-1*radius,radius):
        block_action.x = centerPosition[0]+x
        for y in range(-1*radius,radius):
            block_action.y = centerPosition[1]+y
            for z in range(-1*downHeight,upHeight):
                if(z>=63):continue
                block_action.z = centerPosition[2] + z
                if(sqrt((block_action.x-centerPosition[0])**2 + (block_action.y-centerPosition[1])**2) <= radius):
                    if(mapData.get_color(block_action.x, block_action.y, block_action.z) is not None):
                        connection.protocol.broadcast_contained(block_action, save=True)
    players = (connection.protocol.team_1 if connection.team.id==1 else connection.protocol.team_2).get_players()
    if(friendly_fire): players += connection.team.get_players()
    for player in players:
        ploc = player.get_location()
        if(sqrt((ploc[0]-centerPosition[0])**2 + (ploc[1]-centerPosition[1])**2)<=radius and (centerPosition[2]-upHeight+4) <= (ploc[2]) <= (centerPosition[2]+downHeight+2)):
            player.kill(kill_type=4)
            connection.personalSuccessNukeTime = time()
            if(connection.team.id==0):
                connection.protocol.team1SuccessNukeTime = time()
            else:
                connection.protocol.team2SuccessNukeTime = time()
    
    for i in range(0,grenadeAmount):
        randomDistance = maximumRadius - ((maximumRadius-radius) * exp(-fallOff*i))
        fuse = (propogationTime)/(grenadeAmount-radius)*i
        randomDegrees = random() * 360
        grenadeX = centerPosition[0] + (randomDistance * cos(randomDegrees))
        grenadeY = centerPosition[1] + (randomDistance * sin(randomDegrees))
        grenade = connection.protocol.world.create_object(Grenade, fuse, Vertex3(grenadeX, grenadeY, min(62,mapData.get_z(grenadeX, grenadeY)+ceil((random()-0.25)*1.5))), None, Vertex3(0,0,2), connection.grenade_exploded)
        grenade.name = "noStreakNade"
    if(connection.team.id==0):
        connection.protocol.team1NukeTime = time()
    else:
        connection.protocol.team2NukeTime = time()
    connection.personalNukeTime = time()
    connection.nukesAvailable-=1
    
    
def apply_script(protocol, connection, config):
    class nukeConnection(connection):
        personalSuccessNukeTime = 0
        personalNukeTime = 0
        nukesAvailable = 0
        def on_kill(self, killer, kill_type, grenade):
            #print("registered kill")
            if(grenade is not None):
                if(grenade.name == "nukeGrenade"):
                    killer.personalSuccessNukeTime = time()
                    if(killer.team.id==0):
                        killer.protocol.team1SuccessNukeTime = time()
                    else:
                        killer.protocol.team2SuccessNukeTime = time()
            connection.on_kill(self, killer, kill_type, grenade);
    class nukeProtocol(protocol):
        team1SuccessNukeTime = 0
        team2SuccessNukeTime = 0
        team1NukeTime = 0
        team2NukeTime = 0
    return nukeProtocol, nukeConnection