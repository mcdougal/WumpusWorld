from collections import defaultdict
from prover import Prover

class Agent(object):
    def __init__(self, world):
        self.world = world
        self.prover = Prover()
        self.wumpus = None
        self.pits = set()
        self.safe = {self.position}
        self.unsafe = defaultdict(set)
        self.visited = [self.position]

    @property
    def position(self):
        return self.world.agent

    def inspect_position(self):
        if self.world.agent_on_stench():
            self.found_stench()
        else:
            self.no_stench()

        if self.world.agent_on_breeze():
            self.found_breeze()
        else:
            self.no_breeze()

        if self.world.agent_on_gold():
            self.found_gold()

        self.search_for_wumpus()
        self.search_for_pit()

    def search_for_wumpus(self):
        adjacent_hidden_cells = self.get_adjacent_hidden_cells()
        if self.wumpus is not None or not adjacent_hidden_cells:
            return
        print "Agent is searching for Wumpus"
        for cell in adjacent_hidden_cells:
            if self.prover.check_wumpus(*cell):
                print "!Agent deduced Wumpus at", cell
                self.wumpus = cell
                self.prover.add_wumpus(*cell)
                return
        print "Agent did not find Wumpus"

    def found_stench(self):
        print "!Agent found a stench"
        self.prover.add_stench(*self.position)

    def no_stench(self):
        self.prover.add_no_stench(*self.position)

    def search_for_pit(self):
        adjacent_hidden_cells = self.get_adjacent_hidden_cells()
        if not adjacent_hidden_cells:
            return
        print "Agent is searching for pit"
        for cell in adjacent_hidden_cells:
            if self.prover.check_pit(*cell):
                print "!Agent deduced pit at", cell
                self.pits.add(cell)
                self.prover.add_pit(*cell)
                return
        print "Agent did not find pit"

    def found_breeze(self):
        print "!Agent found a breeze"
        self.prover.add_breeze(*self.position)

    def no_breeze(self):
        self.prover.add_no_breeze(*self.position)

    def found_gold(self):
        print "!Agent found gold!"
        print "Agent is picking up gold"
        self.world.pickup_gold()
        if self.found_all_gold():
            print "!Agent found all the gold! Hooray!"
            self.leave_world()

    def found_all_gold(self):
        return self.world.num_gold == 0

    def make_move(self):
        self.inspect_position()

        print "Agent is checking adjacent hidden cells"
        cell = self.get_adjacent_safe_hidden_cell()
        if cell is not None:
            print "Agent found safe hidden cell", cell
            return self.travel_to(cell)
        print "Agent could not find safe hidden cell"

        print "Agent is re-checking visited cells"
        for cell in reversed(self.visited[:-1]):
            print "Agent is checking", cell
            cell2 = self.get_adjacent_safe_hidden_cell(cell)
            if cell2 is not None:
                print "Agent found safe hidden cell", cell2
                return self.travel_to(cell2)

        print "!Agent can't find a move!"
        self.leave_world()

    def leave_world(self):
        print "Agent is heading to goal"
        self.travel_to(self.world.goal)
        if self.position != self.world.goal:
            print "!Agent cannot find his way to goal!"
            print "!Agent is giving up, doomed to forever wander aimlessly through the destitute labyrinth of the Wumpus world. If only his logic had been better! If only his creator had added more rules!"
            quit()
        print "!Agent is exiting the Wumpus world"
        self.world.exit()

    def travel_to(self, cell):
        if cell not in self.get_adjacent_cells():
            print "Agent is traveling to cell", cell
            path = self.get_path_to_cell(cell)
            print "Agent found safe path to cell", cell, "->", path
        else:
            path = [cell]
        if path:
            for cell in path:
                self.world.move_agent(cell)
                print "!Agent moved to cell", cell
                self.visited.append(cell)

    def is_safe(self, cell):
        print "Checking safety of", cell
        if cell in self.safe:
            print cell, "was already determined to be safe"
            return True
        if cell in self.unsafe[self.world.time]:
            print cell, "was already determined to be unsafe at time", self.world.time
            return False

        if cell == self.wumpus:
            safe = False
        elif cell in self.pits:
            safe = False
        else:
            safe = self.prover.check_safe(*cell)

        if safe:
            print cell, "is safe"
            self.safe.add(cell)
        else:
            print cell, "is not safe at time", self.world.time
            self.unsafe[self.world.time].add(cell)

        return safe

    def is_hidden(self, cell):
        return cell not in self.world.visible_cells

    def is_visible(self, cell):
        return not self.is_hidden(cell)

    def get_adjacent_safe_hidden_cell(self, start=None):
        for cell in self.get_adjacent_hidden_cells(start):
            if self.is_safe(cell):
                return cell

    def get_adjacent_hidden_cells(self, cell=None):
        return set(filter(self.is_hidden, self.get_adjacent_cells(cell)))

    def get_adjacent_visible_cells(self, cell=None):
        return set(filter(self.is_visible, self.get_adjacent_cells(cell)))

    def get_adjacent_cells(self, cell=None):
        if cell is None:
            cell = self.position
        x, y = cell
        adjacent_cells = [
            (x-1, y),
            (x+1, y),
            (x, y-1),
            (x, y+1), ]

        return set(filter(self.world.in_bounds, adjacent_cells))

    def get_path_to_cell(self, dest):
        print "Agent is searching for safe path to cell", dest
        checked_cells = set()
        path_cells = {self.position}
        paths = []

        if self.is_visible(dest):
            dest_check = self.get_adjacent_visible_cells
        else:
            dest_check = self.get_adjacent_hidden_cells

        for cell in dest_check():
            if cell == dest:
                return [cell]

        checked_cells.add(self.position)

        for cell in self.get_adjacent_visible_cells():
            path = [cell]
            paths.append(path)
            path_cells.add(cell)

        while len(checked_cells) < len(self.world.visible_cells):
            new_paths = []
            for path in paths:
                last_cell = path[-1]

                for cell in dest_check(last_cell):
                    if cell == dest:
                        return path + [cell]

                checked_cells.add(last_cell)

                cells = self.get_adjacent_visible_cells(last_cell)
                cells = cells - path_cells
                for cell in cells:
                    new_path = path + [cell]
                    new_paths.append(new_path)
                    path_cells.add(cell)

            paths = new_paths
