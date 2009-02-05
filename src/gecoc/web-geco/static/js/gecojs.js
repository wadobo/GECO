var mimasterpwd = "";
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

    $(".pwdname").click(function(){
        pwd = $(this).next().html();
        show_passwd();
    });
    $(".close").click(function(){
        $(".input").fadeOut(300);
        $("#overlay").fadeOut(300);
    });

    $("#rec").click(function(){
        mimasterpwd = $("#masterpwd").attr("value");
        $("#masterpwd").attr("value", "");
        $(".input").fadeOut(300);
        $("#overlay").fadeOut(300);
        setTimeout(forget, 10 * 60 * 1000);
        really_show();
    });
    $("#forget").click(function(){
        forget();
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
    if(mimasterpwd == ""){
        $(".input").fadeIn(300);
        $("#masterpwd").select();
        $("#overlay").fadeIn(300);
    }
    else {
        really_show();
    }
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

function forget(){
    mimasterpwd = "";
    pwd = "";
}

function array_of_bytes(key){
    var retkey = new Array();
    for (var i=0; i<key.length; i+=2){
        retkey[i/2] = parseInt(key.charAt(i) +
                key.charAt(i+1), 16);
    }
    return retkey;
}

function array_of_bytes2(key){
    var retkey = [];
    for (var i=0; i<key.length; i++){
        retkey.push(key.charCodeAt(i));
    }
    while (retkey.length % 16){
        retkey.push(0);
    }
    return retkey;
}

function array_to_string(key){
    var retkey = '';
    for (var i=0; i<key.length; i++){
        value = String.fromCharCode(key[i]);
        if(key[i] == 0)
            break;
        retkey += value;
    }
    return retkey;
}

function getkey(key){
    var hexkey = SHA256(key);
    return array_of_bytes(hexkey);
}
function getiv(key){
    var hexkey = hex_md5(key);
    return array_of_bytes(hexkey);
}

function encrypt(key, clear){
    var realkey = getkey(key);
    var realiv = getiv(key);

    var value = slowAES.encrypt(array_of_bytes2(clear), slowAES.modeOfOperation.CBC, realkey,
            16, realiv);
    return value.cipher;
};

function decrypt(key, cypher){
    var realkey = getkey(key);
    var realiv = getiv(key);
    var realcypher = cypher.split('#');

    var value = slowAES.decrypt(realcypher, 256, slowAES.modeOfOperation.CBC, realkey, 16, realiv);
    return array_to_string(value);
};
