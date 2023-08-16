#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType


src = r"""
# define
\- (2)
- (3)
    - (4)
        - (5)
        - (5)
        - (5)
# define list
- (5)
    - (5)
        - (5)
        - (5)
- (5)
- (6)
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