# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt


from pisi.actionsapi import kerneltools
from pisi.actionsapi import shelltools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

WorkDir = "."
KDIR = kerneltools.getKernelVersion()
NoStrip = ["/lib/modules"]

BuildDir = "common/lib/modules/fglrx/build_mod"

if get.buildTYPE() == 'emul32':
    Target = "x86"
    Libdir = "/usr/lib32"
else:
    Target = get.ARCH().replace("i686", "x86")
    Libdir = "/usr/lib"

XDir = "xpic" + ("_64a" if Target == "x86_64" else "")

def setup():
    shelltools.export("SETUP_NOCHECK", "1")
    shelltools.system("sh amd-driver-installer-*-x86.x86_64.run --extract .")

    if get.buildTYPE() == "emul32":
        return

    # Needed during kernel module compiling
    shelltools.sym("../../../../../arch/%s/lib/modules/fglrx/build_mod/libfglrx_ip.a" % Target, "%s/libfglrx_ip.a" % BuildDir)

    pisitools.dosed("%s/make.sh" % BuildDir, r"^linuxincludes=.*", "linuxincludes=/lib/modules/%s/build/include" % KDIR)
    pisitools.dosed("%s/make.sh" % BuildDir, r"^uname_r=.*", "uname_r=%s" % KDIR)
    pisitools.dosed("common/etc/ati/authatieventsd.sh", "/var/lib/xdm/authdir/authfiles", "/var/run/xauth")

    shelltools.system("patch -p1 < do_mmap.patch")
    shelltools.system("patch -p1 < desktop-files.patch")
    shelltools.system("patch -p1 < ati-powermode.patch")
    shelltools.system("patch -p1 < fix-build-kernel-3.8.patch")

    pisitools.dosed("./", "linux/version.h", "generated/uapi/linux/version.h", namePattern = ".*\.(c|h|sh)$")
    pisitools.dosed("common/lib/modules/fglrx/build_mod/firegl_public.c", "(#define __AGP__BUILTIN__)", r"\1\n#ifndef VM_RESERVED\n#define VM_RESERVED (VM_DONTEXPAND | VM_DONTDUMP)\n#endif")

def build():
    if get.buildTYPE() == "emul32":
        return

    shelltools.cd(BuildDir)
    shelltools.system("sh make.sh")

def install():
    # Controlcenter binaries
    if not get.buildTYPE() == 'emul32':
        pisitools.dobin("arch/%s/usr/X11R6/bin/*" % Target)
        pisitools.dobin("common/usr/X11R6/bin/*")
        pisitools.dosbin("arch/%s/usr/sbin/*" % Target)
        pisitools.dosbin("common/usr/sbin/*")

    # Controlcenter libraries
    # The other files under /usr/share are common files like icon,man,doc ,etc ..
    DIRS = {
            "common/usr/share/doc/fglrx/examples/etc/acpi/events":  "/etc/acpi",
            "common/etc/*":                         "/etc",
            "arch/%s/usr/X11R6/lib*/*" % Target:    Libdir,
            "arch/%s/usr/lib*/*" % Target:          Libdir,
            "common/usr/share/*":                     "/usr/share"
            }

    # Emul32 package don't need files that belongs to /usr/share
    if get.buildTYPE() == "emul32":
        del DIRS["common/usr/share/*"]
        del DIRS["common/etc/*"]
        del DIRS["common/usr/share/doc/fglrx/examples/etc/acpi/events"]

    for source, target in DIRS.items():
        pisitools.insinto(target, source)

    # X.org drivers
    pisitools.domove("%s/modules" % Libdir, "%s/fglrx" % Libdir)
    pisitools.insinto("%s/fglrx/modules" % Libdir, "%s/usr/X11R6/lib*/modules/*" % XDir)

    # libGl library name changed to fglrx-libGl since 1.15
    pisitools.domove("%s/fglrx/fglrx-libGL.so.1.2" % Libdir, "%s/fglrx" % Libdir, "libGL.so.1.2")

    pisitools.domove("%s/fglrx/modules/dri" % Libdir, "%s/xorg/modules/" % Libdir)

    pisitools.domove("%s/fglrx/modules/extensions/fglrx/fglrx-libglx.so" % Libdir,
                     "%s/fglrx/modules/extensions" % Libdir, "libglx.so")

    # Necessary symlinks
    pisitools.dosym("%s/xorg/modules/dri/fglrx_dri.so" % Libdir, "%s/dri/fglrx_dri.so" % Libdir)

    pisitools.dosym("libatiuki.so.1.0", "%s/libatiuki.so.1" % Libdir)
    pisitools.dosym("libatiuki.so.1", "%s/libatiuki.so" % Libdir)

    pisitools.dosym("libfglrx_dm.so.1.0", "%s/libfglrx_dm.so.1" % Libdir)
    pisitools.dosym("libfglrx_dm.so.1", "%s/libfglrx_dm.so" % Libdir)

    pisitools.dosym("libAMDXvBA.so.1.0", "%s/libAMDXvBA.so.1" % Libdir)
    pisitools.dosym("libAMDXvBA.so.1", "%s/libAMDXvBA.so" % Libdir)

    pisitools.dosym("libXvBAW.so.1.0", "%s/libXvBAW.so.1" % Libdir)
    pisitools.dosym("libXvBAW.so.1", "%s/libXvBAW.so" % Libdir)


    # remove static libs
    pisitools.remove("%s/*.a" % Libdir)
    if shelltools.isFile("%s%s/fglrx/modules/esut.a" % (get.installDIR(), Libdir)):
        pisitools.remove("%s/fglrx/modules/esut.a" % Libdir)

    # compatibility links
    pisitools.dosym("xorg/modules", "%s/modules" % Libdir)

    #OpenCL
    DIRS = {
            "arch/%s/usr/bin/clinfo" % Target                : "/usr/bin",
            "arch/%s/etc/*" % Target                         : "/etc",
            "arch/%s/usr/lib*/libamdocl*" % Target            : Libdir,
            "arch/%s/usr/lib*/libOpenCL*" % Target            : Libdir,
            }
    
    if get.buildTYPE() == "emul32":
        del DIRS["arch/%s/usr/bin/clinfo" % Target]
        del DIRS["arch/%s/etc/*" % Target]

    for source, target in DIRS.items():
        pisitools.insinto(target, source)
    
    pisitools.dosym("libOpenCL.so.1", "%s/libOpenCL.so" % Libdir)

    # OK, That's the end of emul32 build, it's time to exit.
    if get.buildTYPE() == "emul32":
        return

    # Header Files
    pisitools.insinto("/usr/include/ATI/GL","common/usr/include/ATI/GL/*")
    pisitools.insinto("/usr/include/GL","common/usr/include/GL/*")

    # Another compatibility link
    pisitools.dosym("/usr", "/usr/X11R6")

    pisitools.dosym("../security/console.apps/amdcccle-su", "/etc/pam.d/amdcccle-su")

    # copy compiled kernel module
    pisitools.insinto("/lib/modules/%s/extra" % KDIR, "common/lib/modules/fglrx/fglrx.%s.ko" % KDIR, "fglrx.ko")

    # control script for ACPI lid state and AC adapter state
    pisitools.insinto("/etc/acpi", "common/usr/share/doc/fglrx/examples/etc/acpi/ati-powermode.sh")

    pisitools.domove("/usr/share/icons/ccc_large.xpm", "/usr/share/pixmaps", "amdcccle.xpm")
    pisitools.removeDir("/usr/share/icons")

    # not needed as xdg-utils package provides xdg-su
    pisitools.remove("/usr/bin/amdxdg-su")

    #LICENSE information
    #~ pisitools.dodoc("LICENSE.txt")

    # Fix file permissions
    exec_file_suffixes = (".sh", ".so", ".so.1.2")
    exec_dir_suffixes = ("/bin", "/sbin", "/lib")

    import os
    for root, dirs, files in os.walk(get.installDIR()):
        for name in files:
            filePath = os.path.join(root, name)
            if os.path.islink(filePath):
                continue
            if root.endswith(exec_dir_suffixes) \
                or name.endswith(exec_file_suffixes):
                shelltools.chmod(filePath, 0755)
            else:
                shelltools.chmod(filePath, 0644)
