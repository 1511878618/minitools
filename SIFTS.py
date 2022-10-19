#!/usr/bin/env python
# -*-coding:utf-8 -*-

import argparse
import json
from os import access
from time import sleep
import os.path as osp
import requests


def get_SIFTS(accession, fields="all"):
    if fields=="all":
        base_url = "https://www.ebi.ac.uk/pdbe/api/mappings/"
    else:
        raise NotImplementedError
    url = base_url+accession
    print(url)
    callback = requests.get(base_url+accession)

    if callback.status_code != 200:
        raise ValueError(f"failed to get {accession} from SIFTS, HTTP status :{callback.status_code}")

    return callback.json()
def save_json(python_dict, save_dir):
    with open(save_dir, "w") as f:
        f.write(json.dumps(python_dict))


def getParser():
    parser = argparse.ArgumentParser(description="Mappings (as assigned by the SIFTS process) from PDB structures to UniProt, Pfam, InterPro, CATH, SCOP, IntEnz, GO, Ensembl and HMMER accessions (and vice versa).")
    parser.add_argument("-i", "--accession", dest="accession", type=str, required=True, help="PDB id-code OR UniProt accession code OR Pfam accession code OR Interpro accession code OR CATH cathcode OR SCOP sunid OR IntEnz EC code OR GO accession")
    parser.add_argument("-o", "--output", dest="output_dir", type=str, required=True)
    return parser

if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    
    accession = args.accession
    output_dir = osp.join(args.output_dir, f"{accession}.json")
    call_back_json = get_SIFTS(accession=accession, fields="all")
    
    print(f"Saving the result to {output_dir}")
    save_json(call_back_json, output_dir)
    sleep(0.1)
