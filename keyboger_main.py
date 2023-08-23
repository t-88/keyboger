#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType
from keyboger_trans_html import KeybogerHtmlTranspiler

src = ""
file_path = "syntax-preview/main.bl"
with open(file_path,"r") as f:
    src = f.read().strip()


# print(src)
# print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)


transpiler =  KeybogerHtmlTranspiler(parser.setting)
transpiler.start_transpiling(parser.head)
transpiler.save("syntax-preview")



