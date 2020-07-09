from piqueserver.commands import command, player_only, target_player

#      Kills, Loop, amount rewarded, connection stat rewarded, reward message
rewards = [[5, 5, 1, "nukesAvailable", "You have been given a nuke"],
[2, 1, 1, "liveGrenades", ""],
[2, 1, 1, "superGrenades", "You have been given a super grenade"]
            ]

@command('killstreak', 'streak')
@target_player
@player_only
def killstreak(connection, player):
    """
    Checks the killstreak of a player.
    /killstreak <player>
    """
    connection.send_chat("%s has a %d killstreak." %(player.name, player.killStreak))
    
def apply_script(protocol, connection, config):
    class killstreakConnection(connection):
        killStreak = 0
        def on_spawn(self, position):
            self.killStreak = 0
            connection.on_spawn(self, position)
        def on_kill(self, killer, kill_type, grenade):
            if(grenade is not None):
                if("NoStreak" in grenade.name):
                    connection.on_kill(self, killer, kill_type, grenade);
                    return
            if(kill_type is not None):
                if(kill_type==4):
                    connection.on_kill(self, killer, kill_type, grenade);
                    return
            self.killStreak = 0
            if(killer is not None):
                killer.killStreak += 1
                for reward in rewards:
                    if(reward[0] == killer.killStreak or ((killer.killStreak-reward[0])%reward[1]==0 and killer.killStreak>=reward[0])):
                        setattr(killer, reward[3], getattr(killer, reward[3]) + reward[2])
                        killer.send_chat_notice(reward[4])
            connection.on_kill(self, killer, kill_type, grenade);
    return protocol, killstreakConnection