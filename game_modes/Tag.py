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
sectionConfig = config.section('tag')
safeTimeConfig = sectionConfig.option('safeTime', default = 5)
shotsTagConfig = sectionConfig.option('shotsTag', default = False)
pointsEveryXSecondsConfig = sectionConfig.option('pointsEveryXSeconds', default = 5)
taggerTimeConfig = sectionConfig.option('taggerTime', default = 30)

@command('tag')
def tagTutorial(connection):
    connection.send_chat("The longer the runner survives, the more points they gain")
    connection.send_chat("The tagger, who is \"it\" must try to hit a runner")
    connection.send_chat("To play tag, runners must run away and hide from the tagger")


def apply_script(protocol, connection, config):
    class tagProtocol(protocol):
        game_mode = CTF_MODE
        newRunnerCallID = None
        spawnPoints = []
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
            if(sum(1 for _ in self.protocol.team_2.get_players()) == 0):
                self.protocol.broadcast_chat("Tagger has disconnected, points awarded, congrats!")
                self.protocol.givePlayersPointsForTime(exclude = [self])
                self.protocol.selectRandomTagger(exclude = [self])
            connection.on_disconnect(self)
            
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            #self.givePoints(10)
            
            #if tagger hits a runner and (melee or shots count)
            if(self.team.id==1 and hit_player.team.id==0 and (kill_type==MELEE_KILL or shotsTagConfig.get())):
                if(hit_player.spawnTime + safeTimeConfig.get() < time()):
                    self.set_team(self.protocol.team_1)
                    hit_player.set_team(self.protocol.team_2)
                    hit_player.spawnAtPos = hit_player.get_location()
                    protocol.broadcast_chat(self.protocol, "{} has been tagged, they are now it!".format(hit_player.name))
                    self.protocol.givePlayersPointsForTime(exclude = [self])
                else:
                    self.send_chat("You can't tag them yet, theyre still safe!")
            elif(self.team.id == 0):
                self.send_chat("You are a runner, you cannot attack!")
            elif(kill_type!=MELEE_KILL and not shotsTagConfig.get()):
                self.send_chat("You must use melee!")
            return False
        
        on_block_build_attempt = on_line_build_attempt = on_block_destroy = lambda *args : False
        
        def on_position_update(self):
            taggers = [_ for _ in self.protocol.team_2.get_players()]

            sky = (135, 206, 235)
            red = (102,0,0)
            print(self.protocol.team_2.color)
            distance = 9999
            color = sky
            if(self.team.id==0):
                for tagger in taggers:
                    tpos = tagger.get_location()
                    ppos = self.get_location()
                    distance = min(distance, ( (tpos[0]-ppos[0])**2 + (tpos[1]-ppos[1])**2 + (tpos[2]-ppos[2])**2)**(1/2))
                if(distance < 20):
                    pc = max(0,(distance-5)/15) #percent
                    pc = pc**2
                    randomAdd = 5 * (random() - 0 if self.positiveColorOffset else 1)
                    self.positiveColorOffset = not self.positiveColorOffset
                    
                    color = (randomAdd + sky[0]*pc + red[0]*(1-pc),
                            randomAdd + sky[1]*pc + red[1]*(1-pc),
                            randomAdd + sky[2]*pc + red[2]*(1-pc))

            fd = FogColor()
            fd.color = color
            self.send_contained(fd)

            connection.on_position_update(self)
            
        def get_spawn_location(self):
            if(self.spawnAtPos is not None):
                pos = self.spawnAtPos
                self.spawnAtPos = None
            else:
                pos = choice(self.protocol.getSpawns())
            return pos
        
        def on_spawn(self, position):
            taggers = sum(1 for _ in self.protocol.team_2.get_players())
            if(taggers > 1 and self.team.id == 1):
                self.set_team(self.protocol.team_1)
                self.spawnAtPos = self.spawnAtPos
            if(taggers == 0):
                self.set_team(self.protocol.team_2)
                self.spawnAtPos = self.spawnAtPos
                return None
            
            if(self.team.id==1):
                self.protocol.newTaggerTime()
            '''
            print(connection.on_spawn(self, position))
            if self is not None:
                if "spawns" in self.protocol.map_info.extensions:
                    spawns = self.protocol.map_info.extensions['spawns']
                    for i in spawns:
                        for x in range(i[0][0],i[1][0]+1):
                            for y in range(i[0][1], i[1][1]+1):
                                for z in range(i[0][2], i[1][2]+1):
                                    self.spawnpoints.append((x,y,z))
            '''
            self.spawnTime = time()
            connection.on_spawn(self, position)
    return tagProtocol, tagConnection