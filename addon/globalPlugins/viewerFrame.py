# objectViewer add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024-2025 hwf1324 <1398969445@qq.com>

import sys

import config
import gui.guiHelper
import wx
import wx.py
from gui.dpiScalingHelper import DpiScalingHelperMixinWithoutInit
from gui.nvdaControls import AutoWidthColumnListCtrl
from NVDAObjects import NVDAObject

from .objectTree import NVDAObjectTree


class ObjectViewerFrame(DpiScalingHelperMixinWithoutInit, wx.Frame):
	def __init__(self, parent, namespace):
		super().__init__(
			parent,
			wx.ID_ANY,
			# Translators: The title of the Object Viewer frame.
			_("Object Viewer"),
			# style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP,
		)

		self.panel: wx.Panel = wx.Panel(self)

		self.objectTree: NVDAObjectTree = NVDAObjectTree(parent=self.panel)
		self.objectDevInfoList = createDevInfoList(self.panel)

		if not namespace:
			namespace = {}
		self.crust = self.createCrust(namespace)
		self.namespace = self.crust.shell.interp.locals

		self.frameContentsSizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.frameContentsSizer)
		self.frameContentsSizer.Add(
			self.panel, proportion=1, flag=wx.EXPAND, border=gui.guiHelper.BORDER_FOR_DIALOGS
		)
		self.panelContentsSizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.panelContentsSizer)
		splitterSizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.treeContentsSizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

		self.treeContentsSizer.Add(self.objectTree, proportion=1, flag=wx.EXPAND)
		self.propertieContentsSizer: gui.guiHelper.BoxSizerHelper = gui.guiHelper.BoxSizerHelper(
			self.panel, sizer=wx.StaticBoxSizer(wx.VERTICAL, self.panel, _("Object Properties"))
		)
		self.objectPropertieLabel: wx.StaticText = wx.StaticText(self.panel, label="")
		font: wx.Font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.objectPropertieLabel.SetFont(font)

		self.propertieContentsSizer.sizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)
		self.propertieContentsSizer.addItem(self.objectPropertieLabel)
		self.propertieContentsSizer.addItem(self.objectDevInfoList, proportion=1, flag=wx.EXPAND)
		splitterSizer.Add(self.treeContentsSizer, proportion=1, flag=wx.EXPAND)
		splitterSizer.Add(self.propertieContentsSizer.sizer, proportion=1, flag=wx.EXPAND)
		self.panelContentsSizer.Add(splitterSizer, proportion=1, flag=wx.EXPAND)
		self.panelContentsSizer.Add(self.crust, proportion=1, flag=wx.EXPAND)

		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectionChanged, self.objectTree)

		self.makeMenuBar()

		# setting the size must be done after the parent is constructed.
		self.SetMinSize(self.scaleSize(self.MIN_SIZE))
		self.SetSize(self.scaleSize(self.INITIAL_SIZE))
		# the size has changed, so recenter on the screen
		self.SetTransparent(int(255 * 0.9))
		self.CentreOnScreen()

	INITIAL_SIZE = (800, 480)
	MIN_SIZE = (470, 240)

	def createCrust(self, namespace):
		import buildVersion

		introText = _(
			f"Python {sys.version.split()[0]} on {sys.platform}, NVDA {buildVersion.version}\n"
			"NOTE: The 'obj' variable refers to the NVDA object selected in the tree."
		)

		crust = wx.py.crust.Crust(
			self.panel, size=(-1, 200), locals=namespace, intro=introText, showInterpIntro=False
		)
		crust.shell.SetBufferedDraw(False)
		crust.filling.text.SetBufferedDraw(False)
		crust.display.SetBufferedDraw(False)

		return crust

	def makeMenuBar(self):
		treeMenu: wx.Menu = wx.Menu()
		menu_addTreeNotesMode: wx.Menu = wx.Menu()
		self.addTreeNotesChildrenMode: wx.MenuItem = menu_addTreeNotesMode.AppendRadioItem(
			wx.ID_ANY, _("children")
		)
		self.addTreeNotesChildrenMode.Check(config.conf["objectViewer"]["addTreeNotesMode"] == "children")
		self.addTreeNotesIteratorMode: wx.MenuItem = menu_addTreeNotesMode.AppendRadioItem(
			wx.ID_ANY, _("iterator")
		)
		self.addTreeNotesIteratorMode.Check(config.conf["objectViewer"]["addTreeNotesMode"] == "iterator")
		self.Bind(wx.EVT_MENU, self.onToggleAddTreeNotesMode, self.addTreeNotesChildrenMode)
		self.Bind(wx.EVT_MENU, self.onToggleAddTreeNotesMode, self.addTreeNotesIteratorMode)
		menu_reviewMode: wx.Menu = wx.Menu()
		self.nvdaReviewMode: wx.MenuItem = menu_reviewMode.AppendCheckItem(
			wx.ID_ANY,
			_("NVDA &behavior"),
			_("NVDA behavior"),
		)
		self.nvdaReviewMode.Check(config.conf["objectViewer"]["nvdaReviewMode"])
		self.Bind(wx.EVT_MENU, self.onToggleNVDAReviewMode, self.nvdaReviewMode)
		menu_reviewMode.AppendSeparator()
		self.simpleReviewMode: wx.MenuItem = menu_reviewMode.AppendCheckItem(
			wx.ID_ANY,
			_("&Simple review mode"),
			_("Simple review mode"),
		)
		self.simpleReviewMode.Check(config.conf["objectViewer"]["simpleReviewMode"])
		if self.nvdaReviewMode.IsChecked():
			self.simpleReviewMode.Enable(False)
		self.Bind(wx.EVT_MENU, self.onToggleReviewMode, self.simpleReviewMode)
		treeMenu.AppendSubMenu(menu_addTreeNotesMode, _("&Add tree notes mode..."))
		treeMenu.AppendMenu(
			wx.ID_ANY,
			_("&Review mode..."),
			menu_reviewMode,
			_("Configure the way the tree view retrieves NVDA objects."),
		)
		self.Bind(wx.EVT_MENU, self.onToggleReviewMode, self.simpleReviewMode)
		self.menuBar: wx.MenuBar = wx.MenuBar()
		self.menuBar.Append(treeMenu, _("Objects &tree"))
		self.SetMenuBar(self.menuBar)

	def onToggleAddTreeNotesMode(self, event: wx.CommandEvent):
		if event.GetId() == self.addTreeNotesChildrenMode.GetId():
			config.conf["objectViewer"]["addTreeNotesMode"] = "children"
		elif event.GetId() == self.addTreeNotesIteratorMode.GetId():
			config.conf["objectViewer"]["addTreeNotesMode"] = "iterator"

		self.objectTree.CollapseAll()
		event.Skip()

	def onToggleNVDAReviewMode(self, event: wx.CommandEvent):
		if event.IsChecked():
			config.conf["objectViewer"]["nvdaReviewMode"] = True
			self.simpleReviewMode.Enable(False)
		else:
			self.simpleReviewMode.Enable(True)

		config.conf["objectViewer"]["addTreeNotesMode"] = "iterator"
		self.objectTree.CollapseAll()
		event.Skip()

	def onToggleReviewMode(self, event: wx.CommandEvent):
		config.conf["objectViewer"]["simpleReviewMode"] = event.IsChecked()
		self.objectTree.CollapseAll()
		event.Skip()

	def onSelectionChanged(self, event: wx.TreeEvent):
		"""Handle selection changed event."""
		obj: NVDAObject = self.objectTree.GetItemData(event.GetItem())
		self.namespace["obj"] = self.obj = obj

		self.Freeze()
		self.objectDevInfoList.DeleteAllItems()
		self.objectPropertieLabel.SetLabel(self.objectTree.getObjectDisplayText(obj))
		updateDevInfoList(self.objectDevInfoList, obj.devInfo)

		self.Thaw()

		event.Skip()


def createDevInfoList(parent: wx.Panel) -> AutoWidthColumnListCtrl:
	devInfoList: AutoWidthColumnListCtrl = AutoWidthColumnListCtrl(
		parent=parent,
		style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES,
	)
	devInfoList.InsertColumn(0, _("Property"))
	devInfoList.InsertColumn(1, _("Value"))

	return devInfoList


def updateDevInfoList(devInfoList: AutoWidthColumnListCtrl, devInfo: list[str]):
	for line in zip(range(len(devInfo)), devInfo):
		objPropertyName, _, objPropertyValue = line[1].partition(": ")
		lineIndex = devInfoList.InsertItem(line[0], objPropertyName)
		devInfoList.SetItem(lineIndex, 1, objPropertyValue)
