#!/usr/bin/env python
from optparse import OptionParser
import sys, os
import logging
import vs2007
import vs2007.process
import vs2007.api
import socket
import select
from threading import Thread
import paho.mqtt.client as mqtt
import json
from time import sleep 

import signal
signal.signal(signal.SIGINT,signal.SIG_DFL)

prog = "vs-sentinel"

stage_info = {	"status":{
                            "isConnected":"false",
			    			"isRunning":"false",
			    		},
			    "position":{
                            "x_world":"",
                            "y_world":"",
                        }
            }

vsapi = None
config = None
#config = vs2007.config()
#config = vs2007.Config().config
options = {}
#def _config():

def _process():
    return vs2007.process.VS2007Process()

def _parser():
    global config
    config = vs2007.config()
    parser = OptionParser("""usage: %prog [options]

SYNOPSIS AND USAGE
  %prog [options]

DESCRIPTION
  
EXAMPLE

SEE ALSO
  http://dream.misasa.okayama-u.ac.jp
  https://gitlab.misasa.okayama-u.ac.jp/pythonpackage/vs2007/blob/master/vs2007/command_api.py

IMPLEMENTATION
  Orochi, version 9
  Copyright (C) 2014-2020 Okayama University
  License GPLv3+: GNU GPL version 3 or later

HISTORY
  September 2, 2020: Add Program
""")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
    parser.add_option("--stage-name",action="store",type="string",dest="stage_name", default=config['stage_name'],help="set the name of stage to identify the MQTT message (default: '%default') which the program will publish and subscribe to.")
    parser.add_option("--mqtt-host",action="store",type="string",dest="mqtt_host", default=config['mqtt_host'],help="set the address of the MQTT broker (default: %default) which the program will connect to.")
    parser.add_option("--mqtt-port",action="store",type="int",dest="mqtt_port", default=config['mqtt_port'],help="set the port of the MQTT broker (default: %default) which the program will connect to.")
#    parser.add_option("--tls-path",action="store",type="string",dest="tls_path", default=config['tls_path'],help="set the tls file path of the MQTT broker (default: %default) which the program will connect to.")
#    parser.add_option("--timeout",action="store",type="int",dest="timeout", default=0,help="set timeout in msec (default: 0 msec)")
    parser.add_option("-l","--log_level",dest="log_level",default="INFO",help="set log level")    
    return parser

def _parse_options():
    parser = _parser()
    (options, args) = parser.parse_args()
    options.topic_info = 'stage/info/' + options.stage_name
    options.topic_ctrl = 'stage/ctrl/' + options.stage_name

    return options, args

def _get_api(options):
    logging.info("getting API...")
    if vs2007.process.VS2007Process.is_running():
        return vs2007.api.VS2007API(None, 10)

def _clear_api():
    logging.info("clearing API...")
    vs2007.api.VS2007API.g_hVSWnd = None
    vs2007.process.VS2007Process.pid = None
    
def _send_command(command, timeout = 0):
    if vs2007.process.VS2007Process.is_running():
        vs2007p = vs2007.process.VS2007Process()
        return vs2007p.send_command(command, timeout)
# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    logging.info("Connected with result code " + str(rc))
    logging.info("subscribe topic |%s| to receive stage control command..." % options.topic_ctrl)
    client.subscribe(options.topic_ctrl)  # subするトピックを設定 

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, flag, rc):
    if rc != 0:
        print("Unexpected disconnection.")

# publishが完了したときの処理
def on_publish(client, userdata, mid):
    logging.info("published: {0}".format(mid))

# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
    logging.info("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    data = json.loads(msg.payload)
    global vsapi

    if vsapi is None:
        logging.debug('_get_api...')
        vsapi = _get_api(options)
        logging.debug('api:{}'.format(vsapi))

    if vsapi is not None:
        command = 'SET_MARKER_POSITION POINT,%s,%s' % (data["d_x"], data["d_y"])
        if stage_info["status"]["isConnected"] == "true":
            command = 'SET_STAGE_POSITION POINT,%s,%s' % (data["d_x"], data["d_y"])
        try:
            output = vsapi.send_command_and_receive_message(command, 1000)
            logging.info("vsapi {} -> {}".format(command, output))
            vals = output.split()
            status = vals[0]
            if status == 'TIMEOUT':
                vsapi = None
                _clear_api()
        except Exception as e:
            print('Exception occurred |%s|...' % command, file=sys.stderr)
            print(e, file=sys.stderr)
    else:
        logging.warning('VS not available')

def publisher(client):
    print("publisher...")
    #vsapi = None
    # 永久に繰り返す
    global vsapi

    while True:
        if vs2007.process.VS2007Process.is_running():
            stage_info["status"]["isRunning"] = "true"
        else:
            stage_info["status"]["isRunning"] = "false"

        if vsapi is None:
            logging.debug('_get_api...')
            vsapi = _get_api(options)
            logging.debug('api:{}'.format(vsapi))
            if vsapi is None:
                stage_info["status"]["isAvailable"] = "false"
                json_message = json.dumps( stage_info )
                client.publish(options.topic_info,json_message)
                logging.info("publish message {} on topic {}".format(json_message, options.topic_info))
                sleep(1)
                continue
        stage_info["status"]["isAvailable"] = "true"

        command = 'GET_STAGE_POSITION'
        try:
            output = vsapi.send_command_and_receive_message(command, 1000)
            logging.info("vsapi {} -> {}".format(command, output))
            vals = output.split()
            status = vals[0]
            if status == 'TIMEOUT':
                vsapi = None
                _clear_api()
            elif status == 'SUCCESS':
                stage_info['status']['isConnected'] = "true"
                vv = vals[1].split(',')
                if vv[0] == 'POINT':
                    stage_info['position']['x_world'] = vv[1]
                    stage_info['position']['y_world'] = vv[2]

            elif status == 'FAILURE':
                stage_info['status']['isConnected'] = "false"
                command = 'GET_MARKER_POSITION'
                try:
                    output = vsapi.send_command_and_receive_message(command, 1000)
                    logging.info("vsapi {} -> {}".format(command, output))
                    vals = output.split()
                    status = vals[0]
                    if status == 'TIMEOUT':
                        vsapi = None
                        _clear_api()
                    elif status == 'SUCCESS':
                        vv = vals[1].split(',')
                        if vv[0] == 'POINT':
                            stage_info['position']['x_world'] = vv[1]
                            stage_info['position']['y_world'] = vv[2]
                except Exception as e:
                    print('Exception occurred |%s|...' % command, file=sys.stderr)
                    print(e, file=sys.stderr)

        except Exception as e:
            print('Exception occurred |%s|...' % command, file=sys.stderr)
            print(e, file=sys.stderr)

        json_message = json.dumps( stage_info )
        client.publish(options.topic_info,json_message)
        logging.info("publish message {} on topic {}".format(json_message, options.topic_info))
        sleep(1)


def main():
    global options
    (options, args) = _parse_options()
    logging.basicConfig(level=options.log_level.upper(), format='%(asctime)s %(levelname)s:%(message)s')
    logging.debug(options)
    client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
    client.on_connect = on_connect         # 接続時のコールバック関数を登録
    client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
    client.on_publish = on_publish         # メッセージ送信時のコールバック
    client.on_message = on_message
    #client.tls_set(options.tls_path)
    logging.info('connecting %s:%s' % (options.mqtt_host, options.mqtt_port))
    client.connect(options.mqtt_host, options.mqtt_port, 60)  # 接続先は自分自身
    # 通信処理スタート
    client.loop_start()    # subはloop_forever()だが，pubはloop_start()で起動だけさせる
    publisher(client)
    

if __name__ == '__main__':
    main()
