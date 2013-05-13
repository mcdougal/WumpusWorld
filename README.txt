==================================
WUMPUS WORLD AI SIMULATION
==================================
by: Cedric McDougal

>> World File Input
- looks for "wumpus_world.txt" in the "worlds" directory
- you can pass in a different file using the -w flag (relative path)

>> Prover9 Integration
- uses the included compiled version of Prover9
- version used is LADR-2009-11A

>> How to run
1. make sure you have a wumpus world file (see "World File Input")
1. cd into the directory containing the file "run.py"
2. type "python run.py"
3. press Enter

>> Options
-w WORLD, --world WORLD
                      world file relative path (default:
                      worlds/wumpus_world.txt)
-t TIME, --time TIME  jump to a certain time
-v, --verbose         display intermediate decision making

>> System Requirements
- Python 2.7
- Preferably run on a Linux system because that's what it was developed and tested on
