#!/bin/bash
from=$1
alias=$2
target=$3

rsync -t -r --progress -s $from $alias:$target > /tmp/pifb.log