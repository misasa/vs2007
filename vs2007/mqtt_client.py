#!/usr/bin/env python
from optparse import OptionParser
import sys, os
import logging
import vs2007
import vs2007.process
import vs2007.messenger
from vs2007._version import __version__ as VERSION
#import vs2007.api
#import vs2007.comm
#import vs2007.get_position
#import vs2007.set_position
import socket
import select
from threading import Thread
import paho.mqtt.client as mqtt
import json
import datetime
import time
from time import sleep 

import signal
signal.signal(signal.SIGINT,signal.SIG_DFL)

prog = "vs-sentinel"
_status = {
            "isStageConnected":"false",
            "isVSRunning":"false",
            "isAPIAvailable":"false",
            "isStageMoving":"false",
            "dataname":"",
}
_position = {
              "x_world":"",
              "y_world":"",
}
stage_info = {	"status": _status,
			          "position": _position
}

vs_handle = None
is_connected = False
config = None
process = None
vs_handler = vs2007.messenger.VSHandler()

options = {}

def _process():
    return vs2007.process.VS2007Process()

def _parser():
    global config
    config = vs2007.config()
    parser = OptionParser("""usage: %prog [options]

SYNOPSIS AND USAGE
  %prog [options]

DESCRIPTION
    MQTT publisher and subscriber for vs-remote app. This program
    publishes stage or marker position regulary and receives commands
    from vs-remote app.
    Note that this program reads `~/.vs2007rc' for configuration.
    Set `stage-name' line on the configuration file as below.

    stage-name: myStage

    If you see timeout error, set `timeout'
    line on the configration file as below and raise the
    value.  Default setting is 5000 mseconds.

    timeout: 5000  

EXAMPLE
    CMD> vs-sentinel
    CMD> vs-sentinel --stage-name myStage
    CMD> vs-sentinel --stage-name myStage --timeout 8000 
SEE ALSO
  http://dream.misasa.okayama-u.ac.jp
  https://github.com/misasa/vs2007/blob/master/vs2007/command_api.py

IMPLEMENTATION
  Orochi, version 9
  Copyright (C) 2014-2020 Okayama University
  License GPLv3+: GNU GPL version 3 or later

HISTORY
  September 2, 2020: Add Program
""")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
    parser.add_option("--stage-name",action="store",type="string",dest="stage_name",default=config['stage_name'],help="set the name of stage to identify the MQTT message (default: '%default') which the program will publish and subscribe to.")
    parser.add_option("--mqtt-host",action="store",type="string",dest="mqtt_host",default=config['mqtt_host'],help="set the address of the MQTT broker (default: %default) which the program will connect to.")
    parser.add_option("--mqtt-port",action="store",type="int",dest="mqtt_port",default=config['mqtt_port'],help="set the port of the MQTT broker (default: %default) which the program will connect to.")
#    parser.add_option("--tls-path",action="store",type="string",dest="tls_path", default=config['tls_path'],help="set the tls file path of the MQTT broker (default: %default) which the program will connect to.")
    parser.add_option("--timeout",action="store",type="int",dest="timeout",default=config['timeout'],help="set timeout in msec (default: %default)")
    parser.add_option("-l","--log_level",dest="log_level",default="INFO",help="set log level")
    return parser

def _parse_options():
    parser = _parser()
    (options, args) = parser.parse_args()
    options.topic_info = 'stage/info/' + options.stage_name
    options.topic_status = 'stage/status/' + options.stage_name
    options.topic_position = 'stage/position/' + options.stage_name
    options.topic_ctrl = 'stage/ctrl/' + options.stage_name

    return options, args

def _get_vs_handle(options):
  global vs_handler
  return vs_handler.get_vs_handle()

def _thread_move(handle, data, client, options):
    global stage_info
    global is_connected

    if (vs2007.process.VS2007Process.is_running() and (handle is not None)):
      _w = vs2007.messenger.Messenger(handle)
      stage_info['status']['isStageMoving'] = "true"
      command = 'CONTROL_MOVE_STAGE %s,%s' % (data["d_x"], data["d_y"])
      t_start = time.time()
      output = _w.command(command)
      _dt = time.time() - t_start
      line = "{0} -> {1} (response: {2:.2f} sec)".format(command, output, _dt)
      logging.info(line)
      _w.close()
      vals = output.split()
      status = vals[0]
      if status == 'SUCCESS':
          stage_info['status']['isStageConnected'] = "true"
      elif status == 'FAILURE':
          stage_info['status']['isStageConnected'] = "false"
      stage_info['status']['isStageMoving'] = "false"
      publish_message(client, options.topic_info, { "command": command, "output":output, "response": _dt})

def _thread_position(handle, client, options):
    logging.info("starting thread_position...")
    if (vs2007.process.VS2007Process.is_running() and (handle is not None)):
      _w = vs2007.messenger.Messenger(handle)
      while True:
        command = 'GET_STAGE_POSITION'
        t_start = time.time()
        output = _w.command(command)
        _dt = time.time() - t_start
        line = "{0} -> {1} (response: {2:.2f} sec)".format(command, output, _dt)
        logging.info(line)
        vals = output.split()
        status = vals[0]
        if status == 'SUCCESS':
            stage_info['status']['isStageConnected'] = "true"
            vv = vals[1].split(',')
            stage_info['position']['x_world'] = vv[0]
            stage_info['position']['y_world'] = vv[1]

        elif status == 'FAILURE':
            stage_info['status']['isStageConnected'] = "false"

        publish_message(client, options.topic_position, _position)
        publish_message(client, options.topic_info, { "command": command, "output":output, "response": _dt})
        sleep(1)

# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    global is_connected

    logging.info("Connected with result code " + str(rc))
    is_connected = True
    logging.info("subscribe topic |%s| to receive stage control command..." % options.topic_ctrl)
    client.subscribe(options.topic_ctrl)  # subするトピックを設定 

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, flag, rc):
    global is_connected

    is_connected = False
    logging.info("on_disconnect")
    logging.info(rc)
    if rc != 0:
        print("Unexpected disconnection.")

# publishが完了したときの処理
def on_publish(client, userdata, mid):
    logging.debug("published: {0}".format(mid))

# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
    logging.info("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    data = json.loads(msg.payload)
    global vs_handle

    if vs_handle is not None:
        thread1 = Thread(target=_thread_move, args=(vs_handle, data, client, options,))
        thread1.setDaemon(True)
        thread1.start()

def publisher(client):
    global is_connected
    global vs_handle
    global process

    while True:
        if not is_connected:
            sleep(1)
            continue
        stage_info['position']['x_world'] = ""
        stage_info['position']['y_world'] = ""
        stage_info["status"]["isVSRunning"] = "false"
        stage_info["status"]["isAPIAvailable"] = "false"
        stage_info["status"]["dataname"] = ""
        if vs2007.process.VS2007Process.is_running():
            stage_info["status"]["isVSRunning"] = "true"
            if process is None:
                process = _process()
            if process and process.is_file_opened:
                stage_info["status"]["dataname"] = process.get_dataname()
        else:
            stage_info["status"]["isRunning"] = "false"
            process = None
            vs2007.process.VS2007Process.pid = None
            vs_handle = None

        if vs_handle is None:
          vs_handle = _get_vs_handle(options)
          if vs_handle is not None:
            thread1 = Thread(target=_thread_position, args=(vs_handle, client, options,))
            thread1.setDaemon(True)
            thread1.start()
            stage_info["status"]["isAPIAvailable"] = "true"
          else:
            stage_info["status"]["isAPIAvailable"] = "false"
            stage_info["status"]["isStageConnected"] = "false"
            stage_info['position']['x_world'] = ""
            stage_info['position']['y_world'] = ""
            publish_message(client, options.topic_position, _position)
        else:
          stage_info["status"]["isAPIAvailable"] = "true"        
        publish_message(client, options.topic_status, _status)
        sleep(1)
def publish_message(client, topic, message):
  message["updated_at"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
  json_message = json.dumps( message )
  rc = client.publish(topic, json_message)
  if rc[0] == mqtt.MQTT_ERR_SUCCESS:
      logging.info("publish message {} on topic {}".format(json_message, topic))
  else:
      logging.info(mqtt.error_string(rc[0]))
      if rc[0] == mqtt.MQTT_ERR_NO_CONN:
          is_connected = False
          logging.info("waiting connection...")
  

def main():
    global options
    (options, args) = _parse_options()
    logging.basicConfig(level=options.log_level.upper(), format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("version %s" % VERSION)
    logging.debug(options)
    
    client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
    client.on_connect = on_connect         # 接続時のコールバック関数を登録
    client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
    client.on_publish = on_publish         # メッセージ送信時のコールバック
    client.on_message = on_message
    #client.tls_set(options.tls_path)
    logging.info('connecting %s:%s' % (options.mqtt_host, options.mqtt_port))
    try:
        client.connect(options.mqtt_host, options.mqtt_port, 60)  # 接続先は自分自身
        client.loop_start()
        publisher(client)
    except Exception as e:
        print(e, file=sys.stderr)
    
if __name__ == '__main__':
    main()