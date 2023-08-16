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
like :[link::https://www.youtube.com/]: or with a name :[link::youtube::https://www.youtube.com/]:

## Imgs
Images Are The Same:
u can use online imgs like this python logo:
:[img::python-logo::https://www.python.org/static/img/python-logo.png]:
or local imgs that are in the same dir: :[local-img::beverage.png]:
img from :[link::flaticon::https://www.flaticon.com/free-icon/beverage_11651492?related_id=11651492&origin=pack]:
or as variable using macros:  
:[local-img::computer]: 

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

""".strip()


print(src)
print()

tknzer = KeybogerTokenizer()
tknzer.tokenize(src,is_src = True)
# tknzer.print_tknz()

parser = KeybogerParser()
parser.parse(tknzer.tknz)

parser.print_tree(parser.head)
