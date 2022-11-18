#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  输入PDB文件所在的目录
#  输出对应的PDB文件的序列以及二级结构的.txt文件到指定目录

import os
import os.path as osp
import re
from multiprocessing import Pool
import argparse
import pandas as pd
from Bio.PDB import PDBParser
from Bio.PDB.DSSP import DSSP
from functools import partial

ALPHAFOLD_PATTERN = r"(?<=AF-)[^-]*(?=-)"


def get_uacc_from_af2(af2_Filename):
    return re.search(ALPHAFOLD_PATTERN, af2_Filename).group()


def parse_protein_name_from_filename(filePath):
    root_path, fileName = osp.split(filePath)
    fileName, file_suffix = osp.splitext(fileName)

    if re.search(ALPHAFOLD_PATTERN, fileName):
        return get_uacc_from_af2(fileName)
    else:
        return fileName


def sec_structure_fromPDB(pdb):
    #  解析PDBfile
    p = PDBParser()
    structure = p.get_structure(parse_protein_name_from_filename(pdb), pdb)
    #  获取PDBfile中第一个结构，如果有多个的时候取第一个
    model = structure[0]
    dssp = DSSP(model, pdb, dssp="mkdssp")
    #  获得二级结构序列
    sequence = ""
    sec_structure = ""

    for property in dssp.property_list:
        sequence += property[1]
        sec_structure += property[2]

    assert len(sequence) == len(sec_structure)

    return sequence, sec_structure


def save_sec_structure(raw_sequence, sec_structure, filename):
    with open(filename, "w") as f:
        f.write(raw_sequence + "\n")
        f.write(sec_structure)
    print(f"saveing to {filename}")


def main(pdb, file_path):
    raw, sec = sec_structure_fromPDB(os.path.join(file_path, pdb))
    # save_sec_structure(raw, sec, os.path.join(save_path, pdb.split(".")[0]+".txt"))
    return {
        "name": parse_protein_name_from_filename(pdb),
        "primary sequence": raw,
        "secondary structure": sec,
    }


def multiprocessing_map(func, iter_list, processes=5):
    pool = Pool(processes)
    res = pool.map(func, iter_list)
    return res


def getParser():
    parser = argparse.ArgumentParser(
        description="""
        pdb to dssp info by dssp at biopython api
        more about dssp:https://swift.cmbi.umcn.nl/gv/dssp/
        more abount biopython:https://biopython.org/
        """
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        help="PDB folder",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="dssp save to ",
    )
    parser.add_argument(
        "-p", "--processes", type=int, dest="processes", help="processes used in this"
    )
    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output
    processes = args.processes

    tmp_func = partial(main, file_path=input_dir)
    print(tmp_func)
    # res = multiprocessing_map(tmp_func, os.listdir(input_dir), processes=args.processes)
    # pd.DataFrame(res).to_csv(output_dir, sep="\t", index=False)
