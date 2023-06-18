#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import textwrap
import pandas as pd 
import numpy as np 
import os.path as osp 
import warnings

warnings.filterwarnings("ignore")



def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog is ....
        @Author: xutingfeng@big.ac.cn
        Version: 1.0
        Example:
        ...

        """
        ),
    )
    parser.add_argument("-i", "--file", dest="file", nargs="+", help="input file", type=str, required=True)
    parser.add_argument("-o", "--out", dest="out", help="output file", type=str, required=True)
    parser.add_argument("-l","--left-pheno",dest="left", help="left pheno", type=str, required=True)
    parser.add_argument("-p", "--pheno", dest="pheno", nargs="+", help="pheno，与--file 需要匹配", type=str, required=True)

    return parser






def read_csv(file, **kwargs):
    if file.endswith('.gz'):
        kwargs["compression"] = 'gzip'

    df = pd.read_csv(file, sep='\s+', **kwargs)
    return df


def getPheno(path):
    return osp.split(path)[1].split('.')[0]

def move_index_to_front(lst, index):

    lst = [lst[index]] + lst[:index] + lst[index+1:]
    return lst



if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    path = args.file
    out = args.out
    pheno = args.pheno
    left = args.left
    colStart=8
    print(f"input file is {path}")
    print(f"output file is {out}")
    print(f"pheno is {pheno}")
    print(f"left pheno is {left}")
    if left is not None:
        if left not in pheno:
            raise ValueError(f"left pheno {left} not in pheno {pheno}")
        else:
            index = pheno.index(left)

            pheno = move_index_to_front(pheno, index)
            path = move_index_to_front(path, index)

    print(pheno)
    print(path)

    dfList = [read_csv(i) for i in path]
    dfList = [df.rename(columns={i:f"{i}_{p}" for i in df.columns[colStart:]}) for df,p in zip(dfList, pheno)] # rename columns
    res= dfList[0].copy()
    leftPheno=pheno[0]
    print(leftPheno)
    for right,p in zip(dfList[1:], pheno[1:]):

        # STEP1 提取与右边有而左边没有的变异，以及左右共有的变异
        rightUniqID=set(right["ID"]).difference(set(res["ID"]))
        rightUniq = right["ID"].isin(rightUniqID)
        rightUniq_df = right[rightUniq]
        leftRightBoth_df = right[~rightUniq]
        
        # STEP2 对于左右共有的变异，直接提取右边需要的列，然后合并到res中
        res = res.merge(leftRightBoth_df[["ID"] + list(leftRightBoth_df.columns[8:])], on='ID', how='outer')
        if rightUniq_df.shape[0] != 0:
            # STEP3 对于右边特有的变异，直接concat到res中，如果没有则跳过
            ## 首先对rightUniq_df进行处理，重命名需要保存的列
            print(f"before merge {p}, res.shape is {res.shape}")
            res = pd.concat([res, rightUniq_df], axis=0, ignore_index=True, sort=False)
            print(f"after merge {p}, res.shape is {res.shape}")
    
    res.to_csv(out, sep='\t', index=False, na_rep='NA')