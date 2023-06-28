#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import textwrap
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog is ....
        @Author: xutingfeng@big.ac.cn
        Version: 1.0
        Example:
        1.读入gwas meta数据，./compare.py --file _apob.regenie.gz regenie apob.bgen.stats.gz bolt --gzip
        2.指定标题：./compare.py --file _apob.regenie.gz regenie apob.bgen.stats.gz bolt --gzip -o regenie_vs_bolt_apob 
        ...

        """
        ),
    )
    parser.add_argument(
        "--file", nargs="+", help="Input files and types like: --file A regenie B bolt "
    )

    parser.add_argument(
        "-o",
        "--output",
        default="compareGWAS.png",
        dest="output",
        help="output file, default compareWGAS.png, should specific name without suffix",
    )
    parser.add_argument("--xlabel", dest="xlabel", help="xlabel")
    parser.add_argument("--ylabel", dest="ylabel", help="ylabel")
    parser.add_argument("--gzip", dest="gzip", help="gzip file", action="store_true")
    parser.add_argument("--resetID", dest="reset", help="resetID", action="store_true")
    parser.add_argument("-s", dest="s",help="scatter dot size", default=4, type=float)
    return parser


def resetSNP(x, ID="SNP", pos="BP"):
    # print(x)
    o = x[ID].split(":")
    o[1] = x[pos]
    o = [str(i) for i in o]
    return ":".join(o)


def load_bolt(boltPath, compression, sep, resetID=False, **kwargs):
    if compression:
        bolt = pd.read_csv(boltPath, compression="gzip", sep=sep)
    else:
        bolt = pd.read_csv(boltPath, sep=sep)
    if resetID:
        bolt["SNP"] = bolt.apply(resetSNP, axis=1)

    bolt["bolt_lmm"] = -np.log10(bolt["P_BOLT_LMM"])
    bolt.rename(columns={"SNP": "ID", "A1FREQ": "bolt_A1FREQ"}, inplace=True)
    return bolt[["ID", "bolt_lmm", "bolt_A1FREQ"]]


def load_regenie(regeniePath, compression, sep, **kwargs):
    if compression:
        regenie = pd.read_csv(regeniePath, compression="gzip", sep=sep)
    else:
        regenie = pd.read_csv(regeniePath, sep=sep)
    regenie = regenie[["ID", "LOG10P", "A1FREQ"]].rename(
        columns={"LOG10P": "regenie", "A1FREQ": "regenie_A1FREQ"}
    )  # "ID" is the SNP ID, "LOG10P" is the p-value, "A1FREQ" is the frequency of the effect allele

    return regenie


def load_gwas_meta(filePath, type, compression, sep, **kwargs):
    if type == "bolt_lmm":
        return load_bolt(filePath, compression, sep, **kwargs)
    elif type == "regenie":
        return load_regenie(filePath, compression, sep, **kwargs)
    else:
        raise ValueError("type must be bolt_lmm or regenie")


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    files = args.file
    sep = "\s+"
    gzip = args.gzip
    output = args.output
    resetID = args.reset
    xlabel = args.xlabel
    ylabel = args.ylabel
    s = args.s
    num_files = len(files)
    if num_files % 2 != 0:
        parser.error("每个文件需要指定一个类型")

    outputList = []
    for i in range(0, num_files, 2):
        filePath = files[i]
        file_type = files[i + 1]
        outputList.append(
            load_gwas_meta(
                filePath=filePath,
                type=file_type,
                compression=gzip,
                sep=sep,
                resetID=resetID,
            )
        )
        print(f"load {filePath} as {file_type}")

    compare = outputList[0].merge(outputList[1], on="ID")

    # columns should be ID file1 file1_A1FREQ file2 file2_A1FREQ....
    axisList = [compare.columns[i] for i in range(1, len(compare.columns), 2)]
    print(f"用于绘图的点有：{compare.shape[0]}")
    # # plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    sns.scatterplot(
        data=compare,
        x=f"{axisList[0]}",
        y=f"{axisList[1]}",
        hue=compare.columns[2],
        s=s,
        ax=ax,zorder=2
    )
    ax.plot(ax.get_xlim(), ax.get_ylim(), "--c", zorder=1)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    fig.savefig(f"{output}.png", dpi=400)
    fig.clf()
