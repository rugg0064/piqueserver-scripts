from pyspades.constants import CTF_MODE
from random import choice
from pyspades.contained import ChangeTeam
from pyspades.constants import MELEE_KILL
from time import time

from twisted.internet import reactor
from twisted.internet.error import AlreadyCalled

safeTime = 5
shotsTag = True
pointsEveryXSeconds = 5
taggerTime = 60

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
            self.newRunnerCallID = reactor.callLater(taggerTime, self.taggerOutOfTime)
            
        def taggerOutOfTime(self):
            if(len(self.players)<=1):
                self.newTaggerTime()
            else:
                self.broadcast_chat("Tagger has run out of time!")
                self.givePlayersPointsForTime(exclude = findTaggers)
                self.selectRandomTagger(exclude = self.findTaggers())
            return
        
        def givePlayersPointsForTime(self, exclude = []):
            for i in self.players:
                player = self.players[i]
                if player not in exclude:
                    print( int((time() - player.spawnTime) // pointsEveryXSeconds))
                    player.givePoints( int((time() - player.spawnTime) // pointsEveryXSeconds))
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
        
        def givePoints(self, amount):
            from pyspades.contained import KillAction, CreatePlayer, PlayerLeft
            cp = CreatePlayer()
            cp.x = 0
            cp.y = 0
            cp.z = 0
            cp.weapon = 0
            cp.player_id = 31
            cp.name = "TAGGED"
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
            if(self.team.id == 1):
                self.protocol.broadcast_chat("Tagger has disconnected, points awarded, congrats!")
                self.protocol.givePlayersPointsForTime(exclude = [self])
                self.protocol.selectRandomTagger(exclude = [self])
            connection.on_disconnect(self)
            
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            #self.givePoints(10)
            
            if(self.team.id==1 and hit_player.team.id==0 and (kill_type==MELEE_KILL or shotsTag)):
                if(hit_player.spawnTime + safeTime < time()):
                    self.set_team(self.protocol.team_1)
                    hit_player.set_team(self.protocol.team_2)
                    
                    protocol.broadcast_chat(self.protocol, "{} has been tagged, they are now it!".format(hit_player.name))
                    self.protocol.givePlayersPointsForTime(exclude = [self, hit_player])
                else:
                    self.send_chat("You can't tag them yet, theyre still safe!")
            elif(self.team.id == 0):
                self.send_chat("You are a runner, you cannot attack!")
            elif(kill_type!=MELEE_KILL and not shotsTag):
                self.send_chat("You must use melee!")
            return False
        
        on_block_build_attempt = on_line_build_attempt = on_block_destroy = lambda *args : False
        
        def on_position_update(self):
            #print(self.protocol.newRunnerCallID)
            connection.on_position_update(self)
        
        def get_spawn_location(self):
            pos = choice(self.protocol.getSpawns())
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
            #connection.set_location(self,choice(self.spawnpoints))
    return tagProtocol, tagConnection