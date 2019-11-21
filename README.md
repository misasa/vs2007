# python package -- vs2007

Provide two commands (`vs` and `vs-api`) that control the program `VisualStage 2007`.
The two commands enable users to develop a program by talking to `VisualStage 2007`. 

The command `vs` is for starting/stopping the program `VisualStage 2007`, opening/closing its data file, and outputting its adress and attachment. 
The command `vs-api` is for executing VisualStageAPI as an argument. 

See
[gem package -- visual_stage](https://gitlab.misasa.okayama-u.ac.jp/gems/visual_stage)
and `vs_attach_image.m` in 
[Matlab script -- VisualSpots](http://multimed.misasa.okayama-u.ac.jp/repository/matlab/)
that refer to this package.

# Dependency

## VisualStage 2007 for Windows

TK confirmed this work with VisualStage 2007 (version 1.1).  Very
likely this also works with VisualStage 2007 (version 1.2).

## [Python 3.7 for Windows](https://www.python.org/downloads/windows/)

Include "C:\Python37\;C:\Python37\Scripts\" to %PATH%.

# Installation

Configure git environment to talk to https://gitlab.misasa.okayama-u.ac.jp/ and install this package as Administrator as:

    ADMIN.CMD> pip install git+http://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007.git

Or download [archive.zip](http://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007/repository/archive.zip) to a local directory and install it as Administrator as:

    ADMIN.CMD> pip list
    ADMIN.CMD> pip uninstall vs2007
    $ wget https://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007/repository/archive.zip
    ADMIN.CMD> pip install archive.zip

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
