import yaml
import sys
import os
import shutil
from nose.tools import *
import vs2007

# py -m nose test/test_config
config = {'vsdata_path': 'Z:\\'}
files_dir = os.path.join(os.path.dirname(__file__), 'files')

def setup_tmp():
  if os.path.exists('tmp'):
    print("removing tmp/...")
    shutil.rmtree('tmp')
  print("creating tmp/...")
  os.mkdir('tmp')
  
def setup():
  setup_tmp()
  global saved
  saved = sys.argv

def teardown():
  pass

@with_setup(setup, teardown)
def test_config_without_existing_file():
    vs2007.config_path = 'tmp/.vs2007rc'
    #shutil.copy(os.path.join(files_dir, '.vs2007rc'),'tmp')
    #vs2007.Config.default_path = config_path
    #config = vs2007.Config()
    print(vs2007.default_config)
    eq_(vs2007.default_config, vs2007.config())

def test_config_with_existing_file():
    config_path = 'tmp/.vs2007rc'
    vs2007.config_path = config_path
    mykey = 'hogehoge'
    config = {'mqtt_topic': mykey}
    with open(config_path, 'w') as f:
      yaml.safe_dump(config, f)
    assert 'mqtt_topic' in vs2007.config()
    assert vs2007.config()['mqtt_topic'] == mykey
