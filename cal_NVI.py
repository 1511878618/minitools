#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
from Bio import AlignIO
import numpy as np
import pandas as pd 

RNase_align = AlignIO.read("RNase.fas", format="fasta")
SLF_align = AlignIO.read("SLF.fas", format="fasta")

data = pd.DataFrame([list(str(i.seq)) for i in RNase_align])


def cal_NVI(col):
    col_without_gap = col[col != "-"]

    diff_aa_num = len(col_without_gap.unique())
    max_aa_freq = max(col_without_gap.value_counts())
    length_col = len(col_without_gap)

    NVI = np.log(diff_aa_num / max_aa_freq) / np.log(length_col)
    return NVI


NVI_data = data.apply(cal_NVI, axis=0)

def getParser():
    parser = argparse.ArgumentParser(
        description=f"cal NVI"
    )

    parser.add_argument(
        "-i",
        "--input",
        dest="dataPath",
        type=str,
        required=True,
        help="prodigy input folder",
    )  #  this will

    parser.add_argument("-o", "--output", dest="output_csv", type=str, required=True)
    parser.add_argument("-s", "--suffix", dest="suffix", type=str, default=".txt")

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    prodigy_output_filepath = args.prodigy_output_filepath
    print(f"now using folder is {prodigy_output_filepath}")
    output_csv = args.output_csv
    print(f"sorted result will be in a csv file, location is {output_csv}")
    suffix = args.suffix
    print(f"suffix of prodigy file is {suffix}")

    prodigy_list = [
        read_prodigy_txt(osp.join(prodigy_output_filepath, file))
        for file in os.listdir(prodigy_output_filepath)
        if file.endswith(suffix)
    ]
    # prodigy_list.sort(
    #     key=lambda x: list(x.values())[0][
    #         "[++] Predicted binding affinity (kcal.mol-1)"
    #     ],
    #     reverse=True,
    # )
    # print(pd.DataFrame(prodigy_list[0]).T.columns)
    out = pd.DataFrame(prodigy_list)
    out.to_csv(
        output_csv, index=False
    )
