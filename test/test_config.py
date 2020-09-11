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
    eq_(vs2007.default_config, vs2007.config())

def test_config_with_existing_file():
    config_path = 'tmp/.vs2007rc'
    vs2007.config_path = config_path
    mykey = 'hogehoge'
    config = {'stage_name': mykey}
    with open(config_path, 'w') as f:
      yaml.safe_dump(config, f)
    assert 'stage_name' in vs2007.config()
    assert vs2007.config()['stage_name'] == mykey
    cfg = vs2007.Config()
    assert cfg.config['stage_name'] == mykey

