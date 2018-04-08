from server.core.shells import BaseShell

from server.core.shells.subshells import *

from server.core.helpers import defaultArgMerging


class ExtendableShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : ControlSubShell,
		'python' : PythonAPISubShell,
		'os-shell' : SimpleSubShell,
		'file' : FileSubShell,
		'stage' : StageSubShell,
		}
	Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		log_unrecognised = False,
		**kw
		) :
		args = defaultArgMerging(ExtendableShell.Defaults, kw)
		BaseShell.__init__( self, handler, **args )
