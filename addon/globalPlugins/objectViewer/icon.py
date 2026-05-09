# objectViewer add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024-2025 hwf1324 <1398969445@qq.com>

from ctypes import Structure, byref, c_char, c_int, sizeof, windll
from ctypes.wintypes import DWORD, HANDLE, HICON

import wx

# Code modified from:
# https://solutionfall.com/question/why-isnt-shgetfileinfow-modifying-the-reference-passed-into-the-function/
SHGFI_ICON = 0x000000100
SHGFI_SMALLICON = 0x000000001
SHGFI_LARGEICON = 0x000000000
SHGFI_ATTRIBUTES = 0x000000800
SHIL_JUMBO = 0x0004


class SHFILEINFO(Structure):
	_fields_ = [
		("hIcon", HANDLE),
		("iIcon", c_int),
		("dwAttributes", DWORD),
		("szDisplayName", c_char * 260),
		("szTypeName", c_char * 80),
	]


def extractSmallHICON(pszPath: str) -> HICON:
	"""
	Extract the small icon from the specified `filename`, which might be
	either an executable or an `.ico` file.
	"""

	psfi = SHFILEINFO()
	uFlags = SHGFI_ICON | SHGFI_SMALLICON
	windll.shell32.SHGetFileInfoW(pszPath, 0, byref(psfi), sizeof(psfi), uFlags)

	return psfi.hIcon


def cleanupHICON(hicon: HICON) -> None:
	windll.user32.DestroyIcon(hicon)


# -----------------------------------------------------------------------------


def createIconFromPath(path: str) -> wx.Icon | None:
	icon: wx.Icon = wx.Icon()
	hIcon: HICON = extractSmallHICON(path)
	if hIcon and icon.CreateFromHICON(hIcon):
		return icon

	cleanupHICON(hIcon)
	return None
