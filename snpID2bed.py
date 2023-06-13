#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal

# need to change a lot !


warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog snpID chr:pos:ref:alt => chr start end ref alt columns
        @Author:xutingfeng@big.ac.cn 

        Version: 1.0


        Example
        1. with header and snpID is chr:pos:ref:alt, col sep is white space
            --------------------------------------------------------------------------------------
            SNP     CHR     BP      GENPOS  ALLELE1 ALLELE0 A1FREQ  INFO    CHISQ_LINREG    P_LINREG        BETA    SE      CHISQ_BOLT_LMM_INF    P_BOLT_LMM_INF  CHISQ_BOLT_LMM  P_BOLT_LMM
            1:108274969:T:C 1       108274969       0       C       T       0.0442549       1       3.48143 6.2E-02 0.011646        0.0062442     3.47857 6.2E-02 3.47861 6.2E-02
            1:108274984:A:T 1       108274984       0       T       A       0.000147941     1       0.10202 7.5E-01 0.0372084       0.11680.101484        7.5E-01 0.101477        7.5E-01
            --------------------------------------------------------------------------------------
            General code could be like this: zcat ldl_a.bgen.stats.gz| snpID2bed.py -i 1  > ldl_a.bgen.stats.bed
            -i 1 will specifiy the first column as ID column and will generate output like this:
            --------------------------------------------------------------------------------------
            chr     start   end     ref     alt     SNP     CHR     BP      GENPOS  ALLELE1 ALLELE0 A1FREQ  INFO    CHISQ_LINREG    P_LINREG      BETA    SE      CHISQ_BOLT_LMM_INF      P_BOLT_LMM_INF  CHISQ_BOLT_LMM  P_BOLT_LMM
            chr1 108274969 108274969 T C 1:108274969:T:C 1 108274969 0 C T 0.0442549 1 3.48143 6.2E-02 0.011646 0.0062442 3.47857 6.2E-02 3.47861 6.2E-02
            chr1 108274984 108274984 A T 1:108274984:A:T 1 108274984 0 T A 0.000147941 1 0.10202 7.5E-01 0.0372084 0.1168 0.101484 7.5E-01 0.101477 7.5E-01
            --------------------------------------------------------------------------------------
            if add --no-chr, output will be like this:
            --------------------------------------------------------------------------------------
            chr     start   end     ref     alt     SNP     CHR     BP      GENPOS  ALLELE1 ALLELE0 A1FREQ  INFO    CHISQ_LINREG    P_LINREG      BETA    SE      CHISQ_BOLT_LMM_INF      P_BOLT_LMM_INF  CHISQ_BOLT_LMM  P_BOLT_LMM
            1 108274969 108274969 T C 1:108274969:T:C 1 108274969 0 C T 0.0442549 1 3.48143 6.2E-02 0.011646 0.0062442 3.47857 6.2E-02 3.47861 6.2E-02
            1 108274984 108274984 A T 1:108274984:A:T 1 108274984 0 T A 0.000147941 1 0.10202 7.5E-01 0.0372084 0.1168 0.101484 7.5E-01 0.101477 7.5E-01


        2.  without header and snpID is chr:pos:ref:alt, col sep is white space
            --------------------------------------------------------------------------------------
            1:108274969:T:C 1       108274969       0       C       T       0.0442549       1       3.48143 6.2E-02 0.011646        0.0062442     3.47857 6.2E-02 3.47861 6.2E-02
            1:108274984:A:T 1       108274984       0       T       A       0.000147941     1       0.10202 7.5E-01 0.0372084       0.11680.101484        7.5E-01 0.101477        7.5E-01
            --------------------------------------------------------------------------------------
            --no-header should be specified if input file has no header
            General code could be like this: zcat ldl_a.bgen.stats.gz| snpID2bed.py -i 1 --no-header > ldl_a.bgen.stats.bed
            -i 1 will specifiy the first column as ID column and will generate output like this:
            --------------------------------------------------------------------------------------
            chr1 108274969 108274969 T C 1:108274969:T:C 1 108274969 0 C T 0.0442549 1 3.48143 6.2E-02 0.011646 0.0062442 3.47857 6.2E-02 3.47861 6.2E-02
            chr1 108274984 108274984 A T 1:108274984:A:T 1 108274984 0 T A 0.000147941 1 0.10202 7.5E-01 0.0372084 0.1168 0.101484 7.5E-01 0.101477 7.5E-01
            chr1 108275002 108275002 C T 1:108275002:C:T 1 108275002 0 T C 4.40473e-05 1 0.912245 3.4E-01 -0.205487 0.215339 0.910592 3.4E-01 0.910551 3.4E-01
            --------------------------------------------------------------------------------------
            if add --no-chr, output will be like this:
            1 108274969 108274969 T C 1:108274969:T:C 1 108274969 0 C T 0.0442549 1 3.48143 6.2E-02 0.011646 0.0062442 3.47857 6.2E-02 3.47861 6.2E-02
            1 108274984 108274984 A T 1:108274984:A:T 1 108274984 0 T A 0.000147941 1 0.10202 7.5E-01 0.0372084 0.1168 0.101484 7.5E-01 0.101477 7.5E-01
            1 108275002 108275002 C T 1:108275002:C:T 1 108275002 0 T C 4.40473e-05 1 0.912245 3.4E-01 -0.205487 0.215339 0.910592 3.4E-01 0.910551 3.4E-01
        """
        ),
    )

    parser.add_argument(
        "-i", "--id-col", dest="idCol", type=int, default=1, help="ID column index."
    )
    parser.add_argument(
        "-s",
        "--id-sep",
        dest="idSep",
        type=str,
        default=":",
        help="ID separator. Default: ':' and ID col should be: chr:pos:ref:alt or chr:pos:alt:ref",
    )
    parser.add_argument(
        "-c",
        "--col-sep",
        dest="colSep",
        type=str,
        default=None,
        help="Column separator. Default: None, use white space.",
    )
    parser.add_argument(
        "--no-chr",dest="nochr",action="store_true",default=False,help="Remove 'chr' prefix in chromosome name."
    )
    parser.add_argument("--no-header", dest="noheader", action="store_true", default=False, help="No header in input file.")
    # parser.add_argument()
    return parser


def formatChr(x):
    if x.startswith("chr"):
        return x
    elif x.isdigit():
        if int(x) < 23:
            return "chr" + str(int(x))
        else:
            if x == "23":
                return "chrX"
            elif x == "24":
                return "chrY"
            elif x == "25":
                return "chrX"
            elif x == "26":
                return "chrMT"
    else:
        return x


def reformat(line, idCol=1, idSep=":", colSep=None, nochr=False):
    lineList = line.split(colSep)
    idList = lineList[idCol - 1].split(idSep)
    if not nochr: 
        idList[0] = formatChr(idList[0])

    if colSep is None:
        colSep = " "
    return colSep.join([idList[0], idList[1], idList[1], idList[2], idList[3]] + lineList)


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    idCol = args.idCol
    idSep = args.idSep
    colSep = args.colSep
    nochr = args.nochr

    idx = 1 # count for header 
    for line in sys.stdin:
        line = line.strip()
        if line:
            if idx == 1:  # header line
                if not args.noheader: # defualt have header 
                    sys.stdout.write("chr\tstart\tend\tref\talt\t" + line + "\n")
                    idx +=1
                    continue 
            ss = reformat(line, idCol, idSep, colSep, nochr)
            sys.stdout.write(ss + "\n")
            idx +=1


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
