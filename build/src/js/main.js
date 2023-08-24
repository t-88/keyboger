
var aboutNode;
var aboutButtonNode;
var aboutLinkNode;

window.onload = () => {
    aboutNode = document.getElementById("about");
    aboutNode.style.display = "none";

    aboutButtonNode = aboutNode.querySelectorAll("button")[0]
    aboutButtonNode.onclick = hide_about;
    
    aboutLinkNode = document.getElementById("about-link");
    aboutLinkNode.onclick = show_about;
}



function show_about(e) {
    e.preventDefault();
    aboutNode.style.display = "";
}

function hide_about() {
    aboutNode.style.display = "none";
    document.documentElement.style.margin =  "";
    document.documentElement.style.padding = "";
}


