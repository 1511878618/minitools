#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/

see more about this tab_delimited file at:https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/README
"""
import argparse
import os.path as osp
import re
import warnings
from functools import partial
from itertools import chain
from typing import List

import pandas as pd

warnings.filterwarnings("ignore")


def flatten_list(x: list):
    return list(chain.from_iterable(x))


def strip_comment_head(
    df: pd.DataFrame, comment: str = "#", inplace: bool = True
) -> pd.DataFrame:
    """去除header列可能存在的注释符号，如：#accession .... ，这里#可以是任意的comment符号

    Args:
        df (_type_): _description_
        comment (str, optional): _description_. Defaults to "#".
        inplace (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    if comment in df.columns[0]:  # type: ignore
        if inplace:
            df.rename(
                columns={
                    df.columns[0]: re.split(f"{comment}" + r"[\s]*", df.columns[0])[-1]  # type: ignore
                },
                inplace=True,
            )
        else:
            return df.rename(
                columns={
                    df.columns[0]: re.split(f"{comment}" + r"[\s]*", df.columns[0])[-1]  # type: ignore
                },
                inplace=False,
            )
    else:
        return df


def splitName2Attribution(x):
    """
    splitName2Attribution HGSV 命名法：https://varnomen.hgvs.org/recommendations/general/
    refSeq:https://en.wikipedia.org/wiki/RefSeq#:~:text=The%20Reference%20Sequence%20(RefSeq)%20database,was%20first%20introduced%20in%202000.

    Args:
        str类型: "NM_017547.4(FOXRED1):c.694C>T (p.Gln232Ter)"

    Returns:
        ["NM_017547.4", "Gln232Ter","694C>T"]
    """
    ref_pattern = r"[A-Za-z]+_[0-9]+[\.]*[0-9]*"
    AAS_pattern = r"(?<=(p.))[A-Za-z]{0,3}[^\s()]*"
    SNP_pattern = r"(?<=(c.))[\d]*[^\s()]*"
    ref = re.search(ref_pattern, x).group() if re.search(ref_pattern, x) else None  # type: ignore
    AAS = re.search(AAS_pattern, x).group() if re.search(AAS_pattern, x) else None  # type: ignore
    SNP = re.search(SNP_pattern, x).group() if re.search(SNP_pattern, x) else None  # type: ignore
    return ref, AAS, SNP


def keep_nsSNP(clinvar_variant_summary_snp: pd.DataFrame, subset: str = "Name"):
    """keep nsSNP from clinvar variant summary file, subset is the column of HGVS, it should be Name columns, check https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/README for more.

    Returns:
        pd.DataFrame: nsSNP
    """
    clinvar_variant_summary_snp = clinvar_variant_summary_snp.dropna(
        axis=0, subset=[subset]
    )  # remove NA at Name column

    #  get HGVS of SAV at Name, remove NA entry at AAS
    tmp = clinvar_variant_summary_snp[subset].apply(lambda x: splitName2Attribution(x))
    clinvar_variant_summary_snp["ref_seq"] = tmp.apply(lambda x: x[0])
    clinvar_variant_summary_snp["AAS"] = tmp.apply(lambda x: x[1])
    clinvar_variant_summary_snp["SNP"] = tmp.apply(lambda x: x[2])

    clinvar_variant_summary_snp = clinvar_variant_summary_snp[
        ~clinvar_variant_summary_snp["AAS"].isna()
    ]
    #  remove synonymous SNP from data
    clinvar_variant_summary_sav: pd.DataFrame = clinvar_variant_summary_snp[
        ~clinvar_variant_summary_snp["AAS"].apply(lambda x: "=" in x)
    ]

    del clinvar_variant_summary_sav["ref_seq"]
    del clinvar_variant_summary_sav["AAS"]
    del clinvar_variant_summary_sav["SNP"]

    return clinvar_variant_summary_sav.reset_index(drop=True)


def keep_clinicalsignificance(clinvar_variant_summary: pd.DataFrame, fields: List):
    """keep SNV, if SNV's ClinicalSignificance in fields

    Args:
        clinvar_variant_summary (pd.DataFrame): _description_
        fields (List): list of ClinicalSignificance
    Return:
        filtered clinvar_variant_summary
    """

    def filter_func(x: str, fields: List):
        x = str.lower(x)
        if x in fields:
            return True
        else:
            return False

    if isinstance(fields, str):
        fields = [fields]

    fields = [str.lower(i) for i in fields]
    func = partial(filter_func, fields=fields)

    return clinvar_variant_summary[
        clinvar_variant_summary["ClinicalSignificance"].apply(func)
    ].reset_index(drop=True)


def getParser():
    parser = argparse.ArgumentParser(
        description="""analysis clinvar data from https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/
        default: clinvar variant summary data, not complemnt for vcf.

        Now what user can do is:
        1. keep nsSNP from Assembly(user can specific)
        2. keep ClinicalSAignificance of specific, more see at https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/README
        """
    )
    parser.add_argument(
        "-i",
        dest="input_dir",
        required=True,
        help="clinvar_variant_summary_dir",
        type=str,
    )
    parser.add_argument(
        "--assembly",
        dest="assembly",
        default="37",
        type=str,
        help="37->GRCh37\n 38->GRCh38",
    )
    parser.add_argument(
        "--fields",
        dest="fields",
        action="append",
        nargs="+",
        help="fileds should be in:'Uncertain significance, Pathogenic, Likely pathogenic, Conflicting interpretations of pathogenicity, Likely benign, not provided, Benign, Benign/Likely benign, Pathogenic/Likely pathogenic, other, -, risk factor, drug response, Pathogenic, other, Affects, Pathogenic, risk factor, Conflicting interpretations of pathogenicity, risk factor, association, protective, Pathogenic, drug response, Benign, risk factor, Uncertain significance, risk factor, Benign/Likely benign, risk factor, Pathogenic/Likely pathogenic, risk factor, Uncertain significance, other, Conflicting interpretations of pathogenicity, other, Likely benign, risk factor, Likely pathogenic, risk factor, Uncertain significance, drug response, Likely benign, other, Pathogenic/Likely pathogenic, other, Likely pathogenic, drug response, Benign, other, Benign/Likely benign, other, Pathogenic, Affects, Benign, association, Conflicting interpretations of pathogenicity, drug response, Likely pathogenic, other, Pathogenic, protective, Pathogenic/Likely pathogenic, drug response, Benign/Likely benign, protective, Benign, protective, Conflicting interpretations of pathogenicity, Affects, Conflicting interpretations of pathogenicity, association, drug response, other, Conflicting interpretations of pathogenicity, Affects, association, risk factor, Pathogenic, other, protective, association, risk factor, Uncertain significance, association, Pathogenic, association, Conflicting interpretations of pathogenicity, association, other, risk factor, protective, risk factor, Benign/Likely benign, Affects, Benign/Likely benign, association, Likely benign, association, Conflicting interpretations of pathogenicity, Affects, other, Uncertain significance, Affects, Conflicting interpretations of pathogenicity, protective, Benign, Affects, Conflicting interpretations of pathogenicity, other, risk factor, Likely pathogenic, association, Likely benign, drug response, Pathogenic, protective, risk factor, Likely pathogenic, Affects, Benign, protective, risk factor, Benign, association, risk factor, Benign, drug response, risk factor, Benign, drug response, association, protective, Benign/Likely benign, protective, risk factor, Uncertain significance, protective, Pathogenic/Likely pathogenic, Affects, risk factor, Benign/Likely benign, drug response, risk factor, Benign, association, protective, Likely benign, Affects, Likely benign, protective",
    )
    parser.add_argument(
        "--out",
        dest="output",
        default="clinvar_summary_variant_filter.txt",
        help="output prefix",
    )
    parser.add_argument(
        "--gzip", dest="gzip", action="store_true", help="gzip compress at the output"
    )
    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    clinvar_variant_summary_dir = args.input_dir
    assembly = args.assembly
    fields = flatten_list(args.fields)
    is_gzip_compress = args.gzip
    output_dir = args.output

    if assembly == "37":
        assembly = "GRCh37"
    elif assembly == "38":
        assembly = "GRCh38"
    else:
        raise ValueError(f"{assembly} not in 37 or 38")

    if osp.splitext(clinvar_variant_summary_dir)[-1] in ["gzip", "gz"]:
        clinvar_variant_summary = pd.read_csv(
            clinvar_variant_summary_dir, sep="\t", compression="gzip"
        )
    else:
        clinvar_variant_summary = pd.read_csv(clinvar_variant_summary_dir, sep="\t")

    clinvar_variant_summary = strip_comment_head(clinvar_variant_summary, inplace=False)
    print(f"loading clinvar data with shape:{clinvar_variant_summary.shape}")
    # keep Assembly
    clinvar_variant_summary = clinvar_variant_summary[
        clinvar_variant_summary["Assembly"] == assembly
    ]
    print(f"keep assembly from {assembly}, output is {clinvar_variant_summary.shape}")

    # keep SNP
    clinvar_variant_summary_snp = clinvar_variant_summary[
        clinvar_variant_summary["Type"] == "single nucleotide variant"
    ]
    print(f"keep SNP and the output is {clinvar_variant_summary_snp.shape}")

    # keep nsSNP
    clinvar_variant_summary_snp = keep_nsSNP(clinvar_variant_summary_snp)
    print(f"keep nsSNP and the output is {clinvar_variant_summary_snp.shape}")

    # keep fields

    clinvar_filter_fields_variant_summary_snp = keep_clinicalsignificance(
        clinvar_variant_summary=clinvar_variant_summary_snp, fields=fields
    )
    print(
        f"keep {', '.join(fields)} and the output is {clinvar_filter_fields_variant_summary_snp.shape}"
    )
    if is_gzip_compress:
        output_dir = output_dir + "txt.gz"
        clinvar_filter_fields_variant_summary_snp.to_csv(
            output_dir, sep="\t", index=False, compression="gzip"
        )
    else:
        clinvar_filter_fields_variant_summary_snp.to_csv(
            output_dir + "txt", sep="\t", index=False
        )
