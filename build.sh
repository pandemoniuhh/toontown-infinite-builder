#!/bin/sh

# (C) Freshollie - Oliver Bell - 2017

echo "Building dependencies for toontown infinite"

echo "Building panda3d"
cd panda3d

echo "Downloading required build libraries"
apt-get install -y build-essential pkg-config python-dev libpng-dev libjpeg-dev libtiff-dev zlib1g-dev libssl-dev libx11-dev libgl1-mesa-dev libxrandr-dev libxxf86dga-dev libxcursor-dev bison flex libfreetype6-dev libvorbis-dev libeigen3-dev libopenal-dev libode-dev libbullet-dev nvidia-cg-toolkit libgtk2.0-dev

echo "Making panda"
/usr/bin/python2 makepanda/makepanda.py --everything --installer --no-egl --no-gles --no-gles2

echo "Installing panda"
dpkg -i panda3d*.deb


echo "Building Astron"
cd ..
cd Astron

echo "Installing required build libraries"
apt-get install -y libssl-dev libyaml-dev libboost-all-dev

echo "Building astron"
cmake -DCMAKE_BUILD_TYPE=Release . && make

echo "Copying astron to src"
cp astrond ../src/astron/astrond

echo "Toontown infinite ready to execute"