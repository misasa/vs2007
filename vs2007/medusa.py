import requests
import logging
import os
import yaml

class VS2007Medusa(object):

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(VS2007Medusa, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
            return cls._instance

    def __init__(self, *args, **kw):
        self._config = None
        self._config_path = os.path.join(os.environ['HOME'],".orochirc")

    def _get_config(self):
        if self._config == None:
            logging.info("read config from %s" % self._config_path)
            with open(self._config_path) as file:
                config = yaml.safe_load(file)
                self._config = config
        return self._config

    def _set_config(self, config):
        self._config = config

    config = property(_get_config, _set_config)

    def get_record(self, id):
        url_items = self.config['uri'] + '/records/' + id + '.json'
        r_get = requests.get(url_items, auth = (self.config['user'], self.config['password']))
        if (r_get.status_code == 200):
            return r_get.json()
    
    def get_spots(self, surface_id):
        url_items = self.config['uri'] + '/surfaces/' + str(surface_id) + '/spots.json'
        r_get = requests.get(url_items, auth = (self.config['user'], self.config['password']))
        if (r_get.status_code == 200):
            return r_get.json()