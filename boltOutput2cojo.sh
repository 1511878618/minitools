#!/bin/bash
bolt_lmm_output=$1
output=$2
samplePath=￥3 #/pmaster/xutingfeng/dataset/ukb/dataset/snp/SORT1_2mb_ref_last.sample

N=$(($(cat ${samplePath} | wc -l) - 2))

zcat ${bolt_lmm_output} | awk -v N=${N} 'BEGIN{print "SNP","A1", "A2", "freq", "b", "se", "p", "N"}NR==1{next}{print $1,$5,$6,$7,$11,$12,$16, N}' >${output}
