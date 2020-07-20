from piqueserver.commands import command, player_only

@command('invis')
@player_only
def invis(connection):
    connection.invisible = not player.invisible

def apply_script(protocol, connection, config):
    class worldEditConnection(connection):
                    
        def on_block_destroy(self, x, y, z, mode):
            print((x,y,z))
            return False
                    
        #def on_block_removed(self, x,y,z):
        #    print((x,y,z))
        #    return False
        #    #connection.on_block_removed(self, x,y,z)
    class worldEditProtocol(protocol):
        pass
    return worldEditProtocol, worldEditConnection