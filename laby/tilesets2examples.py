# -*- coding:iso-8859-1 -*-
#
# Jan Thor
# 
# 22.9.2005

# Creates examples for all tilesets.
# All 16 basic tiles appear. Furthermore, some of the higher bits
# are tested, if present.
#
# The similarity of one of the resulting images with the logo of a certain 
# software vendor is purely coincidental.

import laby
import os
import wx
myApp = wx.App(0)

maze = laby.Labyrinth([[118, 122, 122, 126, 124],
                       [117,  16,  48, 113, 117],
                       [117,  64,  32, 116, 117],
                       [119, 120, 114, 127, 125],
                       [115, 122, 122, 123, 121]])
for f in os.listdir("tileset"):
    parts = f.split(".")
    if parts[-1].lower() == "png":
        bits = 4
        if len(parts) > 2:
            bits = int(parts[-2])
        maze.paint(wx.Image("tileset/" + f, wx.BITMAP_TYPE_ANY),
                   bits).SaveFile("example_of_" + f, wx.BITMAP_TYPE_PNG)
