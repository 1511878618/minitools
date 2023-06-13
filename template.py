#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import textwrap


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog is ....
        @Author: xutingfeng@big.ac.cn
        Version: 1.0
        Example:
        ...

        """
        ),
    )

    parser.add_argument(
        "-i",
        "--col_oreder",
        dest="col_order",
        default=[],
        nargs="+",
        help="default is -i 3 1 2 4 5 . -i 2 1 4 5 6 => ID col is 2, chr col is 1, pos col is 4, ref col is 5, alt col is 6. Note col index start from 1.",
        type=str,
    )
    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
