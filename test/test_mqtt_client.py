import os, shutil
from nose.tools import *
from mock import MagicMock
from testfixtures import LogCapture
import paho.mqtt.client as mqtt
import socket
import logging
import sys
import vs2007
import socket
import yaml
import copy
from vs2007.mqtt_client import main, _parse_options
original_default_config = copy.copy(vs2007.default_config)
files_dir = os.path.join(os.path.dirname(__file__), 'files')
vs2007.config_path = 'tmp/.vs2007rc'

def setup_tmp():
  if os.path.exists('tmp'):
    print("removing tmp/...")
    shutil.rmtree('tmp')
  print("creating tmp/...")
  os.mkdir('tmp')

def setup():
  print("setup...")
  setup_tmp()
  vs2007.default_config = original_default_config
  print(vs2007.default_config)
def teardown():
  print('teardown...')

@with_setup(setup, teardown)
def test_help():
    sys.argv = ['vs-sentinel', '--help']
    assert_raises(SystemExit, _parse_options)

@with_setup(setup, teardown)
def test_main_with_options():
    sys.argv = ['vs-sentinel', '-l', 'DEBUG', '--stage-name', 'stage-of-me', '--mqtt-host','mqtt.example.com', '--mqtt-port','8889', '--timeout', '5000']
    logging.basicConfig(
        level='INFO', format='%(asctime)s %(levelname)s:%(message)s')
    logger = logging.getLogger('')

    with LogCapture() as logs:
        mock_client = MagicMock(return_value = None)
        user_data = MagicMock(return_value = None)
        mqtt.Client = MagicMock(return_value = mock_client)
        vs2007.mqtt_client.publisher = MagicMock(return_value = None)
        main()
        mock_client.connect.assert_called_once_with('mqtt.example.com',8889,60)
        vs2007.mqtt_client.publisher.assert_called_once_with(mock_client)
        vs2007.mqtt_client.on_connect(mock_client,user_data,True,0)
        mock_client.subscribe.assert_called_once_with('stage/ctrl/stage-of-me')
        print(str(logs))

@with_setup(setup, teardown)
def test_main_default():
    sys.argv = ['vs-sentinel', '-l', 'DEBUG']
    logging.basicConfig(
        level='INFO', format='%(asctime)s %(levelname)s:%(message)s')
    logger = logging.getLogger('')
    vs2007.default_config['stage_name'] = 'stage-of-myPC'
    with LogCapture() as logs:
        #socket.hostname = MagicMock(return_value = 'myPC')
        mock_client = MagicMock(return_value = None)
        user_data = MagicMock(return_value = None)
        mqtt.Client = MagicMock(return_value = mock_client)
        vs2007.mqtt_client.publisher = MagicMock(return_value = None)
        main()
        mock_client.connect.assert_called_once_with('database.misasa.okayama-u.ac.jp',1883,60)
        vs2007.mqtt_client.publisher.assert_called_once_with(mock_client)
        vs2007.mqtt_client.on_connect(mock_client,user_data,True,0)
        mock_client.subscribe.assert_called_once_with('stage/ctrl/stage-of-myPC')
        print(str(logs))

@with_setup(setup, teardown)
def test_main_with_vs2007rc():
    sys.argv = ['vs-sentinel', '-l', 'DEBUG']
    logging.basicConfig(
        level='INFO', format='%(asctime)s %(levelname)s:%(message)s')
    logger = logging.getLogger('')
    config_path = 'tmp/.vs2007rc'
    vs2007.config_path = config_path
    config = {
        'mqtt_host':'mqtt.example.jp',
        'mqtt_port':2884,
        'stage_name':'stage-of-myDevice',
        'timeout': 3000
    }
    with open(config_path, 'w') as f:
      yaml.safe_dump(config, f)

    with LogCapture() as logs:
        mock_client = MagicMock(return_value = None)
        user_data = MagicMock(return_value = None)
        mqtt.Client = MagicMock(return_value = mock_client)
        vs2007.mqtt_client.publisher = MagicMock(return_value = None)
        main()
        mock_client.connect.assert_called_once_with('mqtt.example.jp',2884,60)
        vs2007.mqtt_client.publisher.assert_called_once_with(mock_client)
        vs2007.mqtt_client.on_connect(mock_client,user_data,True,0)
        mock_client.subscribe.assert_called_once_with('stage/ctrl/stage-of-myDevice')
        print(str(logs))