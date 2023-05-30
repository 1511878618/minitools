#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import argparse
import warnings

import sys

from signal import SIG_DFL, SIGPIPE, signal

warnings.filterwarnings("ignore")

signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.


def getParser():
    parser = argparse.ArgumentParser(
        description=f"merge left and right csv file by left_on and right_on"
    )

    parser.add_argument(
        "-l", "--left", dest="left", required=True, help="left csv file path"
    )

    parser.add_argument(
        "-r", "--right", dest="right", required=True, help="right csv file path"
    )

    parser.add_argument(
        "-o",
        "--on",
        dest="on_str",
        required=False,
        help="like: 0,1;0,3  会把left的第1列和第二列作为合并的索引，右边的第一列和第四列作为合并的索引进行合并。1,2则会两边都拿第一列和第二列进行索引。如果不传入，则默认两个列表进行按行合并，此时how会影响严重影响后续的结果",
    )
    # additional args
    parser.add_argument(
        "--how",
        dest="how",
        default="left",
        help="""
        merge method, default is left, see pandas.merge， "left", "right", "inner", "outter"
        """,
    )
    parser.add_argument(
        "-d",
        "--delimeter",
        dest="sep",
        default="\s+",
        help="default is whitespace， -d ',' 以,分割; 现在支持以下写法： 1. \s+ => left_sep = \s+, right_sep = \s+ 2. \s+;, => left_sep = '\s+', right_sep = ','",
    )
    parser.add_argument(
        "--output_sep",
        dest="output_sep",
        help="输出分隔符, default is input sep，默认是输出空格分隔， --output_sep " " 以空格分割",
    )

    parser.add_argument(
        "--no_header",
        dest="no_header",
        action="store_true",
        help="--no_header，没有header的时候使用",
    )

    return parser


def parse_on_str(on_str):
    # 解析on_str
    if len(on_str_list := on_str.split(";")) == 1:
        on = on_str_list[0].split(",")
        left_on_idx = on
        right_on_idx = on
    else:
        left_on_idx, right_on_idx = on_str_list
    # 格式化为int
    left_on_idx = [int(i) for i in left_on_idx]
    right_on_idx = [int(i) for i in right_on_idx]

    left_on = left.columns[left_on_idx].to_list()
    right_on = right.columns[right_on_idx].to_list()
    return left_on, right_on


def parse_sep_pattern(sep_expression):
    """
    1. \s+ => left_sep = \s+, right_sep = \s+
    2. \s+;, => left_sep = \s+, right_sep = ;
    """
    if len(sep_expression_list := sep_expression.split(";")) == 1:
        left_sep = sep_expression_list[0]
        right_sep = left_sep
    else:
        left_sep, right_sep = sep_expression_list.split(";")

    return left_sep, right_sep


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    sep = args.sep
    no_header = args.no_header
    how = args.how

    if no_header:
        header = None
    else:
        header = 0

    # parse input sep
    left_sep, right_sep = parse_sep_pattern(sep)

    if args.output_sep:
        output_sep = args.output_sep
    else:
        if left_sep == right_sep:  # 两个一样的情况下， 输出sep不变
            output_sep = sep
            # note carefully, 空格分割这一块存在小问题
            if output_sep == "\s+":
                output_sep = " "
        else:
            raise ValueError("输入存在两个sep且不同，--output_sep必须要指定")
        
    
    left = pd.read_csv(args.left, sep=sep, header=header)
    right = pd.read_csv(args.right, sep=sep, header=header)

    if header is None:
        left.columns = [f"{i}_l" for i in range(len(left.columns))]
        right.columns = [f"{i}_r" for i in range(len(right.columns))]

    on_str = args.on_str
    if on_str:
        left_on, right_on = parse_on_str(on_str)
        merge_result = left.merge(
            right, left_on=left_on, right_on=right_on, how=args.how
        )
    else:
        merge_result = left.merge(
            right, how=args.how, left_index=True, right_index=True
        )

    # 奇怪的bug,
    if header is None:
        merge_result.to_csv(sys.stdout, sep=output_sep, index=False, header=header)
    else:
        merge_result.to_csv(
            sys.stdout, sep=output_sep, index=False, columns=merge_result.columns
        )
