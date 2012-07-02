var cookie = "";
var base = "";
var user = "";
var pwd = "";

function urlencode(str) {
    return escape(str).replace(/\+/g,'%2B').replace(/%20/g, '+').replace(/\*/g, '%2A').replace(/\//g, '%2F').replace(/@/g, '%40');
}

function load(uri, f) {
    listModel.clear();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", base + "/api/" + uri, true);
    xhr.onreadystatechange = function()
    {
        if ( xhr.readyState == xhr.DONE)
        {
            if ( xhr.status == 200)
            {
                var jsonObject = eval('(' + xhr.responseText + ')');
                f(jsonObject);
            }
        }
    }
    xhr.send();
}
