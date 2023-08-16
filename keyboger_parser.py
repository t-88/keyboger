from enum import Enum, auto
from keyboger_tokenizer import TokenType


class AstType(Enum):
    head = auto()
    text = auto()
    new_line = auto()
    header = auto()
    inline_macro = auto()
    unordered_list = auto()
    list_container = auto()

macros_ids = [
    "link",
    "img",
    "local-img",
]

class AstElement:
    def __init__(self,ast_typ,content = [],data = {}):
        self.typ = ast_typ
        self.content = content

        self.data = data

    def __repr__(self):
        out = f"<AstElm type={self.typ}"
        if self.content:
            out +=  f" content={self.content}"
        if self.data:
            out +=  f" data={self.data}"
        out += ">"
        return out
    def __str__(self):
        return self.__repr__()

class Keyboger_Setting:
    def __init__(self):
        self.macros = []
    def append_macro(self,src):
        self.macros.append(src)

class KeybogerParser:
    def __init__(self,tknz = []):
        self.tknz = tknz

        self.cur = 0  # idx
        self.head = None # ast

        # macros and saved consts
        self.setting = Keyboger_Setting()


    # check if is over
    def eof_tknz(self):
        return self.tknz[self.cur].typ == TokenType.eof

    # taken from keyboger_tokenizer
    # peek logic
    # get cur char without moving 
    def peek(self,far=0):
        # we add distance
        # check if its not overflowing
        self.cur += far
        if self.eof_tknz():
            self.cur -= far
            return True , None
        # back to original idx
        self.cur -= far
        return False ,  self.tknz[self.cur + far]
    # usefull to remove the need for _ , tkn = self.peek()
    def peek_tkn(self,far=0):
        return self.peek(far)[1]

    def far_peek(self,want,far = 0):
        # far peek retuns a False when overflowing or char  not equal
        overflow , found = self.peek(far)
        return not overflow and want == found.typ 

    # same as peek but advances the col
    def inc(self):
        overflow , tkn = self.peek()
        self.cur += 1
        return overflow , tkn
    
    

    

    # mergin text asts together in-case of bad synatx 
    def sum_up_text(self):
        idx = 0

        while idx < len(self.head.content):
            if self.head.content[idx].typ == AstType.text:
                start_idx = idx
                content = ""
                while idx < len(self.head.content) and self.head.content[idx].typ == AstType.text:
                    content += self.head.content[idx].content
                    idx += 1

                # mergin the ast
                self.head.content = self.head.content[0:start_idx] + [AstElement(AstType.text,content)] + self.head.content[idx:]
                idx -= idx - start_idx 

            idx += 1

    def parse(self,tknz = []):
        # set tknz
        if tknz: self.tknz = tknz
        
        # init
        self.cur = 0

        # create ast using tknz
        self.head = AstElement(AstType.head,[])

        while not self.eof_tknz():
            _ , tkn = self.peek()

            # get output and save it to ast
            ast_elem = self.parse_list(tkn)
            if ast_elem:
                self.head.content.append(ast_elem)
            

            self.inc()


        # mergin text blocks
        self.sum_up_text()

        # print(self.setting.macros)
        # for elem in self.head.content:
            # print(elem)
    

    def merge_lists(self,lists):
        idx = [0]

        # its a recrsive funcion uses global vars 
        # i made sub-function because i didnt want the global vars as a part of the class
        # i used list bc nomral integer didnt work for some reason
        def inner_merge_list(depth = 0):
            # output list
            inner_lists = []
            while idx[0] < len(lists):
                # if we are not in the same lvl
                if lists[idx[0]].data["depth"] != depth:
                    if lists[idx[0]].data["depth"] > depth:
                        # we move up
                        inner_lists.append(AstElement(AstType.list_container,content=inner_merge_list(depth + 1)))
                    else:
                        # or we go down
                        return inner_lists
                else:
                    # same lvl , just append list
                    inner_lists.append(lists[idx[0]])
                    idx[0] += 1
            return inner_lists
        
        return inner_merge_list()
    
    def parse_list(self,tkn):
        correct = True
        if tkn.typ == TokenType.unordered_list:
            lists = []
            # if typ == tab that means we are in a inner loop
            # we just collect lists
            while tkn.typ == TokenType.unordered_list or tkn.typ == TokenType.tab:

                depth = 0
                if tkn.typ == TokenType.tab:
                    while self.far_peek(TokenType.tab):
                        depth += 1
                        self.inc()
                
                # FIXME: maybe there are correct lists fix this
                if not self.far_peek(TokenType.unordered_list):
                    correct = False
                    break
                

                # remove "-"
                self.inc()
                content_ast = self.parse_macro(self.peek_tkn())
                # strip additional spaces
                if content_ast.typ == AstType.text: 
                    content_ast.content = content_ast.content.strip()
                self.inc()

                # save list element
                lists.append(
                    AstElement(AstType.unordered_list,content_ast,data={"depth":depth,"inner":[]})
                    )

                # lists take the whole line
                if self.far_peek(TokenType.new_line):
                    # consume the new-line
                    self.inc()
                else: assert False , "Unreachable" 


                eof , tkn = self.peek()
                if eof: break
            
            # FIXME: done like how i remove one
            self.cur -= 1
            if correct:
                lists = self.merge_lists(lists)
                return AstElement(AstType.list_container,lists)  
        
        return self.parse_macro(tkn)    

    def parse_macro(self,tkn):
        if tkn.typ == TokenType.macro_start:
            # if we find text and macro end that means
            # that this macro is correct
            # we can save it in setting obj
            if self.far_peek(TokenType.text,1) and self.far_peek(TokenType.macro_end,2):
                self.inc()

                _ , tkn  = self.inc()
                self.setting.append_macro(tkn.val)

                self.inc()
                return 
    
        # this macro syntax is wrong so we will just treat it as text
        return self.parse_inline_macro(tkn)
    
    # inline macros
    def parse_inline_macro(self,tkn):
        if tkn.typ == TokenType.inline_macro_start:
            correct = True
            wayback = self.cur
            self.inc()

            # parsing the first element 'id' 
            _ , next_tkn  = self.inc()
            
            content = [ ]

            macro_id = ""
            if next_tkn.val in macros_ids:
                macro_id = self.parse_macro(next_tkn).content
            else:
                correct = False
            
            # now we expect :: 
            # it will short-circuit giving me false so i skip
            correct = correct and self.far_peek(TokenType.double_colon)

            if correct:
                while (not self.far_peek(TokenType.inline_macro_end) and 
                          self.far_peek(TokenType.double_colon)):
    
                    self.inc() # skip the ::
                    _ , next_tkn = self.inc()
                    content.append(self.parse_macro(next_tkn))
    
                if self.far_peek(TokenType.inline_macro_end):
                    return AstElement(AstType.inline_macro,content,data={"id":macro_id})
                else:
                    correct = False
            
            if not correct:
                # in-case wrong syntax
                self.cur = wayback

        return self.parse_new_line(tkn)


    
    def parse_new_line(self,tkn):
        if tkn.typ == TokenType.new_line:
            return AstElement(AstType.new_line)    
        
        return self.parse_header(tkn)
    
    def parse_header(self,tkn):
        if tkn.typ == TokenType.hashtag:
            self.inc()
            counter = 0

            is_hashtag = True
            while not self.eof_tknz() and tkn.typ == TokenType.hashtag:
                counter += 1
                _ , tkn = self.inc()

            content = self.parse_macro(tkn)

            return AstElement(AstType.header,content,data={"depth":counter}) 

        return self.parse_text(tkn)

    def parse_text(self,tkn):
        # making ast_text_elements
        return AstElement(AstType.text,tkn.val)

    def print_tree(self,ast,depth = -1):
        # TODO: add  some kinda of depth spacing
        if ast.typ == AstType.head:
            for elem in ast.content:
                self.print_tree(elem,depth + 1)
        elif ast.typ == AstType.header:
            print(f"Header{ast.data['depth']}: ",end="")
            self.print_tree(ast.content,depth + 1)
            print("")
        elif ast.typ == AstType.inline_macro:
            print("\033[34m" +ast.data["id"] + "\033[0m",end="")
        elif ast.typ == AstType.text:
            print(ast.content,end="")
        elif ast.typ == AstType.new_line:
            print()
        elif ast.typ == AstType.list_container:
            for elem in ast.content:
                self.print_tree(elem)
        elif ast.typ == AstType.unordered_list:
            # print(f"List-Elem: {ast.data['depth']}"+"   " * ast.data["depth"],end="")
            print("   " * ast.data["depth"],end="")
            self.print_tree(ast.content)
            print()
            if ast.data["inner"]:
                self.print_tree(ast.data["inner"])
        else:
            assert False , f"Unreachable {ast}"

    # lists can be very confusing, this helpfucl function makes debuging easier
    def print_lists(self,ast):
        if ast.typ == AstType.list_container:
            print("container:")
            for elem in ast.content:
                print_lists(elem)
        elif ast.typ == AstType.unordered_list:
            print(ast.data["depth"],ast.content)        
            if ast.data["inner"]:
                print_lists(ast.data["inner"])

            
        
 