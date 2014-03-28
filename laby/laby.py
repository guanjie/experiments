# -*- coding:iso-8859-1 -*-
#
# Jan Thor 12. - 21.9.2005
# 
#

import copy
import math
import optparse
import random
import string
import sys
try:
    import wx
    if not wx.GetApp(): myApp = wx.App(0)
except ImportError:
    pass # paint and flatten will not work without wxPython
try:
    import psyco
    psyco.full()
except ImportError:
    pass # things will be slower without psyco, but will keep working

FLAT = 1
RING = 2
TORUS = 3

_doubs = [[6, 12, 3, 9], [5, 5, 3, 9], [6, 10, 3, 10], [5, 3, 3, 10],
          [6, 12, 5, 5], [5, 5, 5, 5], [6, 10, 5, 6], [5, 3, 5, 6],
          [10, 12, 10, 9], [9, 5, 10, 9], 
          [10, 10, 10, 10,], [9, 3, 10, 10], 
          [10, 12, 12, 5], [9, 5, 12, 5], [10, 10, 12, 6], [9, 3, 12, 6]]


class InvalidParameters(Exception):
    u"""Needed for invalid Parameters in random etc."""


class Labyrinth(object):
    u"""A labyrinth is an n * m-array of numbers from 0 to 15.
        
        Assume that 0 means "wall" and 1 means "door". N describes
        whether there is a door on the north side of an atomic tile, 
        E describes the presence of a door in the east, S in the south,
        W in the west. The number describing a single cell is
        
            1 * N  +  2 * E  +  4 * S  +  8 * W
        
        The following example
        
            6	8	4	4	6  12	6	8	
            7  14  15  11  13	7  11  12	
            1	5	3  12	5	3  12	1	
            2  11	8	1	3	8	3	8	
            
        was constructed using random(8, 4) and corresponds to this 
        labyrinth:
        
            +---+-+-+---+---+       +---+-+-+---+---+
            |   | | |   |   |       |6 8|4|4|6 C|6 8|
            | --+ | | | | --+       | --+ | | | | --+
            |         |     |       |7 E F B D|7 B C|
            | | | --+ | --+ |       | | | --+ | --+ |
            | | |   | |   | |       |1|5|3 C|5|3 C|1|
            +-+ +-+ | +-+ +-+       +-+ +-+ | +-+ +-+
            |     | |   |   |       |2 B 8|1|3 8|3 8|
            +-----+-+---+---+       +-----+-+---+---+
                            
        More elaborately:
        
            #####    #   #    #####    #   #
            #   #    #   #    #        #    
            #   #    #   #    #        #    
            #####    #####    #####    #####
              0        1        2        3
            
            #####    #   #    #####    #   #
            #   #    #   #    #        #    
            #   #    #   #    #        #    
            #   #    #   #    #   #    #   #
              4        5        6        7
            
            #####    #   #    #####    #   #
                #        #                  
                #        #                  
            #####    #####    #####    #####
              8        9        A        B
            
            #####    #   #    #####    #   #
                #        #                  
                #        #                  
            #   #    #   #    #   #    #   #
              C        D        E        F                        """
              
    def __init__(self, data = [[]]):
        u"""Create a new labyrinth.
        
            As default, an empty labyrinth is created. It is possible
            to specify the labyrinth as a list of lists of integers.
            One list within this list of lists corresponds to one row
            of cells of the labyrinth."""
        self._data = data

    def clone(self):
        u"""Returns a (deepcopied) clone."""
        return Labyrinth(copy.deepcopy(self._data))

    def empty(cls, n, m):
        u"""Creates an empty labyrinth.
        
            This is a classmethod and returns a new object.
            n is the width, m is the height of the empty labyrinth."""
        data = []
        for i in range(m):
            z = []
            for j in range(n):
                z.append(0)
            data.append(z)
        return Labyrinth(data)
            
    empty = classmethod(empty)
    
    def full(cls, n, m, typ = FLAT):
        u"""Creates a new labyrinth with maximized connectivity.
        
            Every cell is connected with every neighbor. Depending on the
            type (FLAT, RING or TORUS), this is also true for the cells on
            the edge of the labyrinth.
            
            This is a classmethod and returns a new object."""
        data = []
        for i in range(m):
            z = []
            for j in range(n):
                z.append(15)
            data.append(z)
        if typ == RING or typ == FLAT:
            for i in range(n):
                data[0][i] = 14
                data[m - 1][i] = 11
        if typ == FLAT:
            for j in range(m):
                data[j][0] = 7
                data[j][n - 1] = 13
            data[0][0] = 6
            data[0][n - 1] = 12
            data[m - 1][0] = 3
            data[m - 1][n - 1] = 9
        return Labyrinth(data)
        
    full = classmethod(full)

    def width(self):
        u"""Width of the labyrinth in cells."""
        if len(self._data) > 0:
            return len(self._data[0])
        return 0

    def height(self):
        u"""Height of the labyrinth in cells."""
        return len(self._data)
        
    def get(self, x, y):
        u"""Get an individual cell."""
        return self._data[y][x]
        
    def set(self, x, y, value):
        u"""Set the value of an individual cell.
        
            This is usually expected to be an integer, and most of the time
            an integer between 0 and 15 (inclusive), but it doesn't have to.
            """
        self._data[y][x] = value
        
    def getb(self, x, y, b):
        u"""Gets the b'th bit of cell (x, y)."""
        return (self._data[y][x] & 2**b) >> b
        
    def setb(self, x, y, b, value):
        u"""Sets the b'th bit of cell (x, y)."""
        self._data[y][x] = self._data[y][x] | 2**b
        if not value: self._data[y][x] -= 2**b
            
    def change(self, x, y, dir, bit = 1):
        u"""Changes the border between a cell and one of its neighbors.
        
            x and y are the coordinates of the cell; dir is the direction
            (0 = top, 1 = right, 2 = bottom, 3 = left) of the neighboring
            cell; bit indicates whether a wall (0) or a door (1) should be
            added. If no value is provided for bit, a door is added."""
        if dir == 0:
            self.setb(x, y, 0, bit)
            self.setb(x, (y - 1) % self.height(), 2, bit)
        if dir == 1:
            self.setb(x, y, 1, bit)
            self.setb((x + 1) % self.width(), y, 3, bit)
        if dir == 2:
            self.setb(x, y, 2, bit)
            self.setb(x, (y + 1) % self.height(), 0, bit)
        if dir == 3:
            self.setb(x, y, 3, bit)
            self.setb((x - 1) % self.width(), y, 1, bit)
            
    def hood(self, x, y):
        u"""List of accecible neighbors as list of (x, y)-tupels."""
        erg = []
        n = self.width()
        m = self.height()
        if self.getb(x, y, 0):
            erg.append((x, (y - 1) % m))
        if self.getb(x, y, 1):
            erg.append(((x + 1) % n, y))
        if self.getb(x, y, 2):
            erg.append((x, (y + 1) % m))
        if self.getb(x, y, 3):
            erg.append(((x - 1) % n, y))
        return erg

    def count_zeroes(self):
        u"""Number of cells with content 0."""
        erg = 0
        for i in range(self.width()):
            for j in range(self.height()):
                if self.get(i, j) == 0: erg += 1
        return erg
        
    def count_errors(self):
        u"""Number of inconsistencies."""
        erg = 0
        m = self.width()
        n = self.height()
        for i in range(m):
            for j in range(n):
                if self.getb(i, j, 1) != self.getb((i + 1) % m, j, 3): 
                    erg += 1000
                if self.getb(i, j, 2) != self.getb(i, (j + 1) % n, 0): 
                    erg += 1
        return erg
        
    def count_highs(self):
        u"""Number of cells with high bits (content greater 15)."""
        erg = 0
        for i in range(self.width()):
            for j in range(self.height()):
                if self.get(i, j) > 15: erg += 1
        return erg
        
    def area_survey(self):
        u"""Survey of the areas of the labyrinth.
        
            The return value is a tuple (map, areas), consisting of
            a labyrinth of the same size of the original labyrinth, containing
            numbers as the cell values indicating the different areas (see
            area_map() for more details), and a list of areas, each area
            being a list of (x, y)-tupels."""
        n = self.width()
        m = self.height()
        map = Labyrinth.empty(n, m)
        target = n * m
        summe = 0
        areas = []
        while summe < target:
            x = m - 1
            y = n - 1
            for i  in range(n - 1, -1, -1):
                for j in range(m - 1, -1, -1):
                    if map.get(i, j) == 0:
                        x = i
                        y = j
            hungry = [(x, y)]
            areas.append([(x, y)])
            map.set(x, y, len(areas))
            summe += 1
            while len(hungry):
                for x, y in hungry:
                    for xn, yn in self.hood(x, y):
                        if map.get(xn, yn) == 0:
                            hungry.append((xn, yn))
                            areas[-1].append((xn, yn))
                            map.set(xn, yn, len(areas))
                            summe += 1
                    hungry.remove((x, y))
        return (map, areas)
        
    def count_areas(self):
        u"""Number of connected areas."""
        return len(self.area_survey()[1])
        
    def area_map(self):
        u"""Map of the different areas.
        
            This map is, formally, a new labyrinth. The cells carry values
            indicating the area number (starting with 1) to which the 
            corresponding cell in the original labyrinth belongs.
            
            Example:
                                                   +-+-+
                Labyrinth([[0, 0],                 |0|0|
                           [0, 0]]).area_map()     +-+-+ 
                                                   |0|0|
            returns                                +-+-+
            
                [[1, 3],
                 [2, 4]]
                 
            while
                                                  +---+
                Labyrinth([[1, 8],                |1 8|
                           [1, 8]]).area_map()    +---+
                                                  |1 8|
            returns                               +---+
            
                [[1, 1],
                 [2, 2]]
                 
            """
        return self.area_survey()[0]
        
    def maxbit(self):
        u"""Highest bit used (-1 means all zeroes)"""
        erg = 0
        for i in range(self.width()):
            for j in range(self.height()):
                erg = max(erg, self.get(i, j))
        if erg == 0: return -1
        return int(math.log(erg) / math.log(2))

    def random(cls, n, m, typ = FLAT, grains = 1):
        u"""Constructs a random labyrinth.
            
            This is a classmethod and returns a new object.
            
            n is the width, m is the heights in cells.
            
            typ describes the type of the labyrinth. Possible values
            are FLAT, RING and TORUS, with FLAT being the default. RING
            means that passages disappearing on the right may be continued 
            on the left; TORUS means that additionally, passages disappearing
            on the bottom might be continued on the top.
            
            The number of grains describes how many connected areas exist.
            By default, this has the value 1, which means that there is only
            one connected area. The labyrinth is constructed so that two 
            arbitrary points in the labyrinth are connected by exactly one 
            path. If there are more than one grain, some pairs of points may
            be unconnected, but there is still at most one path between two
            points.
            
            The value of grains has to be greater 0 and should not be
            greater than n * m; otherwise, an exception is raised.
            """
        
        # The algorithm works like this:
        #
        # Define some "living" cells (as many as there are grains).
        # Expand the "alive" areas by opening doors between "alive" and
        # "dead" cells, untill all cells are alive.
        
        if grains > n * m or grains < 1:
            raise InvalidParameters

        V = [] # keeps track of "alive" cells
        L = [] # keeps track whether a cell has a *L*ower door
        R = [] # keeps track whether a cell has a door on the *R*ight
        for i in range(m):
            V.append([])
            L.append([])
            R.append([])
            for j in range(n):
                V[i].append(0)
                L[i].append(0)
                R[i].append(0)

        for g in range(grains):
            x = random.randint(0, n - 1)
            y = random.randint(0, m - 1)
            while V[y][x] == 1:
                x = random.randint(0, n - 1)
                y = random.randint(0, m - 1)
            V[y][x] = 1
        
        # define forbidden borders
        yborder = 0
        xborder = 1
        if typ == FLAT: yborder = 1
        if typ == TORUS: xborder = 0

        # Find cells with potential doors (between life and dead cells)
        potential = []
        for i in range(m - xborder):
            for j in range(n):
                if V[i][j] != V[(i + 1) % m][j]:
                    potential.append((0, i, j))
        for i in range(m):
            for j in range(n - yborder):
                if V[i][j] != V[i][(j + 1) % n]:
                    potential.append((1, i, j))

        # Add some doors
        for t in range(grains, m * n):
            di, x, y = potential.pop(random.randint(0, len(potential) - 1))
            V[x][y] = 1
            if di:
                V[x][(y + 1) % n] = 1
                R[x][y] = 1
            else:
                V[(x + 1) % m][y] = 1
                L[x][y] = 1
                
            # update the list of potentials
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if not xborder or (i % m) != m - 1:
                        cand = (0, i % m, j % n)
                        if V[i % m][j % n] != V[(i + 1) % m][j % n]:
                            if cand not in potential: potential.append(cand)
                        else:
                            if cand in potential: potential.remove(cand)
                    if not yborder or (j % n) != n - 1:
                        cand = (1, i % m, j % n)
                        if V[i % m][j % n] != V[i % m][(j + 1) % n]:
                            if cand not in potential: potential.append(cand)
                        else:
                            if cand in potential: potential.remove(cand)
        
        # write the matrix
        data = []
        for i in range(m):
            data.append([])
            for j in range(n):
                z = 8 * R[i][(j - 1) % n] + 4 * L[i][j] \
                    + 2 * R[i][j] + L[(i - 1) % m][j]
                data[i].append(z)
        return Labyrinth(data)
        
    random = classmethod(random)
    
    def random_doors(self, hori = 0.5, vert = None, typ = FLAT):
        u"""Randomly adds doors to the labyrinth.
        
            hori defines the probability of a cell getting an additional
            door in the east (and, therefore, another cell getting an
            additional door in the west). This is expected to be a value
            between 0.0 and 1.0. If no value is provided, hori has the
            value 0.5. If there are already doors present, the probability
            of the presence of a door is higher than hori, since hori
            describes only the probability of an additional door.
            
            vert defines the probability of a cell getting an additional
            door in the south. If no value is provided, this is the same as
            hori.
            
            typ can be FLAT, RING or TORUS, with FLAT being the default.
            Depending on this value, borders are respected."""
        if vert == None: vert = hori
        yborder = self.height() - 1
        xborder = self.width()
        if typ == FLAT: xborder -= 1
        if typ == TORUS: yborder += 1
        for i in range(xborder):
            for j in range(yborder):
                if hori > random.random():
                    self.setb(i, j, 1, 1)
                    self.setb((i + 1) % self.width(), j, 3, 1)
                if vert > random.random():
                    self.setb(i, j, 2, 1)
                    self.setb(i, (j + 1) % self.height(), 0, 1)
        if xborder < self.width():
            for j in range(yborder):
                if vert > random.random():
                    self.setb(self.width() - 1, j, 2, 1)
                    self.setb(self.width() - 1, (j + 1) % self.height(), 0, 1)
        if yborder < self.height():
            for i in range(xborder):
                if hori > random.random():
                    self.setb(i, self.height() - 1, 1, 1)
                    self.setb((i + 1) % self.width(), self.height() - 1, 3, 1)
    
    def paint(self, tileset, bits = 4):
        u"""Converts a labyrinth into an image.
        
            The image has the format of an wx.Image. This function
            needs the presence of the wx image handler; therefor, a 
            wx.App is required. XXX: make easier
            
            The layout is specified with the tileset. This tileset
            is expected to contain all the sixteen possible
            states of an atomic block of a labyrinth (at least one example
            of such a tileset should have been provided together with this
            file). It is also expected to be a wx.Image.
            
            If there are more than 16 states, a bigger tileset must be
            provided, and bits must be a value greater 4.
            """
        
        b = 2**bits
        h = tileset.GetHeight()
        w = tileset.GetWidth() / b
        m = len(self._data)
        n = len(self._data[0])
        tiles = []
        for i in range(b):
                tiles.append(tileset.GetSubImage(wx.Rect(i * w, 0, w, h
                        )).ConvertToBitmap())
        bild = wx.EmptyBitmap(w * n, h * m)
        dc = wx.MemoryDC()
        dc.SelectObject(bild)
        for i in range(m):
            for j in range(n):
                dc.DrawBitmap(tiles[self._data[i][j] % b], j * w, i * h, True)
        return bild.ConvertToImage()
    
    def load(cls, filename):
        u"""Load a new labyrinth from a file.
        
            This is a classmethod and can be called without an instance."""
        lines = file(filename).readlines()
        return Labyrinth(eval("[" + string.join(lines[1:-1], "\n") + "]", 
                          globals()))
                          
    load = classmethod(load)
        
    def save(self, filename):
        u"""Saves a labyrinth in a file."""
        outfile = file(filename, "w")
        text = self.__repr__()
        text = text.replace("([[", "([\n    [")
        text = text.replace("],", "],\n   ")
        text = text.replace("]])", "]\n])")
        outfile.writelines(text)

    def qpath(self, p_from, p_to):
        u"""Finds a path from one cell to another.
        
            p_from and p_to are tupels of the form (x, y), with x and
            y being coordinates. The result is a list of points, starting
            with p_from and ending with p_to.
            
            The resulting path is not guaranteed to be the shortest
            possible path. Furthermore, it is not guaranteed that the path
            from p_to to p_from is the reverse of the path from p_from to
            p_to.
            
            On the other hand, if there are several alternative paths, the
            computation of qpath() is much faster (and less memory intensive)
            than the computation of path().
            
            If there is no connection between p_from and p_to, an empty list
            is returned."""
        burnt = [p_from,]
        path = [p_from,]
        m = self.height()
        n = self.width()
        
        while len(path) > 0 and path[-1] != p_to:
            x, y = path[-1]
            escape = False
            for xd, yd in self.hood(x, y):
                if (xd, yd) not in burnt:
                    xn = xd
                    yn = yd
                    escape = True
            if escape:
                path.append((xn, yn))
                burnt.append((xn, yn))
            else:
                path.pop(-1)
        return path
    
    def _pfind(self, start, stop, cpath):
        # recursion needed for paths()
        x, y = cpath[-1]
        erg = []
        for p in self.hood(x, y):
            if p == stop:
                erg.append(cpath + [p])
            else:
                if p not in cpath:
                    more = Labyrinth._pfind(self, start, stop, cpath + [p])
                    if len(more) > 0:
                        erg += more
        return erg
        
    def paths(self, start, stop):
        u"""A list of all paths from start to stop.
        
            start and stop are supposed to be (x, y)-tupels.
        
            This method should be treated with caution, since it is slow
            and memory-intensive.
            
            The return value is a list of lists of (x, y)-tupels."""
        return self._pfind(start, stop, [start,])
        
    def path(self, start, stop):
        u"""Returns a shortest path between start and stop.
        
            start and stop are supposed to be (x, y)-tupels.
            
            This method should be treated with caution, since it is slow
            and memory-intensive. For a quicker method, see qpath().
            
            The return value is a list of (x, y)-tupels.
            
            It is guaranteed that there is no shorter path from start to stop,
            but it is not guaranteed that path(stop, start) yields the reverse
            path of path(start, stop)."""
        liste = self.paths(start, stop)
        if len(liste) == 0:
            return None
        erg = liste[0]
        for i in range(len(liste)):
            if len(liste[i]) < len(erg):
                erg = liste[i]
        return erg

    def invert(self):
        u"""Exchanges the system of passages with the system of walls."""
        newdata = []
        m = self.width()
        n = self.height()
        for j in range(n):
            z = []
            for i in range(m):
                z.append(15 - (8 * self.getb(i, j, 2)
                               + self.getb((i + 1) % m, j, 3)
                               + 2 * self.getb((i + 1) % m, (j + 1) % n, 0)
                               + 4 * self.getb(i, (j + 1) % n, 1)))
            newdata.append(z)
        self._data = newdata

    def double(self):
        u"""Creates a new maze twice as large.
            
            In this new maze, the border between passages and walls is
            transformed into passages, while both passages and wall become
            walls."""
        maze = self.empty(2 * self.width(), 2 * self.height())
        for i in range(self.width()):
            for j in range(self.height()):
                maze.set(2 * i, 2 * j, _doubs[self.get(i, j)][0])
                maze.set(2 * i + 1, 2 * j, _doubs[self.get(i, j)][1])
                maze.set(2 * i, 2 * j + 1, _doubs[self.get(i, j)][2])
                maze.set(2 * i + 1, 2 * j + 1, _doubs[self.get(i, j)][3])
        return maze
        
    def border(self, size = 1):
        u"""Returns a new maze with a border of 0-cells.
            
            If the labyrinth is a ring or torus, passages cross the border.
            """
        maze = self.empty(self.width() + 2 * size, self.height() + 2 * size)
        for i in range(self.width()):
            for j in range(self.height()):
                maze.set(i + size, j + size, self.get(i, j))
        for s in range(size):
            for i in range(self.width()):
                if self.getb(i, 0, 0):
                    maze.set(i + size, s, 5)
                if self.getb(i, self.height() - 1, 2):
                    maze.set(i + size, self.height() + size + s, 5)
            for j in range(self.height()):
                if self.getb(0, j, 3):
                    maze.set(s, j + size, 10)
                if self.getb(self.width() - 1, j, 1):
                    maze.set(self.width() + size + s, j + size, 10)
        return maze
        
    def transpose(self):
        u"""Transposes the labyrinth in place."""
        newdata = []
        for i in range(len(self._data[0])):
            z = []
            for j in range(len(self._data)):
                z.append(self._data[j][i])
            newdata.append(z)
        self._data = newdata
        
    def __repr__(self):
        u"""String representation."""
        ## return str(type(self))[8:-2] + "(" + repr(self._data) + ")"
        return "laby.Labyrinth(" + repr(self._data) + ")"
        

def flatten(infile, outfile):
    u"""Converts 4x4 into 16x1 subimage matrix.
        
        Reads an image from infile which is supposed to contain a 4x4 matrix
        of subimages, converts it into a horizontal stripe of 16 subimages,
        and writes the result as a PNG file into outfile."""
    inimage = wx.Image(infile, wx.BITMAP_TYPE_ANY)
    h = inimage.GetHeight() / 4
    w = inimage.GetWidth() / 4
    outimage = wx.EmptyBitmap(w * 16, h)
    dc = wx.MemoryDC()
    dc.SelectObject(outimage)
    for i in range(4):
        for j in range(4):
            dc.DrawBitmap(inimage.GetSubImage(wx.Rect(j * w, i * h, w, h
                            )).ConvertToBitmap(), i * 4 * w + j * w, 0, True)
    outimage.ConvertToImage().SaveFile(png(outfile), wx.BITMAP_TYPE_PNG)

def png(text):
    u"""Adds '.png' to a filename, if needed."""
    if text[-4:].lower() == ".png":
        return text
    return text + ".png"

def _test():
    # This is used for tests. It can be called from the command line
    # with the command "test".
    #
    # Replace this code with your own tests.
    #
    print "\n    Creating a 16x12 maze..."
    maze = Labyrinth.random(16, 12)
    print "    Done.\n"
    print "               Width: " + str(maze.width())
    print "              Height: " + str(maze.height())
    print "    Number of zeroes: " + str(maze.count_zeroes())
    print "    Number of errors: " + str(maze.count_errors())
    print "         Highest Bit: " + str(maze.maxbit())
    print "    Number of aereas: " + str(maze.count_areas())
    print "\n    A complete hexadecimal representation:\n"
    for i in range(maze.height()):
        p = "        "
        for j in range(maze.width()):
            p += hex(maze.get(j, i))[2:]
        print p
    print "\n    End of tests."
    

if __name__ == "__main__":
    u"""Builds a labyrinth text file or a labyrinth image file.
    
        There are three different commands possible:
        
        1. make
        =======
        
        laby.py make _outfile_ _width_ _height_ [_options_]
        
        This writes a labyrinth of width _width_ and height _height_
        into the file _outfile_. Possible options are:
        
        -r, --ring:
            Makes a ring-shaped labyrinth.
        -t, --torus:
            Makes a torus-shaped labyrinth.
            
        If both -r and -t are specified, a torus-shaped labyrinth will
        be built. If neither -r nor -t are specified, a flat labyrinth
        will be created.
        
        -i, --image=_imagefile_:
            Creates an additional imagefile _imagefile_.
        -s, --set=_setfile_:
            This option is only relevant if the option -i is set. In
            this case, the setfile _setfile_ will be used to create the
            image. If this option is not set, a default tileset will be
            used.
            
        -g, --grains=_number_of_grains_:
            Number of connected areas in the labyrinth, the default is
            one single connected area.
        
        
        2. convert
        ==========
        
        laby.py convert _infile_ _outfile_ [_options_]
        
        This reads a labyrinth from the textfile _infile_ (created with
        the command make) and writes it to the imagefile _outfile_.
        
        -s, --set=_setfile_:
            Allows the specification of the setfile to be used. If this
            option is not set, a default tileset will be used.
        -b, --bits=_number_of_bits_:
            Number of bits used in the labyrinth/tileset. The default
            value is 4.
        
        It is expected that the file simple.png is in the subdirectory
        /tileset of the file laby.py, since the file tileset/simple.png
        is used as the default tileset.
        
        
        3. flatten
        ==========
        
        laby.py flatten _infile_ _outfile_
        
        Reads an image file _infile_ consisting of 4x4 subimages, converts
        it into a stripe of 16 subimages and writes the result to _outfile_.
        """
    
    gebrauch = "\n%prog make outfile width height [options]\n\n    or\n\n"\
               + "%prog convert infile outfile [options]\n\n    or\n\n"\
               + "%prog flatten infile outfile"
    parser = optparse.OptionParser(usage = gebrauch,
                                   version="%prog 0.1.0")
    parser.add_option("-b", "--bits", default = "4", dest = "bits",
                      help = "Number of bits for painting.")
    parser.add_option("-g", "--grains", default = "1", dest = "grains",
                      help = "Number of connected areas.")
    parser.add_option("-i", "--image", default = None, dest = "img",
                      help = "Additional image.")
    parser.add_option("-r", "--ring", default = False, dest = "ring",
                      action = "store_true",
                      help = "Makes a ring-shaped labyrinth.")
    parser.add_option("-s", "--set", default = sys.path[0]
                                               + "/tileset/simple.png", 
                      dest = "set", help = "Tileset for images.")
    parser.add_option("-t", "--torus", default = False, dest = "torus",
                      action = "store_true",
                      help = "Makes a torus-shaped labyrinth.")
    (opts, args) = parser.parse_args()
    typ = FLAT
    if opts.ring: typ = RING
    if opts.torus: typ = TORUS

    if len(args) < 1:
        print "Missing arguments. See help with option \"--help\"."
        sys.exit(1)
    if args[0][0] not in "cfmt":
        print "Unknown command \"" + args[0] \
              + "\". See help with option \"--help\"."
        sys.exit(1)
    
    # make
    if args[0][0] == "m":
        if len(args) < 4:
            print "Command \"make\" requires 3 arguments: outfile, " \
                  + "width and height."
            sys.exit(1)
        lab = Labyrinth.random(int(args[2]), int(args[3]), typ, 
                               int(opts.grains))
        lab.save(args[1])
        if opts.img:
            lab.paint(wx.Image(opts.set, wx.BITMAP_TYPE_ANY), 
                      int(opts.bits)).SaveFile(png(opts.img), 
                                               wx.BITMAP_TYPE_PNG)
    # convert
    if args[0][0] == "c":
        if len(args) < 3:
            print "Command \"convert\" requires 2 arguments: infile " \
                  + "and outfile."
            sys.exit(1)
        lab = Labyrinth.load(args[1])
        lab.paint(wx.Image(opts.set, wx.BITMAP_TYPE_ANY),
                  int(opts.bits)).SaveFile(png(args[2]), wx.BITMAP_TYPE_PNG)

    # flatten
    if args[0][0] == "f":
        if len(args) < 3:
            print "Command \"flatten\" requires 2 arguments:  infile " \
                  + "and outfile."
            sys.exit(1)
        flatten(args[1], args[2])

    # test
    if args[0][0] == "t": _test()
