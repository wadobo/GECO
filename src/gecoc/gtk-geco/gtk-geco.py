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
SECONDS = 10

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
        self.hide.connect('clicked', self.on_click)

        self.forget_button = self.gladefile.get_widget('forget')
        self.forget_button.connect('clicked', self.forget)

        self.passwords = self.gladefile.get_widget('passwords')
        self.viewport = self.gladefile.get_widget('viewport1')

        self.search = self.gladefile.get_widget('search')

        # TODO conffile
        server = 'https://localhost:4343'
        user, password = 'dani', '123'
        self.gso = gecolib.GSO(xmlrpc_server=server)
        self.gso.auth(user, password)

        self.master = ''

        self.get_passwords()

    def forget(self, *args):
        self.master = ''
        self.unlocked(False)

    def get_master(self):
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
            master_dialog.hide()
            return self.master

    def get_passwords(self):
        self.passwords.destroy()
        self.passwords = gtk.VBox()
        self.passwords.show()
        self.viewport.add(self.passwords)

        passwords = self.gso.get_all_passwords()
        for p in passwords:
            self.add_new(p)

    def add_new(self, p):
        def clicked(button, p):
            clipboard = gtk.clipboard_get()
            master_password = self.get_master()
            password = self.gso.get_password(p['name'], master_password)
            clipboard.set_text(password['password'])
            clipboard.store()
            self.on_click()

        vbox = self.passwords
        hbox = gtk.HBox()

        button = gtk.Button(p['name'])
        button.set_relief(gtk.RELIEF_NONE)
        button.connect('clicked', clicked, p)
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
        edit.connect('clicked', clicked, p)
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
        pass

    def on_add(self, data):
        pass

    def on_click(self, data=None):
        if self.win_visible:
            self.win_visible = False
            self.win.hide()
        else:
            self.win_visible = True
            x, y = self.get_mouse()
            self.win.move(x,y)
            self.win.show()
            self.search.grab_focus()
    
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
