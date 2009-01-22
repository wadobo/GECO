var mimasterpwd = "";

$(document).ready(function() {
    $(".pwdname").click(function(){
        var pwd = $(this).next().html();
        $(".input").fadeIn(300);
        $("#overlay").fadeIn(300);
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
        setTimeout(olvidar, 10 * 60 * 1000);
    });
});

function alertar(){
    alert(mimasterpwd);
}

function olvidar(){
    mimasterpwd = "";
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

    var value = slowAES.decrypt(cypher, 256, slowAES.modeOfOperation.CBC, realkey, 16, realiv);
    return array_to_string(value);
};
