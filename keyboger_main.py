#!/usr/bin/python3

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType


src = r"""

# List
## Un-ordered Lists
-   using lists
    - look inner list
-   another list
    - nice 
    - oga
        - oga
            - oga
            - oga
            - oga
            - oga
            - oga
            - oga
            - oga
            - oga
        - oga
    - boga
-   yet another list

## Ordered Lists
1. This is one
.  u give the first char and the list takes care of the rest
.  inner lists too
    15. smthing like this
    16. no like this
    . auto
    A. cant say anything
        BBV. ?
        . ?
        . ?
        . ?
        . ?
        . ?
    .  wherever happens

# Text Style
""".strip()


# print(src)
# print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)
parser.print_tree(parser.head)



