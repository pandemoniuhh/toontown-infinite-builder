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
    pass

# Ready to download these sources if they do not exist

# https://github.com/freshollie/panda3d/archive/00150976f7b233b4be54e68a36785187a4bfa77b.zip
# https://github.com/freshollie/Astron/archive/3a15606ab15b63b666fdff1e0145417470232dbc.zip
# https://github.com/freshollie/toontown-infinite-resources/archive/f7cfe07d35893bf0c964e668bc46fb605e317d4d.zip
#https://github.com/freshollie/toontown-infinite-source/archive/master.zip