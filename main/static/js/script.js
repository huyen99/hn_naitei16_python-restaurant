// FLASH MESSAGES
var close = document.getElementsByClassName("closebtnmsg");
var i;

for (i = 0; i < close.length; i++) {
    close[i].onclick = function(){
        var div = this.parentElement;
        div.style.opacity = "0";
        setTimeout(function(){ div.style.display = "none"; }, 600);
    }
}

function openNav() {
    document.getElementById("mySidenav").style.width = "100%";
    document.querySelector('body').style.overflow = 'hidden';
}
  
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.querySelector('body').style.overflow = 'auto';
}

function openSearch() {
    document.getElementById("myOverlay").style.display = "block";
    document.querySelector('body').style.overflow = 'hidden';
}

function closeSearch() {
    document.getElementById("myOverlay").style.display = "none";
    document.querySelector('body').style.overflow = 'auto';
}

document.getElementById("toggle_open_search").onclick = openSearch;

document.getElementById("toggle_close_search").onclick = closeSearch;

document.getElementById("toggle_open_nav").onclick = openNav;

document.getElementById("toggle_close_nav").onclick = closeNav;

if (window.location.search.includes('query')) {
    element = document.getElementById("search-result") ? document.getElementById("search-result") : document.getElementById("menu");
    element.scrollIntoView();
}

const navbar = document.querySelector('.mynavbar');
window.onscroll = () => {
    if (window.scrollY > 100) {
        navbar.classList.add('nav-active');
    } else {
        navbar.classList.remove('nav-active');
    }
};

$(document).ready(function(){
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('#scroll').fadeIn();
        } else {
            $('#scroll').fadeOut(); 
        }
    });
    $('#scroll').click(function(){ 
        $("html, body").animate({ scrollTop: 0 }, 600); 
        return false; 
    });
});

function toggleCart(y){
    x = y.getElementsByTagName("i")[0]
    z = y.getElementsByTagName("span")[0]
    if(x.classList.contains('fa-check-circle'))
    {
        x.classList.remove('fa-check-circle')
        x.classList.add('fa-cart-plus')
        z.innerText = "ADD TO CART"
    }
    else
    {
        x.classList.remove('fa-cart-plus')
        x.classList.add('fa-check-circle')
        z.innerText = "REMOVE FROM CART"
    } 
}
