from pyspades.constants import BLUE_FLAG, BLUE_BASE, GREEN_FLAG, GREEN_BASE
from random import choice

def choosePos(self, protocol, spawns, callBack, *args):
    if(spawns is not None):
        optionsx = range(spawns[0][0], spawns[1][0]+1)
        optionsy = range(spawns[0][1], spawns[1][1]+1)
        positions = []
        for x in optionsx:
            for y in optionsy:
                positions.append((x,y))
        pos = choice(positions)
        valueZ = protocol.map.get_z(pos[0],pos[1])
        return((pos[0],pos[1],valueZ))
    return(callBack(*args))

def apply_script(protocol, connection, config):
    class spawnConnection(connection):
        def on_spawn_location(self, pos):
            try:
                spawns = self.protocol.map_info.extensions['team1Spawn' if self.team.id==0 else 'team2Spawn']
                return(choosePos(self, self.protocol, spawns, connection.on_spawn_location, self, pos))
            except Exception as exception:
                print(exception)
                connection.on_spawn_location(self, pos)
    class spawnProtocol(protocol):
        def on_flag_spawn(self, x, y, z, flag, entity_id):
            try:
                spawns = self.map_info.extensions['team1Intel' if entity_id==BLUE_FLAG else 'team2Intel']
                return(choosePos(self, self, spawns, protocol.on_flag_spawn, self, x, y, z, flag, entity_id))
            except Exception as exception:
                print(exception)
                protocol.on_flag_spawn(self, x, y, z, flag, entity_id)
        def on_base_spawn(self, x, y, z, base, entity_id):
            try:
                spawns = self.map_info.extensions['team1Base' if entity_id==BLUE_BASE else 'team2Base']
                return(choosePos(self, self, spawns, protocol.on_base_spawn, self, x, y, z, base, entity_id))
            except Exception as exception:
                print(exception)
                protocol.on_base_spawn(self, x, y, z, base, entity_id)
    return spawnProtocol, spawnConnection