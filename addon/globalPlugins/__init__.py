# objectViewer add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024 hwf1324 <1398969445@qq.com>

import api
import config
import globalPluginHandler
import gui
from NVDAObjects import NVDAObject
from scriptHandler import script

from .viewerFrame import ObjectViewerFrame


# Translators: The name of a category of NVDA commands.
# Script category for Object Viewer commands.
SCRCAT_OBJECTS_VIEWER = _("Object Viewer")

confspec = {
	"nvdaReviewMode": "boolean(default=True)",
	"simpleReviewMode": "boolean(default=False)",
	"addTreeNotesMode": 'string(default="children")',
}

config.conf.spec["objectViewer"] = confspec


class ObjectViewerTool:

	# Note: This is the Borg design pattern which ensures that all
	# instances of this class are actually using the same set of
	# instance data.  See
	# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
	__shared_state = None

	def __init__(self):
		if not ObjectViewerTool.__shared_state:
			ObjectViewerTool.__shared_state = self.__dict__
		else:
			self.__dict__ = ObjectViewerTool.__shared_state

		if not hasattr(self, "initialized"):
			self.initialized: bool = False

	def init(self):
		self._frame = None

		import pythonConsole
		if not pythonConsole.consoleUI:
			pythonConsole.initialize()
		self._namespace = pythonConsole.consoleUI.console.namespace

		self.initialized = True

	def show(self, selectObj: NVDAObject = None, refreshTree: bool = False):
		if not self.initialized:
			self.init()

		if not self._frame:
			self._frame = ObjectViewerFrame(
				gui.mainFrame,
				namespace=self._namespace
			)

		import pythonConsole

		# Take a snapshot of the vars before opening the window. Once the python console window is opened calls
		# to the 'api' module will refer to this new focus.
		pythonConsole.consoleUI.console.updateNamespaceSnapshotVars()
		self._frame.crust.shell.interp.locals.update(pythonConsole.consoleUI.console.namespace)

		if refreshTree:
			self._frame.objectTree.DeleteAllItems()
		if selectObj:
			self._frame.objectTree.selectObject(selectObj)
		self._frame.Show()
		self._frame.Raise()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super().__init__()

	@script(
		# Translators: Description of the script to activate the Objects Viewer.
		description=_("Activate the Object Viewer"),
		category=SCRCAT_OBJECTS_VIEWER
	)
	def script_activateObjectViewer(self, gesture):
		ObjectViewerTool().show()

	@script(
		# Translators: Description of the script to activate the Objects Viewer.
		description=_("Activate the Object Viewer from focus object"),
		category=SCRCAT_OBJECTS_VIEWER
	)
	def script_activateObjectViewerFromFocus(self, gesture):
		ObjectViewerTool().show(selectObj=api.getFocusObject())

	@script(
		# Translators: Description of the script to activate the Objects Viewer.
		description=_("Activate the Object Viewer from mouse object"),
		category=SCRCAT_OBJECTS_VIEWER
	)
	def script_activateObjectViewerFromMouse(self, gesture):
		ObjectViewerTool().show(selectObj=api.getMouseObject())

	@script(
		# Translators: Description of the script to activate the Objects Viewer.
		description=_("Activate the Object Viewer from navigator object"),
		category=SCRCAT_OBJECTS_VIEWER
	)
	def script_activateObjectViewerFromNavigator(self, gesture):
		ObjectViewerTool().show(selectObj=api.getNavigatorObject())
