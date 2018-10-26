#!/usr/bin/env python2

# -*- coding: utf-8 -*-

#
# Author: Mihai Galos
# Date: October 23 , 2018
# Purpose: indicator for the Netatmo Weather Station
# Tested on: Ubuntu 16.04 LTS
#
#
# Licensed under The MIT License (MIT).
# See included LICENSE file or the notice below.
#
# Copyright (c) 2018 Mihai Galos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from netatmo_service_wrapper import Netatmo
import os
import json
import yaml

import gi
gi.require_version('Notify', '0.7')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import Notify
from gi.repository import Gio
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib
from collections import namedtuple

from netatmo_service_wrapper import Credentials


class EntryWindow(gtk.Window):

    def __init__(self, credentials, prefs, callback_on_config_changed):
        gtk.Window.__init__(self, title="Settings")

        self.callback_on_config_changed = callback_on_config_changed

        self.metadata = {}
        self.metadata.update ( {"credentials" : credentials})
        self.metadata.update ( {"prefs" : prefs})
        self.metadata.update ({"ui": {}})

        self.set_border_width(6)
        self.set_default_size(300, 100)

        self.timeout_id = None

        self.vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        self.label = gtk.Label("Config file: ~/.netatmo-indicator-preferences.yaml")
        self.vbox.pack_start(self.label, True, True, 0)


        for k,v in credentials.iteritems():
            self.label_entry(k, v, self.vbox)

        for k,v in prefs.iteritems():
            if type(prefs[k]) is not dict:
                self.label_entry(k, v, self.vbox)

        hbox = gtk.Box(spacing=6)
        self.vbox.pack_start(hbox, True, True, 0)

        self.save_button = gtk.Button("Save")
        self.save_button.connect("pressed", self.on_save_button_pressed)
        hbox.pack_start(self.save_button, True, True, 0)

        self.cancel_button = gtk.Button("Cancel")
        self.cancel_button.connect("pressed", self.on_cancel_button_pressed)
        hbox.pack_start(self.cancel_button, True, True, 0)

        self.add(hbox)
        self.show_all()
        pass

    def label_entry(self, label_name, label_value, parent):
        hbox = gtk.Box(spacing=6)
        parent.add(hbox)

        entry = gtk.Entry()
        entry.set_width_chars(50)
        entry.set_text(label_value)
        hbox.pack_end(entry, False, False, 0)

        label = gtk.Label(label_name)
        hbox.pack_end(label, False, False, 0)

        self.metadata["ui"].update({label_name : entry})

    def on_save_button_pressed(self, button):

        data_to_write = {}

        credentials_file =self.metadata["ui"]["credentials_file"].get_text()
        data_to_write.update({"credentials_file": credentials_file})
        preferences_file = os.path.join(os.path.expanduser('~'), ".netatmo-indicator-preferences.yaml")

        credentials = {}

        for k,v in self.metadata["ui"].iteritems():
            if "credentials_file" != k:
                credentials.update({k : v.get_text()})


        with open(preferences_file, "w+") as outfile:
            yaml.dump(data_to_write, outfile, default_flow_style=False)

        with open(credentials_file, "w+") as outfile:
            yaml.dump(credentials, outfile, default_flow_style=False)

        self.hide()
        self.callback_on_config_changed()

    def on_cancel_button_pressed(self, button):
        self.hide()


class Menu:
    def __init__(self, app, netatmo, aliases, credentials, prefs, callback_on_config_changed):

        self.callback_on_config_changed = callback_on_config_changed

        if hasattr(self, 'app_menu'):
            for item in self.app_menu.get_children():
                self.app_menu.remove(item)
        self.app_menu = gtk.Menu()
        self.credentials = credentials
        self.prefs = prefs
        display_string = ""

        if netatmo.exception is None:
            degree_sign = u'\N{DEGREE SIGN}'
            for k, v in netatmo.data.iteritems():
                if k in aliases:
                    k = aliases[k]
                display_string = display_string+k+": "+str(v)+degree_sign+" "

            app.set_label(display_string, "")
        else:
            display_string = "Error communicating with Netatmo."
            app.set_label(display_string, "")
            contents = [self.app_menu, gtk.ImageMenuItem, 'help-hint',
                        str(netatmo.exception), self.quit, [None]]
            self.add_menu_item(*contents)


        contents = [self.app_menu, gtk.ImageMenuItem, 'gtk-info',
                    'Timestamp: '+netatmo.timestamp, None, [None]
                    ]
        self.add_menu_item(*contents)

        contents = [self.app_menu, gtk.ImageMenuItem, 'gtk-preferences',
                    'Settings', self.on_settings_clicked, [None]
                    ]
        self.add_menu_item(*contents)

        contents = [self.app_menu, gtk.ImageMenuItem, 'exit',
                    'Quit', self.quit, [None]
                    ]
        self.add_menu_item(*contents)

        self.app = app

    def on_settings_clicked(self, *args):
        entry_window = EntryWindow(self.credentials, self.prefs, self.on_config_changed)

    def add_menu_item(self, menu_obj, item_type, image, label, action, args):
        menu_item = self.create_menu_item(action, args, image, item_type, label)
        menu_obj.append(menu_item)
        menu_item.show()

    def create_menu_item(self, action, args, image, item_type, label):

        if item_type is gtk.ImageMenuItem and label:
            menu_item = self.create_menu_item_image_and_label(image, label)
        elif item_type is gtk.ImageMenuItem and not label:
            menu_item = self.create_menu_item_image(image)
        elif item_type is gtk.MenuItem:
            menu_item = gtk.MenuItem(label)
        elif item_type is gtk.SeparatorMenuItem:
            menu_item = gtk.SeparatorMenuItem()
        if action:
            menu_item.connect('activate', action, *args)
        return menu_item

    def create_menu_item_image(self, image):
        menu_item = gtk.ImageMenuItem()
        menu_item.set_always_show_image(True)
        if '/' in image:
            icon = gtk.Image.new_from_file(image)
        else:
            icon = gtk.Image.new_from_icon_name(image, 16)
        menu_item.set_image(icon)
        return menu_item

    def create_menu_item_image_and_label(self, image, label):
        menu_item = gtk.ImageMenuItem.new_with_label(label)
        menu_item.set_always_show_image(True)
        if '/' in image:
            icon = gtk.Image.new_from_file(image)
        else:
            icon = gtk.Image.new_from_icon_name(image, 48)
        menu_item.set_image(icon)
        return menu_item

    def get_menu(self):
        return self.app_menu

    def get_app(self):
        return self.app

    def quit(self, *args):
        gtk.main_quit()

    def on_config_changed(self):
        self.callback_on_config_changed()

class NetatmoIndicator(object):

    def __init__(self):
        current_folder =  os.getcwd()

        self.app = appindicator.Indicator.new(
            'netatmo-indicator', current_folder + "/FF4D00-0.0.png",
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )

        self.app.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.user_home = os.path.expanduser('~')
        self.prefs_file = os.path.join(
            self.user_home, ".netatmo-indicator-preferences.yaml")

        self.note = Notify.Notification.new(__file__, None, None)
        Notify.init(__file__)

        self.cache_icon_theme = self.gsettings_get(
            'org.gnome.desktop.interface', None, 'icon-theme'
        )

        self.fetch_netatmo_data()

        self.make_menu()
        self.update()

    def fetch_netatmo_data(self):

        self.prefs = self.read_prefs_file()

        if "aliases" not in self.prefs:
            self.prefs.update({"aliases": {}})
        NetatmoContainer = namedtuple("NetatmoContainer", "data timestamp exception")
        try:
            self.credentials = Credentials().read_credentials(self.prefs["credentials_file"])
            netatmo = Netatmo(self.prefs["credentials_file"])
            (data, timestamp) = netatmo.get_data()
            exception = None
            self.netatmo = NetatmoContainer(data, timestamp, exception)

        except Exception, err:
            self.credentials={}
            data = {}
            timestamp="?"
            exception = err
            self.netatmo = NetatmoContainer(data, timestamp, exception)
            pass

    def run(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass

    def update(self):
        timeout = 5*60
        glib.timeout_add_seconds(timeout, self.callback)


    def callback(self):
        self.fetch_netatmo_data()

        self.make_menu()
        self.update()

    def make_menu(self):
        menu_object = Menu(self.app, self.netatmo, self.prefs["aliases"], self.credentials, self.prefs, self.callback)
        self.app = menu_object.get_app()
        self.app.set_menu(menu_object.get_menu())


    def gsettings_get(self, schema, path, key):
        """utility: get value of gsettings schema"""
        if path is None:
            gsettings = Gio.Settings.new(schema)
        else:
            gsettings = Gio.Settings.new_with_path(schema, path)
        return gsettings.get_value(key)

    def read_prefs_file(self, *args):

        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file) as f:
                    result = yaml.load(f)
                    f.close()
                    return result
            except yaml.YAMLError as exc:
                raise Exception("File does not exist: "+str(self.prefs_file))
        else:
            data_to_write = {"credentials_file" : os.path.join(self.user_home, ".netatmo-credentials.yaml"), "aliases" : {}}
            with open(self.prefs_file, "w") as outfile:
                yaml.dump(data_to_write, outfile, default_flow_style=False)

            with open(self.prefs_file) as infile:
                return yaml.load(infile)


    def write_prefs_file(self, *args):
        with open(self.prefs_file, 'w') as f:
            try:
                json.dump(self.prefs, f,indent=4, sort_keys=True )
            except Exception as e:
                self.send_notif(
                    self.note,
                    'Failed writing ' + self.prefs_file,
                    str(e)
                )

def main():
    indicator = NetatmoIndicator()
    indicator.run()


if __name__ == '__main__':
    main()
