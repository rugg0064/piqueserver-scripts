from piqueserver.commands import command, player_only
from pyspades.common import get_color as colorIntToTuple, make_color as colorTupleToInt, to_coordinates
from math import floor

from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from pyspades.contained import BlockAction, SetColor

maxUndoRedo = 20
availableModes = ("cuboid", "ellipsoid", "cyl")
availableBrushes = ("wand", "sphere", "cube")

#All functions
'''
colorTupleToInt -- Replaced with pyspades.common
colorIntToTuple -- Replaced with pyspades.common


--Utility functions--
colorToHexString

--Everyday Things for general use --
warp -- Implemented
warph -- Implemented
colorh -- Implemented
displayPos  -- Implemented
displayHPos -- Implemented

--Else--

setMode
connectionAttrFloatChanger
connectionAttrIntChanger
setSmoothStr
setBrushRez
setBrushRez
setColor
printSel
pos1
pos2
hpos1
hpos2
desel
selChunk
activeteWand
expand
shrink
shift
createCyl
stack
get{}position cuboid,ellipsoid,cyl
getNeighbors
getNeighborColors
set
sort_positions
copy
paste
'''

class Color():
    def __init__(self, tuple=None, hex=None):
        if(hex is not None):
            c = colorIntToTuple(hex)
            self.r = c[0]
            self.g = c[1]
            self.b = c[2]
        elif(tuple is not None):
            self.r, self.g, self.b = tuple
    def __repr__(self):
        return str(self.getTuple())
    def getInt(self):
        return (self.r<<16) + (self.g<<8) + (self.b)
    def getTuple(self):
        return (self.r, self.g, self.b)
    def getHex(self):
        return "0x" + (hex(self.r)[2:].zfill(2) + hex(self.g)[2:].zfill(2) + hex(self.b)[2:].zfill(2)).upper()

#Reminder, VXL has functions get_point, set_point, 

#Basic Functions
offsetStrings = ['up', 'down', 'north', 'east', 'south', 'west']
offsets = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)]
def cardinalToOffset(cardinalString):
    return [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)][['up', 'down', 'north', 'east', 'south', 'west'].index(cardinalString)]
def colorToHexString(color):
    r = int(color[0])
    g = int(color[1])
    b = int(color[2])
    return "0x" + (hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2)).upper()
#Replaced with pyspades.common functions

#Commands for everyday use
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
@command('colorh', 'ch')
@player_only
def colorh(connection, *args):
    hit = connection.world_object.cast_ray(512)
    color = connection.protocol.map.get_point( *hit )[1]
    if(color is None):
        connection.send_chat("You are looking at no color")
    else:
        c = Color(tuple = color)
        connection.send_chat("Color: {} or {}".format(c.getTuple(), c.getHex()))
@command('colorpos', 'cp')
def colorp(connection, *args):
    if(len(args)!=3):
        return
        connection.send_chat("Invalid Input")
    try:
        x = int(args[0])
        y = int(args[1])
        z = int(args[2])
    except Exception as E:
        connection.send_chat("Invalid input")
        return
    color = connection.protocol.map.get_color(x,y,z)
    color = Color(tuple = color)
    if(color is None):
        connection.send_chat("({},{},{}) is no block there".format(x,y,z))
    else:
        connection.send_chat("({},{},{}) is color {} or {}".format(x,y,z,color.getTuple(),color.getHex()))
@command('warp')
@player_only
def warp(connection, *args):
    if len(args)==2:
        try:
            x = float(args[0])
            y = float(args[1])
            z = connection.protocol.map.get_z(x,y)-2
            connection.set_location((x, y, z))
            return 
        except Exception as E:
            connection.send_chat("Invalid input")
    if len(args) == 3:
        try:
            x = float(args[0])
            y = float(args[1])
            z = float(args[2])
            connection.set_location((x, y, z))
            return
        except Exception as E:
            connection.send_chat("Invalid input")
@command('warph', 'wh')
@player_only
def warph(connection):
    hit = (connection.world_object.cast_ray(512))
    if(hit is not None):
        x,y,z = hit
        z -= 2
        connection.set_location( (x,y,z) )


#Various ways to set positions
@command('selection','sel')
def printSelection(connection):
    connection.send_chat(str(connection.pos1))
    connection.send_chat(str(connection.pos2))
@command('sortSelection','sortsel','sl')
def sortSelection(connection):
    connection.pos1, connection.pos2 = connection.sortedPositions()
    connection.send_chat("Updated selection")
@command('pos1','p1')
def pos1(connection, *args):
    if(len(args)==3):
        try:
            x = int(args[0])
            y = int(args[1])
            z = int(args[2])
        except Exception as E:
            connection.send_chat("Invalid input")
            return
        connection.pos1 = (x,y,z)
        connection.send_chat("Selected pos: ({},{},{})".format(x,y,z))
        return
    elif(len(args)==0):
        loc = connection.get_location()
        loc = (floor(loc[0]), floor(loc[1]), floor(loc[2]))
        connection.pos1 = loc
        connection.send_chat("Selected pos {}".format(str(loc)))
        return
@command('pos2','p2')
def pos2(connection, *args):
    if(len(args)==3):
        try:
            x = int(args[0])
            y = int(args[1])
            z = int(args[2])
        except Exception as E:
            connection.send_chat("Invalid input")
            return
        connection.pos2 = (x,y,z)
        connection.send_chat("Selected pos: ({},{},{})".format(x,y,z))
        return
    elif(len(args)==0):
        loc = connection.get_location()
        loc = (floor(loc[0]), floor(loc[1]), floor(loc[2]))
        connection.pos2 = loc
        connection.send_chat("Selected pos {}".format(str(loc)))
        return
@command('hpos1')
@player_only
def hpos1(connection):
    hit = connection.world_object.cast_ray(128)
    if hit is not None:
        connection.pos1 = hit
        connection.send_chat("Selected pos: {}".format(hit))
    else:
        connection.send_chat("Didn't hit anything")
        return
@command('hpos2')
@player_only
def hpos1(connection):
    hit = connection.world_object.cast_ray(128)
    if hit is not None:
        connection.pos2 = hit
        connection.send_chat("Selected pos: {}".format(hit))
    else:
        connection.send_chat("Didn't hit anything")
        return
@command('chunk')
def selectChunk(connection):
    position = connection.get_location()
    position = (floor(position[0]), floor(position[1]), floor(position[2]))
    x = (position[0]//64)*64
    y = (position[1]//64)*64
    pos1 = (x,y,0)
    pos2 = (x+64,y+64,63)
    connection.pos1 = pos1
    connection.pos2 = pos2
    connection.send_chat("Selected current chunk ({})".format(to_coordinates(x,y)))

#Adjusting the selection
@command('shift')
@player_only
def shift(connection, *args):
    if(len(args)!=2):
        connection.send_chat("Invalid input")
        return
    in1 = args[0].lower()
    if(in1 not in offsetStrings):
        connection.send_chat("Invalid input")
        return
    try:
        amount = int(args[1])
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    if(connection.pos1 is None or connection.pos2 is None):
        connection.send_chat("You are missing at least one position")
        return
    offset = cardinalToOffset(in1)
    #print(offset)
    outPos1 = [0,0,0]
    outPos2 = [0,0,0]
    for i in range(0,3):
        current_offset = offset[i]
        outPos1[i] = connection.pos1[i] + (current_offset * amount)
        outPos2[i] = connection.pos2[i] + (current_offset * amount)
        
    connection.pos1, connection.pos2 = tuple(outPos1), tuple(outPos2)
    connection.send_chat("Your positions have been shifted {} {} blocks".format(in1, amount))
@command('expand')
@player_only
def expand(connection, *args):
    if(len(args)!=2):
        connection.send_chat("Invalid input")
        return
    in1 = args[0].lower()
    if(in1 not in offsetStrings):
        connection.send_chat("Invalid input")
        return
    try:
        amount = int(args[1])
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    if(connection.pos1 is None or connection.pos2 is None):
        connection.send_chat("You are missing at least one position")
        return
    offset = cardinalToOffset(in1)
    #print(offset)
    outPos1 = [*connection.pos1]
    outPos2 = [*connection.pos2]
    for i in range(0,3):
        if(offset[i] != 0):
            current_offset = offset[i]
            positive = current_offset > 0
            p1Greater = outPos1[i] > outPos2[i]
            if( (p1Greater and positive) or (not p1Greater and not positive) ):
                outPos1[i] += current_offset * amount
            else:
                outPos2[i] += current_offset * amount
            break
    connection.pos1, connection.pos2 = tuple(outPos1), tuple(outPos2)
    connection.send_chat("Your positions have been expanded {} {} blocks".format(in1, amount))
@command('shrink')
@player_only
def shrink(connection, *args):
    if(len(args)!=2):
        connection.send_chat("Invalid input")
        return
    in1 = args[0].lower()
    if(in1 not in offsetStrings):
        connection.send_chat("Invalid input")
        return
    try:
        amount = int(args[1])
    except ValueError as ver:
        connection.send_chat("Invalid input")
        return
    if(connection.pos1 is None or connection.pos2 is None):
        connection.send_chat("You are missing at least one position")
        return
    offset = cardinalToOffset(in1)
    #print(offset)
    outPos1 = [*connection.pos1]
    outPos2 = [*connection.pos2]
    for i in range(0,3):
        if(offset[i] != 0):
            current_offset = offset[i]
            positive = current_offset > 0
            p1Greater = outPos1[i] > outPos2[i]
            if( not ((p1Greater and positive) or (not p1Greater and not positive)) ):
                outPos1[i] += current_offset * amount
            else:
                outPos2[i] += current_offset * amount
            break
    connection.pos1, connection.pos2 = tuple(outPos1), tuple(outPos2)
    connection.send_chat("Your positions has shrunk {} {} blocks".format(in1, amount))

#Color settings
@command('color', 'c')
@player_only
def setColor(connection, *args):
    if len(args) == 0:
        c = connection.colorWE
        if c is not None:
            connection.send_chat("Color: {} or {}".format(c.getTuple(), c.getHex()))
    elif len(args) == 1:
        try:
            hexInt = int('0x' + args[0].upper(), 16)
            connection.colorWE = Color(hex = hexInt)
        except ValueError as ver:
            connection.send_chat('Error, are you trying to input hex? ie: ffa71a?')
    elif len(args) == 3:
        try:
            r = int(args[0])
            g = int(args[1])
            b = int(args[2])
            connection.colorWE = Color(tuple = (r,g,b))
        except ValueError as ver:
            connection.send_chat('There was an error.')
    else:
        connection.send_chat('Invalid input')

def getCylPositions(vector1,vector2):
    positionList = []
    center = ( (vector2[0]+vector1[0])/2, (vector2[1]+vector1[1])/2, (vector2[2]+vector1[2])/2 )
    a = ((vector2[0] - vector1[0]+1))//2
    b = ((vector2[1] - vector1[1]+1))//2
    for x in range(vector1[0], vector2[0]+1):
        for y in range(vector1[1], vector2[1]+1):
            for z in range(vector1[2], vector2[2]+1):
                value = ( ((x-center[0])**2)/(a**2) + ((y-center[1])**2)/(b**2))
                if(value <= 1):
                    positionList.append( (x,y,z) )
    return positionList
def getEllipsoidPositions(vector1, vector2):
    positionList = []
    center = ( (vector2[0]+vector1[0])/2, (vector2[1]+vector1[1])/2, (vector2[2]+vector1[2])/2 )
    a = ((vector2[0] - vector1[0]+1))//2
    b = ((vector2[1] - vector1[1]+1))//2
    c = ((vector2[2] - vector1[2]+1))//2
    for x in range(vector1[0], vector2[0]+1):
        for y in range(vector1[1], vector2[1]+1):
            for z in range(vector1[2], vector2[2]+1):
                value = ( ((x-center[0])**2)/(a**2) + ((y-center[1])**2)/(b**2) + ((z-center[2])**2)/(c**2))
                if(value <= 1):
                    positionList.append( (x,y,z) )
    return positionList
def getCuboidPositions(vector1, vector2): #vector1 < vector2 for all indicies
    positionList = []
    for x in range(vector1[0], vector2[0]+1):
        for y in range(vector1[1], vector2[1]+1):
            for z in range(vector1[2], vector2[2]+1):
                positionList.append( (x,y,z) )
    return positionList
def getPositions(pos1, pos2, mode):
    try:
        #print(mode)
        return (getCuboidPositions, getEllipsoidPositions, getCylPositions)[availableModes.index(mode)](pos1, pos2)
    except ValueError as ver:
        print("VALUE ERROR: " + str(ver))
        return getCuboidPositions(pos1,pos2)
@command('set')
@player_only
def set(connection, *args):
    connection.repairPositions()
    pos1, pos2 = connection.sortedPositions()
    
    positions = getPositions(pos1,pos2, connection.mode)
    
    blockList = []
    if(len(args)==1):
        if(args[0].lower() == "air"):
            for pos in positions:
                blockList.append( (False, pos, None) )
    else:
        for pos in positions:
            blockList.append( (True, pos, connection.colorWE) )
    undoBlocks = []
    map = connection.protocol.map
    for pos in positions:
        point = map.get_point(*pos)
        undoBlocks.append( (point[0], pos, Color(tuple=point[1])) )
    if ( connection.protocol.constructSelection(blockList) ):
        connection.curAction = blockList
        #print(connection.curAction)
        connection.redo = []
        connection.undo.append(undoBlocks)
        if(len(connection.undo)>=maxUndoRedo):
            connection.undo.pop(0)
    
#Undo redo
@command('undo')
@player_only
def undo(connection):  
    if(len(connection.undo)>0):
        toUndo = connection.undo[len(connection.undo)-1]
        connection.protocol.constructSelection(toUndo)
        connection.redo.append(connection.curAction)
        connection.curAction = toUndo
        connection.undo.pop()
        if(len(connection.redo)>=maxUndoRedo):
            connection.send_chat("Redo size too big, deleting oldest item")
            connection.redo.pop(0)
    else:
        connection.send_chat("Nothing to undo")
@command('redo')
@player_only
def redo(connection):
    if(len(connection.redo)>0):
        toRedo = connection.redo[len(connection.redo)-1]
        connection.protocol.constructSelection(toRedo)
        connection.undo.append(connection.curAction)
        connection.curAction = toRedo
        connection.redo.pop()
        if(len(connection.undo)>=maxUndoRedo):
            connection.send_chat("Undo size too big, deleting oldest item")
            connection.undo.pop(0)
    else:
        connection.send_chat("Nothing to redo")

#Worldedit player 'settings'
@command('mode')
@player_only
def setMode(connection, *args):
    if(len(args)==0):
        connection.send_chat("Current mode: %s, possible modes: %s" %(connection.mode, availableModes))
    elif(args[0].lower() in availableModes):
        connection.send_chat("Mode set to %s" %(args[0].lower()))
        connection.mode = args[0].lower()
@command('wand')
@player_only
def activateWand(connection):
    if(connection.brushMode != "wand"):
        connection.brushActive = True
        connection.send_chat("Brush set to wand mode")
    else:
        connection.brushActive = not connection.brushActive
        if(connection.brushActive):
            connection.send_chat("Brush activated")
        else:
            connection.send_chat("Brush deactivated")
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
        else:
            connection.send_chat("Invalid brush, valid brushes: {}".format(availableBrushes))




def apply_script(protocol, connection, config):
    class worldEditConnection(connection):
        brushActive = False
        brushMode = "wand"
        brushSize = 5
        curAction = None
        undo = []
        redo = []
        mode = 'cuboid'
        colorWE = Color(hex = 0x6F6F6F)
        pos1, pos2 = None, None
        def repairPositions(self):
            pos1, pos2 = [*self.pos1], [*self.pos2]
            for i in range(3):
                if(i==2):
                    pos1[i] = max(0,min(pos1[i],63))
                    pos2[i] = max(0,min(pos2[i],63))
                else:
                    pos1[i] = max(0,min(pos1[i],511))
                    pos2[i] = max(0,min(pos2[i],511))
            self.pos1 = tuple(pos1)
            self.pos2 = tuple(pos2)
        def sortedPositions(self):
            if(self.pos1 is None or self.pos2 is None):
                return None
            else:
                p1, p2 = self.pos1, self.pos2
                return ((min(p1[0],p2[0]), min(p1[1],p2[1]), min(p1[2],p2[2])), (max(p1[0],p2[0]), max(p1[1],p2[1]), max(p1[2],p2[2])))
        def on_shoot_set(self, fire):
            if(fire and self.brushActive):
                hit = self.world_object.cast_ray(128)
                if(hit):
                    if(self.brushMode == "wand"):
                        self.pos1 = hit
                        self.send_chat("new position: (%s,%s)" %(self.pos1, self.pos2))
                        connection.on_shoot_set(self, fire)
                        return
                        
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
                    
                    if(self.brushMode == "sphere"):
                        blockList = []
                        positions = getEllipsoidPositions(pos1,pos2)
                        #for pos in positions:
                            #blockList.append( (True, 
                        self.protocol.constructSelection(updateBlocks)
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
            set_color.value = Color(hex = 0x6F6F6F).getInt()
            for block in blockList:
                exists = block[0]
                pos = block[1]
                x,y,z = pos
                color = block[2]
                block_action.x, block_action.y, block_action.z = x, y, z
                if(exists): #Should be a block
                    if(map.get_point(x,y,z)[0]): #if there is a block
                        map.remove_point(x, y, z) #Clear the block for rebuilding with color
                    block_action.value = BUILD_BLOCK
                    set_color.value = color.getInt() 
                    map.set_point(x, y, z, color.getTuple()) #Set color in the map vxl
                    self.broadcast_contained(set_color) #Set color
                    self.broadcast_contained(block_action) #Broadcast the build
                else:
                    if(z >= 63):
                        continue
                    elif(map.get_point(x,y,z)[0]): #THERE IS A BLOCK
                        block_action.value = DESTROY_BLOCK
                        self.broadcast_contained(block_action)
                        map.remove_point(x, y, z)
            return True
    return worldEditProtocol, worldEditConnection