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
        var value = String.fromCharCode(key[i]);
        if(key[i] == 0)
            break;
        retkey += value;
    }
    return retkey;
}

function getkey(key){
    var hexkey = Sha256.SHA256(key);
    return array_of_bytes(hexkey);
}
function getiv(key){
    var hexkey = Md5.hex_md5(key);
    return array_of_bytes(hexkey);
}

function encrypt(key, clear){
    var realkey = getkey(key);
    var realiv = getiv(key);

    var value = SlowAes.slowAES.encrypt(array_of_bytes2(clear), SlowAes.slowAES.modeOfOperation.CBC, realkey,
            16, realiv);
    c = value.cipher.join("#");
    return c
};

function decrypt(key, cypher){
    var realkey = getkey(key);
    var realiv = getiv(key);
    var realcypher = cypher.split('#');

    var value = SlowAes.slowAES.decrypt(realcypher, 256, SlowAes.slowAES.modeOfOperation.CBC, realkey, 16, realiv);
    return array_to_string(value);
};

function getRandomNum(lbound, ubound) {
    return (Math.floor(Math.random() * (ubound - lbound)) + lbound);
}
function getRandomChar(number, lower, upper, other) {
    var numberChars = "0123456789";
    var lowerChars = "abcdefghijklmnopqrstuvwxyz";
    var upperChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    var otherChars = "`~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/? ";
    var charSet = "";
    if (number == true)
        charSet += numberChars;
    if (lower == true)
        charSet += lowerChars;
    if (upper == true)
        charSet += upperChars;
    if (other == true)
        charSet += otherChars;
    return charSet.charAt(getRandomNum(0, charSet.length));
}
function generate(length, Lower, Upper, Number, Other) {
    var rc = "";
    for (var idx = 0; idx < length; ++idx) {
        rc = rc + getRandomChar(Number, Lower, Upper, Other);
    }
    return rc;
}
