from piqueserver.config import config
from twisted.internet import reactor

sectionConfig = config.section('spawnProtection')
protectionTime = sectionConfig.option('protectionTime', default = 5).get()

def apply_script(protocol, connection, config):
    class spawnProtectionConnection(connection):
        invulnerable = False
        protectionCallID = None
        def on_shoot_set(self, fire):
            if(fire is True):
                self.invulnerable = False
            connection.on_shoot_set(self, fire)
            
        def on_hit(self, hit_amount, hit_player, kill_type, grenade):
            if(hit_player.invulnerable):
                return False
            return connection.on_hit(self, hit_amount, hit_player, kill_type, grenade)
        
        def on_spawn(self, pos):
            self.invulnerable = True
            try:
                self.protectionCallID.cancel()
            except AttributeError as aterr:
                pass
            except AlreadyCalled as acerr:
                pass
            except Exception as ex:
                print("Unknown Error: " + type(ex))
            self.regenCallID = reactor.callLater(protectionTime, self.set_invulnerable, False)
            return connection.on_spawn(self, pos)
            
        def set_invulnerable(self, state):
            self.invulnerable = state
    return protocol, spawnProtectionConnection