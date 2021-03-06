#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import pythonmodules
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

def setup():
    pythonmodules.compile()

def install():
    pythonmodules.install()
    shelltools.chmod("%s/usr/bin/runxlrd.py" % get.installDIR(), 0755)

