#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: Extract loci from summary file.       
@Date     :2023/08/21 21:47:37
@Author      :Tingfeng Xu
@version      :1.1
"""
import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal
import os.path as osp
DEFAULT_NA = "NA"

warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.


try:
    import pandas as pd
    import numpy as np 
except ImportError:
    print("缺少pandas模块，开始安装...")
    try:
        import pip 
        pip.main(["install", "pandas","numpy"])
        print("pandas模块安装完成。")
    except:
        print("安装pandas and numpy模块时出错。请手动安装pandas numpy。")
        sys.exit(1)


def get_loci(
    hits,
    pval_col="pval",
    pos_col="pos",
    chrom_col="chrom",
    min_peak_dist=2e6,
    min_pval=1e-6,
):
    hits_by_chrom = dict()
    for hit in hits:
        if hit[pval_col] < min_pval:
            hits_by_chrom.setdefault(hit[chrom_col], []).append(
                hit
            )  # defualt dict could do this

    for hits in hits_by_chrom.values():
        while hits:
            best_assoc = min(hits, key=lambda assoc: assoc[pval_col])
            yield best_assoc
            hits = [
                h for h in hits if abs(h[pos_col] - best_assoc[pos_col]) > min_peak_dist
            ]


def header_mapper(string, header_col):
    """
    Map a header string or index to a column index.

    Args:
        string (str or int): The header string or index to be mapped.
        header_col (list): The list of header strings.

    Returns:
        int or None: The mapped column index, or None if the input is None.

    Notes:
        - If the input string can be converted to an integer, it is treated as an index.
        - If the index is negative, it is treated as counting from the end of the list.
        - If the input is a string, it is treated as a header and its index is returned.
        - If the input is None, None is returned.
    """
    if string is not None:
        try:
            idx = int(string)

            if idx < 0:
                idx = len(header_col) + idx + 1
        except ValueError:
            idx = header_col.index(string) + 1
    else:
        idx = None
    return idx


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog - Genome Position Conversion Tool by Liftover

        Author: Tingfeng Xu (xutingfeng@big.ac.cn)
        Version: 1.0

        This tools will load -i filePath and find all peaks by -c chr pos pval with --min-pval and --min-peak-dist to define the peak.

        Note:
        1. The input file should have a header line.
        2. If the pval is -log10(pval), please use --log10p.
        3. The output will be printed to stdout, so use > to redirect it to a file; or use -o to specify the output file
        4. The delimiter of input file is tab by default, use -d to specify it.

        """
        ),
    )

    parser.add_argument(
        "-i", "--input", help="input summary file", required=True, dest="input"
    )
    parser.add_argument(
        "-c",
        "--cols",
        help="columns of chr pos pval",
        required=False,
        default=[],
        nargs="+",
        dest="cols",
    )
    parser.add_argument(
        "--log10p",
        help="if the pval is -log10(pval)",
        action="store_true",
        dest="log10p",
    )
    parser.add_argument(
        "--min-pval",
        help="minimum p-value to consider",
        type=float,
        default=1e-6,
        dest="min_pval",
    )
    parser.add_argument(
        "--min-peak-dist",
        help="minimum distance between peaks (in bp)",
        type=float,
        default=2e6,
        dest="min_peak_dist",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        help="delimiter of input file",
        default="\t",
        dest="delimiter",
    )
    parser.add_argument(
        "-o", "--output", help="output file", default=None, dest="output"
    )
    parser.add_argument("-t", "--threads", help="threads", default=1, dest="threads",type=int)

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    if not osp.exists(args.input):
        print("Input file not found.")
        sys.exit(1)

    if len(args.cols) != 3:
        print("Please specify the columns of chr pos pval.")
        sys.exit(1)
    threads = args.threads
    is_log10p = args.log10p
    min_pval = args.min_pval
    min_peak_dist = args.min_peak_dist

    input_file = args.input
    compression = "gzip" if input_file.endswith(".gz") else None
    file = pd.read_csv(input_file, sep="\s+", header=0, compression=compression)
        
    output_file = args.output if args.output else sys.stdout

    header = file.columns.tolist()
    # print(header)
    chr, pos, pval = [header[header_mapper(col, header) - 1] for col in args.cols]  #
    # print(chr, pos, pval)
    if is_log10p:
        file[pval] = 10 ** -file[pval]
    if threads ==1:
        locis = get_loci(
            file.to_dict(orient="records"),
            pval_col=pval,
            pos_col=pos,
            chrom_col=chr,
            min_peak_dist=min_peak_dist,
            min_pval=min_pval,
        ) 
    elif threads > 1:
        raise NotImplementedError("Not implemented yet.")
        # from multiprocessing import Pool
        # from functools import partial
        
        # with Pool(threads) as p:             
        #     file_gb_chr = [chr_df[1].to_dict(orient="records") for chr_df in file.groupby(chr)]
        #     get_loci_multi = partial(get_loci, pval_col=pval, pos_col=pos, chrom_col=chr, min_peak_dist=min_peak_dist, min_pval=min_pval)
            
        #     locis = p.map(get_loci, file_gb_chr)
    locis_df = pd.DataFrame(locis)
    locis_df.sort_values(by=[chr, pos], inplace=True)
    if is_log10p:
        locis_df[pval] = -np.log10(locis_df[pval])


    locis_df.to_csv(sys.stdout, sep="\t", index=False)
