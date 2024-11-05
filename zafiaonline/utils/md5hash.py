import hashlib


class Md5:
	def __init__(self):
		pass

	@staticmethod
	def md5_hash(string: str) -> str:
		m = hashlib.md5()
		m.update(string.encode())
		return m.hexdigest()

	def md5salt(self, string: str) -> str:
		for i in range(5):
			string = self.md5_hash(string + "azxsw")
		return string
