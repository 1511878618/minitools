#!/usr/bin/env python
# -*- coding: utf-8 -*-

# need to change a lot !
import pandas as pd 
import argparse
from io import StringIO
import sys
from signal import signal, SIGPIPE, SIG_DFL
import warnings

warnings.filterwarnings("ignore")
signal(SIGPIPE,SIG_DFL) #prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.

def getParser():
    parser = argparse.ArgumentParser(description="parse SIFTS API output json at https://www.ebi.ac.uk/pdbe/api/doc/sifts.html, extract UniProt mapping results from SIFTS Mappings to a csv file of all results")
    parser.add_argument("-t", dest="table", required=False, help="table", type=str)
    parser.add_argument("-f", dest="filter_table", required=False, help="filters", type=str)

    parser.add_argument("--col", dest="col", default=0, type=int, help="col_A")

    parser.add_argument("--header", dest="header", action="store_true", help="header_in A")

    parser.add_argument("--sep", dest="sep", default="\t", type=str, help="sep of A")

    return parser

def merge(A_df:pd.DataFrame, B_df:pd.DataFrame, left_col:int = 0, right_col:int = 0, how:str = "inner", header_in:bool = False):

    merge_df = A_df.merge(B_df, left_on=left_col, right_on=right_col, how=how)
    return merge_df

def load_stdin2df(sep="\t", header=None):
    with StringIO(sys.stdin.read()) as f:
        return pd.read_csv(f, sep=sep, index_col=None, header=header)
    
if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    A = args.table
    B = args.filter_table

    sep_A = args.sep_A
    sep_B = args.sep_B

    skip_A = 1 if args.header_A else 0
    skip_B = 1 if args.header_B else 0

    if A is None and B:
        df_A = load_stdin2df(sep=sep_A, skiprows = skip_A)
        df_B = pd.read_csv(B, sep=sep_B, skiprows = skip_B, index_col=None, header=None) 
    elif B is None and A:
        df_A = pd.read_csv(A, sep=sep_A, skiprows = skip_A, index_col=None,header=None)
        df_B = load_stdin2df(sep=sep_B, skiprows = skip_B)
    elif A and B:
        df_A = pd.read_csv(A, sep=sep_A, skiprows = skip_A, index_col=None, header=None)
        df_B = pd.read_csv(B, sep=sep_B, skiprows = skip_B, index_col=None, header=None) 

    elif A is None and B is None:
        raise TypeError(f"-A or -B should be specific as at least one")
    
    col_A = args.col_A
    col_B = args.col_B

    merge_df = merge(A_df = df_A, B_df = df_B, left_col=col_A, right_col=col_B, how="inner", header_in=False)
    if not merge_df.empty:
        merge_df.to_string(sys.stdout, index=None, header=None)
