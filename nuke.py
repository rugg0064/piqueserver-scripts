from piqueserver.config import config
from piqueserver.commands import command, admin, player_only, target_player
from piqueserver import map
from pyspades.common import Vertex3
from pyspades.world import Grenade
from pyspades import contained as loaders
from math import ceil, sqrt, pi, sin, cos, exp, floor
from random import random
from time import time
from pyspades.constants import GRENADE_KILL, DESTROY_BLOCK
from twisted.internet import reactor

#Things for overriding grenade_explode
from itertools import product
from pyspades.constants import GRENADE_DESTROY
nukeErrorMessage = "Invalid Input, provide coordinate (eg: C3) and region (eg: NE for northeast)"

sectionConfig = config.section('nuke')
radiusConfig = sectionConfig.option('explosionRadius', default = 10)
maximumRadiusConfig = sectionConfig.option('maximumExplosionRadius', default = 50)
flatnessConfig = sectionConfig.option('flatness', default = 0.0083)
shiftnessConfig = sectionConfig.option('shiftness', default = 131)
#f\left(x\right)\ =\ \left(\left(M-N\right)\right)/(1+1e^{-k\left(x-\left(S\right)\right)})
#N = minimum; M = maximum; S = shiftness (slider 0-*200*); F = flatness (slider 0-0.25)
#X axis = grenade, Y axis = distance from radius
propogationTimeConfig = sectionConfig.option('propogationTime', default = 2.5)
upHeightConfig = sectionConfig.option('upHeight', default = 8)
downHeightConfig = sectionConfig.option('downHeight', default = 2)
grenadeAmountConfig = sectionConfig.option('grenadeAmount', default = 400)
teamSuccessCDConfig = sectionConfig.option('teamSuccessCooldown', default = 30)
playerSuccessCDConfig = sectionConfig.option('playerSuccessCooldown', default = 60)
teamCDConfig = sectionConfig.option('teamCooldown', default = 5)
playerCDConfig = sectionConfig.option('playerCooldown', default = 5)

nukeTKConfig = sectionConfig.option('friendlyFire', default = False)

nukeLaunchTimeConfig = sectionConfig.option('launchTime', default = 30)
warningGlobalInitialConfig = sectionConfig.option('warningGlobalInitial', default = True)
warningOnIntervalConfig = sectionConfig.option('warningOnInterval', default = True)
warningIntervalConfig = sectionConfig.option('interval', default = 10)
warningCountdownConfig = sectionConfig.option('warningOnCountdown', default = True)
warningCountdownStartConfig = sectionConfig.option('warningCountdownStart', default = 10)


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
                                        if(warningGlobalInitialConfig.get()):
                                            connection.protocol.broadcast_chat("NUKE INBOUND: %s%s of %s%s" %(verticalDirection, horizontalDirection, chr(horizontal + 97).upper(), str(vertical+1)), global_message = True)
                                    else:
                                        #error
                                        connection.send_chat_error(nukeErrorMessage)
                                        return
                                else:
                                    direction = ["north", "east", "south", "west", "center"]["neswc".find(args[1][0].lower())]
                                    connection.send_chat_notice("Nuking %s of %s%s" %(direction, chr(horizontal + 97).upper(), str(vertical+1)))
                                    if(warningGlobalInitialConfig.get()):
                                        connection.protocol.broadcast_chat("NUKE INBOUND: %s of %s%s" %(direction, chr(horizontal + 97).upper(), str(vertical+1)), global_message = True)
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
                        if(warningGlobalInitialConfig.get()):
                            connection.protocol.broadcast_chat("NUKE INBOUND: %s%s" %(chr(horizontal + 97).upper(), str(vertical+1)), global_message = True)
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
    
    personalSuccessTimeLeft = playerSuccessCDConfig.get()-(time()-connection.personalSuccessNukeTime)
    teamSuccessTimeLeft = teamSuccessCDConfig.get()-(time()-(connection.protocol.team1SuccessNukeTime if connection.team.id==0 else connection.protocol.team2SuccessNukeTime))
    
    personalTimeLeft = playerCDConfig.get()-(time()-connection.personalNukeTime)
    teamTimeLeft = teamCDConfig.get()-(time()-(connection.protocol.team1NukeTime if connection.team.id==0 else connection.protocol.team2NukeTime))
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
    
    randomDegrees = random() * 360
    randomRadius = accuracy * random()
    centerX = aimPosX + (randomRadius * cos(randomDegrees))
    centerY = aimPosY + (randomRadius * sin(randomDegrees))
    
    nukeLaunchTime = nukeLaunchTimeConfig.get()
    
    #dropNuke(centerX, centerY, accuracy, connection)
    reactor.callLater(nukeLaunchTime, dropNuke, centerX, centerY, accuracy, connection.team, connection)
    #warningOnInterval, warningInterval
    warningInterval = warningIntervalConfig.get()
    if(warningOnIntervalConfig.get() and nukeLaunchTime>warningInterval):
        print("WarningOnInterval true and launch time is greater than interval")
        reactor.callLater(nukeLaunchTime%warningInterval, intervalWarning, connection, warningInterval * floor(nukeLaunchTime/warningInterval))
    warningCountdownStart = warningCountdownStartConfig.get()
    if(warningCountdownConfig.get()):
        if(nukeLaunchTime>=warningCountdownStart):
            reactor.callLater(nukeLaunchTime-warningCountdownStart, countdownWarning, connection, warningCountdownStart)
        else:
            print("Cannot print nuke launch time because config option \"nukeLaunchTime\" is not greater than 5")
    connection.personalNukeTime = time()
    connection.nukesAvailable-=1
    

def intervalWarning(connection, timeLeft):
    warningInterval = warningIntervalConfig.get()
    warningCountdown = warningCountdownConfig.get()
    if(timeLeft < warningInterval):
        if(not warningCountdown):
            connection.protocol.broadcast_chat("NUKE IMMINENT", global_message=True)
    else:
        connection.protocol.broadcast_chat("NUKE IN: %s" %(round(timeLeft)), global_message = True)
        if(not(round(timeLeft) <= warningCountdownStartConfig.get()+warningInterval and warningCountdown)):
            reactor.callLater(warningInterval, intervalWarning, connection, min(timeLeft,timeLeft-warningInterval))
        
def countdownWarning(connection, timeLeft):
    if(round(timeLeft)==0):
        connection.protocol.broadcast_chat("NUKE IMMINENT", global_message=True)
    else:
        connection.protocol.broadcast_chat("NUKE IN: %s" %(round(timeLeft)), global_message = True)
        reactor.callLater(1, countdownWarning, connection, timeLeft-1)

def dropNuke(x, y, accuracy, connectionTeam, connection=None):
    mapData = connection.protocol.map
    z = mapData.get_z(x, y)
    centerPosition = [x,y,z]
    
    block_action = loaders.BlockAction()
    block_action.value = DESTROY_BLOCK
    block_action.player_id = 32
    
    radius = radiusConfig.get()
    upHeight = upHeightConfig.get()
    downHeight = downHeightConfig.get()
    for x in range(-1*radius,radius):
        block_action.x = centerPosition[0]+x
        for y in range(-1*radius,radius):
            block_action.y = centerPosition[1]+y
            for z in range(-1*downHeight,upHeight):
                block_action.z = centerPosition[2] + z
                if(block_action.z >= 63): continue
                if(sqrt((block_action.x-centerPosition[0])**2 + (block_action.y-centerPosition[1])**2) <= radius):
                    if(mapData.get_color(block_action.x, block_action.y, block_action.z) is not None):
                        connection.protocol.broadcast_contained(block_action)
                        mapData.remove_point(block_action.x, block_action.y, block_action.z)

    def killPlayers(players):
        for player in players:
            ploc = player.get_location()
            if(sqrt((ploc[0]-centerPosition[0])**2 + (ploc[1]-centerPosition[1])**2)<=radius and (centerPosition[2]-upHeight+4) <= (ploc[2]) <= (centerPosition[2]+downHeight+2)):
                
                #player.kill(kill_type=GRENADE_KILL)
                
                killGrenade = connection.protocol.world.create_object(Grenade, 0.0, Vertex3(-5, -5, -5), None, Vertex3(0,0,2), None)
                killGrenade.name = "NoStreak"
                player.kill(kill_type=GRENADE_KILL, by = connection, grenade = killGrenade)
                
                connection.personalSuccessNukeTime = time()
                if(connectionTeam.id==0):
                    connection.protocol.team1SuccessNukeTime = time()
                else:
                    connection.protocol.team2SuccessNukeTime = time()
    killPlayers(connectionTeam.other.get_players())
    #killPlayers((connection.protocol.team_1 if connectionTeam.id==1 else connection.protocol.team_2).get_players())
    if(nukeTKConfig.get()): 
        killPlayers(connection.team.get_players())
    grenadeAmount = grenadeAmountConfig.get()
    for i in range(0,grenadeAmount):
        randomDistance = (maximumRadiusConfig.get() - radius) / (1 + exp(-flatnessConfig.get() * (i-shiftnessConfig.get())))
        fuse = (propogationTimeConfig.get())/(grenadeAmount-radius)*i
        randomDegrees = random() * 360
        grenadeX = centerPosition[0] + (randomDistance * cos(randomDegrees))
        grenadeY = centerPosition[1] + (randomDistance * sin(randomDegrees))
        grenade = connection.protocol.world.create_object(Grenade, fuse, Vertex3(grenadeX, grenadeY, min(62,mapData.get_z(grenadeX, grenadeY)+ceil((random()-0.25)*1.5))), None, Vertex3(0,0,2), connection.nuke_grenade_exploded)
        
        grenade.team = connectionTeam
        grenade.name = "nadeNoStreak" + ("NukeTeamID"+str(connectionTeam.id))
    if(connectionTeam.id==0):
        connection.protocol.team1NukeTime = time()
    else:
        connection.protocol.team2NukeTime = time()

def apply_script(protocol, connection, config):
    class nukeConnection(connection):
        personalSuccessNukeTime = 0
        personalNukeTime = 0
        nukesAvailable = 0
        
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            connection.on_hit(self, hit_amount, hit_player, kill_type, grenade)
        
        #def nuke_hit(self, hit_amount, hit_player, kill_type, grenade):
            
        
        def nuke_grenade_exploded(self, grenade):
            if(self.name is None):
                self.name = "AAA"
                self.team = self.protocol.team_2 if "NukeTeamID1" in grenade.name else self.protocol.team_1
                grenade.team = self.team
            import math
            if self.name is None or self.team.spectator:
                return
            if grenade.team is not None and grenade.team is not self.team:
                # could happen if the player changed team
                return
            position = grenade.position
            x = position.x
            y = position.y
            z = position.z
            if x < 0 or x > 512 or y < 0 or y > 512 or z < 0 or z > 63:
                return
            x = int(math.floor(x))
            y = int(math.floor(y))
            z = int(math.floor(z)) 
            for player_list in (self.team.other.get_players(), (self,), self.team.get_players() if ("Nuke" in grenade.name and nukeTKConfig.get()) else []):
                for player in player_list:
                    if not player.hp:
                        continue
                    damage = grenade.get_damage(player.world_object.position)
                    if damage == 0:
                        continue
                    returned = self.on_hit(damage, player, GRENADE_KILL, grenade)
                    if returned == False:
                        continue
                    elif returned is not None:
                        damage = returned
                    player.set_hp(player.hp - damage, self, hit_indicator=position.get(), kill_type=GRENADE_KILL,grenade=grenade)
            
            if self.on_block_destroy(x, y, z, GRENADE_DESTROY) == False:
                return
            map = self.protocol.map
            for n_x, n_y, n_z in product(range(x - 1, x + 2), range(y - 1, y + 2), range(z - 1, z + 2)):
                count = map.destroy_point(n_x, n_y, n_z)
                if count:
                    self.total_blocks_removed += count
                    self.on_block_removed(n_x, n_y, n_z)
            block_action = loaders.BlockAction()
            block_action.x = x
            block_action.y = y
            block_action.z = z
            block_action.value = GRENADE_DESTROY
            block_action.player_id = self.player_id
            self.protocol.broadcast_contained(block_action, save=True)
            self.protocol.update_entities()
            
        def on_kill(self, killer, kill_type, grenade):
            if(grenade is not None):
                if("Nuke" in grenade.name):
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