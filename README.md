# vs2007

Offer API to communicate with application program for MS-Windows `VisualStage 2007`.

This is called by [gem package -- vstool](http://devel.misasa.okayama-u.ac.jp/gitlab/gems/vstool/tree/master) and `Mablab script -- vs_attach_image.m`.


# Dependency

## VisualStage 2007 for Windows

TK confirmed this work with VisualStage 2007 (version 1.1).  Very likely this also works with VisualStage 2007 (version 1.2).

##  [Python for Windows] (https://www.python.org/downloads/windows/)

Include "C:\Python27\;C:\Python27\Scripts\" to %PATH%.  TK confirmed `python-2.7.12.msi' and `python-2.7.12.amd64.msi' work for 32-bit and 64-bit Windows (October 6, 2016).

## [pip](https://pip.pypa.io/en/latest/installing.html "download and DOS> python get-pip.py")

TK confirmed Python for Windows includes `pip' 8.1.1.  (October 6, 2016).

## [pywin32] (http://sourceforge.net/projects/pywin32/)

Download and launch installer.  TK downloaded `pywin32-220.win32-py2.7.exe' and `pywin32-220.win-amd64-py2.7.exe' and confirmed to work (October 6, 2016).

## Git

You have to cofigure git environment to talk to
"http://devel.misasa.okayama-u.ac.jp/gitlab/".


# Installation

Install it as Administrator as:

    ADMIN.CMD> pip install git+http://devel.misasa.okayama-u.ac.jp/gitlab/pythonpackage/vs2007.git

Or download [vs2007-xxxyyyzzz.zip](http://devel.misasa.okayama-u.ac.jp/gitlab/pythonpackage/vs2007/repository/archive.zip) to local directory and install it as Administrator as:

    ADMIN.CMD> pip install vs2007-c18fb69e5c558269b4c0285d77b9b12708f37424.zip

Successful installation is confirmed by:

    CMD> vs-api --help
    CMD> vs-api TEST_CMD


# Commands

Commands are summarized as:

| command | description                       | note |
| ------- | --------------------------------- | ---- |
| vs      | Start and stop VisualStage 2007   |      |
| vs-api  | Interactive with VisualStage 2007 |      |


# Usage

See online document with option `--help`.
