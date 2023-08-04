#!/usr/bin/python3

# TODO: maybe some real oop like inheritance



class WBL_TokenType:
    OTag = "OTag"
    CTag = "CTag"
    Ident = "Ident"

skipable = ["\t"," ","\n"]
global_tags = ["script","bloger","style"]

class WBL_Token:
    def __init__(self,typ, value=""):
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
        self.idx = 0
        self.src = ""

    def peek(self,far=0):
        if self.idx + far < len(self.src):
            return self.src[self.idx + far]
        assert False , f"Out of Range: in peek idx={self.idx} far={far}"
    def expect(self,symb):
        if self.peek() == symb:
            self.idx += 1
            return
        assert False , f"Unexpected: in expect expected={typ} got={this.peek()}"
    def get(self):
        char = self.peek()
        self.idx += 1
        return char
    def not_empty(self):
        return self.idx < len(self.src)

class StrToknizer(Tokenizer):
    def __init__(self):
        super().__init__()

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
            while self.not_empty():
                for elem in stopable:
                    if self.peek_str(len(elem)) == elem:
                        return text
                text += self.src[self.idx]
                self.idx += 1
        else:
            while self.not_empty() and self.peek_str(len(stopable)) != stopable:
                text += self.src[self.idx]
                self.idx += 1
        
        return text , self.not_empty()

    def extract_str(self,str_char):
        text = str_char
        while self.idx < len(self.src) and self.peek() != str_char:
            text += self.get()
        text += self.get()
        return text


class WBL_HtmlParser(StrToknizer):
    def __init__(self):
        super().__init__()
        self.js_mdata = {}

    def parse_embedded_code(self):
        self.get(); self.get()
        inner_code , found_it = self.stop_at("}}")

        if not found_it:
            assert False, f"Unexpected: in WBL_HtmlParser parse_embedded_code didnt find closure '{{' code='{inner_code}'"
        self.get(); self.get()

        print(inner_code)

        
    def parse(self,src):
        self.src = src
        self.html_src = ""

        while self.not_empty():
            if self.peek() in skipable:
                self.get()
                continue

            src , found_it = self.stop_at("{{")
            self.html_src += src
            
            if found_it:  
                self.parse_embedded_code()
        print(self.html_src)

class WBL_Tokenizer(StrToknizer):
    def __init__(self):
        super().__init__()
        self.tknz = []

        self.srcs = []
        self.html_parser = WBL_HtmlParser()

    def extract_tag(self):
        self.expect("<")
        closing  = False
        if self.peek() == "/":
            self.get()
            closing = True
            

        tag = ""
        while self.peek() != ">":
            tag  += self.get()
        self.expect(">")
        return tag , closing

    def tokenize(self,src):
        self.src = src
        self.tknz = []
        self.idx = 0

        self.srcs = []
        
        while self.not_empty():
            if self.peek() in skipable:
                self.get()
                continue
            tag  , closing = self.extract_tag()
            if tag not in global_tags:
                assert False , f"Unexpeted tag, expected a global tag got '{tag}'"
            if closing:
                assert False , f"Unexpeted tag type, expected a opening tag got a closing one tag:'{tag}'"
            
            content , _ = self.stop_at(f"</{tag}>")
            tag  , _ = self.extract_tag()
            self.srcs.append((tag,content))
        for src in self.srcs:
            if src[0] == "bloger":
                self.html_parser.parse(src[1])
            # elif src[0] == "script":
                # self.script_tokenizer(src[1])
            # elif src[0] == "style":
                # self.style_tokenizer(src[1])



src = ""
with open("src.wbl","r") as f:
    src = f.read()
tknzer = WBL_Tokenizer()
tknzer.tokenize(src)
