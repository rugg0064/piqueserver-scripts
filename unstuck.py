from piqueserver.commands import command, player_only
from piqueserver.config import config
from math import floor
from random import choice
from time import time
sectionConfig = config.section('unstuck')
cooldownConfig = sectionConfig.option('stuckCooldown', default = 10)
searchXConfig = sectionConfig.option('searchX', default = 0)
searchYConfig = sectionConfig.option('searchY', default = 0)
searchZConfig = sectionConfig.option('searchZ', default = 0)

teleportXConfig = sectionConfig.option('teleportX', default = 3)
teleportYConfig = sectionConfig.option('teleportY', default = 3)
teleportZConfig = sectionConfig.option('teleportZ', default = 3)

@command('unstuck', 'stuck')
@player_only
def unstuck(connection, *args):
    sx,sy,sz = searchXConfig.get(), searchYConfig.get(), searchZConfig.get()
    location = connection.get_location()
    location = (floor(location[0]), floor(location[1]), floor(location[2]))
    
    
    map = connection.protocol.map
    blocksInRange = 0
    for x in range(location[0] - sx, location[0] + sx + 1):
        for y in range(location[1] - sy, location[1] + sy + 1):
            for z in range(location[2] - sz, location[2] + 2 + sz + 1):
                if(not (0<=x<=512 and 0<=y<=512 and 0<=z<=64)):
                    blocksInRange += 1
                elif(map.get_point(x,y,z)[0]):
                    blocksInRange += 1
    maximumPossibleBlocks = ((sx*2)+1) * ((sy*2)+1) * (((sz)*2)+3)
    print("Stuck? %s, %s" %(blocksInRange, blocksInRange > maximumPossibleBlocks*0.3))
    if(not (blocksInRange > maximumPossibleBlocks*0.3)):
        connection.send_chat("You are not stuck enough")
        return
    timeLeft = (connection.lastStuckTime + cooldownConfig.get()) - time()
    if(timeLeft > 0):
        connection.send_chat("unstuck is still on cooldown for %s seconds" %round(timeLeft))
        return
    szx, szy, szz = teleportXConfig.get(), teleportYConfig.get(), teleportZConfig.get()  #looks for a zone in a radius (x,x,x) around the player, only safe positions that are in this area will work
    positions = []
    for x in range(location[0] - szx, location[0] + szx + 1):
        for y in range(location[1] - szy, location[1] + szy + 1):
            if(0<=x<=512 and 0<=y<=512):
                positions.append( (x,y) )
    while len(positions)>0:
        c = choice(positions)
        print("Chose position: %s" %str(c))
        x,y = c
        safePos = map.get_z(x,y)
        if(abs(safePos-location[2]) < 5):
            print("height = " + str(safePos))
            if(not map.get_point(x, y, safePos-1)[0]):
                if(not map.get_point(x, y, safePos-2)[0]):
                    connection.set_location((x, y, safePos-2))
                    connection.lastStuckTime = time()
                    return
        print("havent found a position yet")
        positions.remove(c)
        continue
        
        
    
def apply_script(protocol, connection, config):
    class unstuckConnection(connection):
        lastStuckTime = 0
    return protocol, unstuckConnection