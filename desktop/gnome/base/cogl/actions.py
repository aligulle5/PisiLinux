#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

shelltools.export("HOME", get.workDIR())

def setup():
    autotools.autoreconf("-fiv")
    autotools.configure("\
                         --disable-static \
                         --with-pic \
                         --enable-introspection=yes \
                         --enable-cairo=yes \
                         --enable-gdk-pixbuf=yes \
                         --enable-cogl-pango=yes \
                         --enable-glx=yes \
                         --enable-gles1=yes \
                         --enable-gles2=yes \
                        ")

def build():
    autotools.make()

def install():
    autotools.install()

    pisitools.dodoc("COPYING", "README")

