# Exercise 1 - documentation

## Overview

This program implements a greedy algorithm to defeat a dragon by optimally choosing which enemy types to defeat. If you defeat the dragon, program prints chosen enemy and how many steps and time it took.

#
## Requirements

### Python Version
- Minimum Python 3.6

#
## Input data format

You have to provide input file in the following format:

```
<dragon_hp>
<enemy_name1>,<time1>,<strength_gained1>,<steps1>
<enemy_name2>,<time2>,<strength_gained2>,<steps2>
<enemy_name3>,<time3>,<strength_gained3>,<steps3>
...
```
### Field Descriptions

**dragon_hp** - Strength of the dragon.

**enemy_name** - Name of path, enemies you choose to fight with.

**time** - Time needed to defeat one enemy you meet on the path.

**strength_gained** - Strength you gain after defeating one enemy.

**steps** - Number of enemies on the path.

### Example Input File
```
15
wizard,30,10,15
knight,60,15,10
bandit,10,5,30
```

#
## Running the Program
```bash
python ex1.py
```

You will be asked for a path to the input file in the format described above.
