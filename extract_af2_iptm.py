#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import os
import os.path as osp
import json
import pandas as pd


def getParser():
    parser = argparse.ArgumentParser(
        description=f"extract iptm+ptm from af2 path，"
    )

    parser.add_argument(
        "-i",
        "--input",
        dest="dataPath",
        type=str,
        required=True,
        help="要提取的iptm+ptm 所处的af输出文件的目录，该路径下需包含所有要提取的af2输出文件夹",
    )  # this will

    parser.add_argument("-o", "--output", dest="output_csv",
                        type=str, required=True, default="output.csv", help="输出保存目录")

    return parser


def extract(path):
    ranking_path = osp.join(path, "ranking_debug.json")
    data = {}
    data["label"] = osp.splitext(osp.split(path)[1])[0]
    if os.path.exists(ranking_path):

        data["iptm+ptm"] = list(sorted([v for k, v in json.load(open(ranking_path))[
                                "iptm+ptm"].items()], reverse=True))[0]  # 只提取最优的iptm

    return data


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    afPath = args.dataPath
    outputPath = args.output_csv

    data = [extract(osp.join(afPath, i)) for i in os.listdir(afPath)]
    output = pd.DataFrame(data)
    # print(output)
    output.to_csv(outputPath, index=False)
