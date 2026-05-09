# objectViewer add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024 hwf1324 <1398969445@qq.com>

from NVDAObjects import NVDAObject


class ObjectIterator:
	def __init__(self, obj: NVDAObject, relation: str = "children", simpleReviewMode: bool = False):
		self.relation = relation
		self.simpleReviewMode = simpleReviewMode
		if relation == "children":
			self.current = obj.simpleFirstChild if simpleReviewMode else obj.firstChild
		elif relation == "parent":
			self.current = obj

	def __iter__(self):
		return self

	def __next__(self):
		if self.current is None:
			raise StopIteration
		obj = self.current
		if self.relation == "children":
			self.current = obj.simpleNext if self.simpleReviewMode else obj.next
		elif self.relation == "parent":
			self.current = obj.simpleParent if self.simpleReviewMode else obj.parent
		return obj
