from PIL import Image
import imghdr
import os
class Address(object):
	def __init__(self, *args, **kw):
		self.__dict__ = args[0]

	def get_attachlist(self):
		if self.attachlist == None:
			return []
		else:
			return self.attachlist

	def to_s(self):
		dic_addr = self.__dict__
		string = "%d\t%d\t%s\t%.3f\t%.3f\t%s" % (dic_addr['address_id'], dic_addr['class_id'], dic_addr['name'], dic_addr['locate_x'], dic_addr['locate_y'], dic_addr['data'])
		return string

	def to_dict(self):
		return self.__dict__

	def to_spot(self):
		addr = self.__dict__
		return {'name': addr['name'].strip('"'), 'world_x': addr['locate_x'], 'world_y': addr['locate_y'], 'description': addr['data'].strip('"') }

class Attach(object):
	def __init__(self, *args, **kw):
		self.__dict__ = args[0]
		if 'base_dir' in kw.keys():
			self.__dict__['path'] = os.path.join(kw['base_dir'], self.__dict__['file'])

	def is_cropped(self):
		return self.__dict__['name'].count('@crop')
	
	def is_warped(self):
		return self.__dict__['name'].count('@spin')

	def path(self):
		return self._dict__['path']

	def what(self):
		return imghdr.what(self.path)

	def content_type(self):
		image = Image.open(self.path)
		return Image.MIME[image.format]

	def corners_on_world(self):
		di = self.to_dict()
		c = [di['locate_x'], di['locate_y']]
		s = [di['size_x'],di['size_y']]
		lu = [(c[0] - s[0]/2.0), (c[1] + s[1]/2.0)]
		ru = [(c[0] + s[0]/2.0), (c[1] + s[1]/2.0)]
		rb = [(c[0] + s[0]/2.0), (c[1] - s[1]/2.0)]
		lb = [(c[0] - s[0]/2.0), (c[1] - s[1]/2.0)]
		return [lu,ru,rb,lb]

	def to_s(self):
		dic_attach = self.__dict__
		line = "%d\t%d\t%d\t%s\t%s" % (self.address_id,dic_attach['attach_id'],dic_attach['class_id'],dic_attach['name'],dic_attach['file'])
		if not dic_attach['class_id'] == 0:
			line += "\t%.3f\t%.3f" % (dic_attach['locate_x'],dic_attach['locate_y'])
			line += "\t%.3f\t%.3f" % (dic_attach['center_x'],dic_attach['center_y'])
			line += "\t%.3f\t%.3f" % (dic_attach['size_x'],dic_attach['size_y'])
			line += "\t%d" % (dic_attach['imag'])
		return line
	
	def to_dict(self):
		return self.__dict__