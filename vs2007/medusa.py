import requests
import logging
import os
import json
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
    
    def create_surface(self, surface_name, **kwargs):
        url_items = self.config['uri'] + '/surfaces.json'
        payload = {'surface[name]': surface_name}
        r_post = requests.post(url_items, data = payload, auth = (self.config['user'], self.config['password']))
        if (r_post.status_code == 201):
            surface = r_post.json()
            url_items = self.config['uri'] + format('/surfaces/%d/spots.json' % surface['id'])
            if ('addrs' in kwargs.keys()):
                for addr in kwargs['addrs']:
                    spot = addr.to_spot()
                    payload = {}
                    for key in spot:
                        payload[format('spot[%s]' % key)] = spot[key]
                    r_post = requests.post(url_items, data = payload, auth = (self.config['user'], self.config['password']))
            if ('attachs' in kwargs.keys()):
                url_items = self.config['uri'] + format('/surfaces/%d/images.json' % surface['id'])
                for attach in kwargs['attachs']:
                    di = attach.to_dict()
                    path, ext = os.path.splitext(attach.path)
                    filename = di['name'] + ext
                    fileDataBinary = open(attach.path, 'rb')
                    files = {'attachment_file[data]': (filename, fileDataBinary, attach.content_type())}
                    r_post = requests.post(url_items, files = files, auth = (self.config['user'], self.config['password']))
                    if (r_post.status_code == 201):
                        surface_image = r_post.json()
                        url_up = self.config['uri'] + format('/surfaces/%d/images/%d.json' % (surface['id'], surface_image['id']))
                        payload = {}
                        payload['surface_image[corners_on_world]'] = ':'.join([format("%.4f,%.4f" % (x,y))  for x,y in  attach.corners_on_world()])
                        r_put = requests.put(url_up, data = payload, auth = (self.config['user'], self.config['password']))

    def get_spots(self, surface_id):
        url_items = self.config['uri'] + '/surfaces/' + str(surface_id) + '/spots.json'
        r_get = requests.get(url_items, auth = (self.config['user'], self.config['password']))
        if (r_get.status_code == 200):  
            return r_get.json()
