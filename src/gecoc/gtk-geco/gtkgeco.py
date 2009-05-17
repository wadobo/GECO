#!/usr/bin/python
# -*- coding: utf-8 -*-
# License: GPLv3
# Author: Daniel Garcia <dani@danigm.net>

import os, sys
import gtk
gtk.gdk.threads_init()
import threading

import gobject
import datetime
from gecoc import gecolib

__version__ = '1.0'
IMG = 'glade'
SECONDS = 600
CONFFILE = 'geco.conf'

def remove_text(button):
    alignment = button.get_children()[0]
    hbox = alignment.get_children()[0]
    image, label = hbox.get_children()
    label.set_text('')

class TrayIcon(gtk.StatusIcon):
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        menu = '''
                <ui>
                <menubar name="Menubar">
                <menu action="Menu">
                <menuitem action="Add"/>
                <menuitem action="Config"/>
                <menuitem action="About"/>
                <menuitem action="Quit"/>
                </menu>
                </menubar>
                </ui>
        '''
        actions = [
                ('Menu',  None, 'Menu'),
                ('Add', gtk.STOCK_ADD, '_Add...', None, 'Add', self.on_add),
                ('Config', gtk.STOCK_PREFERENCES, '_Config...', None, 'Configure', self.on_config),
                ('About', gtk.STOCK_ABOUT, '_About...', None, 'About gtk-GECO', self.on_about),
                ('Quit',gtk.STOCK_QUIT,'_Quit',None, 'Quit', self.on_quit),
                ]

        ag = gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)
        self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent
        self.current_icon_path = ''
        gtk.StatusIcon.set_from_file(self, os.path.join(IMG, "lock.png"))
        self.set_visible(True)
        self.connect('popup-menu', self.on_popup_menu)
        self.connect('activate', self.on_click)

        popupfile = os.path.join(IMG, 'popup.glade')
        self.builder = gtk.Builder()
        self.builder.add_from_file(popupfile)
        self.win = self.builder.get_object('popup')
        self.win.show_all()
        self.win.hide()
        self.win_visible = False
        filename = os.path.join(IMG, 'lock.png')
        self.win.set_icon_from_file(filename)

        self.hide = self.builder.get_object('hide')
        remove_text(self.hide)
        self.hide.connect('clicked', self.hide_win)

        self.forget_button = self.builder.get_object('forget')
        self.forget_button.connect('clicked', self.forget)

        self.passwords = self.builder.get_object('passwords')
        self.viewport = self.builder.get_object('viewport1')

        cipher = self.builder.get_object('cipher')
        cipher.connect('clicked', self.cipher)

        generate = self.builder.get_object('generate')
        generate.connect('clicked', self.generate)

        self.new_form = self.builder.get_object('new')

        self.pref_form = self.builder.get_object('prefs')
        prefs = self.builder.get_object('prefs_button')
        prefs.connect('clicked', self.on_config)

        exp = self.builder.get_object('export')
        exp.connect('clicked', self.export_file)

        imp = self.builder.get_object('import')
        imp.connect('clicked', self.import_file)

        save = self.builder.get_object('save_conf')
        save.connect('clicked', self.save_conf)

        register = self.builder.get_object('register')
        register.connect('clicked', self.register)

        del_user = self.builder.get_object('del_user')
        del_user.connect('clicked', self.del_user)

        refresh = self.builder.get_object('refresh')
        remove_text(refresh)
        refresh.connect('clicked', self.get_passwords)

        add_button = self.builder.get_object('add_button')
        remove_text(add_button)
        add_button.connect('clicked', self.on_add)
        
        # TODO add change master password signals
        # change background color if not the same 
        # cmasterp1 == cmasterp2 and cmasternp1 == cmasternp2
        # change_master_button -> gso.change_master(cmasterp1, cmasternp1)
        
        self.master = ''
        self.auth()

    def __get_config_form(self):
        server = self.builder.get_object('pref_server').get_text()
        user = self.builder.get_object('pref_user').get_text()
        password = self.builder.get_object('pref_pass').get_text()
        
        return server, user, password

    def __set_config_form(self):
        server = self.builder.get_object('pref_server')
        user = self.builder.get_object('pref_user')
        password = self.builder.get_object('pref_pass')

        s, u, p = self.get_opts()

        server.set_text(s)
        user.set_text(u)
        password.set_text(p)
    
    def message(self, msg="ERROR no se por qué :(", type='err'):
        type = gtk.MESSAGE_ERROR if type == 'err' else gtk.MESSAGE_INFO
        dialog = gtk.MessageDialog(type=type,
                buttons=gtk.BUTTONS_CLOSE,
                message_format=msg)
        dialog.run()
        dialog.destroy()

    def get_opts(self):
        if os.path.exists(CONFFILE):
            f = open(CONFFILE)
            to_read = f.read()
            f.close()

            master = self.get_master()
            if not master:
                return '', '', ''
            aes = gecolib.AES()
            to_read = aes.decrypt(to_read, master)

            all = [i for i in to_read.split('\n') if i]
            values = {}
            for opt in all:
                try:
                    key, value = map(str.strip, opt.split('='))
                    values[key] = value
                except:
                    return '', '', ''
            
            return values['server'], values['user'], values['passwd']
        else:
            return '', '', ''

    def auth(self, server='', user='', password=''):
        if not server:
            server, user, password = self.get_opts()
            if not server:
                self.message('No encuentro el fichero de configuración, o está erroneo.\n'\
                        'Configúralo en Preferencias', type='info')
                return

        self.set_blinking(True)
        t = threading.Thread(target=self.remote_auth,
                args=(server, user, password))
        t.start()

    def remote_auth(self, server, user, password):
        # TODO use, gobject.idle_add
        try:
            self.gso = gecolib.GSO(xmlrpc_server=server)
            self.gso.auth(user, password)
        except Exception, e:
            self.message('Error en el login: %s' % str(e))
            return

        try:
            gtk.gdk.threads_enter()
            self.statusbar = self.builder.get_object('statusbar')
            self.statusbar.push(0, server)
            self.get_passwords()
            self.set_blinking(False)
        finally:
            gtk.gdk.threads_leave()

    def del_user(self, widget, *args):
        server, user, passwd = self.__get_config_form()
        gso = gecolib.GSO(xmlrpc_server=server)
        gso.auth(uer, passwd)

        try:
            gso.unregister()
            self.message('Cuenta borrada', type='info')
        except Exception, e:
            self.message('Error al borrar la cuenta: %s' % str(e))

    def register(self, widget, *args):
        server, user, passwd = self.__get_config_form()
        gso = gecolib.GSO(xmlrpc_server=server)
        gso.auth(user, passwd)

        try:
            gso.register(user, passwd)
            self.message('Registrado con éxito', type='info')
        except Exception, e:
            self.message('Error en el registro: %s' % str(e))

    def save_conf(self, widget, *args):
        server, user, passwd = self.__get_config_form()
        f = open(CONFFILE, 'w')
        to_save = 'server = %s\n'\
                'user = %s\n'\
                'passwd = %s\n' % (server, user, passwd)

        master = self.get_master()
        aes = gecolib.AES()
        to_save = aes.encrypt(to_save, master)

        f.write(to_save)
        f.close()
        self.auth(server, user, passwd)

    def export_file(self, widget, *args):
        dialog = gtk.FileChooserDialog(action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            try:
                out = open(filename, 'w')
                out.write(self.gso.export())
                self.message('Exportación realizada con éxito', type='info')
            except Exception, e:
                self.message('No se ha podido exportar: %s' % str(e))

        dialog.destroy()

    def import_file(self, widget, *args):
        dialog = gtk.FileChooserDialog(action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            try:
                inp = open(filename).read()
                self.gso.restore(inp)
                self.message('Importación realizada con éxito', type='info')
            except Exception, e:
                self.message('No se ha podido importar: %s' % str(e))

        dialog.destroy()
        self.get_passwords()

    def forget(self, *args):
        self.master = ''
        self.unlocked(False)

    def get_master(self):
        self.hide_win()

        if self.master:
            return self.master
        else:
            master_dialog = \
                    gtk.MessageDialog(buttons=gtk.BUTTONS_OK_CANCEL,
                    message_format="Contraseña maestra")

            master_input = gtk.Entry()
            master_input.set_visibility(False)
            master_input.show()
            master_input.set_activates_default(True)

            master_dialog.vbox.pack_start(master_input, False, True)

            master_dialog.set_default_response(gtk.RESPONSE_OK)

            response = master_dialog.run()
            if response == gtk.RESPONSE_OK:
                self.master = master_input.get_text()
                master_input.set_text('')
                self.unlocked(True)
                gobject.timeout_add(SECONDS * 1000, self.forget)
            master_dialog.destroy()
            return self.master

    def get_passwords(self, *args):
        self.passwords.destroy()
        self.passwords = gtk.VBox()
        self.passwords.show()
        self.viewport.add(self.passwords)

        try:
            passwords = self.gso.get_all_passwords()
        except Exception, e:
            self.message('Error obteniendo contraseñas: %s' % str(e))
            return

        def cmp(x, y):
            if x['name'] > y['name']: return 1
            else: return -1
        passwords.sort(cmp)

        for p in passwords:
            self.add_new(p)

    def add_new(self, p):
        def clicked(button, event, p):
            if event.button == 3:
                password = p['account']
            else:
                master_password = self.get_master()
                password = self.gso.get_password(p['name'], master_password)
                password = password['password']
                
            clipboard = gtk.clipboard_get()
            clipboard.set_text(password)
            clipboard.store()
            self.hide_win()

        vbox = self.passwords
        hbox = gtk.HBox()

        # PASSWORD 
        button = gtk.Button(p['name'])
        button.set_relief(gtk.RELIEF_NONE)
        button.connect('button_press_event', clicked, p)
        tooltip = '\t<b>%s</b>:\n\t%s' % (p['account'], p['description'])
        button.set_tooltip_markup(tooltip)
        button.set_alignment(0, 0.5)
        hbox.add(button)
        
        exp = p['expiration']
        expdate = datetime.datetime.fromtimestamp(float(exp))
        days = (expdate - datetime.datetime.now()).days
        if days > 20:
            img = 'green.png'
        if 20 >= days > 7:
            img = 'yellow.png'
        if days <= 7:
            img = 'red.png'

        expiration = gtk.Image()
        expiration.set_from_file(os.path.join(IMG, img))
        hbox.pack_start(expiration, False, False)

        # EDIT
        edit = gtk.Button(stock=gtk.STOCK_EDIT)
        edit.set_relief(gtk.RELIEF_NONE)
        edit.connect('clicked', self.on_add, p)
        remove_text(edit)
        hbox.pack_start(edit, False)

        # DELETE
        delete = gtk.Button(stock=gtk.STOCK_DELETE)
        delete.set_relief(gtk.RELIEF_NONE)
        delete.connect('clicked', self.delete, p)
        remove_text(delete)
        hbox.pack_start(delete, False)

        hbox.show_all()

        vbox.pack_start(hbox, False, False)

    def on_quit(self,widget):
        sys.exit()

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

    def on_about(self, data):
        dialog = gtk.AboutDialog()
        dialog.set_name('GTK GECO')
        dialog.set_version(__version__)
        dialog.set_comments('Gestor de Contraseñas distribuido')
        dialog.set_website('http://danigm.net/geco')
        dialog.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(IMG, 'poweredby.png')))
        dialog.run()
        dialog.destroy()

    def on_config(self, data):
        # hide window
        self.hide_win()

        server, user, passwd = self.__get_config_form()
        if not user:
            self.__set_config_form()

        dialog = self.pref_form
        response = dialog.run()

        dialog.hide()
        # Refresh
        server, user, passwd = self.__get_config_form()
        self.auth(server, user, passwd)

    def on_add(self, data, p=None):
        # hide window
        self.hide_win()

        self.new_form.show()
        name = self.builder.get_object('name')
        account = self.builder.get_object('account')
        type = self.builder.get_object('type')
        exp = self.builder.get_object('expiration')
        desc = self.builder.get_object('desc')
        password = self.builder.get_object('password')

        if p:
            # EDIT, not new
            name.set_text(p['name'])
            name.editable = False
            account.set_text(p['account'])
            type.set_text(p['type'])
            e = p['expiration']
            expdate = datetime.datetime.fromtimestamp(float(e))
            days = (expdate - datetime.datetime.now()).days
            exp.set_text(str(days))
            desc.get_buffer().set_text(p['description'])
            password.set_text(p['password'])
        else:
            # new
            name.set_text('')
            name.editable = True
            account.set_text('')
            type.set_text('')
            exp.set_text('180')
            desc.get_buffer().set_text('')
            password.set_text('')

        response = self.new_form.run()

        if response == 1:
            args = {}
            args['account'] = account.get_text()
            buff = desc.get_buffer()
            args['description'] = buff.get_text(buff.get_start_iter(),
                    buff.get_end_iter())
            args['type'] = type.get_text()
            args['expiration'] = int(exp.get_text())

            try:
                if p:
                    self.gso.del_password(name.get_text())
                self.gso.set_raw_password(name.get_text(), password.get_text(), args)
            except Exception, e:
                self.message('Error: %s' % str(e))

            self.get_passwords()

        self.new_form.hide()

    def generate(self, button):
        master = self.get_master()
        length = self.builder.get_object('length').get_text()
        length = int(length)
        lower = self.builder.get_object('low').get_active()
        upper = self.builder.get_object('up').get_active()
        digits = self.builder.get_object('digits').get_active()
        other = self.builder.get_object('other').get_active()

        clear = self.builder.get_object('clear')

        new_pass = gecolib.generate(length, lower, upper, digits,
                other)

        clear.set_text(new_pass)
        self.strength(new_pass)
        self.cipher_pass(new_pass)

    def strength(self, password):
        bar = self.builder.get_object('strength')
        strength = gecolib.strength(password)

        text_strength = ('Mala', 'Buena', 'Fuerte', 'Perfecta')
        index = int(strength * (len(text_strength)-1))
        text_strength = text_strength[index]
        bar.set_text(text_strength)
        bar.set_fraction(strength)

    def cipher_pass(self, new_pass):
        master = self.get_master()
        password = self.builder.get_object('password')

        aes = gecolib.AES()
        cipher = aes.encrypt(new_pass, master)
        password.set_text(cipher)

    def cipher(self, button):
        p1 = self.builder.get_object('p1').get_text()
        p2 = self.builder.get_object('p2').get_text()
        self.strength(p1)

        if p1 == p2:
            self.cipher_pass(p1)
        else:
            bar = self.builder.get_object('strength')
            bar.set_text("Las contraseñas no coinciden")
            bar.set_fraction(0)

    def on_click(self, data=None):
        if self.win_visible:
            self.win_visible = False
            self.win.hide()
        else:
            self.win_visible = True
            x, y = self.get_mouse()
            self.win.move(x,y)
            self.win.show()

    def hide_win(self, *args):
        if self.win_visible:
            self.win_visible = False
            self.win.hide()
    
    def unlocked(self, boolean):
        if not boolean:
            gtk.StatusIcon.set_from_file(self, os.path.join(IMG, "lock.png"))
        else:
            gtk.StatusIcon.set_from_file(self, os.path.join(IMG, "unlock.png"))

    def get_mouse(self):
        win_w, win_h = self.win.get_size()
        screen = self.get_screen()
        width, height = screen.get_width(), screen.get_height()
        
        rootwin = screen.get_root_window()
        x, y, mods = rootwin.get_pointer()

        if x + win_w > width:
            x = width - win_w

        if y + win_h > height:
            y = height - win_h

        return x, y

    def delete(self, button, p):
        # hide window
        self.hide_win()
        name = p['name']
        message = '¿Estás seguro de que quieres eliminar la contraseña "%s"?' % name
        dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_YES_NO,
                message_format=message)
        response = dialog.run()
        
        if response == gtk.RESPONSE_YES:
            self.gso.del_password(name)
            self.get_passwords()

        dialog.destroy()

def main():
    t = TrayIcon()
    gtk.main()

if __name__ == '__main__':
    main()
