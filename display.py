import os
import re
import sys

LOG_LINES_MAX = 20
REMOVE_COLOR_OPEN = re.compile("\\033\[1;\d+m")
REMOVE_COLOR_CLOSE = re.compile("\\033\[0m")

class Display(object):
    def __init__(self, world, jump_to_time, verbose):
        self.world = world
        self.jump_to_time = jump_to_time
        self.verbose = verbose
        self.current_line = None
        self.lines = []
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self

    def write(self, data):
        if self.current_line is None:
            self.current_line = data
        else:
            self.current_line += data

        if data.endswith("\n"):
            if self.verbose or self.current_line.startswith("!"):
                self.current_line = self.current_line.strip("!")
                self.lines.append(self.current_line)
                self.display()
            self.current_line = None

    def __exit__(self, type, value, traceback):
        sys.stdout = self.stdout

    def remove_color(self, txt):
        txt = REMOVE_COLOR_OPEN.sub("",txt)
        txt = REMOVE_COLOR_CLOSE.sub("",txt)
        return txt

    def display(self):
        stdout = sys.stdout
        sys.stdout = self.stdout

        os.system("clear")
        world_lines = self.world.draw()
        if not hasattr(self, "world_line_width"):
            self.world_line_width = len(self.remove_color(world_lines[0])) - 1
        if not hasattr(self, "log_lines_limit"):
            world_height = (self.world.size[1]*4)-6
            self.log_lines_limit = min(world_height, LOG_LINES_MAX)

        msg_lines = [
            "\n",
            "time: %s\n" % self.world.time,
            "score: %s\n" % self.world.score,
            "\n",
            "-"*40+"\n", ]

        if len(self.lines) > self.log_lines_limit:
            log_lines = self.lines[-self.log_lines_limit:]
        else:
            log_lines = self.lines

        msg_lines += log_lines
        msg_lines.append("\n")
        msg_lines.append("> Press any key to continue, or q to exit\n")

        len_diff = len(world_lines) - len(msg_lines)
        if len_diff > 0:
            for i in range(len_diff-1):
                msg_lines.append("\n")
            msg_lines.append("")
        elif len_diff < 0:
            for i in range(-len_diff):
                world_lines.append(" "*self.world_line_width+"\n")

        for world_line, msg_line in zip(world_lines, msg_lines):
            sys.stdout.write(world_line.strip("\n"))
            sys.stdout.write(" "*10)
            sys.stdout.write(msg_line)

        if self.world.time >= self.jump_to_time:
            from getch import getch
            ch = getch()
            if ch == "q":
                quit()

        sys.stdout = stdout
