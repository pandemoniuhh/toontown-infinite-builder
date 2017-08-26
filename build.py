import os
import sys

PYTHON_PATH = sys.executable

# (C) Freshollie - Oliver Bell - 2017

WINDOWS = sys.platform.startswith("win")
if WINDOWS:
    os.system("@echooff")
    
print("Building dependencies for toontown infinite")
print("Building panda3d")
print("-"*20)

os.system("cd panda3d")

if not WINDOWS:
    