from server.core.shells import BaseShell
from server.core.shells.subshells import *

from server.core.helpers import defaultArgMerging


class SimpleShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : SimpleSubShell,
		}
	Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		**kw
		) :
		args = defaultArgMerging(SimpleShell.Defaults, kw)
		BaseShell.__init__( self, handler, **args )
