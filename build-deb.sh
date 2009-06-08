#!/bin/bash

packages='src/gecod src/gecoc src/gecoc/gtk-geco src/gecoc/web-geco'
root=$(pwd)
mkdir $root/packages

for i in $packages
do
    cd $i
    yes | debuild -us -uc
    cd ..
    mv *.deb $root/packages
    cd $root
done
