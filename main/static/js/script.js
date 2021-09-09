$(document).ready(function(){
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    
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
        $.ajax({
            type: "POST",
            url: "review/",
            data: {
                'rating': _rating, 
                'comment': _comment, 
                'csrfmiddlewaretoken': csrftoken
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
        $.ajax({
            type: "POST",
            url: "review/" + _reviewId + "/reply/",
            data: {
                'content': _content,
                'csrfmiddlewaretoken': csrftoken
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
        var _parentId = localStorage.getItem("parentId")
        $('#replyForm' + _parentId).attr('class', 'collapse in');
        $('#replyList' + _parentId).attr('class', 'collapse in');
        var _id = localStorage.getItem("newReplyId");
        e = document.getElementById(_id);
        e.scrollIntoView({behavior: "auto", block: "center", inline: "center"});
        e.classList.add("animate__animated");
        e.classList.add("animate__tada");
        localStorage.clear();
    }
    
    $('[id^="deleteReview"]').on('click', function(){
        review_id = this.id.split('-')[1];
        var rating = $(this).data('rating');
        var answer = confirm(gettext('Are you sure you want to delete this review?'));
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        if (answer == true) {
            $.ajax({
                type: 'DELETE',
                url: window.location.origin + lang + 'delete-review/' + parseInt(review_id),
                data: {
                    'review_id': review_id,
                },
                dataType: 'json',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(response){
                    $("#comment" + review_id).remove();
                    var comment_count = $(document.querySelector('.badge'))[0]
                    var comment_remain = parseInt(comment_count.innerText) - 1;
                    comment_count.innerText = comment_remain;
                    var star_wrap = $('p.star-wrap');
                    var comment_wrap = $('div.comment-wrap');
                    var new_rating = parseFloat(response.new_average);
                    var rate_dict = response.rate_dict;
                    for (var i = 1; i <= 5; i++) {
                        $('#star-' + i).remove();
                    }
                    comment_wrap.children().remove();
                    for (var i = 1; i <= 5; i++) {
                        _html = '';
                        if (i <= new_rating) {
                            _html +=    `<button type="button" id="star-${i}" class="btn btn-warning btn-xs" aria-label="Left Align">
                                            <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
                                        </button>`;
                        }
                        else {
                            _html +=    `<button type="button" id="star-${i}" class="btn btn-default btn-xs" aria-label="Left Align">
                                            <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
                                        </button>`;
                        }
                        star_wrap.append(_html);
                    }
                    var _html = `<div class="col-sm-4">
                                    <div class="rating-block">
                                        <h4>${gettext("Average user rating")}</h4>
                                        <h2 class="bold padding-bottom-7">${new_rating} <small>/ 5</small></h2>`;
                    for (var i = 1; i <= 5; i++) {
                        if (i <= new_rating) {
                            _html +=        `<button type="button" class="btn btn-warning btn-sm" aria-label="Left Align">
                                                <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
                                            </button>`;
                        }
                        else {
                            _html +=        `<button type="button" class="btn btn-default btn-grey btn-sm" aria-label="Left Align">
                                                <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
                                            </button>`;
                        }
                    }
                    _html +=        `</div>
                                </div>
                                <div class="col-sm-4 col-sm-offset-1">
                                    <h4>${gettext("Rating breakdown")}</h4>
                                    <div class="count-wrap">`;
                    for (var i = 5; i >= 1; i--) {
                        _html +=        `<div class="pull-left">
                                            <div class="pull-left count-key">
                                                <div>${i}<span class="glyphicon glyphicon-star"></span></div>
                                            </div>
                                            <div class="pull-left count-progress">
                                                <div class="progress count-row">
                                                <div 
                                                    class="progress-bar progress-bar-${rate_dict[i][0]}" 
                                                    role="progressbar" aria-valuenow="${i}" aria-valuemin="0" aria-valuemax="5" style="width: ${rate_dict[i][2]}%">
                                                </div>
                                                </div>
                                            </div>
                                            <div class="pull-right count-value">${rate_dict[i][1]}</div>
                                        </div>`;
                    }
                    _html +=        `</div>
                                </div>`;
                    comment_wrap.append(_html);
                },
                error: function(rs, e){
                    console.log(rs.responseText);
                },
            });
        }
    });
    
    $('[id^="deleteReply"]').on('click', function(){
        reply_id = this.id.split('-')[1];
        review_id = $(this).attr('name').split('-')[1];
        var answer = confirm(gettext('Are you sure you want to delete this comment?'));
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        if (answer == true) {
            $.ajax({
                type: 'DELETE',
                url: window.location.origin + lang + 'delete-reply/',
                data: {
                    'reply_id': reply_id,
                },
                dataType: 'json',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(response){
                    if (response.success == true) {
                        $("#reply" + reply_id).remove();
                        replyCount = $("#replyCount" + review_id)[0]
                        newCount = parseInt(replyCount.innerText.split()[0]) - 1;
                        if (newCount == 1) {
                            replyCount.innerText = newCount + gettext(" COMMENT");
                        }
                        else {
                            replyCount.innerText = newCount + gettext(" COMMENTS");
                        }
                    }
                },
                error: function(rs, e){
                    console.log(rs.responseText);
                },
            });
        }
    });

    $('#password-reset').attr('style', 'height: 0px;');
    $('#user-info').attr('style', 'height: 0px;');

    $(window).resize(function() {
        var element = document.querySelector(".about");
        var description = $(element).data('about');
        if (description) {
            if (description.length > 50 && $(window).width() < 1000) {
                element.innerHTML = description.substring(0, description.indexOf(' ', 50)) + "...";
            }
            else element.innerHTML = description;
        }
    });

    // TOGGLE ADD TO CART ICON IN HOMEPAGE
    function toggleCartHome(y){
        x = y.getElementsByTagName("i")[0];
        if(x.classList.contains('fa-check-circle'))
        {
            x.classList.remove('fa-check-circle')
            x.classList.add('fa-cart-plus')
        }
        else
        {
            x.classList.remove('fa-cart-plus')
            x.classList.add('fa-check-circle')
        } 
    }
    
    // TOGGLE ADD TO CART ICON IN DETAIL PAGE
    function toggleCartDetail(y){
        x = y.getElementsByTagName("i")[0];
        z = y.getElementsByTagName("span")[0];
        if (x.classList.contains('fa-check-circle')) {
            x.classList.remove('fa-check-circle');
            x.classList.add('fa-cart-plus');
            z.innerText = gettext("ADD TO CART");
        }
        else {
            x.classList.remove('fa-cart-plus');
            x.classList.add('fa-check-circle');
            z.innerText = gettext("REMOVE FROM CART");
        } 
    }
    
    // ADD OR REMOVE FROM CART ON POST REQUEST
    $(document).on('click', '[id^="atc"]', function(e){
        e.preventDefault();
        var icon = e.currentTarget;
        var id = this.id;
        var food_id = $(this).attr('value');
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        $.ajax({
            type: 'POST',
            url: window.location.origin + lang + 'add-to-cart/',
            data: {
                'id': food_id,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(rs){
                if (id == "atc-detail") toggleCartDetail(icon);
                else toggleCartHome(icon);
            },
            error: function(rs, e){
                console.log("Error");
            },
        });
    });
    
    // REMOVE FROM CART ON CLICK REMOVE BUTTON
    $(document).on('click', '[id^="remove-button"]', function(e){
        e.preventDefault();
        var item_id = $(this).attr('value');
        var item_name = $(this).attr('name');
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        $.ajax({
            type: 'POST',
            url: window.location.origin + lang + 'remove-from-cart/' + item_id,
            data: {
                'item': item_name,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(rs){
                if (rs.success) {
                    $('#tb-row-'+item_id).remove();
                    var container = document.getElementsByClassName('quantity');
                    for(var i=0; i<container.length; i++) {
                        changeSubtotalOnLoad(container[i]);
                    }
                    total();
                }
            },
            error: function(rs, e){
                console.log("Error");
            },
        });
    });
    
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
        if (!tbody) return;

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
    
    $("#checkout").on('click', function(){
        var tbody = $("#all_foods")[0];
        var cfs = $("#checkoutfs")[0];
        var pdict = {};

        for (var i = 0; i < tbody.rows.length; i++) {
            PID = tbody.rows[i].cells[1].getElementsByClassName('pid')[0].innerText;
            noitems = tbody.rows[i].cells[3].getElementsByTagName('input')[0].value;
            pdict[PID] = noitems;
        }
        cfs.getElementsByTagName('input')[1].value = JSON.stringify(pdict);
        cfs.submit();
    });
    
    $("[id^='order-cancel']").on('click', function(){
        var uuid = this.id.replace("order-cancel-", '');
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        var answer = confirm(gettext('Are you sure you want to cancel this order?'));
        if (answer == true) {
            $.ajax({
                type: 'POST',
                url: window.location.origin + lang + 'cancel-order/',
                data: {
                    'uuid': uuid,
                    'csrfmiddlewaretoken': csrftoken
                },
                dataType: 'json',
                success: function(response){
                    if (response.success == true) {
                        var _html = `<mark>${response.new_status}</mark>`
                        $('#action-button-' + uuid)[0].innerHTML = '';
                        $('#order-status-' + uuid)[0].innerHTML = _html;
                    }
                },
                error: function(rs, e){
                    console.log(rs.responseText);
                },
            });
        }
    });
    
    $("[id^='save-']").on('click', function(){
        localStorage.setItem("saveButtonClicked", this.id);
    });
    
    if (localStorage.getItem("saveButtonClicked")) {
        var button_id = localStorage.getItem("saveButtonClicked")
        e = document.getElementById(button_id).offsetParent;
        e.scrollIntoView({behavior: "auto", block: "center", inline: "center"});
        localStorage.clear();
    }
    
    $("#rzp-button1").on('click', function(){
        var order_id = $(this).data('order');
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        $.ajax({
            type: 'POST',
            url: window.location.origin + lang + 'open-payment/',
            data: {
                'lang': lang,
                'order_id': order_id,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(rs){
                var order = rs.order;
                var options = {
                    "key": `${rs.razorpay_id}`, 
                    "amount": `${rs.amount}`, 
                    "currency": "USD",
                    "name": "Online Restaurant",
                    "description": "Test Transaction",
                    "image": "/static/img/logo.jpeg",
                    "order_id": `${rs.rp_order_id}`, 
                    "callback_url": `${rs.callback_url}`,
                    "prefill": {
                        "name": `${order.recipient}`,
                        "email": `${rs.email}`,
                        "contact": `+94${order.phone_number}`,
                    },
                    "notes": {
                        'shipping_address': `${order.address}`,
                        'city': `${order.city}`,
                        'country': `${order.country}`,
                        'zip_code': `${order.zip_code}`,
                    },
                    "theme": {
                        "color": "#910DFD"
                    }
                };
                var rzp1 = new Razorpay(options);
                rzp1.open();
            },
            error: function(rs, e){
                console.log("Error");
            },
        });
    });
    
    function toggleSave(x){
        if(x.classList.contains('far'))
        {
            x.classList.remove('far')
            x.classList.add('fas')
        }
        else
        {
            x.classList.remove('fas')
            x.classList.add('far')
        } 
    }
    
    // ADD OR REMOVE FROM WISHLIST
    $(document).on('click', '[id^="like"]', function(e){
        e.preventDefault();
        var icon = e.currentTarget;
        var food_id = $(this).attr('value');
        var option = $(this).attr('name');
        if (window.location.href.indexOf('/en-us/') != -1) lang = '/en-us/';
        else lang = '/vi/';
        if (option == 'wishlist-view') {
            var wishlist_len = $('#wishlist-p ul em')[0];
            var new_wishlist_len = parseInt(wishlist_len.innerText.split(' ')[2]) - 1;
            $.ajax({
                type: 'DELETE',
                url: window.location.origin + lang + 'remove-from-wishlist/' + parseInt(food_id),
                dataType: 'json',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(rs){
                    $('#wishlist-' + food_id).remove();
                    var _html = '';
                    if (new_wishlist_len == 1) {
                        _html += `${gettext("You have 1 item in wishlist")}`;
                    }
                    else {
                        _html += `${gettext("You have")} ${new_wishlist_len} ${gettext("items in wishlist")}`;
                    }
                    wishlist_len.innerText = _html;
                },
                error: function(rs, e){
                    console.log("Error");
                },
            });
        }
        else {
            $.ajax({
                type: 'POST',
                url: window.location.origin + lang + 'add-to-wishlist/',
                data: {
                    'food_id': food_id,
                    'csrfmiddlewaretoken': csrftoken
                },
                dataType: 'json',
                success: function(rs){
                    toggleSave(icon.children[0]);
                },
                error: function(rs, e){
                    console.log("Error");
                },
            });
        }
    });
});
