import sys
import pathlib

# allow pytest to find modules in the bin directory
project_root = pathlib.Path(__file__).parent.parent
sys.path.append(str(project_root / "bin"))
