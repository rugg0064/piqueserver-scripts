from piqueserver.commands import command, player_only
from math import floor, ceil, sqrt
from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from pyspades.contained import BlockAction, SetColor

availableModes = ("cuboid", "ellipsoid", "cyl")
availableBrushes = ("wand", "sphere", "smooth")
def colorTupleToInt(r, g, b):
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

@command('mode')
@player_only
def mode(connection, *args):
    if(len(args)==0):
        connection.send_chat("Current mode: %s, possible modes: %s" %(connection.mode, availableModes))
    elif(args[0].lower() in availableModes):
        connection.send_chat("Mode set to %s" %(args[0].lower()))
        connection.mode = args[0].lower()

@command('brushsize')
@player_only
def mode(connection, *args):
    if(len(args)==0):
        connection.send_chat("Current brush size: %s" %(str(connection.brushSize)))
    else:
        try:
            connection.brushSize = int(args[0])
        except ValueError as ver:
            connection.send_chat("Invalid input")
            return

@command('sel')
@player_only
def printSel(connection):
    connection.send_chat(str(connection.pos1))
    connection.send_chat(str(connection.pos2))

@command('warp')
@player_only
def warp(connection, *args):
    print('warp')
    if len(args)==2:
        try:
            x = int(args[0])
            y = int(args[1])
            z = connection.protocol.map.get_z(x,y)
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

@command('warph')
@player_only
def warph(connection):
    connection.set_location( (connection.world_object.cast_ray(512)) )

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

@command('brush')
@player_only    
def activateBrush(connection, *args):
    if(len(args)==0):
        connection.brushActive = not connection.brushActive
        connection.send_chat("Brush set to %s, current mode: " %("active" if connection.brushActive else "inactive", connection.brushMode))
    else:
        connection.brushActive = True
        if(args[0].lower() in availableBrushes):
            connection.send_chat("Brush mode set to %s" %(args[0].lower()))
            connection.brushMode = args[0].lower()
        
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
            pos1[i] += off * amount
            pos2[i] += off * amount
        else:
            continue
    connection.pos1, connection.pos2 = tuple(pos1),tuple(pos2)

@command('cyl')
@player_only
def createCyl(connection, *args):
    if(len(args)!=2):
        print("bad input")
        return
    try:
        radius = int(args[0])
        height = int(args[1])
    except ValueError as error:
        print("bad input")
        return
    blocks = []
    print("aaa")
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
                #blocks.append( (True, (x,y,z), connection.WEColor) )
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

def getNeighbors(pos, map):
    neighbors = 0
    for x in range(pos[0]-1, pos[0]+1+1):
        for y in range(pos[1]-1, pos[1]+1+1):
            for z in range(pos[2]-1, pos[2]+1+1):
                if( x!=pos[0] or y!=pos[1] or z!=pos[2]):
                    if(map.get_point(x,y,z)[0]):
                        neighbors += 1
    return neighbors
    
def getNeighborColors(pos, map):
    colors = []
    for x in range(pos[0]-1, pos[0]+1+1):
        for y in range(pos[1]-1, pos[1]+1+1):
            for z in range(pos[2]-1, pos[2]+1+1):
                point = map.get_point(x,y,z)
                if(point[0]):
                    if(point[1] != (0,0,0)):
                        colors.append(point[1])
    n = len(colors)
    if(n==0):
        return None
    r,g,b = 0,0,0
    for color in colors:
        r += color[0]**2
        g += color[1]**2
        b += color[2]**2
    r /= n
    r = sqrt(r)
    g /= n
    g = sqrt(g)
    b /= n
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

@command('color', 'c')
@player_only
def setColor(connection, *args):
    if len(args) == 0:
        c = connection.WEColor
        if c is not None:
            r, g, b = colorIntToTuple(c)
            connection.send_chat(str(c) + " or " + str((r, g, b)) + ", or 0x" + hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2))
        else:
            connection.send_chat('You havent set a color yet! use /color or /c')
    else:
        if len(args) == 1:
            try:
                hexInt = int('0x' + args[0], 16)
                if 0 < hexInt < 16777215:
                    connection.WEColor = hexInt
            except ValueError as ver:
                connection.send_chat('Error, are you trying to input hex? ie: ffa71a?')
        elif len(args) == 3:
            try:
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
                connection.WEColor = make_color(r, g, b)
            except ValueError as ver:
                print(ver)
                connection.send_chat('There was an error.')
        else:
            connection.send_chat('Invalid input')

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

@command('smoothstr')
@player_only
def smoothSize(connection, *args):
    if(len(args)==0):
        connection.send_chat("Current brush size: %s" %(str(connection.brushSize)))
    else:
        try:
            connection.smoothStr = int(args[0])
        except ValueError as ver:
            connection.send_chat("Invalid input")
            return

def apply_script(protocol, connection, config):
    class worldEditConnection(connection):
        mode = "cyl"
        WEColor = 0x707070
        pos1 = None
        pos2 = None
        brushActive = False
        brushMode = "wand"
        brushSize = 0
        smoothStr = 15
        def on_shoot_set(self, fire):
            if(fire and self.brushActive):
                hit = self.world_object.cast_ray(128)
                if(hit):
                    if(self.brushMode == "wand"):
                        self.pos1 = hit
                        self.send_chat("new position: (%s,%s)" %(self.pos1, self.pos2))
                    if(self.brushMode == "sphere"):
                        pos1 = [*hit]
                        pos2 = [*hit]
                        value = self.brushSize
                        pos1[0] -= value
                        pos1[1] -= value
                        pos1[2] -= value
                        pos2[0] += value
                        pos2[1] += value
                        pos2[2] += value
                        blocks = []
                        for position in getEllipsoidPositions(pos1,pos2):
                            blocks.append( (True, position, self.WEColor) )
                        self.protocol.constructSelection(blocks)
                    if(self.brushMode == "smooth"):
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
                        positions = getEllipsoidPositions(pos1,pos2)
                        shouldExist = []
                        for position in positions:
                            neighbors = getNeighbors(position, map)
                            shouldExist.append(neighbors > self.smoothStr)   
                        blocks = []
                        for i in range(0, len(positions)):
                            '''
                            neighborColorResult = getNeighborColors(positions[i], map)
                            getPoint = map.get_point(*positions[i])
                            if(neighborColorResult):
                                color = colorTupleToInt(*neighborColorResult)
                            elif(getPoint[0]):
                                color = colorTupleToInt(*getPoint[1])
                            else:
                                color = self.WEColor
                            '''
                            color = self.WEColor
                            blocks.append( (shouldExist[i], positions[i], color) )
                        self.protocol.constructSelection(blocks)
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
                color = block[2]
                if(blockExists): #IF THERE SHOULD BE A BLOCK
                    if(map.get_point(x,y,z)[0]):#IF THERE IS A BLOCK
                        #block_action.value = DESTROY_BLOCK
                        #self.broadcast_contained(block_action)
                        map.remove_point(x, y, z)
                    #if(not map.get_point(x,y,z)[0]): #IF THERE IS NO BLOCK
                    block_action.value = BUILD_BLOCK
                    self.broadcast_contained(block_action)
                    set_color.value = color
                    map.set_point(x, y, z, colorIntToTuple(color))
                    self.broadcast_contained(set_color)
                else: #IF THERE SHOULD BE NO BLOCK
                    if(map.get_point(x,y,z)[0]): #THERE IS A BLOCK
                        block_action.value = DESTROY_BLOCK
                        self.broadcast_contained(block_action)
                        map.remove_point(x, y, z)
                        
    return (worldEditProtocol, worldEditConnection)