#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date     :2023/08/23 22:08:39
@Author      :Tingfeng Xu
@version      :1.0
'''


import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal
import math

warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog GWAS format standardization tool for formated to regenie
        @Author: xutingfeng@big.ac.cn

        GWAS SSF: https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1
        GWAS Standard

        Version: 1.0
        


        """
        ),
    )
    parser.add_argument(
        "--pval",
        dest="pval",
        help="turn pval to log10p",
        action="store_true",
        required=False,
    )
    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    # see gwas-ssf_v1.0.0.pdf: https://github.com/EBISPOT/gwas-summary-statistics-standard

    # parse args
    needTurnToLog10p = args.pval


    fields_dict = {
        "CHROM": 1,
        "GENPOS": 2,
        "ID": 12,
        "ALLELE0": 4,
        "ALLELE1": 3,
        "A1FREQ": 7,
        "N": 15,
        "TEST": None,
        "BETA": 5,
        "SE": 6,
        "CHISQ": None,
        "LOG10P": 8,
        "EXTRA": None,
    }
    # CHROM GENPOS ID ALLELE0 ALLELE1 A1FREQ N TEST BETA SE CHISQ LOG10P EXTRA

    line_idx = 1
    for line in sys.stdin:
        line = line.strip()  # remove \n
        ss = line.split()

        if line_idx == 1:
            # get user specified column index
            formated_ss = [k for k in fields_dict.keys()]
        else:
            formated_ss = []
            for key, key_idx in fields_dict.items():
                if key_idx is not None:
                    if key == "LOG10P":
                        if needTurnToLog10p:
                            new_value = -1 * math.log10(float(ss[key_idx - 1]))
                    new_value = ss[key_idx - 1]
                    
                else:
                    new_value = "NA"

                formated_ss.append(new_value)

        formated_ss = "\t".join(formated_ss)  # \t delimter

        sys.stdout.write(f"{formated_ss}\n")
        line_idx += 1


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
