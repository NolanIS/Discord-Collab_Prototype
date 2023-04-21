from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]


# Really handy, 4 line, __init__ file that was discussed on:
# https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
# Allows python files to be dropped into the Langs folder and be auto-registered into the available language list
# Sub-folders (for language implementations) are ignored