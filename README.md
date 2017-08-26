# Toontown Infinite Builder

This repository contains the instructions for building aston and panda3d to run this version of Toontown-Infinite.

## Building
Building will build the astrond executable, the panda3d library for your operating system, and then place them in the correct directories

### Requirements

- Python 2.7
- pip

### Linux

`sudo python build.py`

### Windows

`\path\to\python build.py`


**Note:** Windows doesn't build astron.exe and just uses the already provided repository version.

If you dont trust this, you will have to follow the build instructions and build your own.

## Executing

### Server

Easiest way is to execute `python src/ToontownClusterManager.py`

Otherwise manually run the files under `src/astron/<your os>/`

### Client

To run a client execute the desired launcher under `src/<your os>/`
