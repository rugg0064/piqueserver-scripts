from pyspades.constants import BLUE_FLAG, BLUE_BASE, GREEN_FLAG, GREEN_BASE
from random import choice

def choosePos(map, extensionObj):
    x1,y1 = extensionObj[0]
    x2,y2 = extensionObj[1]
    positions = []
    for x in range(x1,x2):
        for y in range(y1,y2):
            z = map.get_z(x,y)
            positions.append( (x,y,z) )
    return choice(positions)
'''
def choosePos(self, protocol, spawns, callBack, *args):
    waterSpawns = protocol.map_info.extensions['water_spawn']
    #print("SPAWNING")
    if(spawns is not None):
        optionsx = range(spawns[0][0], spawns[1][0]+1)
        optionsy = range(spawns[0][1], spawns[1][1]+1)
        positions = []
        for x in optionsx:
            for y in optionsy:
                ZLevel = protocol.map.get_z(x,y)
                #print(ZLevel)
                if(not (ZLevel > 63)):
                    positions.append((x,y,ZLevel))
        pos = choice(positions)
        #valueZ = protocol.map.get_z(pos[0],pos[1])
        return((pos[0],pos[1],pos[2]))
    return(callBack(*args))
'''

def apply_script(protocol, connection, config):
    class spawnConnection(connection):
        def on_spawn_location(self, pos):
            try:
                spawns = self.protocol.map_info.extensions['team1Spawn' if self.team.id==0 else 'team2Spawn']
                return choosePos(self.map, spawns)
                #return(choosePos(self, self.protocol, spawns, connection.on_spawn_location, self, pos))
            except Exception as exception:
                print(exception)
                connection.on_spawn_location(self, pos)
    class spawnProtocol(protocol):
        def on_flag_spawn(self, x, y, z, flag, entity_id):
            print("Spawning")
            try:
                spawns = self.map_info.extensions['team1Intel' if entity_id==BLUE_FLAG else 'team2Intel']
                return choosePos(self.map, spawns)
                #return(choosePos(self, self, spawns, protocol.on_flag_spawn, self, x, y, z, flag, entity_id))
            except Exception as e:
                print("Exception", e)
                protocol.on_flag_spawn(self, x, y, z, flag, entity_id)
        def on_base_spawn(self, x, y, z, base, entity_id):
            try:
                spawns = self.map_info.extensions['team1Base' if entity_id==BLUE_BASE else 'team2Base']
                return choosePos(self.map, spawns)
                #return(choosePos(self, self, spawns, protocol.on_base_spawn, self, x, y, z, base, entity_id))
            except Exception as exception:
                print(exception)
                protocol.on_base_spawn(self, x, y, z, base, entity_id)
    return spawnProtocol, spawnConnection