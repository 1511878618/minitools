#!/bin/bash

if [[ "$1" == *".gz" ]]; then
    zcat $1 | awk 'NR==1{print;next}{print $0 | "sort -k1,1 -k2n"}' | tr " " "\t" >${1%.*}.locuszoom
    gzip ${1%.*}.locuszoom
else
    cat $1 | awk 'NR==1{print;next}{print $0 | "sort -k1,1 -k2n"}' | tr " " "\t" >${1%.*}.locuszoom
    gzip ${1%.*}.locuszoom
fi
