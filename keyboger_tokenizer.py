from enum import Enum , auto

class TokenType(Enum):
    text = auto()
    double_colon = auto()
    new_line = auto()
    inline_macro_start = auto()
    inline_macro_end = auto()
    macro_start = auto()
    macro_end = auto()
    hashtag = auto()
    
    eof = auto()
    count = auto()

class Token:
    def __init__(self,tkn_typ, val = ""):
        self.typ = tkn_typ
        self.val = val
    
    def __repr__(self):
        out = f"<Token type={self.typ}"
        if self.val != "":
            out +=  f" value={self.val}"
        out += ">"
        return out
    def __str__(self):
        return self.__repr__()


class KeybogerTokenizer:
    def __init__(self,file_path = ""):
        self.file_path = ""
        self.src = ""
        self.src = self.load_file(file_path)
        self.lines = [] # split src into lines

        self.row = 0
        self.col = 0   # idx of char into the line

        self.tknz = [] # saved tokens
        self.first_in_line = True 
    



    # load file using file path
    def load_file(self,data,is_src = False) -> str:
        if is_src:  
            # sending src
            # data = src
            return data

        # data = file_path
        if data == self.file_path:
            # src didnt change same file path
            return self.src     

        self.file_path = data
        src = ""
        with open(self.file_path,"r") as f:
            src =  f.read()
        return src
        

    def print_tknz(self,before="",after=""):
        for tkn in self.tknz:
            print(f"{before}{tkn}{after}")  
    
        
    
    # boundry checks
    # row
    def end_of_lines(self):
        return self.row >= len(self.lines)
    # col
    def end_of_src(self):
        if self.end_of_lines():
            return True
        return self.col >= len(self.lines[self.row])
    

    # peek logic
    # get cur char without moving 
    def peek(self,far=0):
        # we add distance
        # check if its not overflowing
        self.col += far
        if self.end_of_src():
            self.col -= far
            return True , ""
        # back to original col
        self.col -= far

        return False ,  self.lines[self.row][self.col + far]
    def far_peek(self,want,far = 0):
        # far peek retuns a False when overflowing or char  not equal
        overflow , found = self.peek(far)
        return not overflow and want == found 
        
    # get cur line without moving 
    def peek_line(self):
        if self.end_of_lines():
            return False , ""
        return True ,  self.lines[self.row]

    # same as peek but advances the col
    def inc(self):
        overflow , char = self.peek()
        self.col += 1
        return overflow , char


    # adding token to tknz
    # one interface maybe helpfull when i want to separate tknz by new-lines
    def add_tkn(self,tkn_typ,val = ""):
        self.tknz.append(Token(tkn_typ,val))

    # i keep adding chars untill i find a langauge char (:[,]:,[...)
    def check_special_chars(self,cur):
        if cur == "\\":
            # we deal with "\" here 
            # i do it so i dont get tkns separated by "\" 
            overflow , char  = self.peek(1)

            # if we overflow we return "\"
            returned = cur
            # else we return escaped char
            if not overflow: 
                returned = char
                self.inc()
            return False , returned

        elif cur == ":":
            # i let the main tokenizer function take care of adding tokens
            # ::
            if self.far_peek(":",1):   return True , cur
            # :[
            elif self.far_peek("[",1): return True , cur
        
        elif cur == "[": return True , cur
        elif cur == "]": return True , cur

        # headers
        elif self.first_in_line:
            if cur == "#": return True , cur

        return False , cur
    
    def tokenize_special_chars(self,cur):
        if cur == ":":
            if self.far_peek(":",1):
                self.add_tkn(TokenType.double_colon,"::")
                self.inc()
            elif self.far_peek("[",1):
                self.add_tkn(TokenType.inline_macro_start,":[")
                self.inc()
            else:
                assert False , "Unreachable"

        elif cur == "[":
            self.add_tkn(TokenType.macro_start,"[")
        elif cur == "]":
            if self.far_peek(":",1):
                self.add_tkn(TokenType.inline_macro_end,"]:")
                self.inc()
            else:
                self.add_tkn(TokenType.macro_end,"]")    
        
        elif cur == "#":
            counter = 0
            while self.far_peek("#",counter):
                self.add_tkn(TokenType.hashtag,"#")
                counter += 1
            self.col += counter    



        
        else:  
            assert False , "Unreachable"



    def tokenize(self,data = None, is_src = False):
        if data:
            self.src = self.load_file(data,is_src)

        self.col , self.row = 0, 0
        self.lines = self.src.split("\n") 
        self.tknz = []
        self.first_in_line = True 

        
        while not self.end_of_lines():
            _ , line = self.peek_line()
            while not self.end_of_src():
                # we go through the text and we stop of we find
                # any special char

                text = ""

                # this will get its value in the loop
                cur = None

                is_normal = True
                while is_normal:
                    # deal with overflow
                    overflow , cur = self.peek()
                    if overflow: break

                                

                    is_normal , cur  = self.check_special_chars(cur)

                    # check if its the first char in line
                    # ignore spaces and tabs 
                    if self.first_in_line:
                        self.first_in_line = cur in [" ","\t"]

                    
                    # check_special_chars return true if there is special char
                    # so i inverse the output 
                    is_normal = not is_normal

                    # found special char
                    if not is_normal: break

                    text += cur
                    self.inc()

                if text:
                    self.add_tkn(TokenType.text,text)
                if not is_normal:
                    self.tokenize_special_chars(cur)

                self.col += 1
            self.col = 0
            self.first_in_line = True
            self.row += 1

            self.add_tkn(TokenType.new_line)
        self.add_tkn(TokenType.eof)

        


