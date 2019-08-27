from pathlib import Path
import sys
"""
Hack for imports to work not depending on execution path
"""
sys.path += [str(Path(__file__).parent.absolute())]
