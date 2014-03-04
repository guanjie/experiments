# Game.py

import cmd
from room import get_room


class Game(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.loc = get_room(1)

    def move(self, dir):
        newroom = self.loc._neighbors(dir)
        if newroom is None:
            print ("you can't go that way")
        else:
            self.loc = get_room(newroom)

    def look(self):
        print(self.loc.name)
        print("")

    def do_n(self, arg):
        """Go north"""
        self.move("n")
        pass

    def do_e(self, arg):
        """Go east"""
        self.move("e")
        pass

    def do_w(self, arg):
        """Go west"""
        self.move("w")
        pass

    def do_s(self, arg):
        """Go south"""
        self.move("s")
        pass

    def do_quit(self, args):
        """Leaves the game"""
        print("Thank you for playing")
        return True

if __name__ == "__main__":
    g = Game()
    g.cmdloop()
