#!/bin/bash

cd $(dirname $(realpath "$0"))
cd ..


make clean
make
python build-out/polyglot_pyc/polyglot_codestats.pyc 'src-*' 'bin'
