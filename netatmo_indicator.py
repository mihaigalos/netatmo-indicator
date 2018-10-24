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

import gi
gi.require_version('Notify', '0.7')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import Notify
from gi.repository import Gio
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib


class Menu:
    def __init__(self, app, netatmo_data, netatmo_exception):
        if hasattr(self, 'app_menu'):
            for item in self.app_menu.get_children():
                self.app_menu.remove(item)
        self.app_menu = gtk.Menu()

        self.mounted_devs = {}

        display_string = ""

        if netatmo_exception is None:
            degree_sign = u'\N{DEGREE SIGN}'
            for k, v in netatmo_data.iteritems():
                display_string = display_string+k+": "+str(v)+degree_sign+" "

            app.set_label(display_string, "")
        else:
            display_string = "Error communicating with Netatmo."
            app.set_label(display_string, "")
            contents = [self.app_menu, gtk.ImageMenuItem, 'help-hint',
                        str(netatmo_exception), self.quit, [None]]
            self.add_menu_item(*contents)

        contents = [self.app_menu, gtk.ImageMenuItem, 'exit',
                    'Quit', self.quit, [None]
                    ]
        self.add_menu_item(*contents)
        self.app = app


    def add_menu_item(self, menu_obj, item_type, image, label, action, args):

        menu_item, icon = None, None
        if item_type is gtk.ImageMenuItem and label:
            menu_item = gtk.ImageMenuItem.new_with_label(label)
            menu_item.set_always_show_image(True)
            if '/' in image:
                icon = gtk.Image.new_from_file(image)
            else:
                icon = gtk.Image.new_from_icon_name(image, 48)
            menu_item.set_image(icon)
        elif item_type is gtk.ImageMenuItem and not label:
            menu_item = gtk.ImageMenuItem()
            menu_item.set_always_show_image(True)
            if '/' in image:
                icon = gtk.Image.new_from_file(image)
            else:
                icon = gtk.Image.new_from_icon_name(image, 16)
            menu_item.set_image(icon)
        elif item_type is gtk.MenuItem:
            menu_item = gtk.MenuItem(label)
        elif item_type is gtk.SeparatorMenuItem:
            menu_item = gtk.SeparatorMenuItem()
        if action:
            menu_item.connect('activate', action, *args)

        menu_obj.append(menu_item)
        menu_item.show()

    def get_menu(self):
        return self.app_menu

    def get_app(self):
        return self.app

    def quit(self, *args):
        gtk.main_quit()

class NetatmoIndicator(object):

    def __init__(self):
        current_folder =  os.getcwd()

        self.app = appindicator.Indicator.new(
            'netatmo-indicator', current_folder+"/FF4D00-0.0.png",
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )

        self.app.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.user_home = os.path.expanduser('~')
        self.prefs_file = os.path.join(
            self.user_home, ".netatmo-indicator-preferences.json")
        self.prefs = self.read_prefs_file()

        self.note = Notify.Notification.new(__file__, None, None)
        Notify.init(__file__)

        self.cache_icon_theme = self.gsettings_get(
            'org.gnome.desktop.interface', None, 'icon-theme'
        )

        self.mounted_devs = {}
        self.fetch_netatmo_data()

        self.make_menu()
        self.update()

    def fetch_netatmo_data(self):
        try:
            netatmo = Netatmo()
            self.netatmo_data = netatmo.get_data()
            self.netatmo_exception = None
        except Exception, err:
            self.netatmo_exception = err
            pass

    def run(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass

    def update(self):
        timeout = 15 * 60
        glib.timeout_add_seconds(timeout, self.callback)
        self.fetch_netatmo_data()

    def callback(self):
        if self.cache != data:
            if len(self.cache) != len(data):
                self.make_menu()
            else:
                self.update_label(i[0], label)
            self.cache = data
        self.update()



    def make_menu(self, *args):
        menu_object = Menu(self.app, self.netatmo_data, self.netatmo_exception)
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
        default = {'fields': [True] * 5, 'autostart': False}
        if not os.path.exists(self.prefs_file):
            return default

        with open(self.prefs_file) as f:
            try:
                return json.load(f)
            except:
                return default

    def write_prefs_file(self, *args):
        with open(self.prefs_file, 'w') as f:
            try:
                json.dump(self.prefs, f,
                          indent=4, sort_keys=True
                          )
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
