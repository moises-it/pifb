#!/bin/bash
from=$1
alias=$2
target=$3

rsync -t -r --progress $from $alias:$target > /tmp/pifb.log