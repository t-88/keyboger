#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType


src = r"""
# Code blocks
same as markdown: ``` print("Wats Up") ``` **bold** ad
a **bold**

# Code blocks
same as markdown: ``` print("Wats Up") ```


## Macros
macros handle state or moving parts, maybe animation cant say for sure,
smthing like a blog preview title tree
:[make :: tree]:
""".strip()


# print(src)
# print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)
parser.print_tree(parser.head)



