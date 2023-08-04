#!/usr/bin/python3
import os
import datetime

def read_file(file_path):
    src = None
    with open("Developing_A_Bloging_Engine/main.bl","r") as f:
        src = f.read()
    assert src != None , "read_file: cant read file for some reason"
    return src

src = read_file("Developing_A_Bloging_Engine/main.bl")

class TokenType:
    eof = "eof"
    osqr_brack = "osqr_brack"
    csqr_brack = "csqr_brack"
    hashtag     = "hashtag"
    text =  "text"
    d_colon = "d_colon"
    unordered_list   = "unordered_list"
    colon = ":"

    mapped = {
        "[":"osqr_brack"  ,
        "]":"csqr_brack",
        "#":"hashtag",
        "-":"unordered_list",
        ":" : "colon" 
    }

skipable = ['\n',' ','\t']
STRING_CHARS =  ["'",'"']

    
class Token:
    def __init__(self,typ,value=""):
        self.typ = typ
        self.value = value
    def __repr__(self):
        out = f"<Token type={self.typ}"
        if self.value != "":
            out +=  f" value={self.value}"
        out += ">"
        return out
    def __str__(self):
        return self.__repr__()
class BlSetting:
    def __init__(self):
        self.dir_name = "tmp-" + str(datetime.datetime.now())
    def set(self,option,value):
        if option == "dir-name":
            self.dir_name = value

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

    def tokenize(self,src):
        self.src = src
        self.tknz = []
        self.idx = 0
        
        
        while self.idx < len(self.src):
            char = self.src[self.idx] 
            self.idx += 1
            if char in TokenType.mapped.keys():
                if char == "[":
                    text = ""
                    while self.idx < len(self.src) and self.peek() != "]":
                        text += self.src[self.idx]
                        self.idx += 1
                    self.expect("]")

                    settings = [val.strip() for val in text.split(":")]
                    self.settings.set(settings[0], settings[1])
                elif self.peek() == ":":
                    self.idx += 1
                    value = [self.stop_at("::")]
                    while self.peek_str(2) == "::":
                        self.idx += 2
                        value.append(self.stop_at(["::"," ","\n"]))
                    self.tknz.append(Token(TokenType.d_colon,value=value))
                else:
                    self.tknz.append(Token(TokenType.mapped[char]))
            elif char in  skipable: pass
            else:
                text = ""
                if char in STRING_CHARS:
                    text += self.extract_str(char)
                else:
                    text += char
                while self.idx < len(self.src) and self.peek() != "\n" and self.peek_str(2) != "::":
                    if self.peek() in STRING_CHARS: 
                        print('     ',text)
                        text += self.extract_str(self.get())
                    else:
                        text += self.peek()
                        self.idx += 1
                self.tknz.append(Token(TokenType.text,value=text))


        self.tknz.append(Token(TokenType.eof))

class Transpiler:
    def __init__(self,tknz = []):
        self.tknzer = Tokenizer()
        self.tknz = tknz
        self.idx = 0
    def create_dir(self):
        if not os.path.exists("build/"):
            os.mkdir("build")
        if not os.path.exists("build/" + self.tknzer.settings.dir_name):
            os.mkdir("build/" + self.tknzer.settings.dir_name)
        else:
            os.mkdir("build/" + self.tknzer.settings.dir_name +"-" + str(datetime.datetime.now()))
    def run_transpile(self,src):
        self.create_dir()
        self.tknzer.tokenize(src)
        self.tknz = self.tknzer.tknz
        self.transpile()

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


    def transpile(self):
        self.idx = 0
        self.src = ""
        while self.tknz[self.idx].typ != TokenType.eof:
            self.src += self.parse_token()
            self.idx += 1
        print(self.src)
    def parse_token(self):
        tkn =  self.peek()
        if tkn.typ == TokenType.text:
            return self.create_p(tkn.value)
        elif tkn.typ == TokenType.hashtag:
            priority = 0
            while self.peek().typ == TokenType.hashtag:
                priority += 1
                self.idx += 1
            return self.create_hX(priority,self.peek().value)
        elif tkn.typ == TokenType.unordered_list:
            self.idx += 1
            return self.create_ul(self.parse_token())
        elif tkn.typ == TokenType.d_colon:
            return ""
        else:
            assert False , f"Unexpected token in parse_token token: {tkn}"
        

transpiler =  Transpiler()
transpiler.run_transpile(src)
# for tkn in transpiler.tknz:
    # print(tkn) 