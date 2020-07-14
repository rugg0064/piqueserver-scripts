from piqueserver.commands import command, admin, player_only, target_player
from math import floor
from pyspades.contained import BlockAction, SetColor
from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from pyspades.common import make_color

@command('stack')
@player_only
def stack(connection, *args):
    pos1 = connection.selectPos1
    pos2 = connection.selectPos2
    
    try:
        offset = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)][['up', 'down', 'north', 'east', 'south', 'west'].index(args[0])]
    except ValueError:
        return
    if(None in (pos1,pos2)):
        return
    try:
        amount = int(args[1])
    except Exception as E:
        amount = 1
    map = connection.protocol.map
    xh = abs(pos1[0]-pos2[0])+1 #IN XYZ ORDER
    yh = abs(pos1[1]-pos2[1])+1
    zh = abs(pos1[2]-pos2[2])+1
    allBlocks = [None]*(xh*yh*zh)
    allPositions = [None]*len(allBlocks)
    i = 0
    for x in range(*(pos1[0], pos2[0] + 1) if pos1[0] < pos2[0] else (pos2[0], pos1[0] + 1)):
        for y in range(*(pos1[1], pos2[1] + 1) if pos1[1] < pos2[1] else (pos2[1], pos1[1] + 1)):
            for z in range(*(pos1[2], pos2[2] + 1) if pos1[2] < pos2[2] else (pos2[2], pos1[2] + 1)):
                allBlocks[i] = map.get_point(x, y, z)
                allPositions = (x,y,z)
                i += 1
    
    operations = []
    for run in range(0, amount):
        operations.append([])
        operations[run-1].append("NEW")
        block_action = BlockAction()
        block_action.value = DESTROY_BLOCK
        block_action.player_id = 32
        set_color = SetColor()
        set_color.value = connection.selectColor if connection.selectColor is not None else 0x707070
        set_color.player_id = 32
        i = 0
        for x in range(*(pos1[0], pos2[0] + 1) if pos1[0] < pos2[0] else (pos2[0], pos1[0] + 1)):
            block_action.x = x + (offset[0]*xh*(run+1))
            for y in range(*(pos1[1], pos2[1] + 1) if pos1[1] < pos2[1] else (pos2[1], pos1[1] + 1)):
                block_action.y = y + (offset[1]*yh*(run+1))
                for z in range(*(pos1[2], pos2[2] + 1) if pos1[2] < pos2[2] else (pos2[2], pos1[2] + 1)):
                    block_action.value = DESTROY_BLOCK
                    block_action.z = z + (offset[2]*zh*(run+1))
                    if(not allBlocks[i][0]):
                        if map.get_point(block_action.x, block_action.y, block_action.z):
                            connection.protocol.broadcast_contained(block_action)
                            map.remove_point(block_action.x, block_action.y, block_action.z)
                        i += 1
                        operations[run-1].append("blank")
                        continue
                    else:
                        if(not map.get_point(block_action.x, block_action.y, block_action.z)):
                            block = allBlocks[i]
                            blockColor = block[1]
                            icolor = blockColor[0]*(256**2) + blockColor[1]*256 + blockColor[2]
                            set_color.value = icolor
                            connection.protocol.broadcast_contained(set_color)
                        else:
                            block_action.value = BUILD_BLOCK
                            connection.protocol.broadcast_contained(block_action)
                            block = allBlocks[i]
                            blockColor = block[1]
                            icolor = blockColor[0]*(256**2) + blockColor[1]*256 + blockColor[2]
                            icolor = blockColor[0]*(256**2) + blockColor[1]*256 + blockColor[2]
                            set_color.value = icolor
                            connection.protocol.broadcast_contained(set_color)
                            
                            ctuple = (set_color.value >> 16 & 255, set_color.value >> 8 & 255, set_color.value & 255)
                            map.set_point(block_action.x, block_action.y, block_action.z, ctuple)
                        i += 1
                        operations[run-1].append("block")
                        continue
                
@command('warp')
@player_only
def warp(connection, *args):
    print('warp')
    if len(args)==2:
        try:
            x = int(args[0])
            y = int(args[1])
            z = connection.protocol.map.get_z(x,y)-2
            connection.set_location((x, y, z))
            return 
        except Exception as E:
            print(E)
    if len(args) == 3:
        try:
            x = int(args[0])
            y = int(args[1])
            z = int(args[2])
            connection.set_location((x, y, z))
            return
        except Exception as E:
            print(E)

@command('pos1')
@player_only
def pos1(connection):
    loc = connection.get_location()
    loc = (floor(loc[0]), floor(loc[1]), floor(loc[2]))
    connection.selectPos1 = loc
    connection.send_chat('Selected pos: ' + str(loc))

@command('pos2')
@player_only
def pos2(connection):
    loc = connection.get_location()
    loc = (floor(loc[0]), floor(loc[1]), floor(loc[2]))
    connection.selectPos2 = loc
    connection.send_chat('Selected pos: ' + str(loc))

@command('hpos1')
@player_only
def hpos1(connection):
    hit = connection.world_object.cast_ray(128)
    if hit is not None:
        connection.selectPos1 = hit
        connection.send_chat('Selected pos: ' + str(hit))
    else:
        return

@command('hpos2')
@player_only
def hpos2(connection):
    hit = connection.world_object.cast_ray(128)
    if hit is not None:
        connection.selectPos2 = hit
        connection.send_chat('Selected pos: ' + str(hit))
    else:
        return

@command('sel')
@player_only
def printSel(connection):
    connection.send_chat(str(connection.selectPos1))
    connection.send_chat(str(connection.selectPos2))

@command('color', 'c')
@player_only
def setColor(connection, *args):
    if len(args) == 0:
        c = connection.selectColor
        if c is not None:
            connection.send_chat(str(c))
            r = c >> 16 & 255
            g = c >> 8 & 255
            b = c & 255
            connection.send_chat(str((r, g, b)) + ' or ' + str(hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2j kbm) + hex(b)[2:].zfill(2)))
        else:
            connection.send_chat('You havent set a color yet! use /color or /c')
    else:
        if len(args) == 1:
            try:
                hexInt = int('0x' + args[0], 16)
                if 0 < hexInt < 16777215:
                    connection.selectColor = hexInt
            except Exception as bbb:
                print(bbb)
                connection.send_chat('Error, are you trying to input hex? ie: ffa71a?')

        elif len(args) == 3:
            try:
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
                connection.selectColor = make_color(r, g, b)
            except Exception as bbb:
                print(bbb)
                connection.send_chat('There was an error.')

        else:
            connection.send_chat('Invalid input')

@command('shift')
@player_only
def shift(connection, *args):
    pos1 = connection.selectPos1
    pos2 = connection.selectPos2
    if len(args) < 2:
        connection.send_chat('Invalid input')
        return
    if args[0] not in ('up', 'down', 'north', 'east', 'south', 'west'):
        connection.send_chat('Invalid input')
        return
    else:
        try:
            amount = int(args[1])
        except Exception as E:
            print('error')
            return

        if None in (pos1, pos2):
            connection.send_chat('You are missing a position, try /sel to see your positions')
            return
        if 'up' in args:
            if pos1[2] < pos2[2]:
                connection.selectPos1 = (
                 pos1[0], pos1[1], pos1[2] - amount)
                connection.selectPos2 = (pos2[0], pos2[1], pos2[2] - amount)
            else:
                connection.selectPos2 = (
                 pos2[0], pos2[1], pos2[2] - amount)
                connection.selectPos1 = (pos1[0], pos1[1], pos1[2] - amount)
            return
        if 'down' in args:
            if pos1[2] > pos2[2]:
                connection.selectPos1 = (
                 pos1[0], pos1[1], pos1[2] + amount)
                connection.selectPos2 = (pos2[0], pos2[1], pos2[2] + amount)
            else:
                connection.selectPos2 = (
                 pos2[0], pos2[1], pos2[2] + amount)
                connection.selectPos1 = (pos1[0], pos1[1], pos1[2] + amount)
        else:
            if 'north' in args:
                if pos1[1] < pos2[1]:
                    connection.selectPos1 = (
                     pos1[0], pos1[1] - amount, pos1[2])
                    connection.selectPos2 = (pos2[0], pos2[1] - amount, pos2[2])
                else:
                    connection.selectPos2 = (
                     pos2[0], pos2[1] - amount, pos2[2])
                    connection.selectPos1 = (pos1[0], pos1[1] - amount, pos1[2])
            else:
                if 'south' in args:
                    if pos1[1] > pos2[1]:
                        connection.selectPos1 = (
                         pos1[0], pos1[1] + amount, pos1[2])
                        connection.selectPos2 = (pos2[0], pos2[1] + amount, pos2[2])
                    else:
                        connection.selectPos2 = (
                         pos2[0], pos2[1] + amount, pos2[2])
                        connection.selectPos1 = (pos1[0], pos1[1] + amount, pos1[2])
                else:
                    if 'east' in args:
                        if pos1[0] > pos2[0]:
                            connection.selectPos1 = (
                             pos1[0] + amount, pos1[1], pos1[2])
                            connection.selectPos2 = (pos2[0] + amount, pos2[1], pos2[2])
                        else:
                            connection.selectPos2 = (
                             pos2[0] + amount, pos2[1], pos2[2])
                            connection.selectPos1 = (pos1[0] + amount, pos1[1], pos1[2])
                    elif 'west' in args:
                        if pos1[0] < pos2[0]:
                            connection.selectPos1 = (
                             pos1[0] - amount, pos1[1], pos1[2])
                            connection.selectPos2 = (pos2[0] - amount, pos2[1], pos2[2])
                        else:
                            connection.selectPos2 = (
                             pos2[0] - amount, pos2[1], pos2[2])
                            connection.selectPos1 = (pos1[0] - amount, pos1[1], pos1[2])

@command('expand')
@player_only
def expand(connection, *args):
    pos1 = connection.selectPos1
    pos2 = connection.selectPos2
    if len(args) < 2:
        print('error')
        return
    if args[0] not in ('up', 'down', 'north', 'east', 'south', 'west'):
        print('error')
        return
    else:
        try:
            amount = int(args[1])
        except Exception as E:
            print('error')
            return

        if None in (pos1, pos2):
            connection.send_chat('You are missing a position, try /sel to see your positions')
            return
        if 'up' in args:
            if pos1[2] < pos2[2]:
                connection.selectPos1 = (
                 pos1[0], pos1[1], pos1[2] - amount)
            else:
                connection.selectPos2 = (
                 pos2[0], pos2[1], pos2[2] - amount)
            return
        if 'down' in args:
            if pos1[2] > pos2[2]:
                connection.selectPos1 = (
                 pos1[0], pos1[1], pos1[2] + amount)
            else:
                connection.selectPos2 = (
                 pos2[0], pos2[1], pos2[2] + amount)
        else:
            if 'north' in args:
                if pos1[1] < pos2[1]:
                    connection.selectPos1 = (
                     pos1[0], pos1[1] - amount, pos1[2])
                else:
                    connection.selectPos2 = (
                     pos2[0], pos2[1] - amount, pos2[2])
            else:
                if 'south' in args:
                    if pos1[1] > pos2[1]:
                        connection.selectPos1 = (
                         pos1[0], pos1[1] + amount, pos1[2])
                    else:
                        connection.selectPos2 = (
                         pos2[0], pos2[1] + amount, pos2[2])
                else:
                    if 'east' in args:
                        if pos1[0] > pos2[0]:
                            connection.selectPos1 = (
                             pos1[0] + amount, pos1[1], pos1[2])
                        else:
                            connection.selectPos2 = (
                             pos2[0] + amount, pos2[1], pos2[2])
                    elif 'west' in args:
                        if pos1[0] < pos2[0]:
                            connection.selectPos1 = (
                             pos1[0] - amount, pos1[1], pos1[2])
                        else:
                            connection.selectPos2 = (
                             pos2[0] - amount, pos2[1], pos2[2])

@command('set')
@player_only
def set(connection, *args):
    pos1 = connection.selectPos1
    pos2 = connection.selectPos2
    if pos1 is None or pos2 is None:
        connection.send_chat('You are missing a position, try /sel to see your positions')
        return
    block_action = BlockAction()
    block_action.value = DESTROY_BLOCK
    block_action.player_id = 32
    set_color = SetColor()
    set_color.value = connection.selectColor if connection.selectColor is not None else 0x707070
    set_color.player_id = 32
    map = connection.protocol.map
    n = 0
    for x in range(*(pos1[0], pos2[0] + 1) if pos1[0] < pos2[0] else (pos2[0], pos1[0] + 1)):
        block_action.x = x
        for y in range(*(pos1[1], pos2[1] + 1) if pos1[1] < pos2[1] else (pos2[1], pos1[1] + 1)):
            block_action.y = y
            for z in range(*(pos1[2], pos2[2] + 1) if pos1[2] < pos2[2] else (pos2[2], pos1[2] + 1)):
                block_action.z = z
                if 'air' in args:
                    if map.get_point(x, y, z):
                        connection.protocol.broadcast_contained(block_action)
                        map.remove_point(x, y, z)
                        n += 1
                        continue
                else:
                    if not map.get_point(x, y, z):
                        connection.protocol.broadcast_contained(block_action)
                    if map.get_point(x, y, z):
                        block_action.value = BUILD_BLOCK
                        connection.protocol.broadcast_contained(block_action)
                    connection.protocol.broadcast_contained(set_color)
                    ctuple = (set_color.value >> 16 & 255, set_color.value >> 8 & 255, set_color.value & 255)
                    map.set_point(x, y, z, ctuple)
                n += 1

    connection.send_chat('set %s blocks' % n)

def apply_script(protocol, connection, config):

    class worldEditConnection(connection):
        selectPos1 = None
        selectPos2 = None
        selectColor = None

        def on_block_destroy(self, x, y, z, value):
            connection.on_block_destroy(self, x, y, z, value)

        def on_block_build_attempt(self, x, y, z):
            connection.on_block_build_attempt(self, x, y, z)

    class worldEditProtocol(protocol):
        pass

    return (
     worldEditProtocol, worldEditConnection)