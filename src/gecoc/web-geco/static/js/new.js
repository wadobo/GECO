jQuery(document).ready(function() {
		$('#password').keyup(function(){
            $('#result').html(passwordStrength($('#password').val(),$('#username').val()));
            $('#same').html(samepass($('#password').val(),$('#password2').val()));
        })
		$('#password2').keyup(function(){
            $('#same').html(samepass($('#password').val(),$('#password2').val()));
        })

})

function samepass(p1, p2){
    if (p1 != p2)
        return "No coinciden!";
    else
        return "";
}

function generate_pass(){
    l = parseInt($("#length").val());
    punct = $("#punct").attr('checked');
    low = $("#low").attr('checked');
    up = $("#up").attr('checked');
    digits = $("#digits").attr('checked');
    new_pass = generate(l, low, up, digits, punct);
    $('#password').val(new_pass);
    $('#password2').val(new_pass);
    $('#gen').val(new_pass);

    $('#result').html(passwordStrength($('#password').val(),$('#username').val()));
    $('#same').html(samepass($('#password').val(),$('#password2').val()));
    set_pass();
    return false;
}

function set_pass(){
    if (get_master("really_set()"))
        really_set();
    return false;
}

function really_set(){
    cipher = encrypt(mimasterpwd, $("#password").val());
    $("#cpassword").val(cipher);
    return false;
}

function show(){
    $("#show_pass").show();
    $("#noshow").hide();
    return false;
}
function hide(){
    $("#show_pass").hide();
    $("#noshow").show();
    return false;
}
