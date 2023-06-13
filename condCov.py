#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os.path as osp
import argparse
import textwrap


def generateCovWithTagSNP(covPath, plink2EtractTagSNPGenoTypePath, outputRootDir):
    cov = pd.read_csv(covPath, sep="\s+")
    TagSNPs = pd.read_csv(plink2EtractTagSNPGenoTypePath, sep="\s+")

    TagSNPNum = TagSNPs.shape[1] - 6
    print(f"读入{TagSNPNum}个SNP")
    TagSNPName = TagSNPs.columns[6:].to_list()
    supplement = []
    for idx, currentTagSNPName in enumerate(TagSNPName):
        subdata = TagSNPs[["FID", "IID", currentTagSNPName]]
        covWithCurrentTagSNP = cov.merge(
            subdata, left_on=["FID", "IID"], right_on=["FID", "IID"]
        )
        covWithCurrentTagSNPOutputPath = osp.join(outputRootDir, f"tagSNP_{idx}.cov")
        covWithCurrentTagSNP.to_csv(covWithCurrentTagSNPOutputPath, index=False, sep=" ")

        supplement.append([currentTagSNPName, covWithCurrentTagSNPOutputPath])
        print(f"{currentTagSNPName}保存到{covWithCurrentTagSNPOutputPath}")

    with open(osp.join(outputRootDir, "sup.log"), "w") as f:
        for i in supplement:
            f.write(f"{i[0]}\t{i[1]}")


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        merge cov file at FID IID columns with file plink2 extract tagSNP file named targetFile by code: plink2 --pfile xxx --extract tagSNP.list --export A --out targetFile. Also a sup.log will record each tagSNP real ID => file.cov 
        Warning:
            1. current both file should be space delimeter 
            2. current tagSNP file should be have this columns: FID IID col1 col2 col3 col4 TagSNP1 TagSNP2.. so, default will start from 7 col to take it as tagSNP
        @Author: xutingfeng@big.ac.cn
        Version: 1.0
        Example file 
            cov file like below 
            -------------------------------------------------------------
            FID IID genotype_array inferred_sex age_visit PC1 PC2 PC3 PC4 PC5 PC6 PC7 PC8 PC9 PC10 assessment_center age_squared
            1000017 1000017 UKBL 1.0 56.0 -11.369 3.56718 -1.97553 0.213937 -12.4342 -1.69838 -0.0906869 -3.49819 4.7626 3.15321 11021 3136.0
            1000025 1000025 UKBB 1.0 62.0 -12.162 2.7747 0.175048 2.55493 8.75958 -0.0441244 -1.4973 0.0526797 0.276735 2.1188 11014 3844.0
            1000038 1000038 UKBL 1.0 60.0 -12.8698 6.41566 -5.1061 -1.29631 -6.34291 -2.93587 1.69063 -1.9321 3.71241 -0.0633382 11008 3600.0
            -------------------------------------------------------------

            targetFile like below 
            -------------------------------------------------------------
            FID     IID     PAT     MAT     SEX     PHENOTYPE       1:55505647:G:T_G        1:109817192:A:G_A       2:20410480:A:G_A        2:21288321:A:G_A   19:11196356:AC:A_AC     19:11910554:T:C_T
            -1      -1      0       0       0       -9      2       1       1       1       2       2
            -2      -2      0       0       0       -9      2       2       0       0       2       2
            -3      -3      0       0       0       -9      2       2       1       0       2       2


            """
        ),
    )

    parser.add_argument("-c", "--cov", dest="cov", help="cov file Path")
    parser.add_argument(
        "-t",
        "--cond",
        dest="cond",
        help="cond SNP ",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="output root dir",
    )
    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    covPath = args.cov
    tagSNPPath = args.cond
    output = args.output

    generateCovWithTagSNP(covPath, tagSNPPath, output)
