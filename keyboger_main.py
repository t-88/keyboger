#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType


src = r"""
# define
1. 1
. 2
    a. 3
    . 3
    . 4
    . 3
        A. 3
        B. 3
        . 3
        . 3
            2. 3
                2. 3
                3. 3
                . 3
                8. 3
                . 3
                . 3
# define inerr
. A
    . B
    . B
    . B
        AA. B
        . B
            . B
            . B
            . B
            . B
# define list
""".strip()


# print(src)
# print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)
parser.print_tree(parser.head)






# <AstElm type=AstType.head 
#     content=[
#         <AstElm type=AstType.list_container 
#             content=[
#                 <AstElm type=AstType.unordered_list 
#                 content=<AstElm type=AstType.text content=using lists> 
#                 data={'depth': 0, 
#                 'inner': 
#                     <AstElm type=AstType.list_container 
#                         content=[
#                             <AstElm type=AstType.unordered_list 
#                             content=<AstElm type=AstType.text content=look inner list 1> data={'depth': 1, 'inner': None}>]>}>]>, 
#                     <AstElm type=AstType.list_container 
#                         content=[
#                             <AstElm type=AstType.unordered_list 
#                         content=<AstElm type=AstType.text content=look inner list 1> data={'depth': 0, 'inner': None}>]>]>