from piqueserver.commands import command, player_only
from math import floor, ceil, sqrt
from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from pyspades.contained import BlockAction, SetColor
from random import random

DIRT_COLOR = (101, 65, 40)

availableModes = ("cuboid", "ellipsoid", "cyl")
availableBrushes = ("wand", "sphere", "smooth", "paint", "noise", "ground", "surface", "blend", "terrain")

def colorTupleToInt(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)
    return r*(256**2) + g*256 + b

def colorIntToTuple(n):
    n = int(n)
    r = (n>>16) & 0b11111111
    g = (n>>8) & 0b11111111
    b = n & 0b11111111
    return (r,g,b)

@command('pos')
@player_only
def displayPos(connection):
    pos = connection.get_location()
    connection.send_chat("Your position: %s" %(str(floor(pos[0])) + ", " + str(floor(pos[1])) + ", " + str(floor(pos[2]))))

@command('posh', 'ph')
@player_only
def displayHPos(connection):
    hit = connection.world_object.cast_ray(512)
    connection.send_chat("Looking at position: %s" %(str(floor(hit[0])) + ", " + str(floor(hit[1])) + ", " + str(floor(hit[2]))))

@command('mode')
@player_only
def setMode(connection, *args):
    if(len(args)==0):
        connection.send_chat("Current mode: %s, possible modes: %s" %(connection.mode, availableModes))
    elif(args[0].lower() in availableModes):
        connection.send_chat("Mode set to %s" %(args[0].lower()))
        connection.mode = args[0].lower()

def connectionAttrFloatChanger(connection, attr, *args):
    if(len(args)==0):
        connection.send_chat("Current %s: %s" %(attr, getattr(connection, attr)))
    else:
        try:
            setattr(connection, attr, float(args[0]))
            connection.send_chat("%s set to: %s" %(attr, getattr(connection, attr)))
        except ValueError as ver:
            connection.send_chat("Invalid input")
            return
def connectionAttrIntChanger(connection, attr, *args):
    if(len(args)==0):
        connection.send_chat("Current %s: %s" %(attr, getattr(connection, attr)))
    else:
        try:
            setattr(connection, attr, int(args[0]))
            connection.send_chat("%s set to: %s" %(attr, getattr(connection, attr)))
        except ValueError as ver:
            connection.send_chat("Invalid input")
            return

@command('brushsize')
@player_only
def setBrushSize(connection, *args):
    connectionAttrIntChanger(connection, "brushSize", *args)
    
@command('smoothstr')
@player_only
def setSmoothStr(connection, *args):
    connectionAttrFloatChanger(connection, "smoothStr", *args)
    
@command('brushrez')
@player_only
def setBrushRez(connection, *args):
    connectionAttrIntChanger(connection, "brushRez", *args)
    
@command('brush')
@player_only    
def setBrush(connection, *args):
    if(len(args)==0):
        connection.brushActive = not connection.brushActive
        connection.send_chat("Brush set to %s, current mode: %s" %("active" if connection.brushActive else "inactive", connection.brushMode))
    else:
        connection.brushActive = True
        if(args[0].lower() in availableBrushes):
            connection.send_chat("Brush mode set to %s" %(args[0].lower()))
            connection.brushMode = args[0].lower()

@command('color', 'c')
@player_only
def setColor(connection, *args):
    if len(args) == 0:
        c = connection.WEColor
        if c is not None:
            r, g, b = colorIntToTuple(c)
            connection.send_chat(str(c) + " or " + str((r, g, b)) + ", or 0x" + hex(r)[2:].zfill(2).upper() + hex(g)[2:].zfill(2).upper() + hex(b)[2:].zfill(2).upper())
        else:
            connection.send_chat('You havent set a color yet! use /color or /c')
    else:
        if len(args) == 1:
            try:
                hexInt = int('0x' + args[0].upper(), 16)
                if 0 < hexInt < 16777215:
                    connection.WEColor = hexInt
            except ValueError as ver:
                connection.send_chat('Error, are you trying to input hex? ie: ffa71a?')
        elif len(args) == 3:
            try:
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
                connection.WEColor = colorTupleToInt(r, g, b)
            except ValueError as ver:
                connection.send_chat('There was an error.')
        else:
            connection.send_chat('Invalid input')

@command('colorh', 'ch')
@player_only
def colorh(connection, *args):
    hit = connection.world_object.cast_ray(512)
    color = connection.protocol.map.get_point( *hit )[1]
    if(color is None):
        connection.send_chat("You are looking at no color")
    else:
        connection.send_chat("Color: %s, or 0x%s" %(color, hex(color[0])[2:].zfill(2).upper() + hex(color[1])[2:].zfill(2).upper() + hex(color[2])[2:].zfill(2).upper()))

@command('sel')
@player_only
def printSel(connection):
    connection.send_chat(str(connection.pos1))
    connection.send_chat(str(connection.pos2))

@command('warp')
@player_only
def warp(connection, *args):
    if len(args)==2:
        try:
            x = int(args[0])
            y = int(args[1])
            z = connection.protocol.map.get_z(x,y)
            connection.set_location((x, y, z))
            return 
        except Exception as E:
            connection.send_chat("Invalid input")
    if len(args) == 3:
        try:
            x = int(args[0])
            y = int(args[1])
            z = int(args[2])
            connection.set_location((x, y, z))
            return
        except Exception as E:
            connection.send_chat("Invalid input")

@command('warph', 'wh')
@player_only
def warph(connection):
    hit = (connection.world_object.cast_ray(512))
    x,y,z = hit
    z -= 2
    connection.set_location( (x,y,z) )

@command('pos1')
@player_only
def pos1(connection):
    loc = connection.get_location()
    loc = (floor(loc[0]), floor(loc[1]), floor(loc[2]))
    connection.pos1 = loc
    connection.send_chat('Selected pos: ' + str(loc))

@command('pos2')
@player_only
def pos2(connection):
    loc = connection.get_location()
    loc = (floor(loc[0]), floor(loc[1]), floor(loc[2]))
    connection.pos2 = loc
    connection.send_chat('Selected pos: ' + str(loc))

@command('hpos1')
@player_only
def hpos1(connection):
    hit = connection.world_object.cast_ray(128)
    if hit is not None:
        connection.pos1 = hit
        connection.send_chat('Selected pos: ' + str(hit))
    else:
        return

@command('hpos2')
@player_only
def hpos2(connection):
    hit = connection.world_object.cast_ray(128)
    if hit is not None:
        connection.pos2 = hit
        connection.send_chat('Selected pos: ' + str(hit))
    else:
        return

@command('desel')
@player_only
def desel(connection):
    connection.pos1 = None
    connection.pos2 = None
    
@command('chunk')
@player_only
def selChunk(connection):
    position = connection.get_location()
    position = (floor(position[0]), floor(position[1]), floor(position[2]))
    x = floor(position[0]/64)*64
    y = floor(position[1]/64)*64
    pos1 = (x,y,0)
    pos2 = (x+64,y+64,64)
    connection.pos1 = pos1
    connection.pos2 = pos2

@command('wand')
@player_only
def activateWand(connection):
    connection.brushActive = not connection.brushActive
    connection.brushMode = "wand"
    if(connection.brushActive):
        connection.send_chat("Brush set to wand mode")
    else:
        connection.send_chat("Brush mode disabled")

@command('expand')
@player_only
def expand(connection, *args):
    if(len(args)!=2):
        connection.send_chat("Invalid input")
        return
    try:
        offset = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)][['up', 'down', 'north', 'east', 'south', 'west'].index(args[0])]
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    try:
        amount = int(args[1])
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    if(connection.pos1 is None or connection.pos2 is None):
        return
    pos1,pos2 = sort_positions(connection.pos1, connection.pos2)
    pos1 = [*pos1]
    pos2 = [*pos2]
    for i in range(0,3):
        off = offset[i]
        if(off>0):
            pos2[i] += off * amount
        elif(off<0):
            pos1[i] += off * amount
        else:
            continue
    connection.pos1, connection.pos2 = tuple(pos1),tuple(pos2)

@command('shrink')
@player_only
def shrink(connection, *args):
    if(len(args)!=2):
        connection.send_chat("Invalid input")
        return
    try:
        offset = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)][['up', 'down', 'north', 'east', 'south', 'west'].index(args[0])]
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    try:
        amount = int(args[1])
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    if(connection.pos1 is None or connection.pos2 is None):
        return
    pos1,pos2 = sort_positions(connection.pos1, connection.pos2)
    pos1 = [*pos1]
    pos2 = [*pos2]
    for i in range(0,3):
        off = offset[i]
        if(off>0):
            pos2[i] -= off * amount
        elif(off<0):
            pos1[i] -= off * amount
        else:
            continue
    connection.pos1, connection.pos2 = tuple(pos1),tuple(pos2)
            
@command('shift')
@player_only
def shift(connection, *args):
    if(len(args)!=2):
        return
    try:
        offset = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)][['up', 'down', 'north', 'east', 'south', 'west'].index(args[0])]
    except ValueError as ver:
        return
    try:
        amount = int(args[1])
    except ValueError as ver:
        return
    if(connection.pos1 is None or connection.pos2 is None):
        return
    pos1,pos2 = sort_positions(connection.pos1, connection.pos2)
    pos1 = [*pos1]
    pos2 = [*pos2]
    for i in range(0,3):
        off = offset[i]
        if(off!=0):
            connection.pos1[i] += off * amount
            connection.pos2[i] += off * amount
        else:
            continue
    connection.pos1, connection.pos2 = tuple(pos1),tuple(pos2)

@command('cyl')
@player_only
def createCyl(connection, *args):
    if(len(args)!=2):
        connection.send_chat("Invalid input")
        return
    try:
        radius = int(args[0])
        height = int(args[1])
    except ValueError as error:
        connection.send_chat("Invalid input")
        return
    blocks = []
    pos1 = [*connection.get_location()]
    pos2 = [*connection.get_location()]
    pos1[0] -= radius
    pos1[1] -= radius
    pos1[2] -= 1
    pos2[0] += radius
    pos2[1] += radius
    pos2[2] -= height
    
    pos1 = [round(pos1[0]), round(pos1[1]), round(pos1[2])]
    pos2 = [round(pos2[0]), round(pos2[1]), round(pos2[2])]
    blocks = []
    for position in getCylPositions(pos1,pos2):
        blocks.append( (True, position, connection.WEColor) )
    connection.protocol.constructSelection(blocks)
    
@command('stack')
@player_only
def stack(connection, *args):
    if(not (len(args)>=1)):
        connection.send_chat("Missing arguments")
        return
    try:
        offset = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)][['up', 'down', 'north', 'east', 'south', 'west'].index(args[0])]
    except ValueError as ver:
        connection.send_chat("Invalid arguments")
        return
    try:
        amount = int(args[1])
    except IndexError as ier:
        amount = 1
    except ValueError as ver:
        connection.send_chat("Invalid Arguments")
        return
    pos1 = connection.pos1
    pos2 = connection.pos2
    if pos1 is None or pos2 is None:
        connection.send_chat('You are missing a position, try /sel to see your positions')
        return
    map = connection.protocol.map
    blocks = []
    pos1,pos2 = sort_positions(connection.pos1, connection.pos2)
    for x in range(pos1[0],pos2[0]+1):
        for y in range(pos1[1],pos2[1]+1):
            for z in range(pos1[2],pos2[2]+1):
                block = map.get_point(x,y,z)
                blocks.append((block[0], (x,y,z), block[1]))
    if(-1 in offset):
        index = offset.index(-1)
    elif(1 in offset):
        index = offset.index(1)
    else: return
    height = pos2[index]-pos1[index]
    
    for run in range(0,amount):
        newBlocks = []
        for block in blocks:
            pos = [*block[1]]
            for i in range(0,3):
                off = offset[i]
                if(off!=0):
                    pos[i] += off * (height+1) * (run+1)
                else:
                    continue
            c = colorTupleToInt(*block[2]) if block[2] is not None else None
            newBlocks.append((block[0], tuple(pos), c))
        connection.protocol.constructSelection(newBlocks)
    
def getCuboidPositions(pos1, pos2):
    pos1, pos2 = sort_positions(pos1, pos2)
    positions = []
    for x in range(pos1[0],pos2[0]+1):
        for y in range(pos1[1],pos2[1]+1):
            for z in range(pos1[2],pos2[2]+1):
                positions.append( (x,y,z) )
    return positions

def getEllipsoidPositions(pos1, pos2):
    pos1, pos2 = sort_positions(pos1, pos2)
    center = (floor((pos2[0]+pos1[0])/2), floor((pos2[1]+pos1[1])/2), floor((pos2[2]+pos1[2])/2))
    positions = []
    a = ((pos2[0] - pos1[0]) + 1)/2
    b = ((pos2[1] - pos1[1]) + 1)/2
    c = ((pos2[2] - pos1[2]) + 1)/2
    for x in range(pos1[0],pos2[0]+1):
        for y in range(pos1[1],pos2[1]+1):
            for z in range(pos1[2],pos2[2]+1):
                value = ( ((x-center[0])**2)/ceil(a**2) + ((y-center[1])**2)/ceil(b**2) + ((z-center[2])**2)/ceil(c**2))
                if(value <= 1):
                    positions.append( (x,y,z) )
    return positions
    
def getCylPositions(pos1, pos2):
    pos1, pos2 = sort_positions(pos1, pos2)
    center = (floor((pos2[0]+pos1[0])/2), floor((pos2[1]+pos1[1])/2), floor((pos2[2]+pos1[2])/2))
    positions = []
    a = ((pos2[0] - pos1[0]) + 1)/2
    b = ((pos2[1] - pos1[1]) + 1)/2
    for x in range(pos1[0],pos2[0]+1):
        for y in range(pos1[1],pos2[1]+1):
            for z in range(pos1[2],pos2[2]+1):
                value = ( ((x-center[0])**2)/ceil(a**2) + ((y-center[1])**2)/ceil(b**2))
                if(value <= 1):
                    positions.append( (x,y,z) )
    return positions
    
def getPositions(pos1, pos2, mode):
    try:
        return (getCuboidPositions, getEllipsoidPositions, getCylPositions)[availableModes.index(mode)](pos1, pos2)
    except ValueError as ver:
        print("VALUE ERROR: " + str(ver))
        return getCuboidPositions(pos1,pos2)

def getNeighbors(pos, resolution, map):
    neighbors = 0
    for x in range(pos[0]-resolution, pos[0]+resolution+1):
        for y in range(pos[1]-resolution, pos[1]+resolution+1):
            for z in range(pos[2]-resolution, pos[2]+resolution+1):
                if( x!=pos[0] or y!=pos[1] or z!=pos[2]):
                    if(not (0<=x<=512 or 0<=y<=512 or 0<=y<=64)):
                        neighbors += 1
                    elif(map.get_point(x,y,z)[0]):
                        neighbors += 1
    return neighbors
    
def getNeighborColors(pos, resolution, map): #DUMPY RIGHT NOW
    colors = []
    for x in range(pos[0]-resolution, pos[0]+resolution+1):
        for y in range(pos[1]-resolution, pos[1]+resolution+1):
            for z in range(pos[2]-resolution, pos[2]+resolution+1):
                point = map.get_point(x,y,z)
                if(point[0]):
                    if(point[1] == (0,0,0)):
                        colors.append(DIRT_COLOR)
                    else:
                        colors.append(point[1])
    n = len(colors)
    if(n==0):
        return None
    r,g,b = 0,0,0
    for color in colors:
        r += (color[0]**2)
        g += (color[1]**2)
        b += (color[2]**2)
    r /= n
    g /= n
    b /= n
    r = sqrt(r)
    g = sqrt(g)
    b = sqrt(b)
    return (r,g,b)
    
@command('set')
@player_only
def set(connection, *args):
    pos1 = connection.pos1
    pos2 = connection.pos2
    if pos1 is None or pos2 is None:
        connection.send_chat('You are missing a position, try /sel to see your positions')
        return
    blocks = []
    pos1,pos2 = sort_positions(connection.pos1, connection.pos2)
    for position in getPositions(pos1, pos2, connection.mode):
        if("air" in args):
            blocks.append( (False, position, connection.WEColor) )
        else:
            blocks.append( (True, position, connection.WEColor) )
    connection.protocol.constructSelection(blocks)

def sort_positions(pos1, pos2):
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2
    nx1 = min(x1, x2)
    nx2 = max(x1, x2)
    ny1 = min(y1, y2)
    ny2 = max(y1, y2)
    nz1 = min(z1, z2)
    nz2 = max(z1, z2)
    return ((nx1, ny1, nz1),(nx2, ny2, nz2))

@command('copy')
@player_only
def copy(connection):
    pos1 = connection.pos1
    pos2 = connection.pos2
    if pos1 is None or pos2 is None:
        connection.send_chat('You are missing a position, try /sel to see your positions')
        return
    blocks = []
    pos1,pos2 = sort_positions(pos1, pos2)
    location = connection.get_location()
    map = connection.protocol.map
    for position in getCuboidPositions(pos1,pos2):
        point = map.get_point(*position)
        x,y,z = position
        x-=floor(location[0])
        y-=floor(location[1])
        z-=floor(location[2])
        position = (x,y,z)
        solid = point[0]
        color = point[1]
        if(color is not None):
            if(color == (0,0,0)):
                color = DIRT_COLOR
            color = colorTupleToInt(*point[1])
        blocks.append( (solid, position, color) )
    connection.copyBlocks = blocks

@command('paste')
@player_only
def paste(connection):
    location = connection.get_location()
    blocks = connection.copyBlocks
    if(blocks is None):
        return
    updateBlocks = []
    for block in blocks:
        position = block[1]
        x,y,z = position
        x+=floor(location[0])
        y+=floor(location[1])
        z+=floor(location[2])
        position = (x,y,z)
        color = block[2]
        updateBlocks.append( (block[0], position, color) )
    connection.protocol.constructSelection(updateBlocks)

def apply_script(protocol, connection, config):
    class worldEditConnection(connection):
        mode = "cuboid"
        WEColor = 0x707070
        pos1 = None
        pos2 = None
        brushActive = False
        brushMode = "wand"
        brushSize = 5
        smoothStr = 0.5
        brushRez = 1
        copyBlocks = None
        def on_shoot_set(self, fire):
            if(fire and self.brushActive):
                hit = self.world_object.cast_ray(128)
                if(hit):
                    if(self.brushMode == "wand"):
                        self.pos1 = hit
                        self.send_chat("new position: (%s,%s)" %(self.pos1, self.pos2))
                    
                    map = self.protocol.map
                    pos1 = [*hit]
                    pos2 = [*hit]
                    value = self.brushSize
                    pos1[0] -= value
                    pos1[1] -= value
                    pos1[2] -= value
                    pos2[0] += value
                    pos2[1] += value
                    pos2[2] += value
                    brushPositions = getEllipsoidPositions(pos1,pos2)
                    updateBlocks = []
                    if(self.brushMode == "sphere"):
                        for position in brushPositions:
                            updateBlocks.append( (True, position, self.WEColor) )
                        self.protocol.constructSelection(updateBlocks)
                    elif(self.brushMode == "smooth"):
                        for position in brushPositions:
                            neighbors = getNeighbors(position, self.brushRez, map)
                            if(neighbors > (((self.brushRez*2)+1)**3)*self.smoothStr): #Should be a block
                                neighborColor = getNeighborColors(position, 2, map)
                                color = self.WEColor
                                if(neighborColor is not None):
                                    color = colorTupleToInt(*neighborColor)
                                updateBlocks.append( (True, position, color) )
                            else:#Should be no block
                                if(map.get_point(*position)[0]): #But there is
                                    updateBlocks.append( (False, position, self.WEColor) )
                        self.protocol.constructSelection(updateBlocks)
                    elif(self.brushMode == "blend"):
                        for position in brushPositions:
                            if(map.get_point(*position)[0]):
                                neighborColor = getNeighborColors(position, self.brushRez, map)
                                if(neighborColor is None):
                                    continue
                                color = colorTupleToInt(*neighborColor)
                                updateBlocks.append( (True, position, color) )
                        self.protocol.constructSelection(updateBlocks)
                    elif(self.brushMode == "paint"):
                        for position in brushPositions:
                            if(map.get_point(*position)[0]):
                                updateBlocks.append( (True, position, self.WEColor) )
                        self.protocol.constructSelection(updateBlocks)
                    elif(self.brushMode == "noise"):
                        for position in brushPositions:
                            point = map.get_point(*position)
                            if(point[0]):
                                color = point[1]
                                if(color == (0,0,0)):
                                    color = DIRT_COLOR
                                r,g,b = color
                                shade = (random()-0.5)*10
                                r += shade
                                g += shade
                                b += shade
                                r = min(255,max(0,r))
                                g = min(255,max(0,g))
                                b = min(255,max(0,b))
                                r,g,b = int(r), int(g), int(b)
                                updateBlocks.append( (True, position, colorTupleToInt(r,g,b)) )
                        self.protocol.constructSelection(updateBlocks)
                    elif(self.brushMode == "surface"):
                        for position in brushPositions:
                            neighbors = getNeighbors(position, 1, map)
                            if(map.get_point(*position)[1]):
                                if(neighbors<26):
                                    updateBlocks.append( (True, position, self.WEColor) )
                        self.protocol.constructSelection(updateBlocks)
                    elif(self.brushMode == "ground"):
                        for position in brushPositions:
                            neighbors = getNeighbors(position, self.brushRez, map)
                            if(neighbors==(((self.brushRez*2)+1)**3) - 1):
                                updateBlocks.append( (True, position, self.WEColor) )
                    elif(self.brushMode == "terrain"):
                        for position in brushPositions:
                            neighbors = getNeighbors(position, 1, map)
                            if(map.get_point(*position)[1]):
                                if(neighbors<26): #It is a surface block
                                    slopeField = []
                                    for i, x in enumerate(range(position[0]-1, position[0]+1)):
                                        for j, y in enumerate(range(position[1]-1, position[1]+1)):
                                            slopeField.append(map.get_z(x,y))
                                    slope = max(slopeField) - min(slopeField)
                                    if(slope > 5):
                                        r,g,b = 0x70, 0x70, 0x70
                                    else:
                                        off = (random()-0.5)*10
                                        r = min(255,max(0,off))
                                        g = min(255,max(0,0x80 + off))
                                        b = min(255,max(0,off))
                                    updateBlocks.append( (True, position, colorTupleToInt(r,g,b)) )
                        self.protocol.constructSelection(updateBlocks)


                        self.protocol.constructSelection(updateBlocks)
                    connection.send_chat(self, "Brush complete")
            connection.on_shoot_set(self, fire)
            
        def on_secondary_fire_set(self, fire): 
            if(fire and self.brushActive):
                hit = self.world_object.cast_ray(128)
                if(hit):
                    if(self.brushMode == "wand"):
                        self.pos2 = hit
                        self.send_chat("new position: (%s,%s)" %(self.pos1, self.pos2))
            connection.on_secondary_fire_set(self, fire)
    class worldEditProtocol(protocol):
        def constructSelection(self, blockList):
            map = self.map
            block_action = BlockAction()
            block_action.value = BUILD_BLOCK
            block_action.player_id = 32
            set_color = SetColor()
            set_color.player_id = 32
            set_color.value = 0x707070
            for block in blockList:
                blockExists = block[0]
                x = block[1][0]
                y = block[1][1]
                z = block[1][2]
                block_action.x, block_action.y, block_action.z = x, y, z
                if(not (0<=x<=512 or 0<=y<=512 or 0<=y<=64)):
                    continue
                color = block[2]
                if(blockExists): #IF THERE SHOULD BE A BLOCK
                    if(map.get_point(x,y,z)[0]):#IF THERE IS A BLOCK
                        map.remove_point(x, y, z)
                    #if(not map.get_point(x,y,z)[0]): #IF THERE IS NO BLOCK
                    block_action.value = BUILD_BLOCK
                    self.broadcast_contained(block_action)
                    set_color.value = color
                    map.set_point(x, y, z, colorIntToTuple(color))
                    self.broadcast_contained(set_color)
                else: #IF THERE SHOULD BE NO BLOCK
                    if(z>=63):
                        continue
                    if(map.get_point(x,y,z)[0]): #THERE IS A BLOCK
                        block_action.value = DESTROY_BLOCK
                        self.broadcast_contained(block_action)
                        map.remove_point(x, y, z)
                        
    return (worldEditProtocol, worldEditConnection)