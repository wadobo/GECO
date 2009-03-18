#!/usr/bin/python
# -*- coding: utf-8 -*-
# License: GPLv3
# Author: Daniel Garcia <dani@danigm.net>

import os,sys
import gtk
import gtk.glade
import gobject
import datetime
from gecoc import gecolib

__version__ = '0.1'
IMG = 'glade'
SECONDS = 600

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
        self.gladefile = gtk.glade.XML(popupfile)
        self.win = self.gladefile.get_widget('popup')
        self.win.show_all()
        self.win.hide()
        self.win_visible = False

        self.hide = self.gladefile.get_widget('hide')
        remove_text(self.hide)
        self.hide.set_relief(gtk.RELIEF_NONE)
        self.hide.connect('clicked', self.hide_win)

        self.forget_button = self.gladefile.get_widget('forget')
        self.forget_button.connect('clicked', self.forget)

        self.passwords = self.gladefile.get_widget('passwords')
        self.viewport = self.gladefile.get_widget('viewport1')

        cipher = self.gladefile.get_widget('cipher')
        cipher.connect('clicked', self.cipher)

        generate = self.gladefile.get_widget('generate')
        generate.connect('clicked', self.generate)

        self.new_form = self.gladefile.get_widget('new')

        self.pref_form = self.gladefile.get_widget('prefs')
        prefs = self.gladefile.get_widget('prefs_button')
        prefs.connect('clicked', self.on_config)

        filechooser = self.gladefile.get_widget('file_exp_button')
        filechooser.connect('clicked', self.chooser)

        # TODO conffile
        # TODO conectar en un thread
        server = 'https://localhost:4343'
        user, password = 'dani', '123'
        self.gso = gecolib.GSO(xmlrpc_server=server)
        self.gso.auth(user, password)

        self.master = ''

        self.statusbar = self.gladefile.get_widget('statusbar')
        self.statusbar.push(0, server)

        self.get_passwords()

    def chooser(self, widget, *args):
        exp = self.gladefile.get_widget('file_exp')
        dialog = gtk.FileChooserDialog(action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=('Cancelar', 0, 'Seleccionar', 1))
        response = dialog.run()
        if response == 1:
            filename = dialog.get_filename()
            exp.set_text(filename)
        dialog.destroy()

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

    def get_passwords(self):
        self.passwords.destroy()
        self.passwords = gtk.VBox()
        self.passwords.show()
        self.viewport.add(self.passwords)

        passwords = self.gso.get_all_passwords()
        def cmp(x, y):
            if x['name'] > y['name']: return 1
            else: return -1
        passwords.sort(cmp)

        for p in passwords:
            self.add_new(p)

    def add_new(self, p):
        def clicked(button, p):
            clipboard = gtk.clipboard_get()
            master_password = self.get_master()
            password = self.gso.get_password(p['name'], master_password)
            clipboard.set_text(password['password'])
            clipboard.store()
            self.hide_win()

        vbox = self.passwords
        hbox = gtk.HBox()

        # PASSWORD 
        button = gtk.Button(p['name'])
        button.set_relief(gtk.RELIEF_NONE)
        button.connect('clicked', clicked, p)
        tooltip = '\t<b>%s</b>:\n\t%s' % (p['account'], p['description'])
        button.set_tooltip_markup(tooltip)
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

        vbox.add(hbox)

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
        dialog = self.pref_form
        response = dialog.run()

        dialog.hide()

    def on_add(self, data, p=None):
        # hide window
        self.hide_win()

        self.new_form.show()
        name = self.gladefile.get_widget('name')
        account = self.gladefile.get_widget('account')
        type = self.gladefile.get_widget('type')
        exp = self.gladefile.get_widget('expiration')
        desc = self.gladefile.get_widget('desc')
        password = self.gladefile.get_widget('password')

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
            except:
                # TODO sacar un mensaje de error
                pass

            self.get_passwords()

        self.new_form.hide()

    def generate(self, button):
        master = self.get_master()
        length = self.gladefile.get_widget('length').get_text()
        length = int(length)
        lower = self.gladefile.get_widget('low').get_active()
        upper = self.gladefile.get_widget('up').get_active()
        digits = self.gladefile.get_widget('digits').get_active()
        other = self.gladefile.get_widget('other').get_active()

        clear = self.gladefile.get_widget('clear')

        new_pass = gecolib.generate(length, lower, upper, digits,
                other)

        clear.set_text(new_pass)
        self.strength(new_pass)
        self.cipher_pass(new_pass)

    def strength(self, password):
        bar = self.gladefile.get_widget('strength')
        strength = gecolib.strength(password)

        text_strength = ('Mala', 'Buena', 'Fuerte', 'Perfecta')
        index = int(strength * (len(text_strength)-1))
        text_strength = text_strength[index]
        bar.set_text(text_strength)
        bar.set_fraction(strength)

    def cipher_pass(self, new_pass):
        master = self.get_master()
        password = self.gladefile.get_widget('password')

        aes = gecolib.AES()
        cipher = aes.encrypt(new_pass, master)
        password.set_text(cipher)

    def cipher(self, button):
        p1 = self.gladefile.get_widget('p1').get_text()
        p2 = self.gladefile.get_widget('p2').get_text()
        self.strength(p1)

        if p1 == p2:
            self.cipher_pass(p1)
        else:
            bar = self.gladefile.get_widget('strength')
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

if __name__ == '__main__':
    t = TrayIcon()
    gtk.main()
