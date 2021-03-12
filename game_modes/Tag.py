from pyspades.constants import CTF_MODE
from piqueserver.config import config
from random import choice, random
from pyspades.contained import ChangeTeam
from pyspades.constants import MELEE_KILL
from time import time
from piqueserver.commands import command, player_only
from twisted.internet import reactor
from twisted.internet.error import AlreadyCalled
from pyspades.contained import KillAction, CreatePlayer, PlayerLeft, StateData, CTFState, FogColor
from math import floor
sectionConfig = config.section('tag')
safeTimeConfig = sectionConfig.option('safeTime', default = 5)
shotsTagConfig = sectionConfig.option('shotsTag', default = False)
pointsEveryXSecondsConfig = sectionConfig.option('pointsEveryXSeconds', default = 5)
taggerTimeConfig = sectionConfig.option('taggerTime', default = 30)
disqualificationBonusConfig = sectionConfig.option('disqualificationBonus', default = 10)
taggerComboCountConfig = sectionConfig.option('taggerComboCount', default = 5)
taggerComboTimeConfig = sectionConfig.option('taggerComboTime', default = 1)

@command('tag')
def tagTutorial(connection):
    connection.send_chat("The longer the runner survives, the more points they gain")
    connection.send_chat("The tagger, who is \"it\" must try to hit a runner")
    connection.send_chat("To play tag, runners must run away and hide from the tagger")

@command('kill')
def killCommand(connection):
    connection.send_chat("You cannot use the kill command")

def apply_script(protocol, connection, config):
    class tagProtocol(protocol):
        game_mode = CTF_MODE
        newRunnerCallID = None
        spawnPoints = []
        spawnsCache = None
        def getSpawns(self):
            if(len(self.spawnPoints)==0):
                if "spawns" in self.map_info.extensions:
                    spawns = self.map_info.extensions['spawns']
                    for i in spawns:
                        for x in range(i[0][0],i[1][0]+1):
                            for y in range(i[0][1], i[1][1]+1):
                                for z in range(i[0][2], i[1][2]+1):
                                    self.spawnPoints.append((x,y,z))
            return self.spawnPoints
        
        def findTaggers(self):
            taggers = []
            for i in self.players:
                player = self.players[i]
                if(player.team.id == 1):
                    taggers.append(player)
            return taggers
        
        def newTaggerTime(self):
            try:
                self.newRunnerCallID.cancel()
            except AttributeError as aterr:
                pass
            except AlreadyCalled as acerr:
                pass
            except Exception as ex:
                print("Unknown Error: " + type(ex))
            self.newRunnerCallID = reactor.callLater(taggerTimeConfig.get(), self.taggerOutOfTime)
            
        def taggerOutOfTime(self):
            if(len(self.players)<=1):
                self.newTaggerTime()
            else:
                self.broadcast_chat("Tagger has run out of time!")
                self.givePlayersPointsForTime(exclude = self.findTaggers())
                self.selectRandomTagger(exclude = self.findTaggers())
            return
        
        def givePlayersPointsForTime(self, exclude = []):
            for i in self.players:
                player = self.players[i]
                if player not in exclude:
                    #print( int((time() - player.spawnTime) // pointsEveryXSecondsConfig.get()))
                    player.givePoints( int((time() - player.spawnTime) // pointsEveryXSecondsConfig.get()))
                    player.spawnTime = time()
                    
        def selectRandomTagger(self, exclude = []):
            playerConnections = []
            for i in self.players:
                player = self.players[i]
                if(player not in exclude):
                    playerConnections.append(player)
                else:
                    player.set_team(self.team_1)
            if(len(playerConnections)>0):
                chosenOne = choice(playerConnections)
                chosenOne.set_team(self.team_2)
                
    class tagConnection(connection):
        spawnTime = 0
        positiveColorOffset = False
        spawnAtPos = None

        lastHitTaggerTime = 0
        taggerHitCombo = taggerComboCountConfig.get()
        
        def givePoints(self, amount):
            cp = CreatePlayer()
            cp.x = 0
            cp.y = 0
            cp.z = 0
            cp.weapon = 0
            cp.player_id = 31
            cp.name = "TAG POINTS"
            cp.team = self.team.other.id
            self.protocol.broadcast_contained(cp, save=True)
            
            ka = KillAction()
            ka.player_id = 31
            ka.killer_id = self.player_id
            self.kill_type = 0
            self.respawn_time = 0
            for i in range(amount):
                self.protocol.broadcast_contained(ka, save=True)
            
            pl = PlayerLeft()
            pl.player_id = 31
            self.protocol.broadcast_contained(pl, save=True)
        
        def on_disconnect(self):
            if(self.team.id == 1 and sum(1 for _ in self.protocol.team_2.get_players()) <= 1):
                self.protocol.broadcast_chat("Tagger has disconnected, points awarded, congrats!")
                self.protocol.givePlayersPointsForTime(exclude = [self])
                self.protocol.selectRandomTagger(exclude = [self])
            connection.on_disconnect(self)
            
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            if(self.team.id == 1): #Tagger is who hit someone
                if(hit_player.team.id == 0): # Tagger hit a Runner
                    if(kill_type == MELEE_KILL or shotsTagConfig.get()): #Allowed hit
                        if(hit_player.spawnTime + safeTimeConfig.get() < time()): #not spawn protected
                            self.set_team(self.protocol.team_1)
                            hit_player.spawnAtPos = hit_player.get_location()
                            hit_player.set_team(self.protocol.team_2)
                            protocol.broadcast_chat(self.protocol, "{} has been tagged, they are now it!".format(hit_player.name))
                            self.protocol.givePlayersPointsForTime(exclude = [self])
                        else: #runner currently spawn protected
                            self.send_chat("You can't tag them yet, theyre still safe!")
                    else: #not allowed hit type
                        self.send_chat("You must use a spade to tag!")
            elif(self.team.id == 0): #Runner is who hit someone
                if(kill_type == MELEE_KILL):
                    if(hit_player.team.id == 1): # Runner hit a Tagger
                        if(hit_player.spawnTime + safeTimeConfig.get() < time()): #not spawn protected
                            if(self.lastHitTaggerTime + taggerComboTimeConfig.get() < time()): # Hit outside of combo time
                                self.taggerHitCombo = taggerComboCountConfig.get() - 1
                            else: # Hit inside combo time
                                self.taggerHitCombo = self.taggerHitCombo - 1
                            self.lastHitTaggerTime = time()
                            
                            if(self.taggerHitCombo <= 0):
                                protocol.broadcast_chat(self.protocol, "{} has disqualified {}, new tagger selected!".format(self.name, hit_player.name))
                                pointsToGive = disqualificationBonusConfig.get()
                                self.send_chat("You have been given {} points for disqualifying a runner!".format(pointsToGive))
                                self.givePoints(pointsToGive)
                                self.protocol.givePlayersPointsForTime(exclude = [hit_player])
                                self.protocol.selectRandomTagger(exclude = [self, hit_player])
                            else:
                                self.send_chat("If you hit the tagger {} more times he will be disqualified!".format(self.taggerHitCombo))
                        else:
                            self.send_chat("The runner is still spawn protected!")
                    else:
                        self.send_chat("You are a runner, you can only hit the tagger!")
                else:
                    self.send_chat("Runners can only use a spade!")
            return False
        
        on_block_build_attempt = on_line_build_attempt = on_block_destroy = lambda *args : False
        
        def on_position_update(self):
            taggers = [_ for _ in self.protocol.team_2.get_players()]

            sky = (getattr(self.protocol.map_info.info, 'fog', self.protocol.default_fog))
            red = self.protocol.team_2.color
            distance = 9999
            color = sky
            if(self.team.id==0):
                for tagger in taggers:
                    tpos = tagger.get_location()
                    ppos = self.get_location()
                    distance = min(distance, ( (tpos[0]-ppos[0])**2 + (tpos[1]-ppos[1])**2 + (tpos[2]-ppos[2])**2 )**(1/2))
                if(distance < 20):
                    pc = min(1, max(0,(distance-5)/15)) #percent
                    self.positiveColorOffset = not self.positiveColorOffset
                    
                    color = (floor(sky[0]*(pc) + red[0]*(1-pc)),
                             floor(sky[1]*(pc) + red[1]*(1-pc)),
                             floor(sky[2]*(pc) + red[2]*(1-pc)))

            fd = FogColor()
            fd.color = (color[0] << 16) + (color[1] << 8) + (color[2] << 0)
            self.send_contained(fd)

            connection.on_position_update(self)
            
        def get_spawn_location(self):
            if(self.spawnAtPos is not None):
                pos = self.spawnAtPos
                pos = (floor(pos[0]) - 0.5, floor(pos[1]) - 0.5, floor(pos[2]) + 2.0)
                self.spawnAtPos = None
            else:
                pos = choice(self.protocol.getSpawns())
                '''
                totalPosDistanceMax = -999999999
                for point in self.protocol.getSpawns():
                    pointMinDistance = 99999999
                    for ply in self.protocol.players.values():
                        if ply.world_object is not None:
                            print("Asd")
                            pos2 = ply.get_location()
                            distance = ( (pos2[0]-point[0])**2 + (pos2[1]-point[1])**2 + (pos2[2]-point[2])**2 )**(1/2)
                            if(distance < pointMinDistance):
                                pointMinDistance = distance
                    if(pointMinDistance > totalPosDistanceMax):
                        totalPosDistanceMax = pointMinDistance
                        pos = point
                '''
            return pos

        def on_spawn(self, position):

            taggers = sum(1 for _ in self.protocol.team_2.get_players())
            if(taggers > 1 and self.team.id == 1):
                self.set_team(self.protocol.team_1)
            if(taggers == 0):
                self.set_team(self.protocol.team_2)
                return None
            
            if(self.team.id==1):
                self.protocol.newTaggerTime()

            self.spawnTime = time()

            connection.on_spawn(self, position)

            self.set_location(position)
            
    return tagProtocol, tagConnection