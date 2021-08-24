$(document).ready(function(){
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

    // SIDE NAVBAR
    function openNav() {
        document.getElementById("mySidenav").style.width = "100%";
        document.querySelector('body').style.overflow = 'hidden';
    }
    
    function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
        document.querySelector('body').style.overflow = 'auto';
    }
    
    document.getElementById("toggle_open_nav").onclick = openNav;
    document.getElementById("toggle_close_nav").onclick = closeNav;

    // SEARCH
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

    if (window.location.search.includes('query')) {
        element = document.getElementById("search-result") ? document.getElementById("search-result") : document.getElementById("menu");
        element.scrollIntoView();
    }

    // NAVBAR
    const navbar = document.querySelector('.mynavbar');
    window.onscroll = () => {
        if (window.scrollY > 100) {
            navbar.classList.add('nav-active');
        } else {
            navbar.classList.remove('nav-active');
        }
    };

    // PAGE SCROLL
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

    // SUBMIT REVIEW ON CLICK
    $("#submitComment").on('click', function(){
        localStorage.clear();
        var _rating = document.querySelector('input[name="rating"]:checked') ? 
            document.querySelector('input[name="rating"]:checked').value : 0;
        var _comment = $("#addComment").val();
        var _csrf_token = $("#commentForm [name=csrfmiddlewaretoken]").val();
        $.ajax({
            type: "POST",
            url: "review/",
            data: {
                'rating': _rating, 
                'comment': _comment, 
                'csrfmiddlewaretoken': _csrf_token
            },
            dataType: 'json',
            success: function(response){
                if (response.review_id != -1) {
                    var _id = "comment" + response.review_id;
                    localStorage.setItem("newCommentId", _id);
                    location.reload();
                }
            },
            error: function(rs, e){
                console.log(rs.responseText);
            },
        });
    })
    
    // SCROLL INTO NEW REVIEW
    if (localStorage.getItem("newCommentId")) {
        var _id = localStorage.getItem("newCommentId");
        e = document.getElementById(_id);
        e.scrollIntoView({behavior: "auto", block: "center", inline: "center"});
        e.classList.add("animate__animated");
        e.classList.add("animate__tada");
        localStorage.clear();
    }
    
    // SUBMIT REPLY ON CLICK
    $('[id^="submitReply"]').on('click', function(){
        localStorage.clear();
        var _reviewId = $(this).data('parent');
        var _content = $("#addReply" + _reviewId).val();
        var _csrf_token = $("#replyForm" + _reviewId + " [name=csrfmiddlewaretoken]").val();
        $.ajax({
            type: "POST",
            url: "review/" + _reviewId + "/reply/",
            data: {
                'content': _content,
                'csrfmiddlewaretoken': _csrf_token
            },
            dataType: 'json',
            success: function(response){
                if (response.reply_id != -1) {
                    var _id = "reply" + response.reply_id;
                    localStorage.setItem("newReplyId", _id);
                    localStorage.setItem("parentId", _reviewId);
                    location.reload();
                }
            },
            error: function(rs, e){
                console.log(rs.responseText);
            },
        });
    });
    
    // SCROLL INTO NEW REPLY
    if (localStorage.getItem("newReplyId")) {
        $("#replyForm" + localStorage.getItem("parentId")).collapse();
        $("#replyList" + localStorage.getItem("parentId")).collapse();
        var _id = localStorage.getItem("newReplyId");
        e = document.getElementById(_id);
        e.classList.add("animate__animated");
        e.classList.add("animate__tada");
        localStorage.clear();
    }

    // TOGGLE ADD TO CART ICON
    function toggleCart(y){
        x = y.getElementsByTagName("i")[0]
        z = y.getElementsByTagName("span")[0]
        if (x.classList.contains('fa-check-circle')) {
            x.classList.remove('fa-check-circle')
            x.classList.add('fa-cart-plus')
            z.innerText = "ADD TO CART"
        }
        else {
            x.classList.remove('fa-cart-plus')
            x.classList.add('fa-check-circle')
            z.innerText = "REMOVE FROM CART"
        } 
    }
    
    // CHANGE SUBTOTAL ON CART'S QUANTITY UPDATE
    document.querySelectorAll(".quantity").forEach(qty => qty.addEventListener("change", changeSubtotal));
    document.querySelector('body').onload = function() {
        var container = document.getElementsByClassName('quantity');
        for(var i=0; i<container.length; i++) {
            changeSubtotalOnLoad(container[i]);
        }
        total();
    };

    // CHANGE SUBTOTAL
    function changeSubtotal(element) {
        var price = this.previousElementSibling.innerHTML;
        var quantity = element.target.value; 
        var subtotal = (parseFloat(price) * parseInt(quantity)).toFixed(2);
        this.nextElementSibling.innerHTML = subtotal;
        total();
    }

    // CHANGE SUBTOTAL ON LOAD
    function changeSubtotalOnLoad(element) {
        var price = element.previousElementSibling.innerHTML;
        var quantity = element.getElementsByTagName('input')[0].value; 
        var subtotal = (parseFloat(price) * parseInt(quantity)).toFixed(2);
        element.nextElementSibling.innerHTML = subtotal;
    }

    // SUM TOTAL
    function total(){
        var totalDisplay = document.getElementById("total_display");
        var totalDisplay2 = document.getElementById("total_display2");
        var endtotalDisplay = document.getElementById("endtotal_display");
        var totalQuantity = document.getElementById("total_quantity");
        var delvCharges = document.getElementById("delv_charges");

        var sum = 0;
        var noitems = 0;
        var tbody = document.getElementById("all_foods");

        for (var i = 0; i < tbody.rows.length; i++) {
            sum = sum + parseFloat(tbody.rows[i].cells[4].innerHTML);
            noitems = noitems + parseInt(tbody.rows[i].cells[3].getElementsByTagName('input')[0].value);
        }
        
        var total = sum.toFixed(2);
        totalDisplay.innerHTML = "$"+total;
        totalDisplay2.innerHTML = "$"+total;
        totalQuantity.innerHTML = noitems;
        endtotalDisplay.innerHTML = delvCharges.innerText ? (parseFloat(total)+parseFloat(delvCharges.innerText)).toFixed(2) : "$"+total;
    }
});
