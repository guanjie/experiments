# -*- coding:iso-8859-1 -*-
#
# Jan Thor
# 
# 20. - 21.9.2005
#
# This modul contains some examples how to use the modul laby.py
# The examples can be started from the command line.

import random
import sys
from laby import *

# samplemaze is connected, consistent, zero-free, circle-free and flat.
samplemaze = [
    [2, 12, 6, 8, 2, 14, 10, 8, 2, 14, 8, 4, 2, 12, 2, 12, 4, 4, 4, 4],
    [4, 3, 13, 4, 4, 7, 8, 4, 4, 7, 10, 9, 4, 3, 14, 15, 9, 7, 9, 5],
    [3, 14, 9, 5, 5, 7, 8, 5, 3, 13, 4, 2, 11, 14, 9, 3, 10, 11, 10, 13],
    [2, 15, 8, 7, 9, 7, 10, 9, 4, 7, 11, 10, 8, 7, 10, 10, 10, 10, 12, 1],
    [2, 15, 10, 11, 8, 7, 10, 10, 9, 5, 6, 14, 8, 7, 12, 4, 6, 8, 3, 12],
    [4, 5, 6, 12, 6, 9, 2, 12, 4, 7, 9, 7, 10, 13, 3, 11, 11, 12, 4, 1],
    [7, 11, 13, 1, 7, 10, 8, 3, 13, 5, 4, 3, 8, 3, 10, 8, 4, 1, 7, 8],
    [5, 4, 3, 10, 9, 4, 2, 10, 15, 9, 7, 10, 8, 6, 10, 10, 9, 4, 7, 8],
    [7, 11, 14, 14, 14, 15, 14, 10, 15, 14, 11, 8, 6, 9, 2, 12, 4, 7, 11, 8],
    [5, 6, 9, 1, 5, 1, 1, 4, 5, 3, 8, 4, 5, 4, 2, 15, 9, 5, 4, 4],
    [5, 3, 8, 2, 15, 10, 14, 9, 3, 14, 10, 11, 13, 7, 10, 9, 4, 7, 9, 5],
    [7, 14, 8, 6, 11, 8, 7, 10, 8, 7, 14, 12, 3, 15, 10, 14, 9, 7, 10, 13],
    [5, 3, 8, 7, 14, 8, 7, 10, 8, 5, 1, 1, 2, 9, 2, 15, 10, 11, 8, 1],
    [5, 2, 14, 13, 7, 8, 3, 8, 6, 15, 10, 10, 14, 14, 8, 7, 10, 14, 8, 4],
    [7, 12, 1, 1, 3, 14, 14, 8, 5, 7, 14, 12, 1, 7, 8, 3, 8, 3, 14, 9],
    [1, 7, 10, 8, 2, 9, 7, 8, 1, 1, 1, 3, 8, 3, 14, 14, 12, 2, 15, 12],
    [6, 15, 14, 8, 4, 4, 3, 14, 14, 10, 10, 14, 10, 8, 1, 5, 3, 8, 1, 5],
    [5, 1, 7, 8, 5, 7, 8, 5, 5, 6, 10, 15, 14, 12, 6, 11, 14, 8, 2, 13],
    [7, 12, 5, 6, 11, 15, 12, 1, 5, 1, 6, 13, 1, 1, 7, 12, 7, 8, 6, 13],
    [1, 1, 3, 11, 8, 1, 1, 2, 9, 2, 9, 1, 2, 10, 9, 1, 1, 2, 9, 1]
]

def ex00():
    # Basic test
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

def ex01():
    # Creates a maze not filling the whole block with start and end point
    #
    # (could be used for a game where the player must find a way from a
    #  starting point to an end point)
    #
    # Doors are added, the greatest area is colored red, and within this
    # area, two random distinct points are chosen and colored green and
    # yellow.
    #
    # Strictly speaking, it could be possible that the largest area has
    # size 1, in which case it would be impossible to find two distinct
    # points in it, and the while loop below would never return. Fortunately,
    # this has only probability 0.334**(2 * 20 * 20), so it's not very
    # likely.
    maze = Labyrinth.empty(20, 20)
    maze.random_doors(0.666)
    map, areas = maze.area_survey()
    maxa = 0
    sela = areas[0]
    for a in areas:
        if len(a) > maxa:
            maxa = len(a)
            sela = a
    for x, y in sela:
        maze.setb(x, y, 4, 1)
    n1 = random.randrange(0, len(sela) - 1)
    n2 = random.randrange(0, len(sela) - 1)
    while n1 == n2:
        n2 = random.randrange(0, len(sela) - 1)
    x1, y1 = sela[n1]
    x2, y2 = sela[n2]
    maze.setb(x1, y1, 5, 1)
    maze.setb(x2, y2, 5, 1)
    maze.setb(x2, y2, 4, 0)
    maze.paint(wx.Image("tileset/small.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex01.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex01.png\""

def ex02():
    # Connect upper left and lower right point
    #
    # Doors are added until both points are connected.
    maze = Labyrinth.empty(20, 20)
    while len(maze.qpath((0, 0), (19, 19))) == 0:
        maze.random_doors(0.01)
    map, areas = maze.area_survey()
    for x, y in areas[0]:
        maze.setb(x, y, 4, 1)
    maze.setb(0, 0, 5, 1)
    maze.setb(19, 19, 5, 1)
    maze.paint(wx.Image("tileset/small.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex02.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex02.png\""

def ex03():
    # Back and forth
    # 
    # In a labyrinth created with random(), there is always exactely one
    # connection between two points; the connection back and forth yields
    # only one path, colored yellow (red + green).
    maze = Labyrinth.random(20, 20)
    path = maze.qpath((0, 0), (19, 19))
    for (x, y) in path:
        maze.setb(x, y, 4, 1)
    path2 = maze.qpath((19, 19), (0, 0))
    for (x, y) in path2:
        maze.setb(x, y, 5, 1)
    maze.paint(wx.Image("tileset/simple.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex03.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex03.png\""

def ex04():
    # Back and forth II
    #
    # With additional doors, there are usually several different ways between
    # two points. One path is colored red, one is colored green, the
    # intersection is colored yellow.
    maze = Labyrinth.random(20, 20)
    maze.random_doors(0.1)
    path = maze.qpath((0, 0), (19, 19))
    for (x, y) in path:
        maze.setb(x, y, 4, 1)
    path2 = maze.qpath((19, 19), (0, 0))
    for (x, y) in path2:
        maze.setb(x, y, 5, 1)
    maze.paint(wx.Image("tileset/simple.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex04.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex04.png\""

def ex05():
    # Find a shortest path among different possibilities
    #
    # This uses path() instead of qpath() to find the shortest path.
    # Unfortunately, path() is too slow to be too useful.
    #
    # Also shows the use of full().
    maze = Labyrinth.full(3, 3)
    path = maze.path((0, 2), (2, 0))
    for (x, y) in path:
        maze.setb(x, y, 4, 1)
    path2 = maze.path((2, 0), (0, 2))
    for (x, y) in path2:
        maze.setb(x, y, 5, 1)
    maze.paint(wx.Image("tileset/simple.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex05.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex05.png\""

def ex06():
    # Invert, Border, Double (and clone(), actually)
    maze = Labyrinth.random(40, 30, RING)
    maze.paint(wx.Image("tileset/small.png", wx.BITMAP_TYPE_ANY), 
               4).SaveFile("ex06a.png", wx.BITMAP_TYPE_PNG)
    maze2 = maze.clone()
    maze2.invert()
    maze2.paint(wx.Image("tileset/small.png", wx.BITMAP_TYPE_ANY), 
                4).SaveFile("ex06b.png", wx.BITMAP_TYPE_PNG)
    maze2 = maze.border(3)
    maze2.paint(wx.Image("tileset/small.png", wx.BITMAP_TYPE_ANY), 
                4).SaveFile("ex06c.png", wx.BITMAP_TYPE_PNG)
    maze2 = maze.double()
    maze2.paint(wx.Image("tileset/small.png", wx.BITMAP_TYPE_ANY), 
                4).SaveFile("ex06d.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex06a.png\" - \"ex06d.png\""

def ex07():
    # More than one grain; coloring of areas
    #
    # The images should be self-explanatory.
    print "Writing..."
    maze = Labyrinth().random(40, 30, TORUS, 25).border(3)
    maze2, areas = maze.area_survey()
    for i in range(maze.width()):
        for j in range(maze.height()):
            maze.set(i, j, maze.get(i, j) + 16 * (maze2.get(i, j) % 8))
    maze.paint(wx.Image("tileset/small.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex07a.png", wx.BITMAP_TYPE_PNG)
    print "More writing..."
    maze = Labyrinth().random(80, 60, FLAT, 40)
    maze2, areas = maze.area_survey()
    for i in range(maze.width()):
        for j in range(maze.height()):
            maze.set(i, j, maze.get(i, j) + 16 * (maze2.get(i, j) % 8))
    maze.paint(wx.Image("tileset/small.7.png", wx.BITMAP_TYPE_ANY), 
               7).SaveFile("ex07b.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex07a.png\" and \"ex07b.png\""

def ex08():
    # Anisotropic doors
    #
    # Doors are added with a preference for a certain direction.
    maze = Labyrinth.empty(30, 20)
    maze.random_doors(0.8, 0.2)
    maze.paint(wx.Image("tileset/simple.png", wx.BITMAP_TYPE_ANY), 
               4).SaveFile("ex08a.png", wx.BITMAP_TYPE_PNG)
    maze = Labyrinth.empty(30, 20)
    maze.random_doors(0.2, 0.8)
    maze.paint(wx.Image("tileset/simple.png", wx.BITMAP_TYPE_ANY), 
               4).SaveFile("ex08b.png", wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex08a.png\" and \"ex08b.png\""
    
def ex09():
    # The winner takes it all
    #
    # For ten labyrinths, doors are randomly added, and a survey of the
    # size of the resulting areas is printed. Usually, there is one large
    # area and a lot of small areas, often of size 1.
    print "\nSize of areas in ten 10x10 mazes with door-probability 1/2:\n"
    for t in range(10):
        maze = Labyrinth.empty(10, 10)
        maze.random_doors(typ = TORUS)
        map, areas = maze.area_survey()
        survey = []
        for a in areas:
            survey.append(len(a))
        survey.sort()
        print survey
        
def ex10():
    # Four possible paths
    #
    # Take the sample maze, add two doors, draw all possible paths
    # from the middle to the lower right corner. Each additional door 
    # doubles the number of possible paths.
    maze = Labyrinth(samplemaze)
    maze.change(15, 6, 1, 1)
    maze.change(16, 19, 1, 1)
    maze.paint(wx.Image("tileset/small.png", wx.BITMAP_TYPE_ANY), 
               4).SaveFile("ex10.png", wx.BITMAP_TYPE_PNG)
    print "Calculating paths..."
    paths = maze.paths((8, 8), (19, 19))
    i = 0
    for p in paths:
        i += 1
        maze2 = maze.clone()
        for (x, y) in p:
            maze2.setb(x, y, 4, 1)
            maze2.paint(wx.Image("tileset/small.7.png", wx.BITMAP_TYPE_ANY), 
                        7).SaveFile("ex10-" + str(i) + ".png", 
                                    wx.BITMAP_TYPE_PNG)
    print "Wrote: \"ex10.png\" and several \"ex-\"?\".png\"."

exs = [ex00, ex01, ex02, ex03, ex04, ex05, ex06, ex07, ex08, ex09, ex10]

if len(sys.argv) < 2:
    print "\nExample:\n\n    examples.py 0\n\nwith\n"
    print " 0  Basic Test"
    print " 1  Partly filling maze with connected points."
    print " 2  Diagonal connection in random field."
    print " 3  Diagonal connection in standard maze."
    print " 4  Diagonal connection with additional doors."
    print " 5  Shortest connection."
    print " 6  Invert, Border, Double."
    print " 7  Standard maze with multiple grains; area coloring."
    print " 8  Random additional doors."
    print " 9  Area size in random field."
    print "10  Multiple paths."
else:
    exs[int(sys.argv[1])]()