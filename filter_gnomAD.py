#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
仅仅过滤gnomAD中，VEP注释包含：
1）CANONICAL=YES
2) HGVSp存在且不为=，即错义突变（包括Ter突变）
"""


from pkg_resources import require
import vcfpy

from proture.prepare.dataset.Vcf import VEP_PARSER
from proture.prepare.mutation.utils import is_missense_mutant_at_HGVSp
import argparse


def getParser():
    parser = argparse.ArgumentParser(description="filter gnomAD")

    parser.add_argument("-i", "--input", dest="gnomAD_dir", type=str, help="gnomAD dir")

    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        type=str,
        default="UniProt_mapping.csv",
        help="output file dir, if end with .gz, will use bgzf.",
    )

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    gnomAD_path = args.gnomAD_dir

    output_dir = args.output_dir

    reader = vcfpy.Reader.from_path(gnomAD_path)
    writer = vcfpy.Writer.from_path(output_dir, reader.header)

    vep_parser = VEP_PARSER(reader.header.get_info_field_info("vep"))

    for record in reader:
        if vep_filter := vep_parser.filter(
            lambda x: is_missense_mutant_at_HGVSp(x["HGVSp"]) and x["CANONICAL"] != "",
            record.INFO["vep"],
            how="all",
        ):
            # print([vep_parser.apply(i)["HGVSp"] for i in vep_filter])
            record.INFO["vep"] = vep_filter
            writer.write_record(record)
