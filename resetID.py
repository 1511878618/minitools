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
        %prog Set/Replace ID for any file. setID as : chr:pos:ref:alt
        @Author: wavefancy@gmail.com (raw code comes from) and xutingfeng@big.ac.cn (modified for this version)

        Version: 1.0

        --header的时候，它会默认忽略第一行，直接输出；而使用--comment的时候，直接输出所有以comment开头的所有行；二者不可以同时使用。

        Example
        1. Reset bim file by code: `cat test.bim| resetID.py -i 2 1 4 6 5 `
            Assume have a bim file: test.bim 
            ----------------------
            2       chr2:20289436:SG        0       20289436        C       A
            2       chr2:20289443:SG        0       20289443        T       C
            2       chr2:20289448:SG        0       20289448        T       C
            output will be like below 
            ----------------------
            2       2:20289443:C:T  0       20289443        T       C
            2       2:20289448:C:T  0       20289448        T       C
            2       2:20289449:A:C  0       20289449        C       A
            if add -k option, the output will be like below, which will keep old ID 
            ----------------------
            2       2:20289443:C:T:chr2:20289443:SG 0       20289443        T C
            2       2:20289448:C:T:chr2:20289448:SG 0       20289448        T C
            2       2:20289449:A:C:chr2:20289449:SG 0       20289449        C A

        2. Reset pvar file by code: `cat test.pvar| resetID.py -i 3 1 2 4 5 --comment '#'| head`
            Assume have a pvar file: test.pvar
            ----------------------
            #CHROM  POS     ID      REF     ALT
            19      10091633        chr19:10091633:SG       G       A
            19      10091645        chr19:10091645:SG       C       T
            ----------------------
            output will be like below
            #CHROM  POS     ID      REF     ALT
            19      10091633        19:10091633:G:A G       A
            19      10091645        19:10091645:C:T C       T

        3. if only resort ID column, use `zcat ldl_a.table.gz|body resetID.py -i 3 -s `
            -i 3 指定ID列，不用指定其他的列了
            可以支持的操作有：
            -s 代表对ref和alt进行排序，这样就不用考虑ref和alt的顺序了
            --add-chr 对chr列加上chr前缀
            --keep 保留原始ID
            --header 有header的时候，它会默认忽略第一行，直接输出；而使用--comment的时候，直接输出所有以comment开头的所有行；二者不可以同时使用。
            Assume IDCol should be: chr:pos:ref:alt
        
        



        """
        ),
    )

    parser.add_argument(
        "-i",
        "--col_oreder",
        dest="col_order",
        default=[],
        nargs="+",
        help="default is -i 3 1 2 4 5 . -i 2 1 4 5 6 => ID col is 2, chr col is 1, pos col is 4, ref col is 5, alt col is 6. Note col index start from 1.如果已经是这个格式了则可以直接 -i 3， 然后进行下面的操作",
        type=str,
    )
    parser.add_argument(
        "-k",
        "--keep",
        dest="keep",
        required=False,
        action="store_true",
        help="Include old rsID.",
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sort",
        required=False,
        action="store_true",
        help="ort the ref and alt alleles, sorted([ref,alt])",
    )
    parser.add_argument(
        "-d",
        "--delimter",
        dest="delimter",
        default=None,
        help="delimter for input file, default is 'any white sapce'.",
    )
    parser.add_argument(
        "-c",
        "--comment",
        dest="comment",
        default=None,
        help="comment char, default is '#'.",
    )
    parser.add_argument("--add-chr", dest="addChr", action="store_true", help="add chr for chr col of ID")
    parser.add_argument(
        "--header",
        dest="header",
        action="store_true",
        help="Set this if input file with header.",
    )
    return parser

def formatChr(x, nochr=False):
    if nochr:
        return x.replace("chr", "")
    else:
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


def resetID(line, orderList, IncludeOld=False, is_sort=False, delimter=None,addChr=False):
    """
    reset ID for any file.
    setID as : chr:pos:ref:alt
    return
    """
    # output results.
    ss = line.split(delimter)
    
    # orderList should contain at least one element, which is ID col
    if len(orderList) ==1:
        idCol = orderList[0]
        oldID = ss[idCol]
        chr, pos, A0, A1 = oldID.split(':') # this time A0 and A1 is not sure, and this mode should work for --sort or --add-chr or do nothing 
    else:
        idCol, chrCol, posCol, refCol, altCol = orderList

        oldID, chr, pos, A0, A1 = ss[idCol], ss[chrCol], ss[posCol], ss[refCol], ss[altCol] # this time A0 is REF and A1 is ALT; this work for rename ID 
    
    if is_sort:
        stemp = sorted([A0, A1])
    else:
        stemp = [A0, A1]

    # if addChr:
    chr = formatChr(chr, not addChr) # addChr is True, then nochr is False, so formatChr will add chr for chr col of ID

    newID = chr + ':' + pos + ':' + stemp[0] + ':' + stemp[1]
    if IncludeOld:  # 是否包含oldID
        newID = newID + ':' + oldID  
    # 更新到ss中
    ss[idCol] = newID

    if delimter is None:
        outputDelimter = "\t"
    else:
        outputDelimter = delimter
    return outputDelimter.join(ss)
    # sys.stdout.write('%s\n'%('\t'.join([ss[x] for x in idIndex])))


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    expr = args.col_order
    if expr == []:
        expr = [3, 1, 2, 4, 5]
    IncludeOld = args.keep
    is_sort = args.sort
    comment = args.comment
    delimter = args.delimter
    header = args.header
    addChr = args.addChr
    # check header and comments
    if comment is not None and header:
        raise ValueError(
            "Error: --header and --comment can not be set at the same time；推荐--header的时候，它会默认忽略第一行，直接输出；而使用--comment的时候，直接输出所有以#开头的"
        )
    if header:
        skip_row = 1
    else:
        skip_row = 0

    orderList = [int(i) - 1 for i in expr]
    output = False
    for line in sys.stdin:
        if skip_row > 0:
            skip_row -= 1
            continue

        line = line.strip()
        if line:
            if output:
                ss = resetID(
                    line=line,
                    orderList=orderList,
                    IncludeOld=IncludeOld,
                    is_sort=is_sort,
                    delimter=delimter,
                    addChr=addChr,
                )
                sys.stdout.write(f"{ss}\n")

            else:
                if comment is not None and line.startswith(comment):
                    sys.stdout.write(f"{line}\n")
                else:
                    output = True
                    ss = resetID(
                        line=line,
                        orderList=orderList,
                        IncludeOld=IncludeOld,
                        is_sort=is_sort,
                        delimter=delimter,
                        addChr=addChr,
                    )
                    sys.stdout.write(f"{ss}\n")


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
