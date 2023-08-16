#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser


src = r"""
[ dir-name : syntax-preview ]
[ link : markdown : https://en.wikipedia.org/wiki/Markdown]
[ img : local : computer : computer-engineer.png]
# Links and Imgs
## Links
basic language syntax is taken from :[link::markdown]:, links can be decalared with a variable name or be normal links.
like :[link:https://www.youtube.com/]: or with a name :[link::youtube::https://www.youtube.com/]:
""".strip()


print(src)
print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)
