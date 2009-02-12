var mimasterpwd = "";
var fun = "";

$(document).ready(function() {
    $("#rec").click(function(){
        mimasterpwd = $("#masterpwd").attr("value");
        $("#masterpwd").attr("value", "");
        $(".input").fadeOut(300);
        $("#overlay").fadeOut(300);
        setTimeout(forget, 10 * 60 * 1000);
        eval(fun);
    });

    $(".close").click(function(){
        $(".input").fadeOut(300);
        $("#overlay").fadeOut(300);
    });
})

function get_master(f){
    if(mimasterpwd == ""){
        $(".input").fadeIn(300);
        $("#masterpwd").select();
        $("#overlay").fadeIn(300);
        fun = f;
        return false;
    }
    else {
        return true;
    }
}

function forget(){
    delete mimasterpwd;
    mimasterpwd = "";
    return false;
}

