# python package -- vs2007

Provide two commands (`vs`, `vs-api` and `vs-sentinel`) that control the program `VisualStage 2007`.
These commands enable users to develop a program by talking to `VisualStage 2007`. 

The command `vs` is for starting/stopping the program `VisualStage 2007`, opening/closing its data file, and outputting its adress and attachment. 
The command `vs-api` is for executing VisualStageAPI as an argument. 
The command `vs-sentinel` is for control `VisualStage 2007` via network.
See
[gem package -- visual_stage](https://github.com/misasa/visual_stage)
and `vs_attach_image.m` in 
[Matlab script -- VisualSpots](http://multimed.misasa.okayama-u.ac.jp/repository/matlab/)
that refer to this package.

# Dependency

## VisualStage 2007 for Windows

TK confirmed this work with VisualStage 2007 (version 1.1).  Very
likely this also works with VisualStage 2007 (version 1.2).

## [Python 3.7 for Windows](https://www.python.org/downloads/windows/)

Include "C:\Python37\;C:\Python37\Scripts\" in %PATH%.

# Installation

Install this package as Administrator as:

    ADMIN.CMD> pip install git+https://github.com/misasa/vs2007/archive/refs/heads/master.zip

or download [vs2007-master.zip](https://github.com/misasa/vs2007/archive/refs/heads/master.zip) to a local directory and install it as Administrator as:

    $ cd ~/Downloads/
    $ wget https://github.com/misasa/vs2007/archive/refs/heads/master.zip
    ADMIN.CMD> cd %USERPROFILE%\Downloads\
    ADMIN.CMD> pip list
    ADMIN.CMD> pip uninstall vs2007
    ADMIN.CMD> pip install vs2007-master.zip

Successful installation is confirmed by:

    CMD> vs-api --help
    CMD> vs-api TEST_CMD

# Commands

Commands are summarized as:

| command | description                       | note |
| ------- | --------------------------------- | ---- |
| vs      | Start and stop VisualStage 2007   |      |
| vs-api  | Interactive with VisualStage 2007 |      |
| vs-sentinel  | Control VisualStage 2007 via network |      |


# Usage

See online document with option `--help`.

# Control a stage from remote

Start VisualStage2007 and lunch vs-sentinel as shown below. Revise configuration file (~/.vs2007rc) when necessary.

    > vs start
    > vs-sentinel
    reading |C:\Users\yyachi\.vs2007rc| ...
    2020-09-23 11:06:38,580 INFO:connecting database.misasa.okayama-u.ac.jp:1883
    publisher...
    2020-09-23 11:06:38,667 INFO:Connected with result code 0
    2020-09-23 11:06:38,677 INFO:subscribe topic |stage/ctrl/stage-of-sisyphus-THINK| to receive stage control command...
    2020-09-23 11:06:40,536 INFO:getting API...
    2020-09-23 11:06:40,560 INFO:vsapi GET_STAGE_POSITION -> FAILURE
    2020-09-23 11:06:40,560 INFO:vsapi GET_MARKER_POSITION -> SUCCESS POINT,-1583.126,-2935.833
    2020-09-23 11:06:40,561 INFO:publish message {"status": {"isConnected": "false", "isRunning": "true", "isAvailable": "true"}, "position": {"x_world": "-1583.126", "y_world": "-2935.833"}} on topic stage/info/stage-of-sisyphus-THINK
    2020-09-23 11:06:40,561 INFO:published: 2
    2020-09-23 11:06:41,561 INFO:vsapi GET_STAGE_POSITION -> FAILURE
    2020-09-23 11:06:41,562 INFO:vsapi GET_MARKER_POSITION -> SUCCESS POINT,-1583.126,-2935.833
    2020-09-23 11:06:41,562 INFO:publish message {"status": {"isConnected": "false", "isRunning": "true", "isAvailable": "true"}, "position": {"x_world": "-1583.126", "y_world": "-2935.833"}} on topic stage/info/stage-of-sisyphus-THINK
    2020-09-23 11:06:41,562 INFO:published: 3
    2020-09-23 11:06:42,563 INFO:vsapi GET_STAGE_POSITION -> FAILURE
    2020-09-23 11:06:42,564 INFO:vsapi GET_MARKER_POSITION -> SUCCESS POINT,-1583.126,-2935.833
    2020-09-23 11:06:42,564 INFO:publish message {"status": {"isConnected": "false", "isRunning": "true", "isAvailable": "true"}, "position": {"x_world": "-1583.126", "y_world": "-2935.833"}} on topic stage/info/stage-of-sisyphus-THINK
    2020-09-23 11:06:42,564 INFO:published: 4
    ....

### Example of configuration file

    > cat ~/.vs2007rc
    ---
    stage_name: stage-of-sisyphus-THINK
    timeout: 8000
    vsdata_path: Z:\
    world_origin: ld
    stage_origin: ru
    
### control via web browser
Access [machine list](https://database.misasa.okayama-u.ac.jp/machine/) and open an [Edit Machine (ex. SIMS-1280)](https://database.misasa.okayama-u.ac.jp/machine/machines/3/edit) for the machine you want to control (by clicking the gear icon next to the machine name on the list).
Input the stage name (for example `stage-of-sisyphus-THINK`) and click OK.
Then you can see the XY position of the stage on web browser in real time.

### control via command line
Download and install a MQTT client software [mosquitto](http://mosquitto.org/download/)
To receive current position (and status) of `stage-of-sisyphus-THINK`, issue following command. 

    > mosquitto_sub -h database.misasa.okayama-u.ac.jp -t stage/info/stage-of-sisyphus-THINK

In order to move the stage `stage-of-sisyphus-THINK` to the specified position (for example [0.0, 0.0]), issue following command.

    > mosquitto_pub -h database.misasa.okayama-u.ac.jp -t stage/ctrl/stage-of-sisyphus-THINK -m "{\"command\":\"GOTO\",\"d_x\":\"0.0\",\"d_y\":\"0.0\"}"
