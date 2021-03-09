from time import time
from pyspades.common import Vertex3

from piqueserver.commands import command
@command('afktest')
def afkTest(connection):
    connection.send_chat("aaa" + str(connection.lastAction))
    
def apply_script(protocol, connection, config):
    class smartAFKConnection(connection):
        lastAction = None
        def on_connect(self):
            lastAction = time()
            connection.on_connect(self)
        positions = []
        def on_position_update(self):
            self.positions.append(self.get_location())
            if(len(self.positions)>=2):
                distances = []
                for i in range(len(self.positions)-1):
                    p1 = Vertex3(*self.positions[i])
                    p2 = Vertex3(*self.positions[i+1])
                    distances.append(p1.distance(p2))
                
                if(min(distances)>1):
                    print('setting time')
                    self.lastAction = time()
                
            if(len(self.positions)>2):
                self.positions.pop(0)
        
        def on_color_set_attempt(self, color):
            connection.on_color_set_attempt(self, color)
            
        def on_chat(self, value, global_message):
            connection.on_chat(self,value,global_message)
            
        def on_tool_set_attempt(self, tool):
            connection.on_tool_set_attempt(self, tool)
            
        def on_team_join(self, team):
            connection.on_team_join(self, team)
            
        def on_grenade_thrown(self, grenade):
            connection.on_grenade_thrown(self, grenade)
            
        def on_block_build_attempt(self, x, y, z):
            connection.on_block_build_attempt(self, x, y, z)
            
        def on_line_build_attempt(self, points):
            connection.on_line_build_attempt(self, points)
            
        def on_block_destroy(self, x, y, z, mode):
            connection.on_block_destroy(self, x, y, z, mode)
            
        def on_shoot_set(self, fire):
            connection.on_shoot_set(self, fire)
            
        def on_secondary_fire_set(self, secondary):
            connection.on_secondary_fire_set(self, secondary)
            
        def on_walk_update(self, up, down, left, right):
            connection.on_walk_update(self, up, down, left, right)
            
    class smartAFKProtocol(protocol):
        pass
    return smartAFKProtocol, smartAFKConnection