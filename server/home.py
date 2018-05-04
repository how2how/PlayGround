import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.core.shells.multi import MultiShell

ms = MultiShell()
ms.start()
