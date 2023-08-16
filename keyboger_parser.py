from enum import Enum, auto
from keyboger_tokenizer import TokenType


class AstType(Enum):
    text = auto()
    new_line = auto()
    header = auto()
    inline_macro = auto()

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
        self.ast = [] # ast

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
    def far_peek(self,want,far = 0):
        # far peek retuns a False when overflowing or char  not equal
        overflow , found = self.peek(far)
        return not overflow and want == found.typ 

    # same as peek but advances the col
    def inc(self):
        overflow , tkn = self.peek()
        self.cur += 1
        return overflow , tkn
    
    

    

    # just adding ast elem here
    def add_ast_element(self,typ,content = []):
        self.ast.append(AstElement(typ,content))

    # mergin text asts together in-case of bad synatx 
    def sum_up_text(self):
        idx = 0

        while idx < len(self.ast):
            if self.ast[idx].typ == AstType.text:
                start_idx = idx
                content = ""
                while idx < len(self.ast) and self.ast[idx].typ == AstType.text:
                    content += self.ast[idx].content
                    idx += 1

                # mergin the ast
                self.ast = self.ast[0:start_idx] + [AstElement(AstType.text,content)] + self.ast[idx:]
                idx -= idx - start_idx 

            idx += 1

    def parse(self,tknz = []):
        # set tknz
        if tknz: self.tknz = tknz
        
        # init
        self.cur = 0

        # create ast using tknz
        self.ast = []

        while not self.eof_tknz():
            _ , tkn = self.peek()

            # get output and save it to ast
            ast_elem = self.parse_macro(tkn)
            if ast_elem:
                self.ast.append(ast_elem)

            self.inc()


        # mergin text blocks
        self.sum_up_text()

        # print(self.setting.macros)
        for elem in self.ast:
            print(elem)
    
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
            if next_tkn.val in macros_ids:
                content = [ self.parse_macro(next_tkn) ]
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
                    return AstElement(AstType.inline_macro,content)
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





            
        
 