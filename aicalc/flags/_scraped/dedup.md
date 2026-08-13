# Dedup counts per flag

- **basic**: 105 distinct scoring blocks to encode (28/466 moves have no procedure for this flag)
- **evaluate_attacks**: 9 distinct scoring blocks to encode (0/466 moves have no procedure for this flag)
- **expert**: 114 distinct scoring blocks to encode (226/466 moves have no procedure for this flag)
- **prio_damage**: 1 distinct scoring blocks to encode (284/466 moves have no procedure for this flag)
- **baton_pass**: 6 distinct scoring blocks to encode (290/466 moves have no procedure for this flag)
- **setup_first_turn**: 1 distinct scoring blocks to encode (375/466 moves have no procedure for this flag)

---
# Scraped & deduplicated AI scoring text

Source: https://bparkpk.github.io/PKMoveScoring/ (466 moves scraped)

Not yet encoded into flags/*.py — extraction and dedup only.


## basic

- 105 distinct scoring blocks (+ 28 moves with no applicable procedure) out of 466 moves


### Shared by 219 move(s): Absorb, Accelerock, Acid, Aerial Ace, Aeroblast, Air Cutter, Air Slash, AncientPower, Assurance, Astonish, Attack Order, Aura Sphere, Aurora Beam, Avalanche, Beat Up, Bite, Blizzard, Body Slam, Bone Club, Bounce, Brave Bird, Brick Break, Bug Bite, Bullet Punch, Bullet Seed, Close Combat, Confusion, Constrict, Counter, Cross Chop, Cross Poison, Crunch, Crush Claw, Crush Grip, Cut, Dark Pulse, Dizzy Punch, Double Hit, Double Kick, Double-Edge, DoubleSlap, Draco Meteor, Dragon Claw, Dragon Pulse, Dragon Rage, Dragon Rush, DragonBreath, Drain Punch, Drill Peck, DynamicPunch, Egg Bomb, Endeavor, Energy Ball, Extrasensory, ExtremeSpeed, Facade, Faint Attack, False Swipe, Feint, Flail, Flash Cannon, Fly, Focus Blast, Focus Punch, Force Palm, Frenzy Plant, Frustration, Fury Attack, Fury Cutter, Fury Swipes, Giga Drain, Giga Impact, Grass Knot, Gunk Shot, Gust, Gyro Ball, HP Dark, HP Fighting, HP Flying, HP Ghost, HP Grass, HP Ice, HP Psychic, HP Rock, Hail Ball, Hammer Arm, Headbutt, Hi Jump Kick, Hurricane, Hyper Beam, Hyper Fang, Hyper Voice, Ice Ball, Ice Beam, Ice Fang, Ice Punch, Ice Shard, Icicle Spear, Icy Wind, Iron Head, Iron Tail, Jump Kick, Karate Chop, Leaf Blade, Leaf Storm, Leech Life, Lick, Low Kick, Luster Purge, Mach Punch, Magical Leaf, Magnet Bomb, Mega Drain, Mega Kick, Mega Punch, Megahorn, Metal Claw, Meteor Mash, Mirror Coat, Mirror Shot, Mist Ball, Needle Arm, Night Shade, Night Slash, Ominous Wind, Outrage, Pay Day, Payback, Peck, Petal Dance, Pin Missile, Pluck, Poison Fang, Poison Jab, Poison Sting, Poison Tail, Pound, Powder Snow, Power Gem, Power Whip, Present, Psybeam, Psychic, Psycho Boost, Psycho Cut, Punishment, Pursuit, Quick Attack, Rage, Razor Leaf, Razor Wind, Return, Revenge, Reversal, Roar of Time, Rock Ball, Rock Blast, Rock Climb, Rock Slide, Rock Smash, Rock Throw, Rock Tomb, Rock Wrecker, Rolling Kick, Scratch, Secret Power, Seed Bomb, Seed Flare, Seismic Toss, Shadow Ball, Shadow Claw, Shadow Force, Shadow Punch, Shadow Sneak, Sheer Cold, Signal Beam, Silver Wind, Sky Attack, Sky Uppercut, Slam, Slash, Sludge, Sludge Bomb, SmellingSalt, Smog, Solar-Beam, SonicBoom, Spacial Rend, Steel Wing, Stomp, Stone Edge, Strength, Submission, Sucker Punch, Super Fang, Superpower, Swallow, Swift, Tackle, Take Down, Thrash, Tri Attack, Triple Axel, Triple Kick, Trump Card, Twineedle, Twister, U-turn, Vacuum Wave, ViceGrip, Vine Whip, Vital Throw, Wake-Up Slap, Wing Attack, Wood Hammer, Wrap, Wring Out, X-Scissor, Zen Headbutt

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 16 move(s): Aqua Cutter, Aqua Jet, Aqua Tail, Bubble, BubbleBeam, Crabhammer, Dive, Heart Swap, Hydro Cannon, Hydro Pump, Muddy Water, Octazooka, Water Ball, Water Gun, Water Pulse, Waterfall

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Water Absorb or Dry Skin, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 12 move(s): Blast Burn, Blaze Kick, Eruption, Fire Fang, Fire Spin, Flame Wheel, Flare Blitz, HP Fire, Magma Storm, Mystical Fire, Overheat, Sacred Fire

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Flash Fire, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 12 move(s): Bone Rush, Bonemerang, Bulldoze, Dig, Drill Run, Earth Power, Earthquake, HP Ground, Mud Bomb, Mud Shot, Mud-Slap, Sand Tomb

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Levitate, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 12 move(s): Charge Beam, Discharge, HP Electric, Shock Wave, Thunder, Thunder Fang, ThunderPunch, ThunderShock, Thunderbolt, Volt Tackle, Wild Charge, Zap Cannon

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Volt Absorb or Motor Drive, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 10 move(s): Heal Order, Lunar Dance, Milk Drink, Moonlight, Morning Sun, Recover, Roost, Slack Off, Softboiled, Synthesis

```
If the user's HP is full:

Score -8 and terminate
```


### Shared by 7 move(s): Ember, Fire Ball, Fire Blast, Fire Punch, Flamethrower, Heat Wave, Lava Plume

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Flash Fire, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Flash Fire, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 6 move(s): Dark Void, Hypnosis, Lovely Kiss, Sleep Powder, Spore, Yawn

```
If the target is already statused:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate

If the target's ability is Insomnia or Vital Spirit:

Score -10 and terminate
```


### Shared by 5 move(s): Acid Armor, Barrier, Harden, Iron Defense, Withdraw

```
If the user's ability is Simple, and its defense is boosted to +3 or more:

Score -10 and terminate

If the user's current defense is boosted to +6:

Score -10 and terminate
```


### Shared by 5 move(s): Brine, Clamp, Scald, Surf, Whirlpool

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Water Absorb, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 5 move(s): Confuse Ray, Flatter, Swagger, Sweet Kiss, Teeter Dance

```
If the target is already confused:

Score -5 and terminate

If the target's ability is Own Tempo:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate
```


### Shared by 4 move(s): Cotton Spore, Fake Tears, Scary Face, String Shot

```
If Trick Room is currently active:

Score -10 and terminate

If the target's speed is reduced to -6:

Score -10 and terminate

If the target's ability is certainly Speed Boost:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 4 move(s): Howl, Meditate, Sharpen, Swords Dance

```
If the user's ability is Simple, and its attack is boosted to +3 or more:

Score -10 and terminate

If the user's current attack is boosted to +6:

Score -10 and terminate
```


### Shared by 3 move(s): Block, Mean Look, Spider Web

```
If the target is already prevented from escaping:

Score -10 and terminate
```


### Shared by 3 move(s): Bug Buzz, Chatter, Uproar

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate
```


### Shared by 3 move(s): Cosmic Power, Defend Order, Stockpile

```
If the user's ability is Simple, and its current defense or special defense is boosted to +3 or more:

Score -10 and terminate

If the user's current defense is boosted to +6:

Score -10 and terminate

If the user's current special defense is boosted to +6:

Score -8 and terminate
```


### Shared by 3 move(s): Explosion, Memento, Selfdestruct

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Damp, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the user has other living party members:

No score change and terminate

If the target has other living party members:

Score -10 and terminate

Otherwise:

Score -1 and terminate
```


### Shared by 3 move(s): Flash, Sand-Attack, SmokeScreen

```
If the target's accuracy is reduced to -6:

Score -10 and terminate

If the user's ability is No Guard:

Score -10 and terminate

If the target's ability is No Guard or Keen Eye:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 3 move(s): Growth, Nasty Plot, Tail Glow

```
If the user's ability is Simple, and its special attack is boosted to +3 or more:

Score -10 and terminate

If the user's current special attack is boosted to +6:

Score -10 and terminate
```


### Shared by 3 move(s): Hidden Power, Judgment, Weather Ball

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target is immune to the move's damage due to Volt Absorb, Motor Drive, Water Absorb, or Flash Fire, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 3 move(s): Poison Gas, PoisonPowder, Toxic

```
If the target is Steel or Poison type:

Score -10 and terminate

If the target's ability is Immunity, Magic Guard, or Poison Heal:

Score -10 and terminate

If the weather is sunny and the target's ability is Leaf Guard, or the weather is rainy and the target's ability is Hydration:

Score -10 and terminate

If the target is already statused:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate
```


### Shared by 2 move(s): Agility, Rock Polish

```
If Trick Room is currently active:

Score -10 and terminate

If the user's ability is Simple, and its speed is boosted to +3 or more:

Score -10 and terminate

If the user's current speed is boosted to +6:

Score -10 and terminate
```


### Shared by 2 move(s): Bide, Metal Burst

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Stall, or the target is holding a Shiny Stone:

Score -10 and terminate

If the user's ability is Stall, or the user is holding a Shiny Stone:

No scoring change and terminate

If the user will attack before the target:

Score -10 and terminate
```


### Shared by 2 move(s): Charm, FeatherDance

```
If the target's attack is reduced to -6:

Score -10 and terminate

If the target's ability is Hyper Cutter:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 2 move(s): Doom Desire, Future Sight

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the user's side is awaiting a future attack:

Score -12 and terminate

If the target's side is awaiting a future attack:

Score -12 and terminate
```


### Shared by 2 move(s): Double Team, Minimize

```
If the user's ability is No Guard, or the target's ability is No Guard:

Score -10 and terminate

If the user's ability is Simple, and its evasion is boosted to +3 or more:

Score -10 and terminate

If the user's current evasion is boosted to +6:

Score -10 and terminate
```


### Shared by 2 move(s): Foresight, Odor Sleuth

```
If the target is already identified by Foresight or Odor Sleuth:

Score -10 and terminate
```


### Shared by 2 move(s): Glare, Stun Spore

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Limber or Magic Guard:

Score -10 and terminate

If the target is already statused:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate
```


### Shared by 2 move(s): GrassWhistle, Sing

```
If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target is already statused:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate

If the target's ability is Insomnia or Vital Spirit:

Score -10 and terminate
```


### Shared by 2 move(s): Guillotine, Horn Drill

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Sturdy and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target is a higher level than the user:

Score -10 and terminate
```


### Shared by 2 move(s): Haze, Psych Up

```
If any of the user's stats are reduced:

No scoring change and terminate

If any of the target's stats are boosted:

No scoring change and terminate

Otherwise:

Score -10 and terminate
```


### Shared by 2 move(s): Ingrain, Magic Coat

```
If the user is already under the effect of Ingrain:

Score -10 and terminate
```


### Shared by 2 move(s): Leer, Tail Whip

```
If the target's defense is reduced to -6:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 2 move(s): Lock-On, Mind Reader

```
If the target is already under the effect of Lock-On:

Score -10 and terminate

If the user's ability is No Guard, or the target's ability is No Guard:

Score -10 and terminate
```


### Shared by 1 move(s): Acupressure

```
If the user's ability is Simple, and any of its stats are boosted to +3 or more:

Score -10 and terminate

If any of the user's stats are boosted to +6:

Score -10 and terminate
```


### Shared by 1 move(s): Amnesia

```
If the user's ability is Simple, and its special defense is boosted to +3 or more:

Score -10 and terminate

If the user's current special defense is boosted to +6:

Score -10 and terminate
```


### Shared by 1 move(s): Aqua Ring

```
If the user is already under the effect of Aqua Ring:

Score -10 and terminate
```


### Shared by 1 move(s): Attract

```
If the target is already infatuated:

Score -10 and terminate

If the target's ability is Oblivious:

Score -10 and terminate

If the target is not the opposite gender as the user:

Score -10 and terminate
```


### Shared by 1 move(s): Baton Pass

```
If the user has no other living party members:

Score -10 and terminate
```


### Shared by 1 move(s): Belly Drum

```
If the user's HP is under 51%:

Score -10 and terminate

If the user's ability is Simple, and its attack is boosted to +3 or more:

Score -10 and terminate

If the user's current attack is boosted to +6:

Score -10 and terminate
```


### Shared by 1 move(s): Bulk Up

```
If the user's ability is Simple, and its current attack or defense is boosted to +3 or more:

Score -10 and terminate

If the user's current attack is boosted to +6:

Score -10 and terminate

If the user's current defense is boosted to +6:

Score -8 and terminate
```


### Shared by 1 move(s): Calm Mind

```
If the user's ability is Simple, and its current special attack or special defense is boosted to +3 or more:

Score -10 and terminate

If the user's current special attack is boosted to +6:

Score -10 and terminate

If the user's current special defense is boosted to +6:

Score -8 and terminate
```


### Shared by 1 move(s): Camouflage

```
If the user is currently under the effect of Camouflage:

Score -10 and terminate
```


### Shared by 1 move(s): Captivate

```
If the target's ability is Oblivious, Clear Body, or White Smoke, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target is not the opposite gender as the user:

Score -10 and terminate

If the target's special attack is reduced to -6:

Score -10 and terminate
```


### Shared by 1 move(s): Copycat

```
If this is the first turn of the battle:

Score -10 and terminate
```


### Shared by 1 move(s): Curse

```
If the user is Ghost type:

If the target is already under the effect of Curse:

Score -10 and terminate

If the target's ability is Magic Guard:

Score -10 and terminate

If the user is not Ghost type:

If the user's ability is Simple, and its current attack or defense is boosted to +3 or more:

Score -10 and terminate

If the user's current attack is boosted to +6:

Score -10 and terminate

If the user's current defense is boosted to +6:

Score -8 and terminate
```


### Shared by 1 move(s): Defog

```
If the target's evasion is not reduced to -6:

No scoring change and terminate

If the target's side of the field has Light Screen or Reflect active:

No scoring change and terminate

If the weather is foggy:

No scoring change and terminate

If the target has no other living party members:

Score -10 and terminate

If the target's side of the field does not have Stealth Rock, Spikes, or Toxic Spikes active:

Score -10 and terminate
```


### Shared by 1 move(s): Disable

```
If the target is already disabled:

Score -8 and terminate
```


### Shared by 1 move(s): Dragon Dance

```
If Trick Room is currently active:

Score -10 and terminate

If the user's ability is Simple, and its current attack or speed is boosted to +3 or more:

Score -10 and terminate

If the user's current attack is boosted to +6:

Score -10 and terminate

If the user's current speed is boosted to +6:

Score -8 and terminate
```


### Shared by 1 move(s): Dream Eater

```
If the target is not asleep:

Score -8 and terminate

If the effectiveness of the move is 0x:

Score -10 and terminate
```


### Shared by 1 move(s): Embargo

```
If the target is already under the effect of Embargo:

Score -10 and terminate

If the target has no item it could Recycle:

No scoring change and terminate

If the fight is a Frontier fight:

Score -10 and terminate
```


### Shared by 1 move(s): Encore

```
If the target is already under the effect of Encore:

Score -8 and terminate
```


### Shared by 1 move(s): Fake Out

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If this is not the first turn the user is active:

Score -10 and terminate
```


### Shared by 1 move(s): Fissure

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Levitate, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Sturdy and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target is a higher level than the user:

Score -10 and terminate
```


### Shared by 1 move(s): Fling

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the user is not holding an item:

Score -10 and terminate

If the user is holding a Poison Barb or Toxic Orb:

If the user's ability is Poison Heal, or the target is protected by Safeguard, or is already statused, or is Poison or Steel type, or has the ability Immunity, Poison Heal, or Magic Guard:

If the user is protected by Safeguard, or is already statused, or is Poison or Steel type, or has the ability Klutz, Immunity, Poison Heal, Magic Guard, or Guts:

Score -5 and terminate

Else:

Score +3 and terminate

If the user is holding a Flame Orb:

If the target is protected by Safeguard, or is already statused, or is Fire type, or has the ability Magic Guard or Water Veil:

If the user protected by Safeguard, or is already statused, or is Fire type, or has the ability Klutz, Magic Guard, Water Veil, or Guts:

Score -5 and terminate

Else:

Score +3 and terminate

If the user is holding a Light Ball:

If the target is protected by Safeguard, or is already statused, or has the ability Limber:

Score -5 and terminate
```


### Shared by 1 move(s): Focus Energy

```
If the user is already under the effect of Focus Energy:

Score -10 and terminate
```


### Shared by 1 move(s): Gastro Acid

```
If the target is already under the effect of Gastro Acid:

Score -10 and terminate

If the target's ability is Multitype, Truant, Slow Start, Stench, Run Away, Pickup, or Honey Gather:

Score -10 and terminate
```


### Shared by 1 move(s): Gravity

```
If Gravity is currently active:

Score -10 and terminate
```


### Shared by 1 move(s): Growl

```
If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target's attack is reduced to -6:

Score -10 and terminate

If the target's ability is Hyper Cutter:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 1 move(s): Guard Swap

```
If the user's defense boosts and special defense boosts are both equal to or greater than the target's:

Score -10 and terminate
```


### Shared by 1 move(s): Hail

```
If the weather is already hail:

Score -8 and terminate

If the foe's ability is Ice Body:

If the user's ability is Ice Body:

No scoring change and terminate

Else:

Score -8 and terminate
```


### Shared by 1 move(s): Helping Hand

```
If the fight is not a double or multi battle:

Score -10 and terminate
```


### Shared by 1 move(s): HP Water

```
NOTE: This is not a scoring function,

but if Gravity is on the field, this move cannot be selected.

This is confirmed on the players side, but unknown on the AI side

If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Water Absorb or Dry Skin, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate
```


### Shared by 1 move(s): Imprison

```
If the user is currently imprisoning the target, or is currently being imprisoned by the target:

Score -10 and terminate
```


### Shared by 1 move(s): Kinesis

```
If the target's special defense is reduced to -6:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 1 move(s): Knock Off

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Sticky Hold:

Score -10 and terminate

If the target is not holding any item:

Score -10 and terminate
```


### Shared by 1 move(s): Last Resort

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the user has not used all of its other moves:

Score -10 and terminate
```


### Shared by 1 move(s): Leech Seed

```
If the target is already under the effect of Leech Seed:

Score -10 and terminate

If the target is Grass type:

Score -10 and terminate

If the target's ability is Magic Guard:

Score -10 and terminate
```


### Shared by 1 move(s): Light Screen

```
If the user's side of the field already has Light Screen active:

Score -8 and terminate
```


### Shared by 1 move(s): Lucky Chant

```
If the user's side of the field is already under the effect of Lucky Chant:

Score -10 and terminate
```


### Shared by 1 move(s): Magnet Rise

```
If the user is already under the effect of Magnet Rise, or has the ability Levitate, or is Flying type:

Score -10 and terminate
```


### Shared by 1 move(s): Metal Sound

```
If Trick Room is currently active:

Score -10 and terminate

If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target's speed is reduced to -6:

Score -10 and terminate

If the target's ability is certainly Speed Boost:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 1 move(s): Miracle Eye

```
If the target is already under the effect of Miracle Eye:

Score -10 and terminate
```


### Shared by 1 move(s): Mist

```
If the user's side of the field already has Mist active:

Score -8 and terminate
```


### Shared by 1 move(s): Natural Gift

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target is immune to the move's damage due to Volt Absorb, Motor Drive, Water Absorb, or Flash Fire, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the user is not holding a berry:

Score -10 and terminate
```


### Shared by 1 move(s): Perish Song

```
If the target is already under the effect of Perish Song:

Score -10 and terminate
```


### Shared by 1 move(s): Power Swap

```
If the user's attack boosts and special attack boosts are both equal to or greater than the target's:

Score -10 and terminate
```


### Shared by 1 move(s): Power Trick

```
If the user is already under the effect of Power Trick:
Score -10 and terminate
```


### Shared by 1 move(s): Psycho Shift

```
If the user is not statused:

Score -10 and terminate

If the target is protected by Safeguard, or is already statused:

Score -10 and terminate

If the user is poisoned:

If the user's ability is Poison Heal:

Score -10 and terminate

If the target is Poison or Steel type, or has the ability Immunity, Poison Heal, or Magic Guard:

Score -10 and terminate

If the user is burned:

If the target is Fire type, or has the ability Water Veil or Magic Guard:

Score -10 and terminate

If the user is paralyzed:

If the target's ability is Limber:

Score -10 and terminate
```


### Shared by 1 move(s): Rain Dance

```
If the user's ability is Swift Swim or Hydration:

If it is already raining:

Score -8 and terminate

Else:

No score change and terminate

If the foe's ability is Hydration, and they are statused:

Score -8 and terminate

If it is already raining:

Score -8 and terminate
```


### Shared by 1 move(s): Recycle

```
If the user has no item to recycle:

Score -10 and terminate
```


### Shared by 1 move(s): Reflect

```
If the user's side of the field already has Reflect active:

Score -8 and terminate
```


### Shared by 1 move(s): Refresh

```
If the user is not burned, paralyzed, poisoned, or badly poisoned:

Score -10 and terminate
```


### Shared by 1 move(s): Roar

```
If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target has no other living party members:

Score -10 and terminate

If the target's ability is Suction Cups, and the user's ability is not Mold Breaker:

Score -10 and terminate
```


### Shared by 1 move(s): Safeguard

```
If the user is already under the effect of Safeguard:

Score -8 and terminate
```


### Shared by 1 move(s): Sandstorm

```
If the weather is already a sandstorm:

Score -8 and terminate
```


### Shared by 1 move(s): Screech

```
If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target's defense is reduced to -6:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 1 move(s): Sleep Talk

```
If the user is not asleep:

Score -8 and terminate
```


### Shared by 1 move(s): Snore

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Wonder Guard, and the effectiveness of the move is not 2x or 4x, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the user is not asleep:

Score -8 and terminate
```


### Shared by 1 move(s): Spikes

```
If the target's side of the field already has 3 layers of Spikes:

Score -10 and terminate

If the target has no other living party members:

Score -10 and terminate
```


### Shared by 1 move(s): Stealth Rock

```
If the target's side of the field already has Stealth Rock active:

Score -10 and terminate

If the target has no other living party members:

Score -10 and terminate
```


### Shared by 1 move(s): Substitute

```
If the user already has a substitute:

Score -8 and terminate

If the user's HP is under 26%:

Score -10 and terminate
```


### Shared by 1 move(s): Sunny Day

```
If the user's ability is not Flower Gift, Leaf Guard, or Solar Power, and the foe's ability is Hydration, and the foe is statused:

Score -10 and terminate

If it is already sunny:

Score -8 and terminate
```


### Shared by 1 move(s): Supersonic

```
If the target's ability is Soundproof, and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target is already confused:

Score -5 and terminate

If the target's ability is Own Tempo:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate
```


### Shared by 1 move(s): Sweet Scent

```
If the target's evasion is reduced to -6:

Score -10 and terminate

If the user's ability is No Guard:

Score -10 and terminate

If the target's ability is No Guard or Keen Eye:

Score -10 and terminate

If the target's ability is Clear Body or White Smoke:

Score -10 and terminate
```


### Shared by 1 move(s): Tailwind

```
If Trick Room is currently active:

Score -10 and terminate

If Tailwind is aleady active:

Score -10 and terminate
```


### Shared by 1 move(s): Teleport

```
Unconditionally:

Score -10 and terminate
```


### Shared by 1 move(s): Thunder Wave

```
If the effectiveness of the move is 0x:

Score -10 and terminate

If the target's ability is Limber or Magic Guard:

Score -10 and terminate

If the target's ability is Volt Absorb or Motor Drive, and the user's ability is not Mold Breaker:

Score -12 and terminate

If the target is already statused:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate
```


### Shared by 1 move(s): Tickle

```
If the target's ability is Clear Body or White Smoke and the user's ability is not Mold Breaker:

Score -10 and terminate

If the target's current attack is reduced to -6:

Score -10 and terminate

If the target's current defense is reduced to -6:

Score -8 and terminate
```


### Shared by 1 move(s): Torment

```
If the target is already under the effect of Torment:

Score -10 and terminate
```


### Shared by 1 move(s): Toxic Spikes

```
If the target's side of the field already has 2 layers of Toxic Spikes:

Score -10 and terminate

If the target has no other living party members:

Score -10 and terminate
```


### Shared by 1 move(s): Trick Room

```
If the user will attack before the foe:

Score -10 and terminate

If the user speed ties with the foe:

50% (128/256) chance of score -10 and terminate
```


### Shared by 1 move(s): Whirlwind

```
If the target has no other living party members:

Score -10 and terminate

If the target's ability is Suction Cups, and the user's ability is not Mold Breaker:

Score -10 and terminate
```


### Shared by 1 move(s): Will-O-Wisp

```
If the target's ability is Water Veil or Magic Guard:

Score -10 and terminate

If the target is a Fire type:

Score -10 and terminate

If the target is already statused:

Score -10 and terminate

If the target is protected by Safeguard:

Score -10 and terminate
```


### Shared by 1 move(s): Worry Seed

```
If the target's ability is Truant, Insomnia, Vital Spirit, or Multitype:

Score -10 and terminate

If the target is asleep, and does not have the move Sleep Talk or Snore:

Score -10 and terminate
```


### No applicable AI procedure (28 moves)

Aromatherapy, Assist, Charge, Conversion 2, Destiny Bond, Detect, Endure, Follow Me, Grudge, Head Smash, Heal Bell, Me First, Metronome, Mimic, Mirror Move, Nature Power, Pain Split, Protect, Rest, Role Play, Sketch, Skill Swap, SolarBeam, Spite, Thief, Transform, Water Spout, Wish


## evaluate_attacks

- 9 distinct scoring blocks (+ 0 moves with no applicable procedure) out of 466 moves


### Shared by 256 move(s): Absorb, Accelerock, Acid, Aerial Ace, Aeroblast, Air Cutter, Air Slash, AncientPower, Aqua Cutter, Aqua Tail, Assurance, Astonish, Attack Order, Aura Sphere, Aurora Beam, Avalanche, Beat Up, Bite, Blast Burn, Blaze Kick, Blizzard, Body Slam, Bone Club, Bounce, Brick Break, Brine, Bubble, BubbleBeam, Bug Bite, Bug Buzz, Charge Beam, Chatter, Clamp, Confusion, Constrict, Crabhammer, Cross Chop, Cross Poison, Crunch, Crush Claw, Crush Grip, Cut, Dark Pulse, Dig, Discharge, Dive, Dizzy Punch, Doom Desire, Double-Edge, Draco Meteor, Dragon Claw, Dragon Pulse, Dragon Rage, Dragon Rush, DragonBreath, Drain Punch, Drill Peck, Drill Run, DynamicPunch, Earth Power, Earthquake, Egg Bomb, Ember, Energy Ball, Eruption, Extrasensory, ExtremeSpeed, Facade, Faint Attack, Fake Out, False Swipe, Feint, Fire Ball, Fire Blast, Fire Fang, Fire Punch, Fire Spin, Flame Wheel, Flamethrower, Flare Blitz, Flash Cannon, Fly, Focus Blast, Force Palm, Frenzy Plant, Frustration, Future Sight, Giga Drain, Giga Impact, Grass Knot, Gunk Shot, Gust, Gyro Ball, HP Dark, HP Electric, HP Fighting, HP Fire, HP Flying, HP Ghost, HP Grass, HP Ground, HP Ice, HP Psychic, HP Rock, HP Water, Hail Ball, Hammer Arm, Headbutt, Heart Swap, Heat Wave, Hi Jump Kick, Hidden Power, Hurricane, Hydro Cannon, Hydro Pump, Hyper Beam, Hyper Fang, Hyper Voice, Ice Ball, Ice Beam, Ice Fang, Ice Punch, Icy Wind, Iron Head, Iron Tail, Judgment, Jump Kick, Karate Chop, Knock Off, Last Resort, Lava Plume, Leaf Blade, Leaf Storm, Leech Life, Lick, Low Kick, Luster Purge, Magical Leaf, Magma Storm, Magnet Bomb, Mega Drain, Mega Kick, Mega Punch, Megahorn, Metal Claw, Meteor Mash, Mirror Shot, Mist Ball, Mud Bomb, Mud Shot, Mud-Slap, Muddy Water, Mystical Fire, Natural Gift, Needle Arm, Night Shade, Night Slash, Octazooka, Ominous Wind, Outrage, Overheat, Pay Day, Payback, Peck, Petal Dance, Pluck, Poison Fang, Poison Jab, Poison Sting, Poison Tail, Powder Snow, Power Gem, Power Whip, Psybeam, Psychic, Psycho Boost, Psycho Cut, Pursuit, Rage, Razor Leaf, Revenge, Roar of Time, Rock Ball, Rock Climb, Rock Slide, Rock Smash, Rock Throw, Rock Tomb, Rolling Kick, Sacred Fire, Sand Tomb, Scald, Scratch, Secret Power, Seed Bomb, Seed Flare, Seismic Toss, Shadow Ball, Shadow Force, Shadow Punch, Sheer Cold, Shock Wave, Signal Beam, Silver Wind, Sky Attack, Sky Uppercut, Slam, Slash, Sludge, Sludge Bomb, SmellingSalt, Smog, Snore, Solar-Beam, SonicBoom, Spacial Rend, Steel Wing, Stomp, Stone Edge, Strength, Submission, Sucker Punch, Superpower, Surf, Swallow, Swift, Tackle, Thrash, Thunder, Thunder Fang, ThunderPunch, ThunderShock, Thunderbolt, Tri Attack, Twister, U-turn, Uproar, ViceGrip, Vine Whip, Vital Throw, Volt Tackle, Wake-Up Slap, Water Ball, Water Gun, Water Pulse, Waterfall, Weather Ball, Whirlpool, Wild Charge, Wing Attack, Wood Hammer, Wrap, Wring Out, X-Scissor, Zap Cannon, Zen Headbutt

```
If the move can KO the target:

Score +4 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 179 move(s): Acid Armor, Acupressure, Agility, Amnesia, Aqua Ring, Aromatherapy, Assist, Attract, Barrier, Baton Pass, Belly Drum, Bide, Block, Brave Bird, Bulk Up, Calm Mind, Camouflage, Captivate, Charge, Charm, Close Combat, Confuse Ray, Conversion 2, Copycat, Cosmic Power, Cotton Spore, Counter, Curse, Dark Void, Defend Order, Defog, Destiny Bond, Detect, Disable, Double Team, Dragon Dance, Dream Eater, Embargo, Encore, Endeavor, Endure, Fake Tears, FeatherDance, Fissure, Flail, Flash, Flatter, Fling, Focus Energy, Follow Me, Foresight, Gastro Acid, Glare, GrassWhistle, Gravity, Growl, Growth, Grudge, Guard Swap, Guillotine, Hail, Harden, Haze, Head Smash, Heal Bell, Heal Order, Helping Hand, Horn Drill, Howl, Hypnosis, Imprison, Ingrain, Iron Defense, Kinesis, Leech Seed, Leer, Light Screen, Lock-On, Lovely Kiss, Lucky Chant, Lunar Dance, Magic Coat, Magnet Rise, Me First, Mean Look, Meditate, Metal Burst, Metal Sound, Metronome, Milk Drink, Mimic, Mind Reader, Minimize, Miracle Eye, Mirror Coat, Mirror Move, Mist, Moonlight, Morning Sun, Nasty Plot, Nature Power, Odor Sleuth, Pain Split, Perish Song, Poison Gas, PoisonPowder, Power Swap, Power Trick, Present, Protect, Psych Up, Psycho Shift, Punishment, Rain Dance, Razor Wind, Recover, Recycle, Reflect, Refresh, Rest, Reversal, Roar, Rock Polish, Role Play, Roost, Safeguard, Sand-Attack, Sandstorm, Scary Face, Screech, Sharpen, Sing, Sketch, Skill Swap, Slack Off, Sleep Powder, Sleep Talk, SmokeScreen, Softboiled, SolarBeam, Spider Web, Spikes, Spite, Spore, Stealth Rock, Stockpile, String Shot, Stun Spore, Substitute, Sunny Day, Super Fang, Supersonic, Swagger, Sweet Kiss, Sweet Scent, Swords Dance, Synthesis, Tail Glow, Tail Whip, Tailwind, Take Down, Teeter Dance, Teleport, Thief, Thunder Wave, Tickle, Torment, Toxic, Toxic Spikes, Transform, Trick Room, Trump Card, Water Spout, Whirlwind, Will-O-Wisp, Wish, Withdraw, Worry Seed, Yawn

```
If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 16 move(s): Bone Rush, Bonemerang, Bullet Seed, Double Hit, Double Kick, DoubleSlap, Fury Attack, Fury Cutter, Fury Swipes, Icicle Spear, Pin Missile, Rock Blast, Rock Wrecker, Shadow Claw, Triple Kick, Twineedle

```
NOTE: The AI will only calculate a single hit for scoring purposes

If the move can KO the target:

Score +4 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 7 move(s): Aqua Jet, Bullet Punch, Ice Shard, Mach Punch, Quick Attack, Shadow Sneak, Vacuum Wave

```
If the move can KO the target:

Score +6 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 4 move(s): Explosion, Focus Punch, Memento, Selfdestruct

```
Unconditionally:

80.1% (205/256) chance of score -2 and continue

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 1 move(s): Bulldoze

```
NOTE: Due to testing, we discovered that Bulldoze uses Magnitude calculations for scoring purposes

This means the when the AI checks for damage rolls, it will have a power listed below.

Actual damage will be what is shown in the calc though.
Base Power and Chances

10 - 5%, 30 - 10%, 50 - 20%, 70 - 30%, 90 - 20%, 110 - 10%, 150 - 5%

If the move can KO the target:

Score +4 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 1 move(s): Pound

```
>If the move can KO the target:

Score +4 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 1 move(s): Return

```
NOTE: Return has a scoring/damage difference!

The AI sees Return as a 102BP move while scoring.

The actual damage is still a 121BP move.

Make sure to adjust the calc BP when checking scoring, and back to default when checking damage.

If the move can KO the target:

Score +4 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


### Shared by 1 move(s): Triple Axel

```
NOTE: Due to testing, we discovered that Triple Axel uses Psywave calculations for scoring purposes

This means the when the AI checks for damage rolls, it will roll a value anywhere between 50%-150% of the Users Level.

Actual damage will be what is shown in the calc though.

If the move can KO the target:

Score +4 and terminate

If the move cannot KO the target, and a different move the user knows would do more damage to the target:

Score -1 and terminate

If the effectiveness of the move is 4x:

68.8% (176/256) chance of score +2 and terminate
```


## expert

- 114 distinct scoring blocks (+ 226 moves with no applicable procedure) out of 466 moves


### Shared by 21 move(s): Air Cutter, Aqua Cutter, Blaze Kick, Crabhammer, Cross Chop, Cross Poison, Dragon Claw, Drill Peck, Drill Run, Karate Chop, Leaf Blade, Megahorn, Night Slash, Poison Tail, Power Whip, Psycho Cut, Razor Leaf, Slash, Spacial Rend, Stone Edge, X-Scissor

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

No scoring change and terminate

If the effectiveness of the move is 2x or 4x:

50% (128/256) chance of score +1 and terminate

Otherwise:

25% (64/256) chance of score +1 and terminate
```


### Shared by 19 move(s): Blast Burn, Double-Edge, Draco Meteor, Eruption, Flare Blitz, Frenzy Plant, Giga Impact, Head Smash, Hydro Cannon, Hyper Beam, Outrage, Overheat, Roar of Time, Sky Attack, Superpower, Thrash, Volt Tackle, Wild Charge, Wood Hammer

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

No scoring change and terminate

If the user's ability is Rock Head or Magic Guard:

Score +1 and terminate
```


### Shared by 11 move(s): Aerial Ace, Aura Sphere, Aurora Beam, Dragon Pulse, Faint Attack, Magical Leaf, Magnet Bomb, Shadow Punch, Shock Wave, Swift, Vital Throw

```
If the user's current accuracy is reduced to -5 or lower, or the target's current evasion is boosted to +5 or more:

Score +1 and continue

If the user's current accuracy is reduced to -3 or lower, or the target's current evasion is boosted to +3 or more:

60.9% (156/256) chance of score +1 and terminate
```


### Shared by 8 move(s): Dark Void, GrassWhistle, Hypnosis, Lovely Kiss, Sing, Sleep Powder, Spore, Yawn

```
If the user also knows the move Nightmare or Dream Eater:

50% (128/256) chance of score +1 and terminate
```


### Shared by 7 move(s): Heal Order, Lunar Dance, Milk Drink, Recover, Roost, Slack Off, Softboiled

```
If the user's HP is full:

Score -3 and terminate

If the user will move before the target:

Score -8 and terminate

If the user's HP is over 69%:

With a 88.3% (226/256) chance:

Score -3 and terminate

If the foe knows the move Snatch:

56.2% (2301/4096) chance of score +2 and terminate

Otherwise:

92.2% (236/256) chance of score +2 and terminate
```


### Shared by 6 move(s): Absorb, Drain Punch, Giga Drain, Heart Swap, Leech Life, Mega Drain

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

80.5% (206/256) of score -3 and terminate
```


### Shared by 6 move(s): Acid Armor, Barrier, Bulk Up, Harden, Iron Defense, Withdraw

```
If the user's current defense is boosted to +3 or more:

60.9% (156/256) chance of score -1 and continue

If the user's HP is full and its current defense is boosted to under +3:

50% (128/256) chance of score +2 and continue

If the user's HP is over 69%:

With a 78.1% (200/256) chance:

No scoring change and terminate

If the user's HP is under 40%:

Score -2 and terminate

If the last move used by the foe was nondamaging, or the foe has not yet used a move:

76.6% (196/256) chance of score -2 and terminate

If the last move used by the foe was special:

Score -2 and terminate

Otherwise:

58.6% (2401/4096) chance of score -2 and terminate
```


### Shared by 5 move(s): Amnesia, Calm Mind, Cosmic Power, Defend Order, Stockpile

```
If the user's current special defense is boosted to +3 or more:

60.9% (156/256) chance of score -1 and continue

If the user's HP is full and its current special defense is boosted to under +3:

50% (128/256) chance of score +2 and continue

If the user's HP is over 69%:

With a 78.1% (200/256) chance:

No scoring change and terminate

If the user's HP is under 40%:

Score -2 and terminate

If the last move used by the foe was nondamaging, or the foe has not yet used a move:

76.6% (196/256) chance of score -2 and terminate

If the last move used by the foe was physical:

Score -2 and terminate

Otherwise:
58.6% (2401/4096) chance of score -2 and terminate
```


### Shared by 5 move(s): Cotton Spore, Fake Tears, Metal Sound, Scary Face, String Shot

```
If the user will move before the target:

Score -3 and terminate

Otherwise:

72.7% (186/256) chance of score +2 and terminate
```


### Shared by 4 move(s): Confuse Ray, Supersonic, Sweet Kiss, Teeter Dance

```
If the target's HP is over 70%:

No scoring change and terminate

Unconditionally:

50% (128/256) chance of score -1 and continue

If the target's HP is under 51%:

Score -1 and continue

If the target's HP is under 31%:

Score -1 and terminate
```


### Shared by 4 move(s): Howl, Meditate, Sharpen, Swords Dance

```
If the user's current attack is boosted to +3 or more:

60.9% (156/256) chance of score -1 and continue

If the user's HP is full and its current attack is boosted to under +3:

50% (128/256) chance of score +2 and continue

If the user's HP is over 39% and under 71%:

84.4% (216/256) chance of score -2 and terminate

If the user's HP is under 40%:

Score -2 and terminate
```


### Shared by 3 move(s): Blizzard, Ice Ball, Sheer Cold

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

80.5% (206/256) chance of score -3 and terminate

If the current weather is hail:

Score +1 and terminate
```


### Shared by 3 move(s): Block, Mean Look, Spider Web

```
If the target is badly poisoned, or infatuated, or under the effect or Curse, or Perish Song:

50% (128/256) chance of score +1 and terminate
```


### Shared by 3 move(s): Brave Bird, Close Combat, Take Down

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user's attack is reduced to -1 or lower:

Score -1 and terminate

If the user will move after the target, and the user's HP is over 59%:

Score -1 and terminate

If the user will move before the target, and the user's HP is over 40%:

Score -1 and terminate
```


### Shared by 3 move(s): Charm, FeatherDance, Growl

```
If the target's current attack level is not +0:

Score -1 and continue

If the target's current attack level is not +0, and the user's HP is under 91%:

Score -1 and continue

If the target's current attack is reduced to -3 or lower:

80.5% (206/256) chance of score -2 and continue

If the target's HP is under 71%:

Score -2 and continue

If the last move used by the target was special:

50% (128/256) chance of score -2 and terminate
```


### Shared by 3 move(s): Explosion, Memento, Selfdestruct

```
If the target's evasion is boosted to +1 or more:

Score -1 and continue

If the target's evasion is boosted to +3 or more:

50% (128/256) chance of score -1 and continue

If the user's HP is under 80%, or the user will attack after the target:

If the user's HP is over 50%:

80.5% (206/256) chance of score -1 and terminate

If the user's HP is under 51%:

50% (128/256) chance of score +1 and continue

If the user's HP is under 31%:

80.5% (206/256) chance of score +1 and terminate

Else:

80.5% (206/256) chance of score -3 and terminate
```


### Shared by 3 move(s): Fissure, Guillotine, Horn Drill

```
Unconditionally:

25% (64/256) chance of score +1 and terminate
```


### Shared by 3 move(s): Flash, Sand-Attack, SmokeScreen

```
If the user's HP is under 70%, or the target's HP is under 71%:

60.9% (156/256) chance of score -1 and continue

If the user's accuracy is reduced to -2 or lower:

68.8% (176/256) chance of score -2 and continue

If the target is badly poisoned:

72.7% (186/256) chance of score +2 and continue

If the target is under the effect of Leech Seed:

72.7% (186/256) chance of score +2 and continue

If the user is under the effect of Ingrain or Aqua Ring:

50% (128/256) chance of score +1 and continue

If the target is under the effect of Curse:

72.7% (186/256) chance of score +2 and continue

If the user's HP is over 70%, or the target's current accuracy level is +0:

No scoring change and terminate

If the user's HP is under 40%, or the target's HP is under 40%:

Score -2 and terminate

Otherwise:

72.7% (186/256) chance of score -2 and terminate
```


### Shared by 3 move(s): Glare, Stun Spore, Thunder Wave

```
If the user will move after the target:

92.2% (236/256) chance of score +3 and terminate

If the user's HP is under 71%:

Score -1 and terminate
```


### Shared by 3 move(s): Icy Wind, Mud Shot, Rock Tomb

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

No scoring change and terminate

If the user will move before the target:

Score -3 and terminate

Otherwise:

72.7% (186/256) chance of score +2 and terminate
```


### Shared by 3 move(s): Leech Seed, Poison Gas, Toxic

```
If the user has a move that inflicts damage:

If the user's HP is under 51%:

80.5% (206/256) chance of score -3 and continue

If the target's HP is under 51%:

80.5% (206/256) chance of score -3 and continue

If the user knows the move Protect or Detect:

76.6% (196/256) chance of score +2 and terminate
```


### Shared by 3 move(s): Leer, Screech, Tail Whip

```
If the user's HP is under 70%, or the target's defense is reduced to -3 or lower:

80.5% (206/256) chance of score -2 and continue

If the target's HP is under 71%:

Score -2 and terminate
```


### Shared by 3 move(s): Moonlight, Morning Sun, Synthesis

```
If the current weather is rain, sandstorm, or hail:

Score -2 and continue

If the user's HP is full:

Score -3 and terminate

If the user will move before the target:

Score -8 and terminate

If the user's HP is over 69%:

With a 88.3% (226/256) chance:

Score -3 and terminate

If the foe knows the move Snatch:

56.2% (2301/4096) chance of score +2 and terminate

Otherwise:

92.2% (236/256) chance of score +2 and terminate
```


### Shared by 3 move(s): Spikes, Stealth Rock, Toxic Spikes

```
With a 50% (128/256) chance:

No scoring change and terminate

Else:

Score +1 and continue

If the user also knows the move Whirlwind or Roar:

75% (192/256) chance of score +1 and terminate
```


### Shared by 2 move(s): Agility, Rock Polish

```
If the user will move before the foe:

Score -3 and terminate

Otherwise:

72.7% (186/256) chance of score +3 and terminate
```


### Shared by 2 move(s): Aromatherapy, Heal Bell

```
If the user, and all of its other party members, are not statused:

Score -5 and terminate
```


### Shared by 2 move(s): Bide, Metal Burst

```
If the foe is asleep, infatuated, or confused:

Score -1 and terminate

If the foe knows the move Revenge, Avalanche, Focus Punch, or Vital Throw:

Score -1 and terminate

If the user's HP is under 31%:

96.1% (246/256) chance of score -1 and continue

If the user's HP is under 51%:

60.9% (156/256) chance of score -1 and continue

Unconditionally:

25% (64/256) chance of score +1 and continue

If the target is under the effect of Taunt, and the last move used by the target deals damage:

60.9% (156/256) chance of score +1 and continue

If the target is under the effect of Taunt:

60.9% (156/256) chance of score +1 and terminate
```


### Shared by 2 move(s): Bug Bite, Pluck

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If this is the user's first turn in battle:

75% (192/256) chance of score +1 and continue

Unconditionally:

50% (128/256) chance of score +1 and terminate
```


### Shared by 2 move(s): Detect, Protect

```
If the foe knows the move Feint or Shadow Force:

50% (128/256) chance of score -2 and continue

If the user's consecutive protection count is 2 or more:

Score -2 and terminate

If the user is badly poisoned, or infatuated, or under the effect of Curse, Leech Seed, Yawn, or Perish Song, or the foe knows the move Recover or Defense Curl:

If the user is under the effect of Lock-On or Mind Reader:

No scoring change and terminate

Else:

Score -2 and terminate

If the foe is badly poisoned, or infatuated, or under the effect of Curse, Leech Seed, Yawn, or Perish Song, or this is a double battle, or the user is under the effect of Lock-On or Mind Reader:

Score +2 and continue

Else:

33.2% (85/256) chance of score +2 and continue

Unconditionally:

50% (128/256) chance of score -1 and continue

If the user's consecutive protection count is 1:

Score -1 and continue

50% (128/256) chance of score -1 and terminate
```


### Shared by 2 move(s): Double Team, Minimize

```
If the user's HP is over 89%:

60.9% (156/256) chance of score +3 and continue

If the user's current evasion is boosted to +3 or more:

50% (128/256) chance of score -1 and continue

If the foe is badly poisoned:

If the user's HP is over 50%:

80.5% (206/256) chance of score +3 and continue

Else:

55.3% (1133/2048) chance of score +3 and continue

If the foe is under the effect of Leech Seed:

72.7% (186/256) chance of score +3 and continue

If the user is under the effect of Ingrain or Aqua Ring:

50% (128/256) chance of score +2 and continue

If the foe is under the effect of Curse:

72.7% (186/256) chance of score +3 and continue

If the user's HP is over 70%, or the user's current evasion level is +0:

No scoring change and terminate

If the user's HP is under 40%, or the foe's HP is under 40%:

Score -2 and terminate

Otherwise:

72.7% (186/256) chance of score -2 and terminate
```


### Shared by 2 move(s): Flail, Reversal

```
If the user will move before the target:

If the user's HP is over 33%:

Score -1 and terminate

If the user's HP is over 20%:

No scoring change and terminate

If the user's HP is under 8%:

Score +1 and continue

60.9% (156/256) chance of score +1 and terminate

If the user will move after the target:

If the user's HP is over 60%:

Score -1 and terminate

If the user's HP is over 40%:

No scoring change and terminate

Otherwise:

60.9% (156/256) chance of score +1 and terminate
```


### Shared by 2 move(s): Foresight, Odor Sleuth

```
If the user is Ghost type:

47.3% (121/256) chance of score +2 and terminate

If the target's current evasion is boosted to +3 or more:

68.8% (176/256) chance of score +2 and terminate

Otherwise:

Score -2 and terminate
```


### Shared by 2 move(s): Lock-On, Mind Reader

```
Unconditionally:

50% (128/256) chance of score +2 and terminate
```


### Shared by 2 move(s): Nasty Plot, Tail Glow

```
If the user's current special attack is boosted to +3 or more:

60.9% (156/256) chance of score -1 and continue

If the user's HP is full and its current special attack is boosted to under +3:

50% (128/256) chance of score +2 and continue

If the user's HP is over 39% and under 71%:

84.4% (216/256) chance of score -2 and terminate

If the user's HP is under 40%:

Score -2 and terminate
```


### Shared by 2 move(s): Pain Split, Snore

```
If the target's HP is under 80%:

Score -1 and terminate

If the user will move before the target:

If the user's HP is over 40%:

Score -1 and terminate

Else:

Score +1 and terminate

If the user will move after the target:

If the user's HP is over 60%:

Score -1 and terminate

Else:

Score +1 and terminate
```


### Shared by 2 move(s): Payback, Revenge

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user will move after the target, and the user's HP is over 29%:

75% (192/256) chance of score +1 and terminate
```


### Shared by 2 move(s): Pursuit, Rage

```
If this is the user's first turn in battle, or the target is Ghost or Psychic type:

50% (128/256) chance of score +1 and continue

If the target knows the move U-Turn:

50% (128/256) chance of score +1 and terminate
```


### Shared by 2 move(s): Roar, Whirlwind

```
If the target has been in battle for more than 3 turns:

75% (192/256) chance of score +2 and continue

50% (128/256) chance of score +2 and terminate

(Overall: 12.5% chance of no scoring change, 50% chance of score +2, 37.5% chance of score +4)

If the target's side of the field has Spikes, Stealth Rock, or Toxic Spikes set:

50% (128/256) chance of score +2 and terminate

If the target's attack, defense, special attack, special defense, or evasion is boosted to +3 or more:

50% (128/256) chance of score +2 and terminate

Otherwise:

Score -3 and terminate
```


### Shared by 2 move(s): Role Play, Skill Swap

```
If the user's ability is in the list below:

Score -1 and terminate

If the target's ability is in the list below:

80.5% (206/256) chance of score +2 and terminate

Otherwise:

Score -1 and terminate

Attached list:

Speed boost

Battle Armor

Sand Veil

Static

Flash Fire

Wonder Guard

Effect Spore

Swift Swim

Huge Power

Rain Dish

Cute Charm

Shed Skin

Marvel Scale

Pure Power

Chlorophyll

Shield Dust

Adaptability

Magic Guard

Mold Breaker

Super Luck

Unaware

Tinted Lens

Filter

Solid Rock

Reckless
```


### Shared by 1 move(s): Acupressure

```
If the user's HP is under 51%:

Score -1 and terminate

If the user's HP is over 90%:

75% (192/256) chance of score +1 and terminate

Otherwise:

37.5% (96/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Aqua Ring

```
If the user's HP is over 29%:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Assurance

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user will move before the target:

No scoring change and terminate

If the user's ability is Rough Skin:

50% (128/256) chance of score +1 and terminate

Otherwise:

25% (64/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Baton Pass

```
If the user's current attack, defense, special attack, special defense, or evasion is boosted to +3 or more:

If the user will move before the foe, and the user's HP is over 60%:

No scoring change and terminate

If the user will move after the foe, and the user's HP is over 70%:

No scoring change and terminate

Otherwise:

68.8% (176/256) chance of score +2 and terminate

If the user's current attack, defense, special attack, special defense, or evasion is boosted to +2 or more:

If the user will move before the foe:

If the user's HP is over 60%:

Score -2 and terminate

Else:

No scoring change and terminate

If the user will move after the foe:

If the user's HP is under 70%:

No scoring change and terminate

Else:

Score -2 and terminate

Otherwise:

Score -2 and terminate
```


### Shared by 1 move(s): Belly Drum

```
If the user's HP is under 90%:

Score -2 and terminate
```


### Shared by 1 move(s): Brick Break

```
If the target's side of the field has Reflect or Light Screen active:

Score +1 and terminate
```


### Shared by 1 move(s): Brine

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the target's HP is at or over 51%:

No scoring change and terminate

If the target's HP is under 51%:

Score +1 and continue

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Captivate

```
If the target's current special attack level is not +0:

Score -1 and continue

If the user's HP is under 91%:

Score -1 and continue

If the target's current special attack is reduced to -3 or lower:

80.5% (206/256) chance of score -2 and continue

If the target's HP is under 71%:

Score -2 and continue

If the last move used by the target was physical, or the target has not yet used a move:

75% (192/256) chance of score -1 and terminate
```


### Shared by 1 move(s): Copycat

```
If the user will move before the target:

If the last move used by the target (if used by the target against itself) would do more damage to the target than any of the user's moves:

87.5% (224/256) chance of score +2 and terminate

If the last move used by the target is in the list below:

50% (128/256) chance of score +2 and terminate

If the last move used by the target (if used by the target against itself) would not do more damage to the target than the user's most damaging move, and the last move used by the target is not in the list below:

68.8% (176/256) chance of score -1 and terminate

Attached list:

Sleep Powder

Lovely Kiss

Spore

Hypnosis

Sing

GrassWhistle

Shadow Punch

Sand-Attack

SmokeScreen

Toxic

Guillotine

Horn Drill

Fissure

Sheer Cold

Cross Chop

Aeroblast

Confuse Ray

Sweet Kiss

Screech

Cotton Spore

Scary Face

Fake Tears

Metal Sound

Thunder Wave

Glare

PoisonPowder

Shadow Ball

DynamicPunch

Hyper Beam

ExtremeSpeed

Thief

Covet

Attract

Swagger

Torment

Flatter

Trick

Superpower

Skill Swap

Psycho Shift

Power Swap

Guard Swap

Sucker Punch

Heart Swap

Switcheroo

Captivate

Dark Void
```


### Shared by 1 move(s): Counter

```
If the foe is asleep, infatuated, or confused:

Score -1 and terminate

If the user's HP is under 31%:

96.1% (246/256) chance of score -1 and continue

If the user's HP is under 51%:

60.9% (156/256) chance of score -1 and continue

If the user also knows the move Mirror Coat:

60.9% (156/256) chance of score +4 and terminate

If the foe is under the effect of Taunt:

60.9% (156/256) chance of score +1 and continue

If the last move used by foe was damaging:

If the last move used by the foe is special:

Score -1 and terminate

Else:

60.9% (156/256) chance of score +1 and terminate

If either of the foe's types is Normal, Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, or Steel:

No scoring change and terminate

Otherwise:

49% (4017/8192) chance of score +4 and terminate
```


### Shared by 1 move(s): Curse

```
If the user is Ghost type:

If the user's HP is under 81%:

Score -1 and terminate

Otherwise:

No scoring change and terminate

If the user's defense is boosted to +4 or more:

No scoring change and terminate

If the user knows the move Trick Room or Gyro Ball:

87.5% (224/256) chance of score +1 and continue

If score +1:

50% (128/256) chance of score +1 and continue

Else:

50% (128/256) chance of score +1 and continue

If the user's defense is boosted to +2 or more:

No scoring change and terminate

Unconditionally:

50% (128/256) chance of score +1 and continue

If the user's defense is boosted to +1 or more:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Defog

```
If the foe's side of the field has Light Screen or Reflect active:

If the user's HP is over 30%:

Score +1 and continue

If the user has no other living party members:

No score change and terminate

If the user's HP is under 31%, and the user has no other living party members:

If the foe's HP is under 71%:

Score -2 and continue

80.5% (206/256) chance of score -2 and terminate

If the foe's side of the field has Spikes, Stealth Rock, or Toxic Spikes active:

50% (128/256) chance of score -1 and continue

If the foe's side of the field does not have Light Screen or Reflect active, and has Spikes, Stealth Rock, or Toxic Spikes active:

Score -2 and continue

If the user's HP is under 70%, or the foe's evasion is reduced to -3 or lower:

80.5% (206/256) chance of score -2 and continue

If the foe's HP is under 71%:

Score -2 and terminate
```


### Shared by 1 move(s): Destiny Bond

```
If the user will move after the foe, or the user's HP is over 70%:

Score -1 and terminate

Unconditionally:

50% (128/256) chance of score -1 and continue

If the user's HP is under 51%:

50% (128/256) chance of score +1 and continue

If the user's HP is under 31%:

60.9% (156/256) chance of score +2 and terminate
```


### Shared by 1 move(s): Disable

```
If the user will move after the target:

No scoring change and terminate

If the last move used by the target was nondamaging, or the target has not yet used a move:

60.9% (156/256) chance of score -1 and terminate

Otherwise:

Score +1 and terminate
```


### Shared by 1 move(s): Dragon Dance

```
If the user will move after the foe:

50% (128/256) chance of score +1 and terminate

If the user's HP is under 51%:

72.7% (186/256) chance of score -1 and terminate
```


### Shared by 1 move(s): Dream Eater

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the target is asleep:

80.1% (205/256) of score +3 and terminate
```


### Shared by 1 move(s): Embargo

```
Unconditionally:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Encore

```
If the target is under the effect of Disable:

88.3% (226/256) chance of score +3 and terminate

If the user will move after the target:

Score -2 and terminate

If the last move used by the target is in the list below:

88.3% (226/256) chance of score +3 and terminate

Otherwise:

Score -2 and terminate

Attached list:

NOTE: This is a vanilla list, there may be a difference in moves.

Dream Eater

Meditate

Sharpen

Howl

Harden

Withdraw

Growth

Haze

Whirlwind

Roar

Conversion

Toxic

Light Screen

Rest

Super Fang

Amnesia

Supersonic

Confuse Ray

Sweet Kiss

PoisonPowder

Poison Gas

Stun Spore

Thunder Wave

Glare

Leech seed

Splash

Swords Dance

Encore

Conversion2

Mind Reader

Lock-On

Heal Bell

Aromatherapy

Spider Web

Mean Look

Block

Nightmare

Protect

Detect

Skill Swap

Foresight

Odor Sleuth

Perish Song

Sandstorm

Endure

Swagger

Attract

Safeguard

Rain Dance

Sunny Day

Belly Drum

Psych Up

Future Sight

Doom Desire

Fake Out

Stockpile

Spit Up

Swallow

Hail

Torment

Will-O-Wisp

Follow me

Charge

Trick

Switcheroo

Role Play

Ingrain

Recycle

Knock Off

Imprison

Refresh

Grudge

Teeter Dance

Mud Sport

Water Sport

Dragon Dance

Camouflage

Gravity

Miracle Eye

Healing Wish

Natural Gift

Feint

Tailwind

Acupressure

Fling

Psycho Shift

Heal Block

Power Trick

Gastro Acid

Lucky Chant

Power Swap

Guard Swap

Worry Seed

Heart Swap

Aqua Ring

Magnet Rise

Trick Room
```


### Shared by 1 move(s): Endeavor

```
If the target's HP is under 70%:

Score -1 and terminate

If the user will move before the target, and the user's HP is over 40%:

Score -1 and terminate

If the user will move after the target, and the user's HP is over 50%:

Score -1 and terminate

Otherwise:

Score +1 and terminate
```


### Shared by 1 move(s): Endure

```
If the user's HP is under 4%:

Score -1 and terminate

If the user's HP is under 35%:

72.7% (186/256) chance of score +1 and terminate

Otherwise:

Score -1 and terminate
```


### Shared by 1 move(s): Facade

```
If the target is burned, paralyzed, poisoned, or badly poisoned:

Score +1 and terminate
```


### Shared by 1 move(s): Fake Out

```
Unconditionally:

Score +2 and terminate
```


### Shared by 1 move(s): Feint

```
If the target does not know protect:

With a 75% (192/256) chance:

No scoring change and terminate

If the user is badly poisoned, or infatuated, or under the effect of Curse, Perish Song, Leech Seed, or Yawn, or the target's HP is not full, or the target is holding Leftovers or Black Sludge:

50% (128/256) chance of score +1 and continue

If the consecutive protection count of the target is 0:

50% (128/256) chance of score +1 and terminate

If the consecutive protection count of the target is 1:

25% (64/256) chance of score +1 and terminate

If the consecutive protection count of the target is 2 or more:

Score -2 and terminate
```


### Shared by 1 move(s): Flatter

```
Unconditionally:

50% (128/256) chance of score +1 and continue

If the target's HP is over 70%:

No scoring change and terminate

Unconditionally:

50% (128/256) chance of score -1 and continue

If the target's HP is under 51%:

Score -1 and continue

If the target's HP is under 31%:

Score -1 and terminate
```


### Shared by 1 move(s): Fling

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

If the user is not holding a King's Rock, Razor Fang, Poison Barb, Toxic Orb, Flame Orb, or Light Ball:

Score -1 and terminate

Else:

No score change and terminate

If the Fling power of the user's item is 10:

Score -2 and terminate

If the Fling power of the user's item is 100 or 130:

If the effectiveness of the move is 2x or 4x:

Score +4 and continue

Else:

50% (128/256) chance of score +1 and continue

75% (192/256) chance of score +1 and terminate

If the Fling power of the user's item is 70, 80, or 90:

75% (192/256) chance of score +1 and terminate

Otherwise:

50% (128/256) chance of score -1 and terminate
```


### Shared by 1 move(s): Fly

```
If the user is holding a Power Herb:

Score +2 and terminate

If the target knows the move Protect or Detect:

Score -1 and terminate

If the effectiveness of the move is 1/4x, 1/2x or 0x:

Score +1 and terminate

If the target is badly poisoned, or under the effect or Curse or Leech Seed:

68.8% (176/256) chance of score +1 and terminate

If the current weather is hail and the user is Ice type, or the current weather is sandstorm and the user is Rock, Ground, or Steel type:

68.8% (176/256) chance of score +1 and terminate

If the user will move after the target:

No scoring change and terminate

If the last move used by the target was Lock-On or Mind Reader:

No scoring change and terminate

Otherwise:

68.8% (176/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Focus Punch

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user is behind a substitute:

Score +5 and terminate

If the target is asleep:

Score +1 and terminate

If the target is infatuated or confused:

60.9% (156/256) chance of score +1 and terminate

If this is the user's first turn in battle:

21.9% (56/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Gastro Acid

```
With a 25% (64/256) chance:

No scoring change and terminate

Else:

Score +1 and continue

If the target's HP is under 71%:

50% (128/256) chance of score -1 and continue

If the target's HP is under 51%:

Score -1 and continue

If the target's HP is under 31%:

Score -1 and terminate
```


### Shared by 1 move(s): Gravity

```
If the foe is Flying type, or has the ability Levitate, or is under the effect of Magnet Rise:

75% (192/256) chance of score +1 and terminate

If the user's HP is over 59%:

37.5% (96/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Growth

```
If the user's current special attack is boosted to +3 or more:

60.9% (156/256) chance of score -1 and continue

If the user's HP is full and its current special attack is boosted to under +3:

50% (128/256) chance of score +2 and continue

If the user's HP is over 39% and under 71%:

72.7% (186/256) chance of score -2 and terminate

If the user's HP is under 40%:

Score -2 and terminate
```


### Shared by 1 move(s): Guard Swap

```
If the user's defense or special defense is boosted to a higher level than the target's:

No score change and terminate

If the target's defense is boosted to a higher level than the user's, and the target's special defense level is exactly +1 higher than the user's:

No score change and terminate

For the following checks, sum together the number of stages the target's defense and special defense are higher than the user's, with each stat being limited to a maximum of +4.

If the sum is equal to 8:

With a 50% (128/256) chance:

Score +5 and terminate

If the sum is greater than or equal to 6:

With a 50% (128/256) chance:

Score +4 and terminate

If the sum is greater than or equal to 4:

With a 50% (128/256) chance:

Score +3 and terminate

If the sum is greater than or equal to 2:

With a 50% (128/256) chance:

Score +2 and terminate

If the sum is or equal to 1:

With a 50% (128/256) chance:

Score +1 and terminate
```


### Shared by 1 move(s): Hail

```
If the user's HP is under 40%:

Score -1 and terminate

If the weather is rain, sun, or sandstorm:

Score +1 and continue

If the user knows the move Blizzard:

Score +2 and continue

If the user's ability is Ice Body:

Score +2 and terminate
```


### Shared by 1 move(s): Hammer Arm

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user will move after the target:

Score +1 and terminate
```


### Shared by 1 move(s): Haze

```
If the user's current attack, defense, special attack, special defense, or evasion is boosted to +3 or more, or the target's current attack, defense, special attack, special defense, or evasion is reduced to -3 or lower:

80.5% (206/256) chance of score -3 and continue

If the user's current attack, defense, special attack, special defense, or evasion is reduced to -3 or lower, or the target's current attack, defense, special attack, special defense, or evasion is boosted to +3 or more:

19.5% (50/256) chance of score +3 and terminate

Otherwise:

80.5% (206/256) chance of score -1 and terminate
```


### Shared by 1 move(s): Imprison

```
If this is not the first turn the user has been in battle:

60.9% (156/256) chance of score +2 and terminate
```


### Shared by 1 move(s): Kinesis

```
If the user's HP is under 70%, or the target's special defense is reduced to -3 or lower:

80.5% (206/256) chance of score -2 and continue

If the target's HP is under 71%:

Score -2 and terminate
```


### Shared by 1 move(s): Knock Off

```
If the target's HP is under 30%:

No scoring change and terminate

If this is not the user's first turn in battle:

29.7% (76/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Last Resort

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user has used all of its other moves:

Score +1 and terminate
```


### Shared by 1 move(s): Light Screen

```
If the user's HP is under 50%:

Score -2 and terminate

If the user's HP is over 89%:

50% (128/256) chance of score +1 and continue

If the last move used by the foe was special:

75% (192/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Lucky Chant

```
If the user's HP is under 70%:

Score -1 and terminate

If the opponent knows a move with a high critical hit ratio:

Score +1 and terminate

Otherwise:

25% (64/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Magic Coat

```
If the user's HP is under 31%:

60.9% (156/256) chance of score -1 and continue

If this is the user's first turn in battle:

41.4% (106/256) chance of score +1 and terminate

Otherwise:

88.3% (226/256) chance of score -1 and terminate
```


### Shared by 1 move(s): Magnet Rise

```
If the user's HP is under 50%:

No scoring change and terminate

If the foe knows the move Earthquake, Earth Power, or Fissure:

Score +1 and continue

If the foe is Ground type:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Me First

```
If the user will move after the target:

Score -2 and terminate

If the last move used by the target (if used by the target against itself) would do more damage to the target than any of the user's moves:

87.5% (224/256) chance of score +1 and continue

If the last move used by the target was not a status move, or the target has not yet used a move:

With a 50% (128/256) chance:

Score +1 and continue

75% (192/256) chance of score +1 and terminate

Else:

No scoring change and terminate

Otherwise:

75% (192/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Miracle Eye

```
If the target is Dark type:

47.3% (121/256) chance of score +2 and terminate

If the target's current evasion is boosted to +3 or more:

68.8% (176/256) chance of score +2 adn terminate

Otherwise:

Score -2 and terminate
```


### Shared by 1 move(s): Mirror Coat

```
If the foe is asleep, infatuated, or confused:

Score -1 and terminate

If the user's HP is under 31%:

96.1% (246/256) chance of score -1 and continue

If the user's HP is under 51%:

60.9% (156/256) chance of score -1 and continue

If the user also knows the move Counter:

60.9% (156/256) chance of score +4 and terminate

If the foe is under the effect of Taunt:

60.9% (156/256) chance of score +1 and continue

If the last move used by foe was damaging:

If the last move used by the foe is physical:

Score -1 and terminate

Else:

60.9% (156/256) chance of score +1 and terminate

If either of the foe's types is Fire, Water, Grass, Electric, Psychic, Ice, Dragon, or Dark:

No scoring change and terminate

Otherwise:

49% (4017/8192) chance of score +4 and terminate
```


### Shared by 1 move(s): Mirror Move

```
If the user will move before the target, and the last move used by the target is in the list below:

50% (128/256) chance of score +2 and terminate

If the last move used by the target is not in the list below, or the target has not yet used a move:

68.8% (176/256) chance of score -1 and terminate

Attached list:

Sleep Powder

Lovely Kiss

Spore

Hypnosis

Sing

GrassWhistle

Shadow Punch

Sand-Attack

SmokeScreen

Toxic

Guillotine

Horn Drill

Fissure

Sheer Cold

Cross Chop

Aeroblast

Confuse Ray

Sweet Kiss

Screech

Cotton Spore

Scary Face

Fake Tears

Metal Sound

Thunder Wave

Glare

PoisonPowder

Shadow Ball

DynamicPunch

Hyper Beam

ExtremeSpeed

Thief

Covet

Attract

Swagger

Torment

Flatter

Trick

Superpower

Skill Swap

Psycho Shift

Power Swap

Guard Swap

Sucker Punch

Heart Swap

Switcheroo

Captivate

Dark Void
```


### Shared by 1 move(s): PoisonPowder

```
If the user's HP is under 50%, or the target's HP is under 51%:

Score -1 and terminate
```


### Shared by 1 move(s): Power Swap

```
If the user's attack or special attack is boosted to a higher level than the target's:

No score change and terminate

If the target's attack is boosted to a higher level than the user's, and the target's special attack level is exactly +1 higher than the user's:

No score change and terminate

For the following checks, sum together the number of stages the target's attack and special attack are higher than the user's, with each stat being limited to a maximum of +4.

If the sum is equal to 8:

With a 50% (128/256) chance:

Score +5 and terminate

If the sum is greater than or equal to 6:

With a 50% (128/256) chance:

Score +4 and terminate

If the sum is greater than or equal to 4:

With a 50% (128/256) chance:

Score +3 and terminate

If the sum is greater than or equal to 2:

With a 50% (128/256) chance:

Score +2 and terminate

If the sum is or equal to 1:

With a 50% (128/256) chance:

Score +1 and terminate
```


### Shared by 1 move(s): Power Trick

```
If the user's HP is over 90%:

62.5% (160/256) chance of score +1 and terminate

If the user's HP is over 60%:

50% (128/256) chance of score +1 and terminate

If the user's HP is over 30%:

35.9% (92/256) chance of score +1 and terminate

Otherwise:

Score -2 and terminate
```


### Shared by 1 move(s): Psych Up

```
If the target's current attack, defense, special attack, special defense, or evasion are boosted to +3 or more:

If the user's current attack, defense, special attack, or special defense are at +0 or below:

Score +1 and terminate

If the user's current evasion is at +0 or below:

Score +2 and terminate

Otherwise:

80.5% (206/256) chance of score -2 and terminate

Otherwise:

Score -2 and terminate
```


### Shared by 1 move(s): Psycho Shift

```
If the user is not statused:

Score -10 and terminate

If the target's HP is over 29%:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Punishment

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

No scoring change and terminate

If the total number of positive stat boosts for the target is 7 or more:

50% (128/256) chance of score +4 and continue

If the total number of positive stat boosts for the target is 6 or more:

50% (128/256) chance of score +3 and continue

If the total number of positive stat boosts for the target is 5 or more:

50% (128/256) chance of score +2 and continue

If the total number of positive stat boosts for the target is 3 or more:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Rain Dance

```
If the user will move after the foe, and the user's ability is Swift Swim:

Score +1 and terminate

If the user's HP is under 40%:

Score -1 and terminate

If the current weather is sun, hail, or sandstorm, or the user's ability is Rain Dish, or the user's ability is Hydration and the user is statused:

Score +1 and terminate
```


### Shared by 1 move(s): Razor Wind

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -2 and terminate

If the user is holding a Power Herb:

Score +2 and terminate

If the target knows the move Protect or Detect:

Score -2 and terminate

If the user's HP is under 39%:

Score -1 and terminate
```


### Shared by 1 move(s): Recycle

```
If the user can recycle a Chesto Berry, Lum Berry, or Starf Berry:

80.5% (206/256) chance of score +1 and terminate

Otherwise:

Score -2 and terminate
```


### Shared by 1 move(s): Reflect

```
If the user's HP is under 50%:

Score -2 and terminate

If the user's HP is over 89%:

50% (128/256) chance of score +1 and continue

If the last move used by the foe was physical:

75% (192/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Refresh

```
If the foes's HP is under 50%:

Score -1 and terminate
```


### Shared by 1 move(s): Rest

```
If the user will move before the foe:

If the user's HP is full:

Score -8 and terminate

If the user's HP is over 50%:

Score -3 and terminate

If the user's HP is over 39%:

With a 72.7% (186/256) chance:

Score -3 and terminate

If the user will move after the foe:

If the user's HP is over 70%:

Score -3 and terminate

If the user's HP is over 59%:

With a 80.5% (206/256) chance:

Score -3 and terminate

If the foe knows the move Snatch:

77.3% (12669/16384) chance of score +3 and terminate

Otherwise:

96.1% (246/256) chance of score +3 and terminate
```


### Shared by 1 move(s): Shadow Force

```
If the effectiveness of the move is 1/4x, 1/2x or 0x:

Score +1 and terminate

If the user is holding a Power Herb:

Score +1 and terminate

If the target is badly poisoned, or under the effect or Curse or Leech Seed:

68.8% (176/256) chance of score +1 and terminate

If the current weather is hail and the user is Ice type, or the current weather is sandstorm and the user is Rock, Ground, or Steel type:

68.8% (176/256) chance of score +1 and terminate

If the user will move after the target:

No scoring change and terminate

If the last move used by the target was Lock-On or Mind Reader:

No scoring change and terminate

Otherwise:

68.8% (176/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Sleep Talk

```
If the user is currently asleep:

Score +10 and terminate

Otherwise:

Score -5 and terminate
```


### Shared by 1 move(s): SmellingSalt

```
If the target is paralyzed:

Score +1 and terminate
```


### Shared by 1 move(s): SolarBeam

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -2 and terminate

If the user is holding a Power Herb, or the current weather is sunny:

Score +2 and terminate

If the target knows the move Protect or Detect:

Score -2 and terminate

If the user's HP is under 39%:

Score -1 and terminate
```


### Shared by 1 move(s): Substitute

```
If the user knows the move Focus Punch:

62.5% (160/256) chance of score +1 and continue

If the user's HP is under 91%:

60.9% (156/256) chance of score -1 and continue

If the user's HP is under 71%:

60.9% (156/256) chance of score -1 and continue

If the user's HP is under 51%:

60.9% (156/256) chance of score -1 and continue

If the user will move after the foe:

No scoring change and terminate

If the last move used by the foe directly inflicts sleep, poison, paralysis, or burns, and the foe is not currently statused:

60.9% (156/256) chance of score +1 and terminate

If the last move used by the foe was Supersonic, Confuse Ray, or Sweet Kiss, and the foe is not currently confused:

60.9% (156/256) chance of score +1 and terminate

If the last move used by the foe was Leech Seed, and the foe is not currently under the effect of Leech Seed:

60.9% (156/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Sunny Day

```
If the user's HP is under 40%:

Score -1 and terminate

If the current weather is rain, hail, or sandstorm, or the user's ability is Flower Gift, or the user's ability is Leaf Guard and the user is statused:

Score +1 and terminate
```


### Shared by 1 move(s): Super Fang

```
If the target's HP is under 51%:

Score -1 and terminate
```


### Shared by 1 move(s): Swagger

```
If the user knows the move Psych Up:

If the target's current attack is reduced to -3 or lower:

If this is the first turn of the battle:

Score +5 and terminate

Else:

Score +3 and terminate

Else:

Score -5 and terminate

Unconditionally:

50% (128/256) chance of score +1 and continue

If the target's HP is over 70%:

No scoring change and terminate

Unconditionally:

50% (128/256) chance of score -1 and continue

If the target's HP is under 51%:

Score -1 and continue

If the target's HP is under 31%:

Score -1 and terminate
```


### Shared by 1 move(s): Sweet Scent

```
If the user's HP is under 70%, or the target's evasion is reduced to -3 or lower:

80.5% (206/256) chance of score -2 and continue

If the target's HP is under 71%:

Score -2 and terminate
```


### Shared by 1 move(s): Tailwind

```
With a 25% (64/256) chance:

No scoring change and terminate

If the user will move before the foe, or the user's HP is under 31%:

Score -1 and terminate

If the user's HP is over 75%:

Score +1 and terminate

Otherwise:

75% (192/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Trick Room

```
If this is a double/multi battle:

No scoring change and terminate

If the user's HP is under 31%, and the user has no living party members:

No scoring change and terminate

If the user will move after the foe:

75% (192/256) chance of score +3 and terminate

Else:

Score -1 and terminate
```


### Shared by 1 move(s): Trump Card

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the remaining PP of the move is 4 or more:

If the foe's ability is Pressure:

88.3% (226/256) chance of score +1 and continue

If the target's current evasion is boosted to +5 or more, or the user's current accuracy is reduced to -5 or lower:

Score +1 and continue

If the target's current evasion is boosted to +3 or more, or the user's current accuracy is reduced to -3 or lower:

60.9% (156/256) chance of score +1 and terminate

If the remaining PP of the move is 1:

Score +3 and terminate

If the remaining PP of the move is 2:

Score +1 and continue

60.9% (156/256) chance of score +1 and terminate

If the remaining PP of the move is 3:

60.9% (156/256) chance of score +1 and terminate
```


### Shared by 1 move(s): U-turn

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user has no other living party members:

No score change and terminate

If the user has a supereffective move against the target:

75% (192/256) chance of score -2 and continue

If no move a party member knows (if used by the user) would deal more damage than the user's most damaging move:

75% (192/256) chance of score -2 and terminate

If the user's HP is over 70%:

75% (192/256) chance of score +1 and continue

If the user's HP is over 30%:

50% (128/256) chance of score +1 and continue

If the user's HP is under 31%:

25% (64/256) chance of score +1 and continue

If the user will move before the target:

Score +1 and terminate

Else:

50% (128/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Wake-Up Slap

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the target is asleep:

Score +1 and terminate
```


### Shared by 1 move(s): Water Spout

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the user will attack after the target:

If the target's HP is over 70%:

No scoring change and terminate
=
Else:

Score -1 and terminate

If the target's HP is over 50%:

No score change and terminate

Otherwise:

Score -1 and terminate
```


### Shared by 1 move(s): Worry Seed

```
If the target knows the move Rest:

Score +1 and continue

If the target's HP is over 49%:

50% (128/256) chance of score +1 and continue

Unconditionally:

75% (192/256) chance of score +1 and terminate
```


### Shared by 1 move(s): Wring Out

```
If the effectiveness of the move is 1/2x, 1/4x, or 0x:

Score -1 and terminate

If the target's HP is under 51%:

Score +1 and continue

50% (128/256) chance of score +1 and terminate
```


### No applicable AI procedure (226 moves)

Accelerock, Acid, Aeroblast, Air Slash, AncientPower, Aqua Jet, Aqua Tail, Assist, Astonish, Attack Order, Attract, Avalanche, Beat Up, Bite, Body Slam, Bone Club, Bone Rush, Bonemerang, Bounce, Bubble, BubbleBeam, Bug Buzz, Bulldoze, Bullet Punch, Bullet Seed, Camouflage, Charge, Charge Beam, Chatter, Clamp, Confusion, Constrict, Conversion 2, Crunch, Crush Claw, Crush Grip, Cut, Dark Pulse, Dig, Discharge, Dive, Dizzy Punch, Doom Desire, Double Hit, Double Kick, DoubleSlap, Dragon Rage, Dragon Rush, DragonBreath, DynamicPunch, Earth Power, Earthquake, Egg Bomb, Ember, Energy Ball, Extrasensory, ExtremeSpeed, False Swipe, Fire Ball, Fire Blast, Fire Fang, Fire Punch, Fire Spin, Flame Wheel, Flamethrower, Flash Cannon, Focus Blast, Focus Energy, Follow Me, Force Palm, Frustration, Fury Attack, Fury Cutter, Fury Swipes, Future Sight, Grass Knot, Grudge, Gunk Shot, Gust, Gyro Ball, HP Dark, HP Electric, HP Fighting, HP Fire, HP Flying, HP Ghost, HP Grass, HP Ground, HP Ice, HP Psychic, HP Rock, HP Water, Hail Ball, Headbutt, Heat Wave, Helping Hand, Hi Jump Kick, Hidden Power, Hurricane, Hydro Pump, Hyper Fang, Hyper Voice, Ice Beam, Ice Fang, Ice Punch, Ice Shard, Icicle Spear, Ingrain, Iron Head, Iron Tail, Judgment, Jump Kick, Lava Plume, Leaf Storm, Lick, Low Kick, Luster Purge, Mach Punch, Magma Storm, Mega Kick, Mega Punch, Metal Claw, Meteor Mash, Metronome, Mimic, Mirror Shot, Mist, Mist Ball, Mud Bomb, Mud-Slap, Muddy Water, Mystical Fire, Natural Gift, Nature Power, Needle Arm, Night Shade, Octazooka, Ominous Wind, Pay Day, Peck, Perish Song, Petal Dance, Pin Missile, Poison Fang, Poison Jab, Poison Sting, Pound, Powder Snow, Power Gem, Present, Psybeam, Psychic, Psycho Boost, Quick Attack, Return, Rock Ball, Rock Blast, Rock Climb, Rock Slide, Rock Smash, Rock Throw, Rock Wrecker, Rolling Kick, Sacred Fire, Safeguard, Sand Tomb, Sandstorm, Scald, Scratch, Secret Power, Seed Bomb, Seed Flare, Seismic Toss, Shadow Ball, Shadow Claw, Shadow Sneak, Signal Beam, Silver Wind, Sketch, Sky Uppercut, Slam, Sludge, Sludge Bomb, Smog, Solar-Beam, SonicBoom, Spite, Steel Wing, Stomp, Strength, Submission, Sucker Punch, Surf, Swallow, Tackle, Teleport, Thief, Thunder, Thunder Fang, ThunderPunch, ThunderShock, Thunderbolt, Tickle, Torment, Transform, Tri Attack, Triple Axel, Triple Kick, Twineedle, Twister, Uproar, Vacuum Wave, ViceGrip, Vine Whip, Water Ball, Water Gun, Water Pulse, Waterfall, Weather Ball, Whirlpool, Will-O-Wisp, Wing Attack, Wish, Wrap, Zap Cannon, Zen Headbutt


## prio_damage

- 1 distinct scoring blocks (+ 284 moves with no applicable procedure) out of 466 moves


### Shared by 182 move(s): Acid Armor, Acupressure, Agility, Amnesia, Aqua Ring, Aromatherapy, Assist, Attract, Barrier, Baton Pass, Belly Drum, Bide, Block, Brave Bird, Bulk Up, Calm Mind, Camouflage, Captivate, Charge, Charm, Close Combat, Confuse Ray, Conversion 2, Copycat, Cosmic Power, Cotton Spore, Counter, Curse, Dark Void, Defend Order, Defog, Destiny Bond, Detect, Disable, Double Team, Dragon Dance, Dream Eater, Embargo, Encore, Endeavor, Endure, Explosion, Fake Tears, FeatherDance, Fissure, Flail, Flash, Flatter, Fling, Focus Energy, Focus Punch, Follow Me, Foresight, Gastro Acid, Glare, GrassWhistle, Gravity, Growl, Growth, Grudge, Guard Swap, Guillotine, Hail, Harden, Haze, Head Smash, Heal Bell, Heal Order, Helping Hand, Horn Drill, Howl, Hypnosis, Imprison, Ingrain, Iron Defense, Kinesis, Leech Seed, Leer, Light Screen, Lock-On, Lovely Kiss, Lucky Chant, Lunar Dance, Magic Coat, Magnet Rise, Me First, Mean Look, Meditate, Memento, Metal Burst, Metal Sound, Metronome, Milk Drink, Mimic, Mind Reader, Minimize, Miracle Eye, Mirror Coat, Mirror Move, Mist, Moonlight, Morning Sun, Nasty Plot, Nature Power, Odor Sleuth, Pain Split, Perish Song, Poison Gas, PoisonPowder, Power Swap, Power Trick, Present, Protect, Psych Up, Psycho Shift, Punishment, Rain Dance, Razor Wind, Recover, Recycle, Reflect, Refresh, Rest, Reversal, Roar, Rock Polish, Role Play, Roost, Safeguard, Sand-Attack, Sandstorm, Scary Face, Screech, Selfdestruct, Sharpen, Sing, Sketch, Skill Swap, Slack Off, Sleep Powder, Sleep Talk, SmokeScreen, Softboiled, SolarBeam, Spider Web, Spikes, Spite, Spore, Stealth Rock, Stockpile, String Shot, Stun Spore, Substitute, Sunny Day, Super Fang, Supersonic, Swagger, Sweet Kiss, Sweet Scent, Swords Dance, Synthesis, Tail Glow, Tail Whip, Tailwind, Take Down, Teeter Dance, Teleport, Thunder Wave, Tickle, Torment, Toxic, Toxic Spikes, Transform, Trick Room, Trump Card, Water Spout, Whirlwind, Will-O-Wisp, Wish, Withdraw, Worry Seed, Yawn

```
Unconditionally:

61% (156/256) chance of score +2 and terminate
```


### No applicable AI procedure (284 moves)

Absorb, Accelerock, Acid, Aerial Ace, Aeroblast, Air Cutter, Air Slash, AncientPower, Aqua Cutter, Aqua Jet, Aqua Tail, Assurance, Astonish, Attack Order, Aura Sphere, Aurora Beam, Avalanche, Beat Up, Bite, Blast Burn, Blaze Kick, Blizzard, Body Slam, Bone Club, Bone Rush, Bonemerang, Bounce, Brick Break, Brine, Bubble, BubbleBeam, Bug Bite, Bug Buzz, Bulldoze, Bullet Punch, Bullet Seed, Charge Beam, Chatter, Clamp, Confusion, Constrict, Crabhammer, Cross Chop, Cross Poison, Crunch, Crush Claw, Crush Grip, Cut, Dark Pulse, Dig, Discharge, Dive, Dizzy Punch, Doom Desire, Double Hit, Double Kick, Double-Edge, DoubleSlap, Draco Meteor, Dragon Claw, Dragon Pulse, Dragon Rage, Dragon Rush, DragonBreath, Drain Punch, Drill Peck, Drill Run, DynamicPunch, Earth Power, Earthquake, Egg Bomb, Ember, Energy Ball, Eruption, Extrasensory, ExtremeSpeed, Facade, Faint Attack, Fake Out, False Swipe, Feint, Fire Ball, Fire Blast, Fire Fang, Fire Punch, Fire Spin, Flame Wheel, Flamethrower, Flare Blitz, Flash Cannon, Fly, Focus Blast, Force Palm, Frenzy Plant, Frustration, Fury Attack, Fury Cutter, Fury Swipes, Future Sight, Giga Drain, Giga Impact, Grass Knot, Gunk Shot, Gust, Gyro Ball, HP Dark, HP Electric, HP Fighting, HP Fire, HP Flying, HP Ghost, HP Grass, HP Ground, HP Ice, HP Psychic, HP Rock, HP Water, Hail Ball, Hammer Arm, Headbutt, Heart Swap, Heat Wave, Hi Jump Kick, Hidden Power, Hurricane, Hydro Cannon, Hydro Pump, Hyper Beam, Hyper Fang, Hyper Voice, Ice Ball, Ice Beam, Ice Fang, Ice Punch, Ice Shard, Icicle Spear, Icy Wind, Iron Head, Iron Tail, Judgment, Jump Kick, Karate Chop, Knock Off, Last Resort, Lava Plume, Leaf Blade, Leaf Storm, Leech Life, Lick, Low Kick, Luster Purge, Mach Punch, Magical Leaf, Magma Storm, Magnet Bomb, Mega Drain, Mega Kick, Mega Punch, Megahorn, Metal Claw, Meteor Mash, Mirror Shot, Mist Ball, Mud Bomb, Mud Shot, Mud-Slap, Muddy Water, Mystical Fire, Natural Gift, Needle Arm, Night Shade, Night Slash, Octazooka, Ominous Wind, Outrage, Overheat, Pay Day, Payback, Peck, Petal Dance, Pin Missile, Pluck, Poison Fang, Poison Jab, Poison Sting, Poison Tail, Pound, Powder Snow, Power Gem, Power Whip, Psybeam, Psychic, Psycho Boost, Psycho Cut, Pursuit, Quick Attack, Rage, Razor Leaf, Return, Revenge, Roar of Time, Rock Ball, Rock Blast, Rock Climb, Rock Slide, Rock Smash, Rock Throw, Rock Tomb, Rock Wrecker, Rolling Kick, Sacred Fire, Sand Tomb, Scald, Scratch, Secret Power, Seed Bomb, Seed Flare, Seismic Toss, Shadow Ball, Shadow Claw, Shadow Force, Shadow Punch, Shadow Sneak, Sheer Cold, Shock Wave, Signal Beam, Silver Wind, Sky Attack, Sky Uppercut, Slam, Slash, Sludge, Sludge Bomb, SmellingSalt, Smog, Snore, Solar-Beam, SonicBoom, Spacial Rend, Steel Wing, Stomp, Stone Edge, Strength, Submission, Sucker Punch, Superpower, Surf, Swallow, Swift, Tackle, Thief, Thrash, Thunder, Thunder Fang, ThunderPunch, ThunderShock, Thunderbolt, Tri Attack, Triple Axel, Triple Kick, Twineedle, Twister, U-turn, Uproar, Vacuum Wave, ViceGrip, Vine Whip, Vital Throw, Volt Tackle, Wake-Up Slap, Water Ball, Water Gun, Water Pulse, Waterfall, Weather Ball, Whirlpool, Wild Charge, Wing Attack, Wood Hammer, Wrap, Wring Out, X-Scissor, Zap Cannon, Zen Headbutt


## baton_pass

- 6 distinct scoring blocks (+ 290 moves with no applicable procedure) out of 466 moves


### Shared by 159 move(s): Barrier, Belly Drum, Bide, Block, Brave Bird, Bulk Up, Camouflage, Captivate, Charge, Charm, Close Combat, Confuse Ray, Conversion 2, Copycat, Cosmic Power, Cotton Spore, Counter, Curse, Dark Void, Defend Order, Defog, Destiny Bond, Disable, Double Team, Embargo, Encore, Endeavor, Endure, Explosion, Fake Tears, FeatherDance, Fissure, Flail, Flash, Flatter, Fling, Focus Energy, Follow Me, Foresight, Gastro Acid, Glare, GrassWhistle, Gravity, Growl, Growth, Grudge, Guard Swap, Guillotine, Hail, Harden, Haze, Head Smash, Heal Bell, Heal Order, Helping Hand, Horn Drill, Howl, Hypnosis, Imprison, Ingrain, Iron Defense, Kinesis, Leech Seed, Leer, Light Screen, Lock-On, Lovely Kiss, Lucky Chant, Lunar Dance, Magic Coat, Magnet Rise, Me First, Mean Look, Meditate, Memento, Metal Burst, Metal Sound, Metronome, Milk Drink, Mimic, Mind Reader, Minimize, Miracle Eye, Mirror Coat, Mirror Move, Mist, Moonlight, Morning Sun, Nature Power, Odor Sleuth, Pain Split, Perish Song, Poison Gas, PoisonPowder, Power Swap, Power Trick, Present, Psych Up, Psycho Shift, Rain Dance, Recover, Recycle, Reflect, Refresh, Rest, Reversal, Roar, Rock Polish, Role Play, Roost, Safeguard, Sand-Attack, Sandstorm, Scary Face, Screech, Selfdestruct, Sharpen, Sing, Sketch, Skill Swap, Slack Off, Sleep Powder, Sleep Talk, SmokeScreen, Softboiled, SolarBeam, Spider Web, Spikes, Spite, Spore, Stealth Rock, Stockpile, String Shot, Stun Spore, Substitute, Sunny Day, Super Fang, Supersonic, Swagger, Sweet Kiss, Sweet Scent, Synthesis, Tail Whip, Tailwind, Take Down, Teeter Dance, Teleport, Thunder Wave, Tickle, Torment, Toxic Spikes, Transform, Trick Room, Whirlwind, Will-O-Wisp, Wish, Withdraw, Worry Seed, Yawn

```
If the user has no other living party members:

No scoring change and terminate

If the user doesn't know the move Baton Pass:

31.25% (81/256) chance of no scoring change and terminate

92% (235/256) chance of score +3 and terminate
```


### Shared by 6 move(s): Acid Armor, Acupressure, Agility, Amnesia, Aromatherapy, Attract

```
If the user has no other living party members:

No scoring change and terminate

If the user doesn't know the move Baton Pass:

31.25% (81/256) chance of no scoring change and terminate

92% (235/256) chance of score +3 and terminate

(If it is the first turn of battle: +8 instead of +3)
```


### Shared by 6 move(s): Aqua Ring, Calm Mind, Dragon Dance, Nasty Plot, Swords Dance, Tail Glow

```
If the user has no other living party members:

No scoring change and terminate

If the user doesn't know the move Baton Pass:

31.25% (81/256) chance of no scoring change and terminate

If it is the first turn of battle:

Score +5 and terminate

If the user's HP is over 59%:

Score +1 and terminate

If the user's HP is under 60%:

Score -10 and terminate
```


### Shared by 2 move(s): Assist, Toxic

```
If the user has no other living party members:

No scoring change and terminate

If the user doesn't know the move Baton Pass:

30.86% (79/256) chance of no scoring change and terminate

If it is the first turn of battle:

92% (235/256) chance of score +8 and terminate

If it is not the first turn of battle:

92.58% (237/256) chance of score +3 and continue

If the user's HP is over 59%:

Score +1 and terminate

If the user's HP is under 60%:

Score -10 and terminate
```


### Shared by 2 move(s): Detect, Protect

```
If the user has no other living party members:

No scoring change and terminate

If the user doesn't know the move Baton Pass:

31.25% (81/256) chance of no scoring change and terminate

If the user's last move was Detect/Protect:

Score -2 and terminate

Else:

Score +2 and terminate
```


### Shared by 1 move(s): Baton Pass

```
If the user has no other living party members:

No scoring change and terminate

If it is the first turn of battle:

Score -2 and terminate

If the user's current attack is boosted to +3 or more:

Score +3 and terminate

If the user's current attack is boosted to +2:

Score +2 and terminate

If the user's current attack is boosted to +1:

Score +1 and terminate

If the user's current special attack is boosted to +3 or more:

Score +3 and terminate

If the user's current aspecial attack is boosted to +2:

Score +2 and terminate

If the user's current special attack is boosted to +1:

Score +1 and terminate
```


### No applicable AI procedure (290 moves)

Absorb, Accelerock, Acid, Aerial Ace, Aeroblast, Air Cutter, Air Slash, AncientPower, Aqua Cutter, Aqua Jet, Aqua Tail, Assurance, Astonish, Attack Order, Aura Sphere, Aurora Beam, Avalanche, Beat Up, Bite, Blast Burn, Blaze Kick, Blizzard, Body Slam, Bone Club, Bone Rush, Bonemerang, Bounce, Brick Break, Brine, Bubble, BubbleBeam, Bug Bite, Bug Buzz, Bulldoze, Bullet Punch, Bullet Seed, Charge Beam, Chatter, Clamp, Confusion, Constrict, Crabhammer, Cross Chop, Cross Poison, Crunch, Crush Claw, Crush Grip, Cut, Dark Pulse, Dig, Discharge, Dive, Dizzy Punch, Doom Desire, Double Hit, Double Kick, Double-Edge, DoubleSlap, Draco Meteor, Dragon Claw, Dragon Pulse, Dragon Rage, Dragon Rush, DragonBreath, Drain Punch, Dream Eater, Drill Peck, Drill Run, DynamicPunch, Earth Power, Earthquake, Egg Bomb, Ember, Energy Ball, Eruption, Extrasensory, ExtremeSpeed, Facade, Faint Attack, Fake Out, False Swipe, Feint, Fire Ball, Fire Blast, Fire Fang, Fire Punch, Fire Spin, Flame Wheel, Flamethrower, Flare Blitz, Flash Cannon, Fly, Focus Blast, Focus Punch, Force Palm, Frenzy Plant, Frustration, Fury Attack, Fury Cutter, Fury Swipes, Future Sight, Giga Drain, Giga Impact, Grass Knot, Gunk Shot, Gust, Gyro Ball, HP Dark, HP Electric, HP Fighting, HP Fire, HP Flying, HP Ghost, HP Grass, HP Ground, HP Ice, HP Psychic, HP Rock, HP Water, Hail Ball, Hammer Arm, Headbutt, Heart Swap, Heat Wave, Hi Jump Kick, Hidden Power, Hurricane, Hydro Cannon, Hydro Pump, Hyper Beam, Hyper Fang, Hyper Voice, Ice Ball, Ice Beam, Ice Fang, Ice Punch, Ice Shard, Icicle Spear, Icy Wind, Iron Head, Iron Tail, Judgment, Jump Kick, Karate Chop, Knock Off, Last Resort, Lava Plume, Leaf Blade, Leaf Storm, Leech Life, Lick, Low Kick, Luster Purge, Mach Punch, Magical Leaf, Magma Storm, Magnet Bomb, Mega Drain, Mega Kick, Mega Punch, Megahorn, Metal Claw, Meteor Mash, Mirror Shot, Mist Ball, Mud Bomb, Mud Shot, Mud-Slap, Muddy Water, Mystical Fire, Natural Gift, Needle Arm, Night Shade, Night Slash, Octazooka, Ominous Wind, Outrage, Overheat, Pay Day, Payback, Peck, Petal Dance, Pin Missile, Pluck, Poison Fang, Poison Jab, Poison Sting, Poison Tail, Pound, Powder Snow, Power Gem, Power Whip, Psybeam, Psychic, Psycho Boost, Psycho Cut, Punishment, Pursuit, Quick Attack, Rage, Razor Leaf, Razor Wind, Return, Revenge, Roar of Time, Rock Ball, Rock Blast, Rock Climb, Rock Slide, Rock Smash, Rock Throw, Rock Tomb, Rock Wrecker, Rolling Kick, Sacred Fire, Sand Tomb, Scald, Scratch, Secret Power, Seed Bomb, Seed Flare, Seismic Toss, Shadow Ball, Shadow Claw, Shadow Force, Shadow Punch, Shadow Sneak, Sheer Cold, Shock Wave, Signal Beam, Silver Wind, Sky Attack, Sky Uppercut, Slam, Slash, Sludge, Sludge Bomb, SmellingSalt, Smog, Snore, Solar-Beam, SonicBoom, Spacial Rend, Steel Wing, Stomp, Stone Edge, Strength, Submission, Sucker Punch, Superpower, Surf, Swallow, Swift, Tackle, Thief, Thrash, Thunder, Thunder Fang, ThunderPunch, ThunderShock, Thunderbolt, Tri Attack, Triple Axel, Triple Kick, Trump Card, Twineedle, Twister, U-turn, Uproar, Vacuum Wave, ViceGrip, Vine Whip, Vital Throw, Volt Tackle, Wake-Up Slap, Water Ball, Water Gun, Water Pulse, Water Spout, Waterfall, Weather Ball, Whirlpool, Wild Charge, Wing Attack, Wood Hammer, Wrap, Wring Out, X-Scissor, Zap Cannon, Zen Headbutt


## setup_first_turn

- 1 distinct scoring blocks (+ 375 moves with no applicable procedure) out of 466 moves


### Shared by 91 move(s): Acid Armor, Acupressure, Agility, Amnesia, Attract, Barrier, Belly Drum, Bulk Up, Calm Mind, Camouflage, Captivate, Charge, Charm, Clamp, Confuse Ray, Cosmic Power, Cotton Spore, Crush Grip, Dark Void, Defend Order, Defog, Double Team, Dragon Dance, Embargo, Fake Tears, FeatherDance, Fire Spin, Flash, Flatter, Glare, GrassWhistle, Growl, Growth, Harden, Howl, Hypnosis, Imprison, Ingrain, Iron Defense, Kinesis, Leech Seed, Leer, Light Screen, Lovely Kiss, Lucky Chant, Magma Storm, Magnet Rise, Meditate, Metal Sound, Minimize, Nasty Plot, Poison Gas, PoisonPowder, Reflect, Rock Polish, Sand Tomb, Sand-Attack, Scary Face, Screech, Seed Flare, Sharpen, Sing, Sleep Powder, SmokeScreen, Spore, Stockpile, String Shot, Stun Spore, Submission, Substitute, Supersonic, Swallow, Sweet Kiss, Sweet Scent, Swords Dance, Tail Glow, Tail Whip, Tailwind, Teeter Dance, Thunder Wave, Tickle, Torment, Toxic, Twister, ViceGrip, Whirlpool, Will-O-Wisp, Withdraw, Worry Seed, Wrap, Yawn

```
If it is the first turn of battle:

68.75% (176/256) chance of score +2 and terminate
```


### No applicable AI procedure (375 moves)

Absorb, Accelerock, Acid, Aerial Ace, Aeroblast, Air Cutter, Air Slash, AncientPower, Aqua Cutter, Aqua Jet, Aqua Ring, Aqua Tail, Aromatherapy, Assist, Assurance, Astonish, Attack Order, Aura Sphere, Aurora Beam, Avalanche, Baton Pass, Beat Up, Bide, Bite, Blast Burn, Blaze Kick, Blizzard, Block, Body Slam, Bone Club, Bone Rush, Bonemerang, Bounce, Brave Bird, Brick Break, Brine, Bubble, BubbleBeam, Bug Bite, Bug Buzz, Bulldoze, Bullet Punch, Bullet Seed, Charge Beam, Chatter, Close Combat, Confusion, Constrict, Conversion 2, Copycat, Counter, Crabhammer, Cross Chop, Cross Poison, Crunch, Crush Claw, Curse, Cut, Dark Pulse, Destiny Bond, Detect, Dig, Disable, Discharge, Dive, Dizzy Punch, Doom Desire, Double Hit, Double Kick, Double-Edge, DoubleSlap, Draco Meteor, Dragon Claw, Dragon Pulse, Dragon Rage, Dragon Rush, DragonBreath, Drain Punch, Dream Eater, Drill Peck, Drill Run, DynamicPunch, Earth Power, Earthquake, Egg Bomb, Ember, Encore, Endeavor, Endure, Energy Ball, Eruption, Explosion, Extrasensory, ExtremeSpeed, Facade, Faint Attack, Fake Out, False Swipe, Feint, Fire Ball, Fire Blast, Fire Fang, Fire Punch, Fissure, Flail, Flame Wheel, Flamethrower, Flare Blitz, Flash Cannon, Fling, Fly, Focus Blast, Focus Energy, Focus Punch, Follow Me, Force Palm, Foresight, Frenzy Plant, Frustration, Fury Attack, Fury Cutter, Fury Swipes, Future Sight, Gastro Acid, Giga Drain, Giga Impact, Grass Knot, Gravity, Grudge, Guard Swap, Guillotine, Gunk Shot, Gust, Gyro Ball, HP Dark, HP Electric, HP Fighting, HP Fire, HP Flying, HP Ghost, HP Grass, HP Ground, HP Ice, HP Psychic, HP Rock, HP Water, Hail, Hail Ball, Hammer Arm, Haze, Head Smash, Headbutt, Heal Bell, Heal Order, Heart Swap, Heat Wave, Helping Hand, Hi Jump Kick, Hidden Power, Horn Drill, Hurricane, Hydro Cannon, Hydro Pump, Hyper Beam, Hyper Fang, Hyper Voice, Ice Ball, Ice Beam, Ice Fang, Ice Punch, Ice Shard, Icicle Spear, Icy Wind, Iron Head, Iron Tail, Judgment, Jump Kick, Karate Chop, Knock Off, Last Resort, Lava Plume, Leaf Blade, Leaf Storm, Leech Life, Lick, Lock-On, Low Kick, Lunar Dance, Luster Purge, Mach Punch, Magic Coat, Magical Leaf, Magnet Bomb, Me First, Mean Look, Mega Drain, Mega Kick, Mega Punch, Megahorn, Memento, Metal Burst, Metal Claw, Meteor Mash, Metronome, Milk Drink, Mimic, Mind Reader, Miracle Eye, Mirror Coat, Mirror Move, Mirror Shot, Mist, Mist Ball, Moonlight, Morning Sun, Mud Bomb, Mud Shot, Mud-Slap, Muddy Water, Mystical Fire, Natural Gift, Nature Power, Needle Arm, Night Shade, Night Slash, Octazooka, Odor Sleuth, Ominous Wind, Outrage, Overheat, Pain Split, Pay Day, Payback, Peck, Perish Song, Petal Dance, Pin Missile, Pluck, Poison Fang, Poison Jab, Poison Sting, Poison Tail, Pound, Powder Snow, Power Gem, Power Swap, Power Trick, Power Whip, Present, Protect, Psybeam, Psych Up, Psychic, Psycho Boost, Psycho Cut, Psycho Shift, Punishment, Pursuit, Quick Attack, Rage, Rain Dance, Razor Leaf, Razor Wind, Recover, Recycle, Refresh, Rest, Return, Revenge, Reversal, Roar, Roar of Time, Rock Ball, Rock Blast, Rock Climb, Rock Slide, Rock Smash, Rock Throw, Rock Tomb, Rock Wrecker, Role Play, Rolling Kick, Roost, Sacred Fire, Safeguard, Sandstorm, Scald, Scratch, Secret Power, Seed Bomb, Seismic Toss, Selfdestruct, Shadow Ball, Shadow Claw, Shadow Force, Shadow Punch, Shadow Sneak, Sheer Cold, Shock Wave, Signal Beam, Silver Wind, Sketch, Skill Swap, Sky Attack, Sky Uppercut, Slack Off, Slam, Slash, Sleep Talk, Sludge, Sludge Bomb, SmellingSalt, Smog, Snore, Softboiled, Solar-Beam, SolarBeam, SonicBoom, Spacial Rend, Spider Web, Spikes, Spite, Stealth Rock, Steel Wing, Stomp, Stone Edge, Strength, Sucker Punch, Sunny Day, Super Fang, Superpower, Surf, Swagger, Swift, Synthesis, Tackle, Take Down, Teleport, Thief, Thrash, Thunder, Thunder Fang, ThunderPunch, ThunderShock, Thunderbolt, Toxic Spikes, Transform, Tri Attack, Trick Room, Triple Axel, Triple Kick, Trump Card, Twineedle, U-turn, Uproar, Vacuum Wave, Vine Whip, Vital Throw, Volt Tackle, Wake-Up Slap, Water Ball, Water Gun, Water Pulse, Water Spout, Waterfall, Weather Ball, Whirlwind, Wild Charge, Wing Attack, Wish, Wood Hammer, Wring Out, X-Scissor, Zap Cannon, Zen Headbutt
