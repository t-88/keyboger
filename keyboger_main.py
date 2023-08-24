#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType
from keyboger_trans_html import KeybogerHtmlTranspiler

import sys

def print_help():
    print("\t -h              : show help")
    print("\t update          : to update main menu page either header info or update rerender blogs db")
    print("\t save  file_path : save new blog") 
def unkown_args():
    print("unkown arg given plz check help")
    print_help()


if __name__ == "__main__":
    # skip first one, file 
    argv = sys.argv[1:]

    if len(argv) == 0:
        print("not enough args")
        print_help()
        exit(1)
    elif len(argv) == 1:
        if argv[0] == "update":
            print("updating...")
            exit()
        elif argv[0] == "save":
            print("file path for the bl src is required")
            print_help()
        elif argv[0] == "-h":
            print_help()
        else:
            unkown_args()
    elif len(argv) == 2:
        if argv[0] == "save":
            print("saving ",argv[1])
            exit()
        else:
            unkown_args()
    else:
        unkown_args()

# src = ""
# file_path = "syntax-preview/main.bl"
# with open(file_path,"r") as f:
    # src = f.read().strip()
# 
# 
# 
# tknzer = KeybogerTokenizer()
# tknzer.tokenize(src,is_src = True)
# 
# parser = KeybogerParser()
# parser.parse(tknzer.tknz)
# 
# 
# transpiler =  KeybogerHtmlTranspiler(parser.setting)
# transpiler.start_transpiling(parser.head)
# transpiler.save("syntax-preview")
