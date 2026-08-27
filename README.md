*This project has been created as part of the 42 curriculum by \<jsmidt\>, \<dijonker\>.*

# Pacman

## Description

CODAM / 42's Pacman project: Recreate the famous arcade game Pac-man!  
This is our version of the Arcade classic. Including 4 ghosts similiar to the original, 10 challenging hand picked maps and a highscore system to compete with your peers.

## Instructions

### Requirements

- Python ≥ 3.10, < 3.14
- `uv` package manager
- The following files provided by the school:
  - mazegenerator-00001-py3-none-any.whl

### Installation

```bash
make install
```

### Expected data layout

```
data/
├── mazegenerator-00001-py3-none-any.whl    # 42's maze generator package
├── highscores/highscores.json
├── font/
│   └── Pixeltype.ttf
├── settings/
│   └── default_settings.json
└── assets/
    ├── ghost.png
    ├── instructions.png
    ├── pacgum.png
    ├── s_pacgum.png
    ├── pacman_animation.png
    ├── pacdeath.png
    ├── pacman_play.png
    └── pactiles.png
```

### Running the game

```bash
make run
```

### Configuration information

The configuration file takes several keys which can be customized in advance, if the configuration file is missing or there are missing keys, the system reverts to default_settings. U can change the settings.json files to your liking. It is also possible to change many of these values in the game's internal settings.

#### Keys

- highscore_filename  
Changes the highscore filesname
- width / height  
Changes the maze's size to your liking.
- lives  
Changes the amount of lives the player starts with
- points_per_pacgum, points_per_super_pacgum, points_per_ghost  
Changes the amount of points that each pick-up will give you

### Highscoring

At the end of a game a player is prompted to provide a name for their score to be saved to the highscore system. The name is automatically limited to ten characters and the inclusion of a '#' will override a name with the text 'StopTrying'. 
The player's score is converted to a dictionary element with their name as the key and their score as the value. Only the ten entries with the highest score are saved to the file and they are sorted in descending order. If a cheat is enabled then a score will not be saved. 

### Maze generation
We initialise the Maze generation with default values only with a different seed for each level.
The maze is extracted as a List[List[int]] and used throughout the program as the unmodified base layer.


## Implementation / Design Decisions  

### Engine  
Engine is the main class managing the gameplay loop, manages all the game related classes and responsible for everything beyond the main menu. It's responsible for handling scores, lives, timers player input and the ghosts moving.

### Pacman   
Pacman is moved on a grid by the player, the possibility of the movement is constantly calculated. Whenever the player hits a wall, movement will stop. When the player wants to switch directions, their required input is stored until the possibility to turn comes along. This makes gameplay smooth and close to the original.

#### Movement
The movement system has seen many reworks, as I decided half way it'd be better to switch to tile based movement, with a positional mask to simulate free movement. This was a big waste of time as later on I switched it back to the movement we have now. 

Movement is possible through bitwise operations. The map is stored in 0-15 valued integers, which will decide when movement is possible for the requested player direction.


#### Rendering
The rendering of the animation is done using an animation counter in our timers class. This will keep track of what frame on our spritesheet to use. 

### Ghost  
All ghost pathfinding uses a personal board called scores. Ghost direction is only calculated at startup, intersections and dead ends meaning that they cannot suddenly turn around.
Ghosts move by a tile-by-tile basis meaning that a new direction is only calculated and set when the top left corner of the sprite aligns with the underlying tile grid.

**Chasing:**  

**Part 1:**  
Set the target. Each ghost has a modification to which point around pacman they target based on the direction pacman is moving. The function used to calculate the route tracks corridors and at intersections have a bias of Up, Right, Down and Left. 
Red - Directly targets Pacman with no modifications.
Blue - Targets two tiles ahead of the direction Pacman is moving.
Pink - Targets two tiles in the opposite direction Pacman is moving.
Orange - Targets two tiles ahead of Pacman.
Note:
Pink and Blue will target Pacman if they are within two tiles distance.

**part 2:**  
Scores is calculated using A* to the set target which was modified based on their colour. The A* calculations use a heuristic of absolute distance. All calculations obey the walls set by the base maze. The ghost will move to an adjacent cell with the lowest value while obeying walls.

**Scatter:**  
Each ten seconds for one second the ghost will pathfind to their original starting position. This is to prevent ghosts from clustering and to give the player more leeway.

**Fleeing:**  
When Pacman has eaten a Supergum ghost will start fleeing for [Lookup how long] seconds. The scores map is calculated using a BFS algorithm with Pacman as the centre. Ghosts will move towards adjacent cells with higher values while obeying the walls. When 1.5 seconds remain for ghosts fleeing they will start to flicker to indicate a changing state.

### JSON_Work:  
Modified JSON load and dump to have the ability to save python-style comments in JSON documents.
This works both inline as well as on seperate lines.

### Settings:  
Stores the specifications of the gameplay, loads settings and saves them. Through the settings menu it's possible to change the maze's size and enable the cheats.

### Constants:  
A class holding all the constants which are widely used

### Button (TextButton, ImageButton, ToggleButton):  
The class which encompasses the functionality all buttons are based on. Textbutton displays text with a font. ImageButton loads a image that is clickable. ToggleButton is a boolean button which can switch between two colours.

### Constants:  
Keeps track of the amount of points a player gets throughout gameplay

## Challenges Faced  

1. __Ghost__  
Ghost movement system was initially based of player movement but it caused issues of severe clipping and passing through walls. Ghost movement was changed so that the direction of movement can only be changed when the top left of the player matches the underlying tile grid. Direction is beforehand validated for its validity and each tick the ghostis moved a set amount of pixels. This system does limit movement speed to adding up to tile size but created no issues.  
A later issue found when introducing the a slower movement speed to ghost which caused them to pass through walls. the issue was that the speed changes before the ghost is allowed to choose a new direction making it highly improbable that the ghosts topleft aligns with the grid. 
Another issue faced was swapping the x and y axis in a important if statement which took a long while to find  

2. __Pygame events__  
Due to unclear understanding of the event system of pygame multiple issues were raised when extracting keyboard and other such input. This was solved by changing the method of recieving keyboard input into checking for a ButtonDown event and then a match case statement for each key including a overflow. All user input is extracted in the same for loop at the same location in loops.  

3. __Player movement__  
During development, I've made too many changes to the nature of movement for the player (Pac-Man), this ended up costing me a lot of time. I started on free, axis based movement. After trying multiple days and misisng a small issue, I decided I'd refactor and change to tile-based movement, where the actual player only changes position every x ticks, which ended up complicating everything much further. 

## Resources

**Libraries:**  
[ Pixeltype font ](https://www.dafont.com/pixeltype.font)  
[ Pygame ](https://www.pygame.org/docs/)   
[ CXFreeze ](https://cx-freeze.readthedocs.io/en/stable/)  

**Other**  
[ Piskel ](https://www.piskelapp.com/p/create/sprite/)

**AI usage:**  
No AI was used or harmed during the production of this ~~film~~ program

## Module Overview

```
src/
├── __main__.py           # Main menu, settings menu, highscores
├── buttons.py            # Our own button classes
├── engine.py             # gameplay loop, rendering
├── ghost.py              # Ghosts, ghostmanager, pathfinding
├── gums.py               # Gums, Supergums, tile visiting
├── highscores.py         # JSON highscoring
├── json_work.py          # JSON modifications, commenting
├── levels.py             # Level / seed handler
├── player.py             # Rendering player / player inputs
├── score.py              # Scoring / points system
├── settings.py           # Settings parser / default settings
└── timers.py             # Keeps track of timings
```

### General Software Architecture

```
                     Constants      Button
                         ╽             ├─╼ ImageButton
  Engine ╾─────────── Settings         ├─╼ TextButton
    │                    ╽             └─╼ ToggleButton
    ├─╼ Highscores ─╼ JSONWork
    ├─╼ Levels  ╿        │
    ├─╼ Timers  │        │
    ├─╼ ScoringSystem    └────────╼ PacmanError
    ├─╼ Pacman                          ├─╼ NonExistingPath
    └─╼ GhostManager                    ├─╼ InvalidJSON
             ╽                          └─╼ InvalidJSONValues
           Ghost
```

## Project Management

The project was divided up into sections and work was divided by preference, work balance and time management. Basic functionality such as Constants, Settings, Maze, Variables and data structure was agreed upon beforehand, but each coder could choose in which way they implemented their functionality while keeping the larger project in mind. Both members of the team checked one anothers code.

### High level division of work
**jsmidt**
- Engine
- Player
- Timers
- Levels
- Scoring  
- Art
- Documentation

**dijonker**
- Main menu
- Buttons
- Settings
- Highscores
- GhostManager
- Ghost
- Art
- Documentation
