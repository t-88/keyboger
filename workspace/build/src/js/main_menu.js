window.onload = () => {
    const blogsNode = document.getElementById("blogs");
    if (blogsNode.children.length == 0) {
        blogsNode.innerHTML += "<center><p style='color:#909090'>No Blogs Yet :)</p></center>"
    }    
}