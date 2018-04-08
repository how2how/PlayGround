from server.core.shells import BaseShell
from server.core.shells.subshells import ControlSubShell, PythonAPISubShell, SimpleSubShell

from server.core.helpers import defaultArgMerging


class StandardShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : ControlSubShell,
		'python' : PythonAPISubShell,
		'os-shell' : SimpleSubShell,
		}
	Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		**kw
		) :
		args = defaultArgMerging(StandardShell.Defaults, kw)
		BaseShell.__init__( self, handler, **args )
		self.sysinfo = None
