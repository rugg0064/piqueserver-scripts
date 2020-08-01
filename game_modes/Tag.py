from pyspades.constants import CTF_MODE
from random import choice
from pyspades.contained import ChangeTeam
from pyspades.constants import MELEE_KILL
from time import time


safeTime = 5
shotsTag = True

def apply_script(protocol, connection, config):
    class tagProtocol(protocol):
        #team_1 = connection.protocol.team_1
        #team_2 = connection.protocol.team_2
        game_mode = CTF_MODE
    class tagConnection(connection):
        spawnTime = 0
        spawnpoints = []
        it = False
        
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            
            if(self.it and self.team.id==1 and not hit_player.it and hit_player.team.id==0 and (kill_type==MELEE_KILL or shotsTag)):
                if(hit_player.spawnTime + safeTime < time()):
                    self.it = False
                    hit_player.it = True
                    self.team = self.team.other
                    hit_player.team = hit_player.team.other
                    self.kill()
                    hit_player.kill(by=self)
                else:
                    self.send_chat("You can't tag them yet, theyre still safe!")
            elif(not self.it):
                self.send_chat("You are a runner, you cannot attack!")
            elif(kill_type!=MELEE_KILL and not shotsTag):
                self.send_chat("You must use melee!")
            return False
        
        #print(spawnpoints)
        def on_block_build_attempt(self, x, y, z):
            #connection.on_block_build_attempt(x, y, z)
            return False
        def on_line_build_attempt(self, points):
            #connection.on_line_build_attempt(self, points)
            return False
        def on_block_destroy(self, x,y,z, mode):
            #connection.on_block_destroy(self, x,y,z, mode)
            return False
        def on_spawn(self, position):
        
            taggers = sum(1 for _ in self.protocol.team_2.get_players())
            if(taggers > 1 and self.team.id == 1):
                self.team = self.team.other
                self.kill()
                return None
            if(taggers == 0):
                self.it = True
                self.team = self.protocol.team_2
                self.kill()
                return None
            
            if(self.team.id==1):
                self.it = True
            
            connection.on_spawn(self, position)
            if self is not None:
                if "spawns" in self.protocol.map_info.extensions:
                    spawns = self.protocol.map_info.extensions['spawns']
                    for i in spawns:
                        for x in range(i[0][0],i[1][0]+1):
                            for y in range(i[0][1], i[1][1]+1):
                                for z in range(i[0][2], i[1][2]+1):
                                    self.spawnpoints.append((x,y,z))
            self.spawnTime = time()
            connection.set_location(self,choice(self.spawnpoints))
    return tagProtocol, tagConnection