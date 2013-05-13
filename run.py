#!/usr/bin/python
from world import WumpusWorld
from agent import Agent
from display import Display
import os
from argparse import ArgumentParser

p = ArgumentParser(description="Wumpus World AI simulation")
p.add_argument('-w','--world',default="worlds/wumpus_world.txt",help="world file relative path (default: worlds/wumpus_world.txt)")
p.add_argument('-t','--time',default=0,help="jump to a certain time")
p.add_argument('-v','--verbose',action="store_true",default=False,help="display intermediate decision making")
args = p.parse_args()

world = WumpusWorld(args.world)
display = Display(world, int(args.time), args.verbose)
agent = Agent(world)

with display:
    print "!Starting Wumpus world simulation..."
    while world.has_agent():
        agent.make_move()
