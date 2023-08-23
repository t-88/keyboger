import os
import shutil
from keyboger_parser import AstType



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



class KeybogerHtmlTranspiler:
    def __init__(self,setting = None):
        self.src = ""
        self.setting = setting 
    
    def start_transpiling(self,ast,setting = None):
        if setting:
            self.setting = setting

        if not self.setting:
            assert False , "KeybogerHtmlTranspiler setting not defined"

        self.src = ""

        #NOTE: expecting the head ast element to be the head 
        for elem in ast.content:
            self.transpile(elem)

    # just taking print_tree function parser and replacing print by write to file
    def transpile(self,ast,depth = -1):
        if ast.typ == AstType.header:
            self.src += "<h%s>" % ast.data['depth']
            self.transpile(ast.content)
            self.src += "</h%s>" % ast.data['depth']
        
        
        elif ast.typ == AstType.inline_macro:
            self.src += self.parse_macro(ast)
        elif ast.typ == AstType.text:
            tag = f"<p>"
            end_tag = "</p>"
            if len(ast.data) > 0:
                tag = ""
                end_tag = ""
                if "bold" in ast.data:
                    tag = f"<strong>"
                    end_tag = "</strong>"
                if "italic" in ast.data:
                    tag += "<em>"
                    end_tag = "</em>" + end_tag 

            self.src += tag            
            self.src += ast.content
            self.src += end_tag            
        elif ast.typ == AstType.new_line:
            self.src += "<br>"

        elif ast.typ == AstType.list_container:
            tag = "ul"
            if ast.content[0].typ == AstType.ordered_list:
                tag = "ol"
            
            
            typ = "1"
            if "typ" in ast.content[0].data:
                typ = ast.content[0].data["typ"]
            
            
            self.src += f"<{tag} type='{typ}'>"
            for elem in ast.content:
                self.transpile(elem)
            self.src += f"</{tag}>"

        elif ast.typ == AstType.unordered_list:
            self.src += "<li >"
            self.transpile(ast.content)
            self.src += "</li>"

        elif ast.typ == AstType.ordered_list:
            value = ""
            if ast.data['typ'] == "1":
                value =  f"value={ast.data['idxer']}"
                self.src += f"<li {value}>"
            else:
                if "start" in ast.data:
                    value =  f"value={ast.data['start']}"
                self.src += f"<li {value}>"

            
            self.transpile(ast.content)
            self.src += "</li>"            

            
        elif ast.typ == AstType.code:
            self.src += "<code class='code-blk'>"
            self.src += ast.content
            self.src += "</code>"                    

        
        else:
            assert False , f"Unreachable {ast}"    

    def parse_macro(self,ast):
        if ast.data["id"] == "link":
            if len(ast.content) == 1:
                # url || var 
                print(self.setting.links)
                if ast.content[0].content in self.setting.links:
                    return f"<a href={self.setting.links[ast.content[0].content]}>{ast.content[0].content}</a>" 
                return f"<a href={ast.content[0].content}>{ast.content[0].content}</a>" 
            else:
                # url , var 
                return f"<a href={ast.content[1].content}>{ast.content[0].content}</a>" 
                        
        elif ast.data["id"] == "local-img":
            if len(ast.content) == 2:
                # name , path
                # adding local img to local-imgs to save later in the same dir as the html
                self.setting.local_imgs[ast.content[0].content] = ast.content[1].content
                return f"<img src='{ast.content[1].content}' alt={ast.content[0].content}>" 
            elif len(ast.content) == 1:
                # name || path
                text = ast.content[0].content
                if text in self.setting.local_imgs:
                    # name
                    return f"<img src='{self.setting.local_imgs[text]}' alt={text}>" 
                else:
                    # path
                    self.setting.local_imgs[ast.content[0].content] = ast.content[0].content
                    return f"<img src='{text}' alt={text}>" 
        
        elif ast.data["id"] == "img":
            if len(ast.content) == 2:
                # name , path 
                return f"<img src='{ast.content[1].content}' alt={ast.content[0].content}>" 
            else:
                # name || path 
                if text in self.setting.online_imgs:
                    # name
                    return f"<img src='{self.setting.online_imgs[text]}' alt={text}>" 
                else:
                    # path
                    return f"<img src='{text}' alt={text}>" 

        elif ast.data["id"] == "css":
            return f"<span style={ast.content[0].content}>{ast.content[1].content}</span>"
        
        
        
        assert False , "Unreachable"
    def save(self,src_dir):
        assert self.setting != None , "KeybogerHtmlTranspiler setting not defined"

        if not os.path.exists("build/" + self.setting.dir_name):
            os.mkdir("build/" + self.setting.dir_name)
        with open("build/" + self.setting.dir_name + "/" + "index.html","w") as f:
            f.write(html_temlplate(self.src))


        # move local imgs
        for local_img in self.setting.local_imgs:
            shutil.copy2(f"{src_dir}/{self.setting.local_imgs[local_img]}",f"build/{self.setting.dir_name}/{self.setting.local_imgs[local_img]}")

