var pwd = "";
var timeout = 0;

$(document).ready(function() {
    link_to_forget();
    setTimeout(link_to_forget, 2 * 1000);

    $("tr").hover(function(){
        $(this).addClass("selected");
    },
    function(){
        $(this).removeClass("selected");
    });

    $(".pwdname").click(function(event){
        event.stopPropagation();
        pwd = $(this).parent().next().html();
        show_passwd();
    });

    $(".showdesc").click(function(){
        text = $(this).html();
        if (text == "+")
            $(this).html("-");
        else
            $(this).html("+");
        desc = $(this).parent().next();
        if (text == "+")
            desc.fadeIn();
        else
            desc.fadeOut();
            });

    $("#freeze").click(function(){
        if(timeout != 0){
            clearTimeout(timeout);
            timeout = 0;
            $(this).html("continuar");
        }
        else{
            n = parseInt($("#counter").html());
            timeout = setTimeout('pass_delete('+(n-1)+')', 1 * 1000);
            $(this).html("detener");
        }
        $("#clear").focus();
        $("#clear").select();
    });
});

function link_to_forget(){
    if(mimasterpwd != "")
        $("#forget").show();
    else
        $("#forget").hide();
    setTimeout(link_to_forget, 2 * 1000);
}

function show_passwd(){
    if (get_master("really_show()"))
        really_show();
}

function pass_delete(n){
    $("#counter").html(n);
    if(n > 0)
        timeout = setTimeout('pass_delete('+(n-1)+')', 1 * 1000);
    else{
        $("#clear").attr("value", "");
        $("#counter").hide();
    }
}

function really_show(){
    var pass = decrypt(mimasterpwd, pwd);
    $("#clear").attr("value", pass);
    $("#clear").focus();
    $("#clear").select();
    $("#counter").show();
    timeout = setTimeout('pass_delete(5)', 1 * 1000);
    
    pass = "";
}

