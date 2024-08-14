#!/bin/bash

cd $(dirname $(realpath "$0"))
cd ..


IF_CLEANUP=false
while getopts "c:nc" opt; do
    case $opt in
        c) IF_CLEANUP=true ;;
        nc) IF_CLEANUP=false ;;
    esac
done

if [ -d '.gradle' ] || [ -d 'build-out' ]; then
    if [ "$OPTIND" -eq 1 ]; then
        read -p 'Type c to remove directories or press Enter to continue: ' user_input
        [ "$user_input" == 'c' ] && IF_CLEANUP=true
    fi
    $IF_CLEANUP && rm -rf .gradle build-out
fi


gradle build
read -p 'Press Enter to continue with codestats ...'

python build-out/polyglot_py_bytecode/polyglot_codestats.pyc 'src-*' 'bin'
