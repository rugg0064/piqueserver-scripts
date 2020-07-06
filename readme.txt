All scripts, descriptions, and sample configs

nuke.py
Large powerful artillery, highly configurable
Requires separate script to give as a reward for a killstreak etc
Sample config, can be pasted at the bottom of config.toml and edited:
[nuke]
explosionRadius=10
maximumExplosionRadius=50
fallOff=0.0025
propogationTime=2.5
upHeight=8
downHeight=2
grenadeAmount=400


hashtag.py
Same as the old version, kicks people who have a hashtag (pound sign) (#) in their name when they connect
no configuration, just enable in config.toml


infiniteBlocksAndLimitedGrenades.py
Gives players infinite blocks and more or less than the default amount of grenades, after throwing real grenades duds will be thrown, then the player will die
Sample config to give the player 5 real grenades and 3 duds before forcing suicide:
[grenades]
startingGrenades=5
duds=3


killstreak.py
A system to give players rewards such as a nuke 
No config.toml options, but customization is done within the python file right now.
To configure, line #4 of killstreak.py contains 

rewards = [[14, 7, 1, "nukesAvailable", "You have been given a nuke"]]

This reward gives the player 1(one) nuke at 14 kills, and 1(one) nuke every 7 after that.
the structure of this is 

Kills, loop, amount rewarded, connection stat rewarded, reward message

To add more streaks, expand the array and fill it with the correct data


regen.py
Functions exactly like the old regen.py, which added a COD style out of combat healing except cleaner code and more predictable
Configure options include the delay to start regenerating, and once regen is activated the speed and amount of the heal
For an almost immediate very fast heal:

[regen]
regenDelay=5.0
healSpeed=0.01
healAmount=1.0