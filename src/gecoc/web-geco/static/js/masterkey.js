var mimasterpwd = "";
var fun = "";

function _ok() {
    $('#pwdForm').modal('hide');

    mimasterpwd = $("#masterpwd").attr("value");
    $("#masterpwd").attr("value", "");

    setTimeout(forget, 10 * 60 * 1000);
    eval(fun);
    return false;
}

$(document).ready(function() {
    $('#masterpwd').keypress(function(e){
        if(e.which == 13) {
            _ok();
        }
    });

    $("#rec").click(function(){
        _ok();
    });
})

function get_master(f){
    if(mimasterpwd == ""){
        $('#pwdForm').modal('show');
        $("#masterpwd").select();
        fun = f;
        return false;
    } else {
        return true;
    }
}

function forget(){
    delete mimasterpwd;
    mimasterpwd = "";
    return false;
}
