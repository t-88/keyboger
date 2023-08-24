import os
import shutil
import datetime

from keyboger_tokenizer import KeybogerTokenizer
from keyboger_parser import KeybogerParser , AstType
import keyboger_consts



def html_blog_temlplate(src,about = ""):
    return f"""<html>
    <head> <link rel="stylesheet" href="../../src/css/style.css"> </head>
    <body>
        <header> 
            <img src="../../src/imgs/pic.png" alt="profile-pic" id="img">
            <a href="../../index.html">Main-Menu</a>
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
            {about}

            <button>close</button>
        </div>
    </div>

    <script src="../../src/js/main.js"> </script>
</html>"""

def html_main_menu_temlplate(custom_info,blogs):
    return f"""<html>
    <head> <link rel="stylesheet" href="src/css/style.css"> </head>
    <head> <link rel="stylesheet" href="src/css/main_menu.css"> </head>
    <body>
        <header id="main-menu-header"> 
            <!-- <img src="src/pic.png" alt="profile-pic" id="img"> -->
            <p id="blog-name">
                Keyboger
            </p>
            <div id="personal-links">
                <a href="https://github.com/"><img src="src/imgs/github-mark-white.svg" alt="" width="35px"></a>
                <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"><img src="src/imgs/youtube.png" alt="" width="50px"></a>
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
    <script src="src/js/main_menu.js"></script>
</html>"""


def check_files():
    # checks for blogs_db.bl and main_menu.bl files if they exist pass else create them

    # add blogs to db
    if not os.path.exists(keyboger_consts.BLOGS_DIR + "blogs_db.bl"):
        # create the file
        with open(keyboger_consts.BLOGS_DIR + "blogs_db.bl","w") as f:   
            f.write("")

        

class KeybogerHtmlTranspiler:
    def __init__(self,setting = None):
        self.src = ""
        self.setting = setting 

        check_files()
    
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
            
            if type(ast.content) == list:
                for elem in ast.content:
                    self.transpile(elem)
            else:            
                self.transpile(ast.content)
            self.src += "</li>"

        elif ast.typ == AstType.ordered_list:
            value = ""
            if ast.data['typ'] == "1":
                value =  f"value={ast.data['idxer']}"
                self.src += f"<li {value}>"
            else:
                if "start" in ast.data:
                    value =  f"value={ast.data['start'] + 1}"
                self.src += f"<li {value}>"

            if type(ast.content) == list:
                for elem in ast.content:
                    self.transpile(elem)
            else:            
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
                ast.content[0].content = ast.content[0].content.strip()
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
                self.setting.local_imgs[ast.content[0].content] = ast.content[1].content.strip()
                return f"<img src='{ast.content[1].content}' alt={ast.content[0].content}>" 
            elif len(ast.content) == 1:
                # name || path
                text = ast.content[0].content.strip()
                if text in self.setting.local_imgs:
                    # name
                    return f"<img src='{self.setting.local_imgs[text]}' alt={text}>" 
                else:
                    # path
                    self.setting.local_imgs[ast.content[0].content] = ast.content[0].content.strip()
                    return f"<img src='{text}' alt={text}>" 
        
        elif ast.data["id"] == "img":
            if len(ast.content) == 2:
                # name , path 
                return f"<img src='{ast.content[1].content}' alt={ast.content[0].content}>" 
            else:
                # name || path 
                if ast.content[0].content in self.setting.online_imgs:
                    # name
                    return f"<img src='{self.setting.online_imgs[ast.content[0].content]}' alt={ast.content[0].content}>" 
                else:
                    # path
                    return f"<img src='{ast.content[0].content}' alt={ast.content[0].content}>" 

        elif ast.data["id"] == "css":
            return f"<span style={ast.content[0].content}>{ast.content[1].content}</span>"
        
        assert False , f"Unreachable {ast}" 
    


    def save(self,src_dir,src = None):
        assert self.setting != None , "KeybogerHtmlTranspiler setting not defined"
        if src != None: self.src = src

        # if there is a file make sure that there is no same name blogs
        blogs_src = "" 
        with open(keyboger_consts.BLOGS_DB_PATH,"r") as f:   
            blogs_src = f.read()
        if f":[link::{self.setting.blog_title}::" in blogs_src:
            print("saving blog same name error, plz change ur blog title in blogs_db.bl file")
            assert False , "name collision plz change blog title or remove blog from blog db"



        # save new blog
        if not os.path.exists(keyboger_consts.BUILD_BLOGS_DIR + self.setting.dir_name):
            os.mkdir(keyboger_consts.BUILD_BLOGS_DIR + self.setting.dir_name)

        about_bl = "" 
        with open(keyboger_consts.BLOGS_DIR + "about.bl","r") as f:
            about_bl = f.read()
        about_html = transpile_src(about_bl)
            

        with open(keyboger_consts.BUILD_BLOGS_DIR + self.setting.dir_name + "/" + "index.html","w") as f:
            f.write(html_blog_temlplate(self.src,about_html))
        
        # move local imgs
        for local_img in self.setting.local_imgs:
            shutil.copy2(f"{src_dir}{self.setting.local_imgs[local_img]}",
                         keyboger_consts.BUILD_BLOGS_DIR + self.setting.dir_name + "/" +  self.setting.local_imgs[local_img])

        

        # save blog in db
        with open(keyboger_consts.BLOGS_DB_PATH,"a") as f:   
            f.write(f"[{datetime.datetime.today().strftime('%Y-%m-%d')}] :[link::{self.setting.blog_title}::./blogs/{self.setting.dir_name}]:\n")

        self.update()

    def save_test(self,src_dir,src = None):
        assert self.setting != None , "KeybogerHtmlTranspiler setting not defined"
        if src != None: self.src = src

        # save new blog
        if not os.path.exists(keyboger_consts.TEST_DIR):
            os.mkdir(keyboger_consts.TEST_DIR)
            
        if not os.path.exists(keyboger_consts.TEST_DIR + self.setting.dir_name):
            os.mkdir(keyboger_consts.TEST_DIR + self.setting.dir_name)


        about_bl = "" 
        with open(keyboger_consts.BLOGS_DIR + "about.bl","r") as f:
            about_bl = f.read()
        about_html = transpile_src(about_bl)
            

        with open(keyboger_consts.TEST_DIR + self.setting.dir_name + "/" + "index.html","w") as f:
            f.write(html_blog_temlplate(self.src,about_html))
        
        # move local imgs
        for local_img in self.setting.local_imgs:
            shutil.copy2(f"{src_dir}{self.setting.local_imgs[local_img]}",
                         keyboger_consts.TEST_DIR + self.setting.dir_name + "/" + self.setting.local_imgs[local_img])

        


    def update(self):
        custom_info = ""
        blogs = ""
        
        # update main menu
        if os.path.exists(keyboger_consts.MAIN_MENU_HEADER_PATH):
            main_menu_src = ""
            with open(keyboger_consts.MAIN_MENU_HEADER_PATH,"r") as f:   
                main_menu_src  = f.read()
            
            custom_info = transpile_src(main_menu_src)

        blogs_src = ""
        with open(keyboger_consts.BLOGS_DB_PATH,"r") as f:   
            blogs_src  = f.read()
        
        blogs = transpile_src(blogs_src)


        with open(keyboger_consts.BUILD_DIR +"index.html","w") as f:
            f.write(html_main_menu_temlplate(custom_info,blogs))





            

def transpile_src(src):
    # takes a src and returns html

    tknzer = KeybogerTokenizer()
    tknzer.tokenize(src,is_src = True)
    

    parser = KeybogerParser()
    parser.parse(tknzer.tknz)

    transpiler = KeybogerHtmlTranspiler(parser.setting)
    transpiler.start_transpiling(parser.head)

    return transpiler.src