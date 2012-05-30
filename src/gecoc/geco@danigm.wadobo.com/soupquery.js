
const Soup = imports.gi.Soup;

function _callback(s, sm, callback) {
    data = eval('[' + sm.response_body.data + ']');
    data = data[0];
    return callback(data);
}

function make_query(uri, data, callback) {
    s = Soup.SessionAsync.new();
    sm = Soup.Message.new('POST', uri);
    sm.set_request("application/x-www-form-urlencoded", 2, data, data.length);
    s.queue_message(sm, function(x, xm) { _callback(x, xm, callback); }, null);
    return true;
}
