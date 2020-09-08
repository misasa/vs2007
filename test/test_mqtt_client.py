from nose.tools import *
import sys
import vs2007
from vs2007.mqtt_client import main, _parse_options

def test_help():
  sys.argv = ['vs-pubsub', '--help']
  assert_raises(SystemExit, _parse_options)
