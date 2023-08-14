#!/usr/bin/python3
import os
import datetime

def read_file(file_path):
    src = None
    with open(file_path,"r") as f:
        src = f.read()
    assert src != None , "read_file: cant read file for some reason"
    return src

src = read_file("Developing_A_Bloging_Engine/step1.bl")

class TokenType:
    eof = 0
    hashtag     = 3
    text =  4
    d_colon = 5
    unordered_list   = 6
    macro = 7
    header = 8

    mapped = {
        "#":"hashtag",
        "-":"unordered_list",
        ":" : "colon" 
    }

skipable = [' ','\t']
STRING_CHARS =  ["'",'"']

    
class Token:
    def __init__(self,typ,value="",pos =(-1 , -1)):
        self.typ = typ
        self.value = value
        self.pos = pos
    def __repr__(self):
        out = f"<Token type={self.typ}"
        if self.value != "":
            out +=  f" value={self.value}"
        out += " pos=(%d,%d)" % (self.pos[0] , self.pos[1])
        out += ">"
        return out
    def __str__(self):
        return self.__repr__()

class BlSetting:
    def __init__(self):
        self.dir_name = "tmp-" + str(datetime.datetime.now())
        self.links = {}
    def set(self,option,value):
        if option == "dir-name":
            self.dir_name = value
        elif option == "link":
            if type(value) != list:
                print("[Error] link should have a key and a value in setting macro") 
            self.links[value[0]] = value[1]  
    def get(self,option,value):
        if option == "link":
            if value in self.links:
                return self.links[value]
            return value

class Tokenizer:
    def __init__(self):
        self.src = ""
        self.tknz = []

        self.idx = 0
        self.char_idx = 0
        self.settings = BlSetting()

    def peek(self,far=0):
        if self.idx + far < len(self.src):
            return self.src[self.idx + far]
        assert False , f"Out of Range: in peek idx={self.idx} far={far}"
    def peek_str(self,far=0):
        if self.idx + far >= len(self.src):
            return "" 
        val = ""
        curr = 0
        while curr < far:
            val += self.peek(curr)
            curr += 1
        return val
    def expect(self,symb):
        if self.peek() == symb:
            self.idx += 1
            return
        assert False , f"Unexpected: in expect expected={typ} got={this.peek()}"


    def stop_at(self,stopable):
        text = ""
        if type(stopable) == list:
            #TODO: maybe change this
            while True:
                for elem in stopable:
                    if self.peek_str(len(elem)) == elem:
                        return text
                text += self.src[self.idx]
                self.idx += 1
        else:
            while self.peek_str(len(stopable)) != stopable:
                text += self.src[self.idx]
                self.idx += 1 
        
        return text

    def get(self):
        char = self.peek()
        self.idx += 1
        return char
    
    def extract_str(self,str_char):
        text = str_char
        while self.idx < len(self.src) and self.peek() != str_char:
            text += self.get()
        text += self.get()
        return text

    def append_token(self,typ,val=None,pos=None):
        self.tknz.append(Token(typ,val,pos))

    def tokenize(self,src):
        self.src = src
        self.lsrc = self.src.split("\n")
        self.tknz = []
        self.idx = 0


        row = 0
        while row < len(self.lsrc):

            col = 0
            line = self.lsrc[row]

            is_first_char = True
            while col < len(line):
                char = line[col]
                nomral_text = False


                if char in skipable:
                    col += 1
                    continue
                if is_first_char:
                    correct = True
                    is_first_char = False
                    if char == "[":
                        correct = line.strip()[-1] == "]"  
                        if correct:
                            self.append_token(TokenType.macro,line[col:],(row,col))
                    elif char == "#":
                        while col < len(line) and line[col] == "#":
                            col += 1
                        if col >= len(line):
                            correct = False
                        if correct:
                            self.append_token(TokenType.header,line,(row,col))
                        else:
                            nomral_text = True
                    elif char == "-":
                        correct = col + 1 < len(line) and line[col + 1] == " "
                        if correct:
                            self.append_token(TokenType.unordered_list,line,(row,col))
                    else:
                        correct = False
                    
                    nomral_text = not correct
                if nomral_text: 
                    col += 1
                    text = char
                    while col < len(line):
                        text  += line[col]
                        col += 1
                    self.append_token(TokenType.text,text,(row,col))

                col += 1
            row += 1

        self.append_token(TokenType.eof)

class Transpiler:
    def __init__(self,tknz = []):
        self.tknzer = Tokenizer()
        self.tknz = tknz
        self.idx = 0
        self.bl_setting = BlSetting()
    def create_dir(self):
        if not os.path.exists("build/"):
            os.mkdir("build")
        if not os.path.exists("build/" + self.tknzer.settings.dir_name):
            os.mkdir("build/" + self.tknzer.settings.dir_name)
        else:
            os.mkdir("build/" + self.tknzer.settings.dir_name +"-" + str(datetime.datetime.now()))
    def run_transpile(self,src):
        # self.create_dir()
        self.tknzer.tokenize(src)
        self.tknz = self.tknzer.tknz
        self.transpile()
        print(self.src)

    def peek(self,far=0):
        if self.idx + far < len(self.tknz):
            return self.tknz[self.idx + far]
        assert False , f"Out of Range: in transpiler peek idx={self.idx} far={far}"
    def expect(self,typ):
        if self.peek() == typ:
            self.idx += 1
            return
        assert False , f"Unexpected: in transpiler expect expected={typ} got={this.peek().typ}"

    def create_hX(self,priority = 1,content=""):
        return f"<h{priority}>{content}</h{priority}>\n"
    def create_p(self,content=""):
        return f"<p>{content}</p>\n"
    def create_ul(self,content=""):
        return f"<ul>{content}</ul>\n"
    
    def create_a(self,key,link):
        return f"<a href='{link}'>{key}</a>\n"


    def transpile(self):
        self.idx = 0
        self.src = ""
        while self.tknz[self.idx].typ != TokenType.eof:
            code = self.parse_token()
            if code:
                self.src += code 
            
            self.idx += 1

    def parse_token(self):
        tkn =  self.peek()
        if tkn.typ == TokenType.macro:
            self.parse_setting_macro(tkn.value)
        elif tkn.typ == TokenType.header:
            priority , text = self.parse_header(tkn.value)
            return self.create_hX(priority,text)
        elif tkn.typ == TokenType.unordered_list:
            return self.create_ul(self.parse_ul(tkn.value))
        elif tkn.typ == TokenType.text:
            return self.create_p(self.parse_text(tkn.value))
        else:
            assert False , f"Unexpected token in parse_token token: {tkn}"
        
    def parse_header(self,src):
        priority = 0
        idx = 0
        while idx < len(src) and src[idx] == "#":
            priority += 1
            idx += 1
        return priority , src[idx:] 
    def parse_ul(self,src):
        return src[1:]
    def parse_text(self,src):
        content = ""
        idx = 0
        while idx < len(src):
            char = src[idx]
            idx += 1
            normal_text = True

            if char == ":" and idx < len(src) and src[idx] == "[":
                correct , code , ahead = self.parse_text_macro(src[idx:])
                normal_text = not correct
                if correct:
                    content += code
                    idx += ahead
            if normal_text:
                if char == "\\":
                    content += src[idx]
                    idx += 1
                else:
                    content += char  
        return content
    def parse_text_macro(self,line):
        macro = ""
        idx = 0
        correct = False
        while idx <  len(line):
            if line[idx] == "]" and idx + 1 < len(line) and line[idx + 1] == ":":
                idx += 2
                correct = True
                break
            macro += line[idx]
            idx += 1
        
        code = ""
        macro = macro[1:].split("::")
        if macro[0] == "link":
            value = self.bl_setting.get(macro[0],macro[1])
            code = self.create_a(macro[1],value)

        return correct , code , idx
    def parse_setting_macro(self,line):
        line = line[1:-1].strip()
        code = line.split(" : ")
        self.bl_setting.set(code[0],code[1:])

transpiler =  Transpiler()
transpiler.run_transpile(src)