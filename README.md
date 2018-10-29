# python package -- vs2007

To provide two commands (vs and vs-api) that control the application program `VisualStage 2007`
on a command line. The vs is a command to start/stop Visual Stage and open/close its data file
as well as to output the adress and the attachement. The vs-api is a command to execute 
VisualStageAPI command specified as an argument.  

See
[gem package -- vstool](https://gitlab.misasa.okayama-u.ac.jp/gems/vstool/tree/master)
`Matlab script -- vs_attach_image.m`
that refer to this package.

# Dependency

## VisualStage 2007 for Windows

TK confirmed this work with VisualStage 2007 (version 1.1).  Very
likely this also works with VisualStage 2007 (version 1.2).

## [Python for Windows](https://www.python.org/downloads/windows/)

Include "C:\Python27\;C:\Python27\Scripts\" to %PATH%.  TK confirmed
`python-2.7.15.msi` and `python-2.7.15.amd64.msi` work for 32-bit and
64-bit Windows (August 29, 2018).

## Git

You have to configure git environment to talk to
"https://gitlab.misasa.okayama-u.ac.jp/".

# Installation

Install it as Administrator as:

    ADMIN.CMD> pip install git+http://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007.git

Or download [vs2007-xxxyyyzzz.zip](http://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007/repository/archive.zip) to a local directory and install it as Administrator as:

    $ cd ~/Downloads
    $ wget http://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007/repository/archive.zip
    $ ls | grep zip
    vs2007-37fd5efca85718a41c6370689886d565ceaf44c6.zip
    ADMIN.CMD> pip install vs2007-37fd5efca85718a41c6370689886d565ceaf44c6.zip

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
