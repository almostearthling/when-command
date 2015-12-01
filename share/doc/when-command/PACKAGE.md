# Packaging When

In order to build a package that is compatible with the Linux FHS and LSB, many changes have been introduced in the directory structure of the **When** source tree. The most significant changes are:

* a new position for the main applet script
* a slightly different hierarchy in the `share` directory, with the introduction of
  - a folder for standard icons in different sizes, under `share/icons/hicolor/<size>/apps/when-command`
  - a `share/doc/when-command` folder which will contain all documentation (`.md` files and `LICENSE`) upon installation
  - the `share/when-command` folder where all resources have been moved, including the main applet script `when-command.py`
* the files needed by the standard Python setup script, as well as the setup script itself (namely `setup.py`, `setup.cfg` and `MANIFEST.in`), have been added to the project
* a stub file that will serve as the main entry point to start `when-command` instead of invoking the main applet script
* other files required by the utilities used to build the Debian package.

Other changes involve the code itself: parts of the script has been modified in order to allow better recognition of the *LSB-based* installation (the one that expects the entry point to be installed in `/usr/bin` and data files in `/usr/share`), even though the possibility has been kept to build a package that installs **When** in `/opt` as it has been usual until now. From now on the preferred installation mode will be the *LSB-based* one, the `/opt` based package is supported on a "best effort" basis for whoever would want to keep **When** separated from the Linux installation.

Unfortunately the new directory setup could require some more effort to allow for local installations (e.g. in the user's home directory), although I'll try to do my best to make this process as easy as possible.


## Requirements for packaging

**When** uses Python 3.x `setuptools` (package `python3-setuptools`, it is possibly already installed on the system) to create the source distribution used bu the packaging system. Most information about how to package an application has been retrieved in [Packaging and Distributing Projects](http://python-packaging-user-guide.readthedocs.org/en/latest/distributing/), in [Introduction to Debian Packaging](https://wiki.debian.org/IntroDebianPackaging) and [Python libraries/application packaging](https://wiki.debian.org/Python/Packaging), as well as in the [setuptools documentation](http://pythonhosted.org/setuptools/). Especially, the `stdeb` for Python 3.x has been used: this package is not provided by the standard repository in *Ubuntu 14.04*, so a *pip* installation may be required:

```
$ pip3 install --user stdeb
```

Also, to build a `.deb` package, the standard `debhelper`, `build-essential` and `fakeroot` packages and tasks are needed. I also installed `python-all`, `python3-all`, `python-all-dev`, `python3-all-dev` and `python-stdeb` (which is available, but it is for Python 2.x and quite old), but they might be not needed.


## Package creation

As far as I'm concerned, this step can be considered black magic. I expected packaging to be a relatively simple thing to do, something more similar to stuffing files into a tarball and then adding some metadata to the archive to allow for the installation tools to figure out how things have to be done. Apparently there is much more than that, especially when it comes to Python applications. And when the main entry point of such a Python application contains a dash, things get worse: none of the standard installation methods that use the `setup.py` script seems to be suitable. That is why, for instance, the `when-command.py` script is considered  a data file in the whole process, whereas a stub script named `when-command` (with no extension) is marked as *script*: we will not use the `entry_points` setup keyword, because we don't absolutely want `setup.py` to generate the stub script for us, since the *supposed-to-be-library* file contains a dash and could be not imported in an easy way.

However, here are the steps I perform to build a `.deb` package.

### 1. Build a source distribution

After unpacking the source tree, the following commands can be used to build a suitable source distribution:

```
$ cd <when-source-tree>
$ python3 setup.py --command-packages=stdeb.command bdist_deb
```

The `python3 setup.py --command-packages=stdeb.command bdist_deb` actually builds a `.deb` file. However this is not the `.deb` file we are looking for: we are more interested in the tarball byproduct that is created in the top directory of the source tree for the moment being, to gain some more control over package creation.

### 2. Create a packaging directory

The formerly created tarball should be moved to an empty directory and unpacked:

```
$ cd <new-directory>
$ cp <when-source-tree>/when-command*.tar.gz .
$ tar xzf when-command*.tar.gz
```

Then use the `py2dsc` tool to create the structure suitable for packaging:

```
$ py2dsc -m "$DEBFULLNAME <$DEBEMAIL>" when-command-<version_identifier>.tar.gz
$ cd deb_dist/when-command-<version_identifier>
```

The guide in [Python libraries/application packaging](https://wiki.debian.org/Python/Packaging) suggests then to edit some files in the `debian` subdirectory, namely `control` and `rules`. The files should read as follows:

**control:**
```
Source: when-command
Maintainer: Francesco Garosi (AlmostEarthling) <franz.g@no-spam-please.infinito.it>
Section: misc
Priority: optional
Build-Depends: python3-setuptools, python3, debhelper (>= 7.4.3)
Standards-Version: 3.9.5
X-Python3-Version: >= 3.4

Package: when-command
Architecture: all
Depends: ${misc:Depends}, ${python3:Depends}, python-support (>= 0.90.0), python3-gi, xprintidle, gir1.2-appindicator3-0.1, python3-pyinotify
Description: When Gnome Scheduler
 When is a configurable user task scheduler, designed with Ubuntu
 in mind. It interacts with the user through a GUI, where the user
 can define tasks and conditions, as well as relationships of
 causality that bind conditions to tasks.
 ```

**rules:**
```
#!/usr/bin/make -f

%:
	dh $@ --with python3

override_dh_auto_clean:
	python3 setup.py clean -a
	find . -name \*.pyc -exec rm {} \;

override_dh_auto_build:
#	python3 setup.py build --force

override_dh_auto_install:
	python3 setup.py install --force --root=debian/when-command --install-layout=deb --install-lib=/usr/share/when-command --install-scripts=/usr/bin

override_dh_python3:
	dh_python3 --shebang=/usr/bin/python3
```

Since we use a stub file, no `links` specification is actually necessary. This in fact differs from the advices given in the aforementioned guide: instead of specifying the target directory for *scripts* as `/usr/share/when-command` (same as the main script) in the package creation `rules`, we let the package install the stub in `/usr/bin` directly and don't rely on symbolic links. This simplifies a little the package creation procedure and provides an even more clean installation.

### 3. Build the package

To build the package the standard Debian utilities can be used, in the following way, when in the `deb_dist/when-command-<version_identifier>` directory:

```
debuild
```

The package is in the `deb_dist` directory. This directory also contains source packages, in the form of `.tar.gz`, `.dsc` and `.changes` files.

For `lintian` to complain somewhat less during the build process, the copyright file can be copied in the `debian` directory in `deb_dist/when-command-<version_identifier>`, issuing something like

```
pkgdir=deb_dist/when-command-<version_identifier>
cp $pkgdir/share/doc/when-command/copyright $pkgdir/debian
```

*before* launching `debuild`.

To build the package, the `DEBFULLNAME` and `DEBEMAIL` environment variables are required, and must match the name and e-mail address provided when the *GPG key* used to sign packages has been generated: see the [Ubuntu Packaging Guide](http://packaging.ubuntu.com/html/getting-set-up.html#create-your-gpg-key) for details.


## The old way

As suggested above, a way to build the old `/opt` based package is still available. I use a script that moves all files in the former positions, removes extra and unused files and scripts, and then builds a `.deb` that can be used to install the applet in `/opt/when-command`. This file can be found in a GitHub [gist](https://gist.github.com/almostearthling/009fbbe27ea5ca921452), together with the `control_template` file that it needs to build the package. It has to be copied to a suitable build directory together with `control_template`, made executable using `chmod a+x makepkg.sh`, modified regarding the variables at the top of the file and launched.
