#!/usr/bin/python3
import os
import datetime
import shutil

def read_file(file_path):
    src = None
    with open(file_path,"r") as f:
        src = f.read()
    assert src != None , "read_file: cant read file for some reason"
    return src



class TokenType:
    eof = 0
    hashtag     = 3
    text =  4
    d_colon = 5
    unordered_list   = 6
    macro = 7
    header = 8
    code = 9
    inline_code = 10
    ordered_list = 11

    mapped = {
        "#":"hashtag",
        "-":"unordered_list",
        ":" : "colon" 
    }

skipable = [' ','\t']
STRING_CHARS =  ["'",'"']

    
def html_temlplate(src):
    return f"""<html>
    <head> <link rel="stylesheet" href="../style.css"> </head>
    <body>
        <header> 
            <img src="../pic.png" alt="profile-pic" id="img">
            <a href="">Main-Menu</a>
            <a href="">Github</a>
            <a href="">About</a>
        </header>
        <div id="blog">
            <section id="content">
            {src}
            </section>
        </div>
    </body>
    <script src="../main.js"> </script>
</html>"""

class Token:
    def __init__(self,typ,value="",pos =(-1 , -1),mdata = None):
        self.typ = typ
        self.value = value
        self.pos = pos
        self.mdata = mdata
    def __repr__(self):
        out = f"<Token type={self.typ}"
        if self.value != "":
            out +=  f" value={self.value}"
        out += f" mdata={self.mdata}"
        out += ">"
        return out
    def __str__(self):
        return self.__repr__()

class BlSetting:
    def __init__(self):
        self.dir_name = "tmp-" + str(datetime.datetime.now())
        self.links = {}
        self.online_imgs = {}
        self.local_imgs = {}
    def set(self,option,value):
        if option == "dir-name":
            self.dir_name = value[0]
        elif option == "link":
            if type(value) != list:
                print("[Error] link should have a key and a value in setting macro") 
            self.links[value[0]] = value[1]  
        elif option == "img":
            if type(value) == list:
                if len(value) == 3:
                    if value[0] == "local":    
                        self.local_imgs[value[1]] = value[2]
                    elif value[0] == "online": 
                        self.online_imgs[value[1]] = value[2]
                else:
                    self.online_imgs[value[1]] = value[2]
            else:
                raise Exception(f"[Error] wrong macro synatx {value} expected more options")
        elif option == "make":
            #TODO: implement more complex ui elements
            pass
        else:
            assert False , f"[Error] unkown macro {option}: {value}"
    def get(self,option,value):
        if option == "link" or option == "img":
            # link : name : url
            if  len(value) == 2:
                return (value[0],value[1])
            
            # link : name
            if value[0] in self.links:
                return (value[0],self.links[value[0]])

            # link : url
            return (value[0],value[0])
        elif option == "img" or option == "local-img":
            output = None
            local_saved = False

            # img : alt : url
            if  len(value) == 2:
                output = (value[0],value[1])
            
            # img : name
            # check  local and online imgs
            if not output:
                if value[0] in self.local_imgs:
                    local_saved = True
                    output = (value[0],self.local_imgs[value[0]])
                elif value[0] in self.online_imgs:
                    output = (value[0],self.online_imgs[value[0]])

            # img : url
            if not output:
                output = (value[0],value[0])

            if not local_saved:
                self.set("img",["local",output[0],output[1]])

            return output        

    def __repr__(self):
        out = f"dir_name: {self.dir_name}\n"
        out += "links:"
        for link in self.links:
            out += f"\t{link} : {self.links[link]}\n"

        if len(self.local_imgs) > 0:
            out += "local_imgs:"
            for img in self.local_imgs:
                out += f"\t{img} : {self.local_imgs[img]}\n"
        if len(self.online_imgs) > 0:
            out += "online_imgs:"
            for img in self.online_imgs:
                out += f"\t{img} : {self.online_imgs[img]}\n"

        
        return out

    def __str__(self):
        return self.__repr__()

class Tokenizer:
    def __init__(self):
        self.src = ""
        self.tknz = []

        self.idx = 0
        self.char_idx = 0
        self.settings = BlSetting()


        self.lsrc = []
        self.line = ""
    def peek(self,idx,src,far=0):
        if idx + far < len(src):
            return src[idx + far]
        assert False , f"Out of Range: in peek idx={idx} far={far}"
    def peek_str(self,idx,src,far=0):
        if idx + far >= len(src):
            return "" 
        val = ""
        curr = 0
        while curr < far:
            val += self.peek(idx,src,curr)
            curr += 1
        return val
    
    def extract_str(self,str_char):
        text = str_char
        while self.idx < len(self.src) and self.peek() != str_char:
            text += self.get()
        text += self.get()
        return text

    def append_token(self,typ,val=None,pos=(-1,-1),mdata = None):
        self.tknz.append(Token(typ,val,pos,mdata = mdata))


    def tokenize_code_blk(self,typ=TokenType.code,inline = False):
        self.col += 3
        
        text = "```"
        done = False
        first_new_line = True
        while not done and self.row < len(self.lsrc):
            while self.col < len(self.line):
                if self.line[self.col] == "\\":
                    text += self.line[self.col + 1]
                    self.col += 2
                elif self.peek_str(self.col,self.line + " ",3) == "```":
                    text += "```"
                    done = True
                    self.col += 2
                    break
                text += self.line[self.col]
                self.col += 1
            if self.col == len(self.line):
                self.col = 0
                self.row += 1
                self.line = self.lsrc[self.row]

                if first_new_line:
                    first_new_line = False
                else:
                    text += "\n" 
        if not inline:
            self.append_token(typ,text,(self.row,self.col))        
        else:
            return Token(typ,text)
    def tokenize_ordered_list(self,char):
        correct = False
        # used for list numbers and letters
        ident = ""

        if char == ".":
            correct = self.line[self.col + 1] == " "
            self.col += 1
        else:
            while self.col < len(self.line) and self.line[self.col] != " " and self.line[self.col] != ".":
                self.col += 1
            # check if next ordered list syntax is correct 
            # check if we are sill in the same line, we stoped at a "." and next char is space
            # ordered list synatx [number| letter]. *

            correct = self.col < len(self.line) and self.line[self.col] == "." and self.col + 1 < len(self.line) and self.line[self.col + 1] == " "
        if correct:
            # either a iden or nothing
            # its the start values of the list
            ident = self.line[:self.col]
            self.line = self.line[self.col + 1:].strip()
            
            # space count is used to know nested lists
            # a tab is one lvl aka 4 spaces 
            pr  = ident.count(" ") // 4

            # remove useless spaces
            ident = ident.strip()

            # type of ordered list letters or numbers
            typ = "1" if ident != "." else ""
            if ident.isalpha():
                typ = "A" if ident.isupper() else "a" 

            # if we start with alpha char 
            # we need to calculate its start pos
            start = "" if ident == "." else ident

            if typ != "1" and ident != ".":
                ident = ident.lower()

                # final start value
                start = 0
                # counts how many letters
                counter = 0
                for char in ident[::-1]:
                    diff = ord(char) - ord('a') + 1
                    start +=  diff * 26 ** counter

                    counter += 1


            self.append_token(TokenType.ordered_list,self.line,mdata={"start":start,"pr" : pr,"typ": typ})
        
        return correct
    def tokenize(self,src):
        self.src = src
        self.lsrc = self.src.split("\n")
        self.tknz = []


        self.row = 0
        while self.row < len(self.lsrc):

            self.col = 0
            self.line = self.lsrc[self.row]

            is_first_char = True
            while self.col < len(self.line):
                char = self.line[self.col]
                nomral_text = False


                if char in skipable:
                    self.col += 1
                    continue

                if is_first_char:
                    correct = True
                    is_first_char = False
                    if char == "[":
                        correct = self.line.strip()[-1] == "]"  
                        if correct:
                            self.append_token(TokenType.macro,self.line[self.col:],(self.row,self.col))
                    elif char == "#":
                        while self.col < len(self.line) and self.line[self.col] == "#":
                            self.col += 1
                        if self.col >= len(self.line):
                            correct = False
                        if correct:
                            self.append_token(TokenType.header,self.line,(self.row,self.col))
                        else:
                            nomral_text = True
                    elif char == "-":
                        pr = 0
                        correct = False
                        list_iden  = ""
                        while self.col < len(self.line) and self.line[self.col] == "-":
                            pr += 1
                            self.col += 1
                        if self.col != len(self.line) and self.line[self.col] == " ":
                            correct =  True

                        if correct:
                            self.append_token(TokenType.unordered_list,self.line,mdata={"pr":pr})
                    elif char == "`":
                        correct = self.peek_str(self.col,self.line + " ",3) == "```"
                        if correct:
                            self.tokenize_code_blk()
                    elif char == "." or str(char).isalnum():
                        # saving curr char in-case that the parsing was wrong
                        saved_pos = self.col
                        correct = self.tokenize_ordered_list(char)
                        if not correct:
                            self.col = saved_pos
                    else:
                        correct = False 
                    nomral_text = not correct
                if nomral_text: 
                    self.col += 1
                    text = char

                    inline_tkns = []
                    while self.col < len(self.line):
                        if self.line[self.col] == "\\":
                            assert self.col + 1 < len(self.line) , "[Error] tokenization list out of range in escape char" 
                            text  += self.line[self.col + 1]
                            self.col += 1
                        elif self.line[self.col] == "`" and self.peek_str(self.col,self.line + " ",3) == "```":
                            inline_tkns.append(self.tokenize_code_blk(TokenType.inline_code,True))
                            text += ":[@]:"
                        else:
                            text  += self.line[self.col]
                        self.col += 1
                    self.append_token(TokenType.text,text,(self.row,self.col))
                    self.tknz += inline_tkns

                self.col += 1
            self.row += 1

        self.append_token(TokenType.eof)

class Transpiler:
    def __init__(self,tknz = []):
        self.tknzer = Tokenizer()
        self.tknz = tknz
        self.idx = 0
        self.bl_setting = BlSetting()
        self.list_idx = 0
        self.list_content = ""
    
    def save(self,src_dir,file_path):
        if not os.path.exists("build/" + self.bl_setting.dir_name):
            os.mkdir("build/" + self.bl_setting.dir_name)
        with open("build/" + self.bl_setting.dir_name + "/" + file_path,"w") as f:
            f.write(html_temlplate(self.src))

        for local_img in self.bl_setting.local_imgs:
            shutil.copy2(f"{src_dir}/{self.bl_setting.local_imgs[local_img]}",f"build/{self.bl_setting.dir_name}/{self.bl_setting.local_imgs[local_img]}")
    
    def run_transpile(self,src):
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
    def create_p(self,content="",attr=""):
        return f"<p {attr}>{content}</p>\n"
    def create_span(self,content="",attr=""):
        return f"<span {attr}>{content}</span>\n"
    def create_ul(self,content=""):
        return f"<ul><li>{content}</li></ul>\n"
    def create_a(self,key,link):
        return f"<a href='{link}'>{key}</a>\n"
    def create_code_blk(self,class_name,code):
        lines =  code.replace(" ","&nbsp;").split("\n")
        code = ""
        for i in range(len(lines)):
            code += "<span>" + lines[i] + "</span>"
            if i != len(lines) - 1:
                code += "<br>"

        tag = "div"
        if class_name == "inline-code-blk":
            tag = "span"



        return f"""
        <{tag} class="{class_name}">
            {code}
        </{tag}>
        """
    def create_bold(self,content):
        return f"<strong>{content}</strong>"
    def create_italic(self,content):
        return f"<i>{content}</i>"
    def create_img(self,alt,link):
        return f"<img alt='{alt}' src='{link}'>\n"


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
            lists = []
            while self.peek().typ == TokenType.unordered_list:
                lists.append(self.peek())
                self.idx += 1
            self.idx -= 1
            self.list_idx = 0
            self.list_content = ""
            self.parse_lists(lists)
            return self.list_content
        elif tkn.typ == TokenType.ordered_list:
            #TODO: same code as TokenType.unordered_list merge
            lists = []
            while self.peek().typ == TokenType.ordered_list:
                lists.append(self.peek())
                self.idx += 1
            self.idx -= 1
            self.list_idx = 0
            self.list_content = ""
            self.parse_ordered(lists)
            return self.list_content
        elif tkn.typ == TokenType.text:
            return self.create_p(self.parse_text(tkn.value))
        elif tkn.typ == TokenType.code:
            return self.create_code_blk("code-blk",tkn.value[3:-3])
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

            if char == "\\":
                content += src[idx]
                idx += 1
            elif char == "*":
                normal_text = False
                text_style = 1
                while idx < len(src) and src[idx] == "*":
                    text_style += 1
                    idx += 1

                text = ""
                while idx < len(src):
                    if src[idx] == "\\":
                        text += src[idx + 1]
                        idx += 1
                    elif src[idx] == "*":
                        idx += text_style
                        break
                    else:
                        text += src[idx]
                    idx += 1
                
                # TODO: Recrusive parsing, i could have a link here?
                if text_style == 1:
                    content += self.create_bold(text)
                elif text_style == 2:
                    content += self.create_italic(text)
                elif text_style == 3:
                    content += self.create_italic(self.create_bold(text))


            elif char == ":" and idx < len(src) and src[idx] == "[":
                if src[idx + 1] == "@":
                    idx += 4
                    self.idx += 1
                    content += self.create_code_blk("inline-code-blk",self.tknz[self.idx].value[3:-3])
                    normal_text = False
                else:
                    correct , code , ahead = self.parse_inline_macro(src[idx:])
                    normal_text = not correct
                    if correct:
                        content += code
                        idx += ahead
            if normal_text:
                content += char  

        return content
    def parse_inline_macro(self,line):
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
            (name,href) = self.bl_setting.get(macro[0],macro[1:])
            code = self.create_a(name,href)
        elif macro[0] == "color":
            # Color Synatx
            # Color: #FFFFFF : text
            code = self.create_span(macro[2],f"style='color : {macro[1]}'")
        elif macro[0] == "img" or macro[0] == "local-img":
            # in imgs we use alt img
            (alt,href) = self.bl_setting.get(macro[0],macro[1:])
            code = self.create_img(alt,href)
        else:
            assert False, "[Error]: Unknown macro %s" % (macro[0])
        return correct , code , idx
    def parse_setting_macro(self,line):
        line = line[1:-1].strip()
        code = line.split(" : ")
        self.bl_setting.set(code[0],code[1:])
    def parse_lists(self,lists,depth = 0):

        while self.list_idx < len(lists):
            tkn = lists[self.list_idx]

            if lists[self.list_idx].mdata["pr"] != depth:
                # we check if we are in upper or lower lvl
                # and deal with it accordingly
                if lists[self.list_idx].mdata["pr"] > depth:
                    # next lvl behavior
                    self.list_content += "<ul>\n"
                    self.parse_lists(lists,depth + 1)
                    self.list_content += "</ul>\n"
                else:
                    # we let prev lvl deal with it 
                    return 
            else:            
                # default behavior when on same lvl
                self.list_content += f"<li>{tkn.value.strip()[tkn.mdata['pr']:]}</li>\n"
                self.list_idx += 1
    def parse_ordered(self,lists,depth = -1,typ = "1"):
        # watch for the end of the list
        # if we are in the same lvl we consume
        while self.list_idx < len(lists):
            tkn = lists[self.list_idx]

            if lists[self.list_idx].mdata["pr"] != depth:
                
                # we check if we are in upper or lower lvl
                # and deal with it accordingly
                if lists[self.list_idx].mdata["pr"] > depth:
                    # next lvl behavior
                    self.list_content += f"<ol type={tkn.mdata['typ']} start={tkn.mdata['start']}>\n"
                    self.parse_ordered(lists,depth + 1, tkn.mdata["typ"])
                    self.list_content += "</ol>\n"
                else:
                    # let prev lvl deal with it
                    return 


            elif typ != tkn.mdata["typ"] and tkn.mdata["typ"] != "":
                # if ol type changes i deal with it 
                # typ == "" means use default
                self.list_content += "</ol>\n"
                self.list_content += f"<ol type='{tkn.mdata['typ']}' start={tkn.mdata['start']}>\n"
                self.parse_ordered(lists,depth, tkn.mdata["typ"])
            
            else:            
                # default behavior when on same lvl
                self.list_content += f"<li>{tkn.value}</li>\n"
                self.list_idx += 1



        

dir_path = "syntax-preview"

src = read_file(f"{dir_path}/main.bl")
src = src.replace("<","&lt;")
src = src.replace(">","&gt;")

transpiler =  Transpiler()
transpiler.run_transpile(src)
transpiler.save(dir_path,"index.html")
print(transpiler.bl_setting)