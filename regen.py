from piqueserver.config import config
from twisted.internet import reactor
from pyspades.constants import FALL_KILL
from twisted.internet.error import AlreadyCalled

sectionConfig = config.section('regen')
regenDelay = sectionConfig.option('regenDelay', default = 5.0).get()
healSpeed = sectionConfig.option('healSpeed', default = 0.05).get()
healAmount = sectionConfig.option('healAmount', default = 1.0).get()

friendly_fire = config.option('friendly_fire', default = True).get()

def apply_script(protocol, connection, config):
    class regenConnection(connection):
        regenCallID = None
        def regen(self):
            connection.set_hp(self, self.hp + healAmount, kill_type=FALL_KILL)
            if(self.hp<100):
                self.regenCallID = reactor.callLater(healSpeed, self.regen)
        def stopRegen(self):
            try:
                self.regenCallID.cancel()
            except AttributeError as aterr:
                pass
            except AlreadyCalled as acerr:
                pass
            except Exception as ex:
                print("Unknown Error: " + type(ex))
        def resetRegen(self):
            self.stopRegen()
            self.regenCallID = reactor.callLater(regenDelay, self.regen)
        def on_fall(self, damage):
            self.resetRegen()
            connection.on_fall(self, damage)
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            if(hit_player.team.id != self.team.id or friendly_fire):
                hit_player.resetRegen()
            connection.on_hit(self, hit_amount, hit_player, kill_type, grenade)
    return protocol, regenConnection