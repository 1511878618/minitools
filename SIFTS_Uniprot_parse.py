#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import os.path as osp
from itertools import chain
from multiprocessing import Pool

import pandas as pd


def flatten_list(x: list):
    return list(chain.from_iterable(x))


def getParser():
    parser = argparse.ArgumentParser(
        description="parse SIFTS API output json at https://www.ebi.ac.uk/pdbe/api/doc/sifts.html, extract UniProt mapping results from SIFTS Mappings to a csv file of all results"
    )
    parser.add_argument(
        "-i",
        "--files",
        dest="files",
        required=False,
        help="json files",
        action="append",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "-f",
        "--fold",
        dest="folder",
        required=False,
        help="specific a folder of json files, conflict with -i",
        default=None,
    )
    parser.add_argument(
        "-o", "--output", dest="output_dir", type=str, default="UniProt_mapping.csv"
    )
    parser.add_argument(
        "-p", "--processes", dest="processes", type=int, help="processes num", default=4
    )
    parser.add_argument(
        "-l",
        "--log",
        dest="log_file",
        default="SIFTS_Uniprot_parse.log",
        help="log file path",
    )
    return parser


def load_json(filepath: str):
    """
    load_json load json file

    Args:
        filepath (str): _description_

    Returns:
        Dict: python dict of json
    """
    with open(filepath, "r") as f:
        return json.loads(f.read())


def parse_SIFTSMapping_json(filepath: str):
    SIFTS_output_JSON_path = filepath

    SIFTS_json = load_json(SIFTS_output_JSON_path)

    accession = list(SIFTS_json.keys())[0]

    UniProt_json = SIFTS_json[accession]["UniProt"]

    if not UniProt_json:
        # return pd.DataFrame({"UniProt Accession":[accession]})
        return pd.DataFrame()
        # exit()
    UniProt_Accession = list(UniProt_json.keys())[0]

    UniProt_Accession_mapping_df = pd.json_normalize(UniProt_json[UniProt_Accession])
    UniProt_Accession_mapping_df.insert(0, column="PDB Accession", value=accession)
    UniProt_Accession_mapping_df.insert(
        0, column="UniProt Accession", value=UniProt_Accession
    )

    mapping_result = UniProt_Accession_mapping_df.pop("mappings")

    mapping_df = pd.concat(
        [pd.json_normalize(json_text) for idx, json_text in mapping_result.items()]
    )
    mapping_df.reset_index(drop=True, inplace=True)

    if len(mapping_df) > 1:
        logging.debug(f"{UniProt_Accession} have {len(mapping_result)}")

        UniProt_Accession_mapping_df = pd.concat(
            [UniProt_Accession_mapping_df] * len(mapping_df)
        ).reset_index(drop=True)

    return pd.merge(
        left=UniProt_Accession_mapping_df,
        right=mapping_df,
        left_index=True,
        right_index=True,
        how="right",
    )


def multiprocessing_map(func, iter_list, processes=5):
    pool = Pool(processes)
    res = pool.map(func, iter_list)
    return res


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    log_file_path = args.log_file
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    files = args.files
    folder = args.folder

    if folder and files is None:
        files = [osp.join(folder, i) for i in os.listdir(folder) if i.endswith(".json")]
    elif files and folder is None:
        files = flatten_list(args.files)
    elif files is None and folder is None:
        raise TypeError(f"at least -i or -f")

    output_dir = args.output_dir
    processes = args.processes
    # print(files)

    result = multiprocessing_map(parse_SIFTSMapping_json, files, processes=processes)

    pd.concat(result).to_csv(output_dir, sep="\t")
