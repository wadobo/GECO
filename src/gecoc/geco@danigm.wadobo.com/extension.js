const St = imports.gi.St;
const Shell = imports.gi.Shell;
const Pango = imports.gi.Pango;
const Clutter = imports.gi.Clutter;
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const Main = imports.ui.main;
const Tweener = imports.ui.tweener;
const PopupMenu = imports.ui.popupMenu;
const PanelMenu = imports.ui.panelMenu;
const ModalDialog = imports.ui.modalDialog;
const Lang = imports.lang;
const Meta = imports.gi.Meta;
const Gtk = imports.gi.Gtk;


const ExtensionUtils = imports.misc.extensionUtils;
const Extension = ExtensionUtils.getCurrentExtension();

const Utils = Extension.imports.utils;
const Gecojs = Extension.imports.gecojs;

const mySettings = Utils.getSettings();


// getting the set icon code from shellshape extension
// http://gfxmonk.net/shellshape/
//
// A BIT HACKY: add the shellshape icon directory to the current theme's search path,
// as this seems to be the only way to get symbolic icons loading properly.
(function() {
    var theme = imports.gi.Gtk.IconTheme.get_default();
    let icon_dir = Extension.dir.get_child('icons');
    if(icon_dir.query_exists(null)) {
        global.log("adding icon dir: " + icon_dir.get_path());
        theme.append_search_path(icon_dir.get_path());
    } else {
        global.log("no icon dir found at " + icon_dir.get_path() + " - assuming globally installed");
    }
})();

let pwd = "123";
let username = "username";
let masterpwd = "";
let base = 'http://localhost:8080';
let indicator;
let account_pressed = false;

let mdata = "";
let conffile= "";
let conffile_data = "";

let text, button;
let cookie;
let passwords;

let dialog;

// always call this function with ask_for_password_dialog
function refresh() {
    indicator._refresh();
}

const key_bindings = {
    'show-geco': function() {
        indicator.menu.toggle();
        indicator.search.grab_key_focus();
    },
    'refresh-geco': function() {
        ask_for_password_dialog(function() {
            refresh();
        });
    },
};


const QuestionDialog = new Lang.Class({
    Name: 'QuestionDialog',
    Extends: ModalDialog.ModalDialog,

    next: null,

    _init: function() {
        this.parent({ styleClass: 'question-dialog' });

        let mainContentLayout = new St.BoxLayout();
        this.contentLayout.add(mainContentLayout, { x_fill: true,
                                                    y_fill: false });

        let messageLayout = new St.BoxLayout({ vertical: true });
        mainContentLayout.add(messageLayout,
                              { y_align: St.Align.START });

        this.subjectLabel = new St.Label({ style_class: 'geco-heading' });
        this.subjectLabel.clutter_text.ellipsize = Pango.EllipsizeMode.NONE;
        this.subjectLabel.clutter_text.line_wrap = true;
        this.subjectLabel.set_text(_("GECO master password"));
        this.subjectLabel.show();

        messageLayout.add(this.subjectLabel,
                          { y_fill:  false,
                            y_align: St.Align.START });

        this.entry = new St.Entry({ style_class: 'geco-pwd-entry',
                                    text: "", can_focus: true,
                                    reactive: true });
        this.entry.clutter_text.set_password_char('\u25cf');
        let d = this;
        this.entry.clutter_text.connect('key-press-event', function(o,e)
        {
            let symbol = e.get_key_symbol();
            if (symbol == Clutter.Return) {
                d._onOk();
            }
        });


        messageLayout.add(this.entry,
                          { y_fill:  true,
                            y_align: St.Align.START });

        this._okButton = { label:  _("Ok"),
                           action: Lang.bind(this, this._onOk),
                           key:    Clutter.KEY_Return,
                         };

        this.setButtons([{ label: _("Cancel"),
                           action: Lang.bind(this, this._onCancel),
                           key:    Clutter.KEY_Escape,
                         },
                         this._okButton]);
    },

    _onOk: function () {
        text = this.entry.get_text();
        if (!text) {
            return;
        }

        masterpwd = text;
        GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 300, forget_master);
        this.close(global.get_current_time());
        if (this.next) {
            this.next();
        }
    },

    _onCancel: function() {
        this.close(global.get_current_time());
    },
});


const ConfigDialog = new Lang.Class({
    Name: 'ConfigDialog',
    Extends: ModalDialog.ModalDialog,

    _init: function() {
        this.parent({ styleClass: 'config-dialog' });

        let mainContentLayout = new St.BoxLayout();
        this.contentLayout.add(mainContentLayout, { x_fill: true,
                                                    y_fill: false });

        let messageLayout = new St.BoxLayout({ vertical: true });
        mainContentLayout.add(messageLayout,
                              { y_align: St.Align.START });

        let subjectLabel = new St.Label({ style_class: 'geco-heading'});
        subjectLabel.set_text(_("GECO config"));
        messageLayout.add(subjectLabel);

        let serverLabel = new St.Label();
        serverLabel.set_text(_("server:"));
        messageLayout.add(serverLabel);
        this.serverEntry = new St.Entry({ style_class: 'geco-pwd-entry',
                                          text: base, can_focus: true,
                                          reactive: true });
        messageLayout.add(this.serverEntry);

        let userLabel = new St.Label();
        userLabel.set_text(_("user:"));
        messageLayout.add(userLabel);
        this.userEntry = new St.Entry({ style_class: 'geco-pwd-entry',
                                          text: username, can_focus: true,
                                          reactive: true });
        messageLayout.add(this.userEntry);

        let pwdLabel = new St.Label();
        pwdLabel.set_text(_("password:"));
        messageLayout.add(pwdLabel);
        this.pwdEntry = new St.Entry({ style_class: 'geco-pwd-entry',
                                       text: pwd, can_focus: true,
                                       reactive: true });
        this.pwdEntry.clutter_text.set_password_char('\u25cf');
        messageLayout.add(this.pwdEntry);


        this._okButton = { label:  _("Ok"),
                           action: Lang.bind(this, this._onOk),
                           key:    Clutter.KEY_Return,
                         };

        this.setButtons([{ label: _("Cancel"),
                           action: Lang.bind(this, this._onCancel),
                           key:    Clutter.KEY_Escape,
                         },
                         this._okButton]);
    },

    _onOk: function () {
        username = this.userEntry.get_text();
        pwd = this.pwdEntry.get_text();
        base = this.serverEntry.get_text();

        ask_for_password_dialog(function() {
            store_config();
            load_config();
        });

        this.close(global.get_current_time());
    },

    _onCancel: function() {
        this.close(global.get_current_time());
    },
});


function forget_master() {
    masterpwd = "";
    indicator._set_icon("lock");
}

function config_dialog() {
    ask_for_password_dialog(function() {
        load_config();
        dialog = new ConfigDialog();
        dialog.open(global.get_current_time());
    });
}

function ask_for_password_dialog(next) {
    if (masterpwd === "") {
        dialog = new QuestionDialog();
        dialog.next = function() {
            next();
            indicator._set_icon("unlock");
        };
        dialog.open(global.get_current_time());
        dialog.entry.grab_key_focus();
    } else {
        indicator._set_icon("unlock");
        next();
    }
}

function load_config() {
    if (!GLib.file_test(conffile, GLib.FileTest.EXISTS)) {
        store_config();
    }

    conffile_data = Shell.get_file_contents_utf8_sync(conffile);
    conffile_data = Gecojs.decrypt(masterpwd, conffile_data);
    let lines = conffile_data.toString().split('\n');
    for (let i=0; i < lines.length; i++) {
        let opt = lines[i].split("=");
        if (opt.length != 2) {
            continue;
        }

        key = opt[0].trim();
        value = opt[1].trim();

        if (key == 'server') {
            base = value;
        } else if (key == 'user') {
            username = value;
        } else if (key == 'passwd') {
            pwd = value;
        }
    }
}

function store_config() {
    let f = Gio.file_new_for_path(conffile);
    let out = f.replace(null, false, Gio.FileCreateFlags.NONE, null);
    content = "server = " + base + "\nuser = " + username + "\npasswd = " + pwd;

    Shell.write_string_to_stream (out, Gecojs.encrypt(masterpwd, content));
}


const GECO = new Lang.Class({
    Name: 'GecoIndicator',
    Extends: PanelMenu.Button,

    _passwords: new Array(),
    _cookie: '',

    _set_icon: function(stat) {
        this.icon = new St.Icon({
            icon_name: 'geco-'+stat+'-symbolic'
            //icon_name: 'dialog-error-symbolic'
            ,style_class: 'system-status-icon'
        });
        this.actor.get_children().forEach(function(c) { c.destroy() });
        this.actor.add_actor(this.icon);
    },

    _set_gnome_icon: function(icon) {
        this.icon = new St.Icon({
            icon_name: icon
            ,style_class: 'system-status-icon'
        });
        this.actor.get_children().forEach(function(c) { c.destroy() });
        this.actor.add_actor(this.icon);
    },

    _init: function(){
        this.parent(St.Align.START);
        this._search_menu();
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._update_menu();
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._settings_menu();
    },

    _search_menu: function() {
        this.searchsection = new PopupMenu.PopupMenuSection("Search");
        let item = new PopupMenu.PopupMenuItem("");
        this.search = new St.Entry(
        {
            name: "gecoSearch",
            hint_text: _("search..."),
            track_hover: true,
            can_focus: true
        });


        let search_text = this.search.clutter_text;
        search_text.connect('key-release-event', function(o,e) {
            indicator.filter(o.get_text());
        });

        this.searchsection.actor.add_actor(this.search);
        this.menu.addMenuItem(this.searchsection);
    },

    _update_menu: function() {
        if (this.pwsection) {
            this.pwsection.removeAll();
        } else {
            this.pwsection = new PopupMenu.PopupMenuSection("Passwords");
            this.menu.addMenuItem(this.pwsection);
        }

        let filtered_list = new Array();
        for (let i=0, j=0; i < this._passwords.length; i++) {
            let pwd = this._passwords[i];
            let regx = ".*" + this.search.get_text() + ".*";
            let reg = new RegExp(regx, "i");

            if (pwd.name.match(reg)) {
                filtered_list[j] = pwd;
                j++;
            }
        }

        for (let i=0; i < filtered_list.length && i < 5; i++) {
            let pwd = filtered_list[i];
            let item = this.create_item(pwd);
            this.pwsection.addMenuItem(item);
        }

        if (filtered_list.length >= 5) {
            let overflowItem = new PopupMenu.PopupSubMenuMenuItem("...");
            for (let i=5; i < filtered_list.length; i++) {
                let pwd = filtered_list[i];
                let item = this.create_item(pwd);
                overflowItem.menu.addMenuItem(item);
            }

            this.pwsection.addMenuItem(overflowItem);
        }
    },

    create_item: function(pwd) {
        let ind = this;
        let item = new PopupMenu.PopupMenuItem(pwd.name);

        let actor = new Clutter.Box({ reactive: true });
        actor.connect('button-press-event', function() {
            ind._get_account(pwd);
        });
        ic = new St.Icon({ icon_name: 'avatar-default-symbolic', icon_size: '24'});
        actor.add_actor(ic);
        actor.show();
        item.actor.add_actor(actor, { align: St.Align.END, expand: false });

        item.connect('activate',function(item, event, position) {
            if ((event.type() == Clutter.EventType.BUTTON_RELEASE &&
                event.get_button() == Clutter.BUTTON_SECONDARY) ||
                (event.type() == Clutter.EventType.KEY_PRESS &&
                event.get_key_symbol() == Clutter.KEY_space)) {
                ind._get_account(pwd);
            }

            ind._get_password(pwd);
        });

        return item;
    },

    _get_password: function(pwd) {
        let clipboard = St.Clipboard.get_default();
        if (account_pressed) {
            account_pressed = false;
        } else {
            ask_for_password_dialog(function() {
                clipboard.set_text(St.ClipboardType.CLIPBOARD, Gecojs.decrypt(masterpwd, pwd.password));
            });
        }
    },

    _get_account: function(pwd) {
        let clipboard = St.Clipboard.get_default();
        clipboard.set_text(St.ClipboardType.CLIPBOARD, pwd.account);
        account_pressed = true;
        return true;
    },

    // always call this function with ask_for_password_dialog
    _refresh: function() {
        load_config();

        let st = this;
        st._set_gnome_icon('emblem-synchronizing-symbolic');
        Utils.make_query(base + "/api/auth", "user="+Utils.urlencode(username)+"&password="+Utils.urlencode(pwd), function(data) {
            st._cookie = data.data;

            Utils.make_query(base + "/api/get_all_passwords", "cookie="+Utils.urlencode(st._cookie), function(data) {
                st._passwords = data.data;
                st._passwords.sort(function(a, b) {
                    if (a.name < b.name)
                        return -1;
                    else if (a.name > b.name)
                        return 1;
                    else
                        return 0;
                });
                st._update_menu();
                st._set_icon('unlock');
            });
        });
    },

    _settings_menu: function() {
        this.cfgsection = new PopupMenu.PopupMenuSection("Setting");

        let item = new PopupMenu.PopupMenuItem(_("refresh"));
        let st = this;
        item.connect('activate', function() {
            ask_for_password_dialog(function() {
                refresh();
            });
        });
        this.cfgsection.addMenuItem(item);

        let item = new PopupMenu.PopupMenuItem(_("forget master"));
        item.connect('activate', function() { forget_master(); });
        this.cfgsection.addMenuItem(item);

        let item = new PopupMenu.PopupMenuItem(_("config"));
        item.connect('activate', function() { config_dialog(); });
        this.cfgsection.addMenuItem(item);


        this.menu.addMenuItem(this.cfgsection);
    },

    filter: function (text) {
        this._update_menu();
    },
});

function debug(msg) {
    text = new St.Label({ style_class: 'helloworld-label', text: "Debug: " + msg });
    Main.uiGroup.add_actor(text);
    text.opacity = 255;
    let monitor = Main.layoutManager.primaryMonitor;
    text.set_position(100, 0);
}

function init(metadata) {
    mdata = metadata;
    conffile = mdata.path + "/geco.conf";
}

function enable() {
    var key;
    for(key in key_bindings) {
        Main.wm.addKeybinding(key,
            mySettings,
            Meta.KeyBindingFlags.NONE,
            Shell.KeyBindingMode.NORMAL |
            Shell.KeyBindingMode.MESSAGE_TRAY |
            Shell.KeyBindingMode.OVERVIEW,
            key_bindings[key]
        );
    }

    indicator = new GECO();
    indicator._set_icon("lock");
    Main.panel.addToStatusArea('geco', indicator);
}

function disable() {
    for(key in key_bindings) {
        Main.wm.removeKeybinding(key);
    }

    indicator.destroy();
    //Mainloop.source_remove(event);
    indicator = null;
}
