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
import math
import dbus
import shutil
import copy
import subprocess
from os import statvfs
from gi.repository import Notify
from gi.repository import Gio
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib
import gi
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
# from collections import OrderedDict


class NetatmoIndicator(object):

    def __init__(self):
        self.app = appindicator.Indicator.new(
            'udisks-indicator', "drive-harddisk-symbolic.svg",
            appindicator.IndicatorCategory.HARDWARE
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

        netatmo = Netatmo()
        self.netatmo_data = netatmo.get_data()
        self.make_menu()
        self.update()

    def run(self):
        """ Launches the indicator """
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass

    def update(self):
        timeout = 15 * 60
        glib.timeout_add_seconds(timeout, self.callback)
        netatmo = Netatmo()
        self.netatmo_data = netatmo.get_data()

    def callback(self):

        icon_theme = self.gsettings_get(
            'org.gnome.desktop.interface', None, 'icon-theme'
        )
        if self.cache != data:
            if len(self.cache) != len(data):
                self.make_menu()
            else:
                self.update_label(i[0], label)
            self.cache = data
        self.update()

    def quit(self, *args):
        """ closes indicator """
        gtk.main_quit()

    def make_menu(self, *args):
        """ generates entries in the indicator"""
        if hasattr(self, 'app_menu'):
            for item in self.app_menu.get_children():
                self.app_menu.remove(item)
        self.app_menu = gtk.Menu()
        self.mounted_devs = {}

        drive_icon = 'gnome-dev-harddisk'
        usb_icon = 'media-removable'
        optical_icon = 'media-optical'

        icon_theme = self.gsettings_get(
            'org.gnome.desktop.interface', None, 'icon-theme'
        )
        if str(icon_theme) == "'ubuntukylin-icon-theme'":
            usb_icon = 'drive-harddisk-usb'

        for k, v in self.netatmo_data.iteritems():

            icon = drive_icon

            contents = [self.app_menu, gtk.ImageMenuItem, icon,
                        k + ": " + str(v), None, [None]]
            self.add_menu_item(*contents)

        contents = [self.app_menu, gtk.SeparatorMenuItem, None,
                    None, None, [None]
                    ]
        self.add_menu_item(*contents)

        contents = [self.app_menu, gtk.ImageMenuItem, 'exit',
                    'Quit', self.quit, [None]
                    ]
        self.add_menu_item(*contents)
        contents = None
        self.app.set_menu(self.app_menu)

    def add_menu_item(self, menu_obj, item_type, image, label, action, args):
        """ dynamic function that can add menu items depending on
            the item type and other arguments"""
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

        # small addition for this specific indicator
        if label:
            if 'Partition' and 'Usage' in label:
                self.mounted_devs[label] = menu_item

        menu_obj.append(menu_item)
        menu_item.show()

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