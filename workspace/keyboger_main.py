#!/usr/bin/python3

import sys
import os

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType
from keyboger_trans_html import KeybogerHtmlTranspiler , transpile_src


def print_help():
    print("\t -h              : show help")
    print("\t update          : to update main menu page either header info or update rerender blogs db")
    print("\t test  dir_path  : builds ur blog and saves it in tests dir, the tested blog dosnt get added to blogs_db")
    print("\t save  dir_path : save new blog") 
def unkown_args():
    print("unkown arg given plz check help")
    print_help()



transpiler =  KeybogerHtmlTranspiler()

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
            transpiler.update()
            exit()
        elif argv[0] == "save" or argv[0] == "test":
            print("dir path for the main.bl src is required")
            print_help()
        elif argv[0] == "-h":
            print_help()
        else:
            unkown_args()
    elif len(argv) == 2:
        if argv[0] == "save" or argv[0] == "test":
            if not os.path.exists(argv[1]):
                print("provided dir doesnt exist")
            elif not os.path.isdir(argv[1]):
                print("plz provide dir path not file path")
            elif not os.path.exists(argv[1]+"main.bl"):
                print("expecting to find main.bl file in dir")
            else:
                dir_path = argv[1]
                src = ""


                with open(dir_path+"main.bl","r") as f:
                    src = f.read().strip()

                tknzer = KeybogerTokenizer()
                tknzer.tokenize(src,is_src = True)

                parser = KeybogerParser()
                parser.parse(tknzer.tknz)

                # parser.print_tree(parser.head)

                transpiler = KeybogerHtmlTranspiler(parser.setting)
                transpiler.start_transpiling(parser.head)
                # 
                if argv[0] == "save":
                    transpiler.save(dir_path)
                else:
                    transpiler.save_test(dir_path)


                print("saving ",argv[1])
                exit()
        else:
            unkown_args()
    else:
        unkown_args()


#TODO: make website responsive 
