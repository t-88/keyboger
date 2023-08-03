#!/usr/bin/python3


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
    unordered_list   = "-"
    colon = ":"

    mapped = {
        "[":"osqr_brack"  ,
        "]":"csqr_brack",
        "#":"hashtag",
        "-":"unordered_list",
        ":" : "colon" 
    }

skipable = ['\n',' ','\t']
    
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

    


class Tokenizer:
    def __init__(self):
        self.src = ""
        self.tknz = []

        self.idx = 0
        self.char_idx = 0
    
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

    def tokenize(self,src):
        self.src = src
        self.tknz = []
        self.idx = 0
        
        
        while self.idx < len(self.src):
            char = self.src[self.idx] 
            self.idx += 1
            if char in ["'",'"']:
                text = char
                while self.idx < len(self.src) and self.src[self.idx] !=  char:
                    text += self.src[self.idx]
                    self.idx += 1
                text += char
                self.idx += 1

                self.tknz.append(Token(TokenType.text,value=text))

            elif char in TokenType.mapped.keys():
                if char == "[":
                    text = ""
                    self.tknz.append(Token(TokenType.mapped[char]))
                    while self.idx < len(self.src) and self.peek() != "]":
                        text += self.src[self.idx]
                        self.idx += 1
                    self.tknz.append(Token(TokenType.text,value=text))
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

                text = char
                while self.idx < len(self.src) and self.peek() != "\n" and self.peek_str(2) != "::":
                    text += self.src[self.idx]
                    self.idx += 1
                self.tknz.append(Token(TokenType.text,value=text))


        self.tknz.append(Token(TokenType.eof))

tknzer = Tokenizer()
tknzer.tokenize(src)
