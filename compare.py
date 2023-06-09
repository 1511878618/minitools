#!/usr/bin/env python
# -*-coding:utf-8 -*-

# import argparse
# import os
# import os.path as osp
# from itertools import product
# from typing import Tuple


# def mkdirs(path):
#     try:
#         os.makedirs(path)
#     except:
#         pass

# def list_dir()

# # def ls_regex(regex_pattern):
# #     """
# #     ls_regex ls like linux ls

# #     Args:
# #         regex_pattern (_type_): regex pattern

# #     Returns:
# #         List: ls result by regex in a list
# #     """
# #     path, pattern = osp.split(regex_pattern)

# #     if path == '':  # if regex_pattern is '*.pdb' then path is './'
# #         path = './'

# #     pattern = re.compile(pattern)
# #     return [osp.join(path, file) for file in os.listdir(path) if re.match(pattern, file)]


# def write_combination(combination: Tuple[str], output_dir: str = "output_dir"):
#     fileName_list = []
#     suffix_list = []
#     contents = []
#     for filepath in combination:
#         fileName, file_suffix = osp.splitext(filepath)
#         root_path, fileName = osp.split(fileName)

#         with open(filepath, "r") as f:
#             contents.append(f.read())
#         fileName_list.append(fileName)
#         suffix_list.append(file_suffix)
#     #  decide suffix of merged file
#     if len(set(suffix_list)) > 1:
#         suffix = ".txt"
#     else:
#         suffix = suffix_list[0]
#     #  decide filename of merged file
#     output_filename = ":".join(fileName_list) + suffix
#     with open(osp.join(output_dir, output_filename), "w") as f:
#         f.write("\n".join(contents))


# def getParser():
#     parser = argparse.ArgumentParser(
#         description=f"-i file_A file_B -i file_C,file_D, this will cat file_A file_C into merged file as order into output dir, any combination of [file_A, file_B] [file_C, file_D].... will be done, example code:``combination -i *HPS10* -i *DUF247* -o one-one-complex/``"
#     )
#     parser.add_argument(
#         "-i",
#         "--input",
#         dest="combination_file",
#         action="append",
#         required=True,
#         nargs="+",
#         help="for example ``combination -i Ol* A* -i S3L* -o ./test`` , this will automatically combination [Ol*, A*] with [S3L*]",
#     )  #  this will
#     parser.add_argument("-o", "--output", dest="output_dir", type=str, required=True)
#     return parser


# if __name__ == "__main__":
#     parser = getParser()
#     args = parser.parse_args()

#     file_list = args.combination_file
#     output_dir = args.output_dir
#     print(file_list)
#     mkdirs(output_dir)
#     print(len(file_list))

#     print(f"will combine these as below and save at {output_dir}")

#     index_repeat = 1 if len(file_list) // 26 <= 1 else len(file_list) // 26 + 1
#     index_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * index_repeat

#     for idx, _list in enumerate(file_list):
#         print(f"{index_str[idx]}:" + "\t".join(_list))

#     combination_list = list(product(*file_list))
#     print(f"combination_list is:" + str(combination_list)[1:-1])

#     for combination in combination_list:
#         write_combination(combination=combination, output_dir=output_dir)
