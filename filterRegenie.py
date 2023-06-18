#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import textwrap
import numpy as np 
import pandas as pd 
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

        输入的数据应该是GWAS输出与VEP的注释merge的结果，并且对应的CQE列转化成了多列而不是在一起

        过滤策略
        1. 指定不需要的consequence，过滤掉它们 -c downstream intron non_coding synonymous，如果没有指定consequence，则默认为downstream intron non_coding synonymous。
        2. 指定GENESYMBOL，过滤掉不在这些GENESYMBOL中的变异，-g A2M A2ML1，如果没有指定GENESYMBOL，则默认进行这不操作。
        3. FDR多重矫正，变异个数/pvalue_cutoff 作为过滤阈值；如果没有指定 -p/pvalue_cutoff，则默认为0.05；需要注意当指定多个基因的时候，会统计多个基因在内的变异个数，而不是单个基因的变异个数
        4. 按照FDR多重矫正的P值进行过滤，如果没有指定 -P/PvalueCol，则默认为12，即第12列的P值进行FDR多重矫正；如果指定了 -P/PvalueCol，则按照指定的列（可以多列，这个时候必须所有均pass才保留）进行FDR多重矫正。
        4. 保存文件到outFilePath

        Example:
        ...

        """
        ),
    )
    parser.add_argument("-i", "--file",dest="filePath",type=str,required=True, help="regenie file path")
    parser.add_argument("-o", "--outFile",dest="outFilePath",type=str,required=True, help="output file path")
    parser.add_argument("-g", "--GENESYMBOL",dest="SYMBOL", default=["downstream", "intron", "non_coding", "synonymous"],required=False, help="filter by GENESYMBOL",nargs="+", type=str)
    parser.add_argument("-c", "--consequence",dest="consequence", default=["downstream", "intron", "non_coding", "synonymous"],required=False, help="filter by consequence",nargs="+", type=str)
    parser.add_argument("-p", "--pvalue_cutoff",dest="pvalue_cutoff", default=0.05,required=False, help="FDR pvalue ", type=float)
    parser.add_argument("--IDCol", dest="IDCol", default=3, required=False, help="ID column index", type=int)
    parser.add_argument("--PvalueCol", dest="PvalueCol", default=[12, ], required=False, help="Pvalue column index will apply FDR at this col，并且请注意指定P值是LOG10P还是其他的；请按照这个规范 --PvalueCol 12 P", nargs="+",type=int)
    parser.add_argument("-P", dest="P",  required=False, help="传入的Pvalue列是LOG10P还是P，-P 表面是非LOG10P，默认是LOG10P", action="store_true")

    return parser

def inFilterList(string, filterList):
    if isinstance(filterList, str):
        filterList = [filterList]
    for each in filterList:
        if each in string:
            return True
    return False 


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    filePath = args.filePath
    outFilePath = args.outFilePath
    SYMBOL = args.SYMBOL
    consequence = args.consequence
    pvalue_cutoff = args.pvalue_cutoff
    IDCol = args.IDCol
    PvalueColList = args.PvalueCol
    P = args.P

    if P:
        LOG10P=False
    else:
        LOG10P=True

    print(f"输入文件：{filePath}")
    print(f"输出文件：{outFilePath}")
    print(f"过滤consequence：{consequence}")
    print(f"过滤GENESYMBOL：{SYMBOL}")
    print(f"过滤Pvalue：{pvalue_cutoff}")
    print(f"ID列：{IDCol}")
    print(f"Pvalue列：{PvalueColList}")
    print(f"是否是LOG10P：{LOG10P}")


    vep = pd.read_csv(filePath, sep="\s+")
    IDCol = vep.columns[IDCol-1]
    PvalueColList = [vep.columns[i-1] for i in PvalueColList]

    keep_consequence = [i for i in vep["Consequence"].unique() if not inFilterList(i,consequence)]

    # step1 filter consequence
    print(f"去除这些consequence: {','.join(consequence)}")
    print(f"原始有{vep.shape[0]}行")
    vep = vep[vep["Consequence"].apply(lambda x: str(x) in keep_consequence)] # turn NA => "NA"
    print(f"过滤后有{vep.shape[0]}行")
    # step2 保留GENESYMBOL对应的数据
    if SYMBOL:
        vep = vep[vep["SYMBOL"].apply(lambda x : inFilterList(str(x), SYMBOL))]
        print(f"保留GENESYMBOL：{SYMBOL}后还有{vep.shape[0]}行")
    # step3 多重矫正
    variantsNum=len(vep[IDCol].unique())
    print(f"目前有{variantsNum}个变异")
    FDRCUTOFF = 0.05/variantsNum
    print(f"FDRCUTOFF: {FDRCUTOFF}")
    print(f"过滤前有{vep.shape[0]}行")

    # TODO：保存所有的变异，但是给他们加上一列表示是否通过了FDR
    if LOG10P:# LOG10P > FDRCUTOFF
        FDRCUTOFF = -np.log10(FDRCUTOFF)
        vep=vep[(vep[PvalueColList] > FDRCUTOFF).all(axis=1)]
        
    else:# Pvalue < FDRCUTOFF; 
        vep=vep[(vep[PvalueColList] < FDRCUTOFF).all(axis=1)]
    print(f"过滤后有{vep.shape[0]}行")

    vep.to_csv(outFilePath, sep="\t", index=False, na_rep="NA")
