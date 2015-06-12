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

class Attach(object):
	def __init__(self, *args, **kw):
		self.__dict__ = args[0]


	def to_s(self):
		dic_attach = self.__dict__
		line = "%d\t%d\t%d\t%s\t%s" % (self.address_id,dic_attach['attach_id'],dic_attach['class_id'],dic_attach['name'],dic_attach['file'])
		if not dic_attach['class_id'] == 0:
			line += "\t%.3f\t%.3f" % (dic_attach['locate_x'],dic_attach['locate_y'])
			line += "\t%.3f\t%.3f" % (dic_attach['center_x'],dic_attach['center_y'])
			line += "\t%.3f\t%.3f" % (dic_attach['size_x'],dic_attach['size_y'])
			line += "\t%d" % (dic_attach['imag'])
		return line