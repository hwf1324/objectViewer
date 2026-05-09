# objectViewer add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024-2025 hwf1324 <1398969445@qq.com>

import api
import config
import wx
from NVDAObjects import NVDAObject

from .icon import createIconFromPath
from .NVDAObjectIterator import ObjectIterator


class NVDAObjectTree(wx.TreeCtrl):
	def __init__(
		self,
		parent: wx.Window,
		simpleReviewMode: bool = config.conf["reviewCursor"]["simpleReviewMode"],
		*args,
		**kwargs,
	):
		super().__init__(parent, *args, **kwargs)
		self.simpleReviewMode = simpleReviewMode
		rootNVDAObject: NVDAObject = api.getDesktopObject()
		imageDPISize: int = int(16 * self.GetDPIScaleFactor())
		il = wx.ImageList(imageDPISize, imageDPISize)
		self.AssignImageList(il)
		self.il = il
		root: wx.TreeItemId = self.AddRoot(self.getObjectDisplayText(rootNVDAObject), data=rootNVDAObject)
		self.SetItemHasChildren(root, True)

		# self.Bind(wx.EVT_TREE_SEL_CHANGING, self.onSelectionChanging)
		self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpanding)
		self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.onItemCollapsed)

	def addTreeNotes(self, parentItem: wx.TreeItemId):
		parentObj: NVDAObject = self.GetItemData(parentItem)
		if config.conf["objectViewer"]["addTreeNotesMode"] == "children":
			self._addTreeNotesFromChildren(parentItem, parentObj)
		elif config.conf["objectViewer"]["addTreeNotesMode"] == "iterator":
			self._addTreeNotesFromIterator(parentItem, parentObj)

	def appendTreeItem(self, parentItem: wx.TreeItemId, obj: NVDAObject) -> wx.TreeItemId:
		item = self.AppendItem(parentItem, self.getObjectDisplayText(obj), data=obj)
		parentObj: NVDAObject = self.GetItemData(parentItem)
		if obj.appModule.appPath and obj.appModule != parentObj.appModule:
			icon = createIconFromPath(obj.appModule.appPath)
			if icon:
				self.SetItemImage(item, self.il.Add(icon), wx.TreeItemIcon_Normal)

		return item

	def _addTreeNotesFromChildren(self, parentItem: wx.TreeItemId, parentObj: NVDAObject):
		for obj in parentObj.children:
			item: wx.TreeItemId = self.appendTreeItem(parentItem, obj)
			if obj.firstChild:
				self.SetItemHasChildren(item, True)
			else:
				self.SetItemHasChildren(item, False)

	def _addTreeNotesFromIterator(self, parentItem: wx.TreeItemId, parentObj: NVDAObject):
		for obj in ObjectIterator(parentObj, "children", self.simpleReviewMode):
			item = self.appendTreeItem(parentItem, obj)
			if obj.simpleFirstChild if self.simpleReviewMode else obj.firstChild:
				self.SetItemHasChildren(item, True)
			else:
				self.SetItemHasChildren(item, False)

	def getObjectDisplayText(self, obj: NVDAObject) -> str:
		return f'{obj.role.displayString} "{obj.name}"'

	def selectObject(self, obj: NVDAObject = api.getNavigatorObject()):
		config.conf["objectViewer"]["addTreeNotesMode"] = "iterator"
		parentItem: wx.TreeItemId = self.GetRootItem()
		self.CollapseAll()
		item: wx.TreeItemId = None
		cookie = None
		objLine = [obj for obj in ObjectIterator(obj, "parent", self.simpleReviewMode)]
		objLine.reverse()

		for obj in objLine:
			if obj == self.GetItemData(parentItem):
				self.Expand(parentItem)
				item, cookie = self.GetFirstChild(parentItem)
				continue
			while item.IsOk():
				if obj == self.GetItemData(item):
					if obj == objLine[-1]:
						self.EnsureVisible(item)
						self.SelectItem(item)
						break
					self.Expand(item)
					parentItem = item
					item, cookie = self.GetFirstChild(parentItem)
					break
				item, cookie = self.GetNextChild(parentItem, cookie)

	def onSelectionChanging(self, event: wx.TreeEvent):
		if not self.GetItemData(event.GetItem()):
			event.Veto()
		event.Skip()

	def onItemExpanding(self, event: wx.TreeEvent):
		self.Freeze()
		self.addTreeNotes(event.GetItem())
		self.Thaw()
		event.Skip()

	def onItemCollapsed(self, event: wx.TreeEvent):
		self.Freeze()
		self.DeleteChildren(event.GetItem())
		self.Thaw()
		event.Skip()
