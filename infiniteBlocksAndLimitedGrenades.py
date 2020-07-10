from piqueserver.config import config
from pyspades.constants import FALL_KILL
from pyspades import contained as loaders
sectionConfig = config.section('grenades')
grenadeLimitConfig = sectionConfig.option('startingGrenades', default = 3)
grenadeDudLimitConfig = sectionConfig.option('duds', default = 5)
startingGrenades = grenadeLimitConfig.get()
dudLimit = grenadeDudLimitConfig.get()
def apply_script(protocol, connection, config):
    class scriptConnection(connection):
        liveGrenades = 0
        dudGrenades = 0
        def on_spawn(self, position):
            self.liveGrenades = startingGrenades
            self.dudGrenades = dudLimit
            connection.on_spawn(self, position)
        
        def on_grenade_thrown(self, grenade):
            self.refillAndSetHPAmmo()
            if(self.liveGrenades>0):
                self.liveGrenades -= 1
                connection.send_chat(self, "%d grenade%s left" %(self.liveGrenades, ("s","")[self.liveGrenades==1]), global_message=False)
                connection.send_chat_notice(self, "%d grenade%s left" %(self.liveGrenades, ("s","")[self.liveGrenades==1]))
            elif(self.dudGrenades>0):
                grenade.fuse = 500000
                self.dudGrenades -= 1
                connection.send_chat(self, "You have %d dud%s, stop throwing more!" %((self.dudGrenades+dudLimit), ("s","")[self.dudGrenades+dudLimit==1]), global_message=False)
                connection.send_chat_notice(self, "%d dud%s left" %((self.dudGrenades), ("s","")[self.dudGrenades==1]))
            else:
                grenade.fuse = 500000
                connection.send_chat_error(self, "You have run out of dud grenades and exploded")
                connection.kill(self)
            connection.on_grenade_thrown(self, grenade)
            
        def refillAndSetHPAmmo(self):
            currentHP = self.hp
            weaponLoader = loaders.WeaponReload()
            weaponLoader.player_id = self.player_id
            weaponLoader.clip_ammo = self.weapon_object.current_ammo
            weaponLoader.reserve_ammo = self.weapon_object.current_stock
            connection.refill(self)
            self.send_contained(weaponLoader)
            connection.set_hp(self, currentHP, kill_type=FALL_KILL)
        
        def on_block_build(self, x,y,z):
            self.refillAndSetHPAmmo()
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            self.refillAndSetHPAmmo()
            connection.on_line_build(self,points)

        def on_refill(self):
            self.liveGrenades = startingGrenades
            self.dudGrenades = dudLimit
            connection.send_chat_notice(self, "Grenades refilled")
            connection.on_refill(self)
    return protocol, scriptConnection