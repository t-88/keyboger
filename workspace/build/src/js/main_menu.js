window.onload = () => {
    const blogsNode = document.getElementById("blogs");
    content =  blogsNode.querySelectorAll("p")
    if (content.length == 0) {
        blogsNode.innerHTML = "<center><p style='color:#909090'>No Blogs Yet :)</p></center>"
    }    
}