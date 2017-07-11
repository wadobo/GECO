const Soup = imports.gi.Soup;
const Gio = imports.gi.Gio;
const Extension = imports.misc.extensionUtils.getCurrentExtension();


function urlencode(str) {
    return escape(str).replace(/\+/g,'%2B').replace(/%20/g, '+').replace(/\*/g, '%2A').replace(/\//g, '%2F').replace(/@/g, '%40');
}

function _callback(s, sm, callback) {
    let data = eval('[' + sm.response_body.data + ']');
    data = data[0];
    return callback(data);
}

function make_query(uri, data, callback) {
    let s = Soup.SessionAsync.new();
    let sm = Soup.Message.new('POST', uri);
    sm.set_request("application/x-www-form-urlencoded", 2, data, data.length);
    s.queue_message(sm, function(x, xm) { _callback(x, xm, callback); }, null);
    return true;
}

// getting the keybinding code from hkb extension
// http://amanda.darkdna.net/hkb/
function getSettings() {
    let dir = Extension.dir.get_child('schemas').get_path();
    let source = Gio.SettingsSchemaSource.new_from_directory(dir,
            Gio.SettingsSchemaSource.get_default(),
            false);

    if(!source) {
        throw new Error('Error Initializing the thingy.');
    }

    let schema = source.lookup('org.gnome.shell.extensions.geco', false);

    if(!schema) {
        throw new Error('Schema missing.');
    }

    return new Gio.Settings({
        settings_schema: schema
    });
}
