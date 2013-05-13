import re
import sys

class WumpusWorld(object):
    def __init__(self, worldfilepath):
        with open(worldfilepath) as worldfile:
            worldstr = worldfile.read()

        # inner function to force it to be private
        def parse(symbol):
            return set(map(
                lambda line: (int(line[-2]), int(line[-1])), # x,y
                re.findall(r"%s[0-9]+" % symbol, worldstr)))

        self.agent = parse("A").pop()
        self.goal = parse("GO").pop()
        self.size = parse("M").pop()
        self.wumpus = parse("W").pop()
        self.stenches = parse("S")
        self.pits = parse("P")
        self.breezes = parse("B")
        self.gold = parse("G")
        self.visible_cells = {self.agent}
        self.num_cells = self.size[0] * self.size[1]
        self.time = 0
        self.score = 0

    @property
    def num_gold(self):
        return len(self.gold)

    def has_agent(self):
        return self.agent is not None

    def move_agent(self, cell):
        self.agent = cell
        self.visible_cells.add(cell)
        self.time += 1
        self.score -= 1

        msg = None
        if self.agent_on_wumpus():
            msg = "You bumped into the Wumpus!"
        elif self.agent_on_pit():
            msg = "You fell into a pit!"
        if msg:
            print "!Uh oh! %s GAME OVER!" % msg
            self.agent = None
            quit()

    def pickup_gold(self):
        if self.agent_on_gold():
            self.score += 1000
            self.gold.remove(self.agent)

    def exit(self):
        if self.agent_on_goal():
            self.agent = None
            print "!Game completed!"
            quit()

    def agent_on_wumpus(self):
        return self.agent == self.wumpus

    def agent_on_stench(self):
        return self.agent in self.stenches

    def agent_on_pit(self):
        return self.agent in self.pits

    def agent_on_breeze(self):
        return self.agent in self.breezes

    def agent_on_gold(self):
        return self.agent in self.gold

    def agent_on_goal(self):
        return self.agent == self.goal

    def in_bounds(self, cell):
        x,y = cell
        right,top = self.size
        return x > 0 and y > 0 and x <= right and y <= top

    #################################
    #
    #  DRAWING
    #
    #################################

    WUMPUS = "\033[1;41mW\033[0m"
    STENCH = "\033[1;31mS\033[0m"
    PIT = "\033[1;44mP\033[0m"
    BREEZE = "\033[1;34mB\033[0m"
    AGENT = "\033[1;37mA\033[0m"
    GOLD = "\033[1;43mG\033[0m"
    VDIV_WIDTH = 2
    BODY_WIDTH = 5
    AGENT_VDIV = "\033[1;43m \033[0m" * VDIV_WIDTH
    AGENT_HDIV = "\033[1;43m \033[0m"
    GOAL_VDIV = "\033[1;42m \033[0m" * VDIV_WIDTH
    GOAL_HDIV = "\033[1;42m \033[0m"
    VISIBLE_VDIV = "\033[1;47m \033[0m" * VDIV_WIDTH
    VISIBLE_HDIV = "\033[1;47m \033[0m"
    VISIBLE_SPACE = "\033[1;0m \033[0m"
    HIDDEN_VDIV = "\033[1;46m \033[0m" * VDIV_WIDTH
    HIDDEN_HDIV = "\033[1;46m \033[0m"
    HIDDEN_SPACE = "\033[1;40m \033[0m"

    def draw(self):
        self.current_line = None
        self.lines = []
        for y in range(self.size[1], 0, -1):
            self.draw_hdiv(y)
            self.draw_line("\n")
            for row in range(3):
                self.draw_cells(y, row)
                self.draw_line("\n")

        self.draw_hdiv(0)
        self.draw_line("\n")
        return self.lines

    def draw_line(self, line):
        if self.current_line is None:
            self.current_line = line
        else:
            self.current_line += line

        if line.endswith("\n"):
            self.lines.append(self.current_line)
            self.current_line = None

    def draw_hdiv(self, y):
        self.draw_hdiv_piece({(1,y),(1,y+1)}, self.VDIV_WIDTH)
        for x in range(1, self.size[0]+1):
            self.draw_hdiv_piece({(x,y), (x,y+1)}, self.BODY_WIDTH)
            self.draw_hdiv_piece(
                {(x,y),(x,y+1),(x+1,y),(x+1,y+1)}, self.VDIV_WIDTH)

    def draw_hdiv_piece(self, adjacent_cells, mult=1):
        if adjacent_cells.intersection({self.agent}):
            self.draw_line(self.AGENT_HDIV*mult)
        elif adjacent_cells.intersection({self.goal}):
            self.draw_line(self.GOAL_HDIV*mult)
        elif adjacent_cells.intersection(self.visible_cells):
            self.draw_line(self.VISIBLE_HDIV*mult)
        else:
            self.draw_line(self.HIDDEN_HDIV*mult)

    def draw_vdiv(self, x, y):
        if {(x,y), (x+1,y)}.intersection({self.agent}):
            self.draw_line(self.AGENT_VDIV)
        elif {(x,y), (x+1,y)}.intersection({self.goal}):
            self.draw_line(self.GOAL_VDIV)
        elif {(x,y), (x+1,y)}.intersection(self.visible_cells):
            self.draw_line(self.VISIBLE_VDIV)
        else:
            self.draw_line(self.HIDDEN_VDIV)

    def draw_cells(self, y, row):
        self.draw_vdiv(0, y)
        for x in range(1, self.size[0]+1):
            if (x,y) not in self.visible_cells:
                self.draw_line(self.HIDDEN_SPACE*self.BODY_WIDTH)
            else:
                self.draw_cell(x, y, row)
            self.draw_vdiv(x, y)

    def draw_cell(self, x, y, row):
        if row == 0:
            self.draw_line(self.VISIBLE_SPACE)
            self.draw_wumpus_space(x, y)
            self.draw_line(self.VISIBLE_SPACE)
            self.draw_pit_space(x, y)
            self.draw_line(self.VISIBLE_SPACE)
        elif row == 2:
            self.draw_line(self.VISIBLE_SPACE)
            self.draw_agent_space(x, y)
            self.draw_line(self.VISIBLE_SPACE)
            self.draw_gold_space(x, y)
            self.draw_line(self.VISIBLE_SPACE)
        else:
            self.draw_line(self.VISIBLE_SPACE*self.BODY_WIDTH)

    def draw_wumpus_space(self, x, y):
        if (x,y) == self.wumpus:
            self.draw_line(self.WUMPUS)
        elif (x,y) in self.stenches:
            self.draw_line(self.STENCH)
        else:
            self.draw_line(self.VISIBLE_SPACE)

    def draw_pit_space(self, x, y):
        if (x,y) in self.pits:
            self.draw_line(self.PIT)
        elif (x,y) in self.breezes:
            self.draw_line(self.BREEZE)
        else:
            self.draw_line(self.VISIBLE_SPACE)

    def draw_agent_space(self, x, y):
        if (x,y) == self.agent:
            self.draw_line(self.AGENT)
        else:
            self.draw_line(self.VISIBLE_SPACE)

    def draw_gold_space(self, x, y):
        if (x,y) in self.gold:
            self.draw_line(self.GOLD)
        else:
            self.draw_line(self.VISIBLE_SPACE)

