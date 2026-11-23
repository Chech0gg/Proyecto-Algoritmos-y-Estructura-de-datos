import sys
from monitorias.cli import principal

if len(sys.argv) == 1:
    sys.argv.append("--demo")

principal()
