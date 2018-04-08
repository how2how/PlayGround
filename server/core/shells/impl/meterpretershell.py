from server.core.shells.subshells import MeterpreterSubShell
from server.core.shells.subshells import ControlSubShell
from server.core.shells import BaseShell


from server.core.helpers import defaultArgMerging


class MeterpreterShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : ControlSubShell,
		'meterpreter' : MeterpreterSubShell,
		}
	# Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		**kw
		) :
		# handler.getOrchestrator().addStream('meterpreter')
		# handler.getOrchestrator().streamIdent.setHardStreamName('meterpreter')
		# handler.getOrchestrator().deleteStream('control')

		args = defaultArgMerging(MeterpreterShell.Defaults, kw)
		BaseShell.__init__( self, handler, **args )
