#!/bin/bash
# 传入bolt_lmm的输出文件，输出locuszoom的输入文件

if [[ "$1" == *".gz" ]]; then
    zcat $1 | awk 'BEGIN{OFS="\t"} {print $2, $3, $5,$6, $16, $11,$12,$7}' >${1%.*}.locuszoom
    # 在这里添加你想要执行的操作
else
    cat $1 | awk 'BEGIN{OFS="\t"} {print $2, $3, $5,$6, $16, $11,$12,$7}' >${1%.*}.locuszoom
fi
