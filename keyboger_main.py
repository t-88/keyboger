#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType


src = r"""
# Text Style
*bold* text is kinda nice and **italic** too, whats better is ***italic-bold***.
maybe add :[color::#FF00FF::Colors]: to text
""".strip()


# print(src)
# print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)
parser.print_tree(parser.head)



