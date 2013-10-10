#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import shelltools
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get


def setup():
    autotools.autoreconf("-fiv")
    autotools.configure("--disable-static  --sysconfdir=/etc --with-included-modules=basic-fc")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    
    pisitools.dodir("/etc/pango")
    shelltools.touch(get.installDIR() +"/etc/pango/pango.modules")
    
    pisitools.dodoc("AUTHORS", "ChangeLog*", "COPYING", "README", "NEWS")
