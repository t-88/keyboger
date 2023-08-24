import os
import shutil
import datetime

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType


def html_blog_temlplate(src):
    return f"""<html>
    <head> <link rel="stylesheet" href="../src/style.css"> </head>
    <body>
        <header> 
            <img src="../src/pic.png" alt="profile-pic" id="img">
            <a href="../index.html">Main-Menu</a>
            <a href="https://github.com/">Github</a>
            <a href="" id="about-link">About</a>
        </header>
        <div id="blog">
            <section id="content">
            {src}
            </section>
        </div>

    </body>

    <div id="about" style="display: none;">
        <div>
            <center><h3>Place Holder About</h3></center>
            <p>
                here u can put ur about info...
            </p>

            <button>close</button>
        </div>
    </div>

    <script src="../src/main.js"> </script>
</html>"""

def html_main_menu_temlplate(custom_info,blogs):
    return f"""<html>
    <head> <link rel="stylesheet" href="src/style.css"> </head>
    <head> <link rel="stylesheet" href="src/main_menu.css"> </head>
    <body>
        <header id="main-menu-header"> 
            <!-- <img src="src/pic.png" alt="profile-pic" id="img"> -->
            <p id="blog-name">
                Keyboger
            </p>
            <div id="personal-links">
                <a href="https://github.com/"><img src="src/github-mark-white.svg" alt="" width="35px"></a>
                <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"><img src="src/youtube.png" alt="" width="50px"></a>
            </div>
        </header>
        <br>
        <br>


        <div id="main-menu-body">
            <div id="custom-info">
                {custom_info}
            </div>
            <br>
            <h2> Blogs </h2>
            <div id="blogs">
                {blogs}
            </div>

        </div>
    </body>
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
    

    def transpile_src(self,src):
        tknzer = KeybogerTokenizer()
        tknzer.tokenize(src,is_src = True)

        parser = KeybogerParser()
        parser.parse(tknzer.tknz)

        self.start_transpiling(parser.head)

    # just taking print_tree function parser and replacing print by write to file
    def transpile(self,ast,depth = -1):
        if ast.typ == AstType.header:
            self.src += "<h%s>" % ast.data['depth']
            self.src += ast.content.content
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

        # save new blog
        if not os.path.exists("build/" + self.setting.dir_name):
            os.mkdir("build/" + self.setting.dir_name)
        with open("build/" + self.setting.dir_name + "/" + "index.html","w") as f:
            f.write(html_blog_temlplate(self.src))
        # move local imgs
        for local_img in self.setting.local_imgs:
            shutil.copy2(f"{src_dir}/{self.setting.local_imgs[local_img]}",f"build/{self.setting.dir_name}/{self.setting.local_imgs[local_img]}")

        # add blogs to db
        if not os.path.exists("build/blogs_db.bl"):
            with open("build/blogs_db.bl","w") as f:   
                f.write("")
        else:
            # if there is a file make sure that there is no same name blogs
            blogs_src = "" 
            with open("build/blogs_db.bl","r") as f:   
                blogs_src = f.read()

            if f":[link::{self.setting.blog_title}::" in blogs_src:
                print("saving blog same name error, plz change ur blog title in blogs_db.bl file")
            
        with open("build/blogs_db.bl","a") as f:   
            f.write(f"[{datetime.datetime.today().strftime('%Y-%m-%d')}] :[link::{self.setting.blog_title}::./{self.setting.dir_name}]:\n")
        
        self.update()


    def update(self):
        custom_info = ""
        blogs = ""
        # update main menu
        if os.path.exists("build/main_menu.bl"):
            main_menu_src = ""

            with open("build/main_menu.bl","r") as f:   
                main_menu_src  = f.read()
            
            self.transpile_src(main_menu_src)
            custom_info = self.src
        

        blogs_src = ""
        with open("build/blogs_db.bl","r") as f:   
            blogs_src  = f.read()
        
        self.transpile_src(blogs_src)
        blogs = self.src


        with open("build/index.html","w") as f:
            f.write(html_main_menu_temlplate(custom_info,blogs))