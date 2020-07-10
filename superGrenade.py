from piqueserver.commands import command, admin, player_only, target_player
from piqueserver.config import config
from pyspades.world import Grenade
from pyspades.common import Vertex3
from random import random
from random import gauss
from math import sqrt
from piqueserver import map
sectionConfig = config.section('superGrenade')
radius = sectionConfig.option('explosionRadius', default = 2.5).get()
grenadeAmount = sectionConfig.option('grenadeAmount', default = 50).get()

@command('supergrenades')
@target_player
@player_only
def checkSuperGrenades(connection, player):
    connection.send_chat("%s has %d super grenades." %(player.name, player.superGrenades))
@admin
@command('givesupergrenade', 'gsg')
@target_player
def givenuke(connection, player):
    """
    Gives a super grenade to target player
    /givesupergrenade *<player>*
    """
    player.superGrenades = player.superGrenades+1
    try:
        connection.send_chat_notice("You have given %s a super grenade." %player.name)
    except AttributeError as ex:
        print("%s has been given a super grenade, but there was a %s error" %(player.name, type(ex)))
    player.send_chat_notice("%s has given you a super grenade." %connection.name)


def apply_script(protocol, connection, config):
    class superGrenadeConnection(connection):
        superGrenades = 0
        def on_spawn(self, position):
            self.superGrenades = 0
            connection.on_spawn(self, position)
        def on_grenade_thrown(self, grenade):
            if(self.superGrenades>0):
                self.superGrenades -= 1
                self.send_chat("Super grenade thrown, %d left" %self.superGrenades)
                grenade.callback = self.superGrenade_exploded
            connection.on_grenade_thrown(self, grenade)
        def grenade_exploded(self, grenade):
            connection.grenade_exploded(self, grenade)
        def superGrenade_exploded(self, grenade):
            mapData = self.protocol.map
            gPos = grenade.position
            for i in range(0, grenadeAmount):
                x, y, z = random()-0.5, random()-0.5, random()-0.5
                dist = sqrt((x)**2 + (y)**2)
                gaussianDistance = (gauss(radius, 2))
                x /= dist
                y /= dist
                z /= dist
                x *= gaussianDistance
                y *= gaussianDistance
                z *= gaussianDistance
                newGrenadePos = Vertex3(gPos.x+x, gPos.y+y, gPos.z+z)
                grenade = self.protocol.world.create_object(Grenade, 0.1, newGrenadePos, None, Vertex3(0,0,1), self.grenade_exploded)
            connection.grenade_exploded(self, grenade)
    return protocol, superGrenadeConnection