from piqueserver.commands import command, player_only, admin, target_player
from pyspades.constants import BUILD_BLOCK
from pyspades.contained import BlockAction, SetColor
c4Color = 0b111111110000000000000000


@command('givec4', 'gc4')
@admin
@target_player
def giveC4(connection, player):
    player.nukesAvailable = player.c4Count+1
    try:
        connection.send_chat_notice("You have given %s a C4 charge." %player.name)
    except AttributeError as ex:
        print("%s has been given a C4 charge, but there was a %s error" %(player.name, type(ex)))
    player.send_chat_notice("%s has given you a C4 charge." %connection.name)

@command('c4')
@player_only
def placeC4(connection, *args):
    if(connection.c4Count<=0):
        connection.send_chat("You have no c4 charges")
        return
    hit = connection.world_object.cast_ray(512)
    if(hit)
        connection.c4Count -= 1
        map = connection.protocol.map
        block_action = BlockAction()
        block_action.value = BUILD_BLOCK
        block_action.player_id = 32
        set_color = SetColor()
        set_color.player_id = 32
        set_color.value = c4Color
        if(not map.get_point(*hit)[0]):
            block_action.x, block_action.y, block_action.z = hit
            connection.protocol.broadcast_contained(block_action)
        connection.protocol.broadcast_contained(set_color)
        connection.protocol.c4BlockPositions.append( (hit) )
    connection.send_chat("Your next block placed will be a C4")
        
def apply_script(protocol, connection, config):
    class c4Connection(connection):
        c4Count = 0
        def on_block_build(self, x, y, z):
            connection.on_block_build(self, x, y, z)
        def on_block_removed(self, x,y,z):
            print((x,y,z))
            connection.on_block_removed(self, x,y,z)
    class c4Protocol(protocol):
        c4BlockPositions = []
    return c4Protocol, c4Connection