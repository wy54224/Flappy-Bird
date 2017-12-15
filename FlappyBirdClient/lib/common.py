import os
import pyglet

visibleSize = {"width":238, "height":512}

THISDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.normpath(os.path.join(THISDIR, '..', 'data'))

TEMPDIR = os.path.normpath(os.path.join(THISDIR, '..', 'temp'))
if not os.path.exists(TEMPDIR):
	os.mkdir(TEMPDIR)

tmp = open(os.path.join(TEMPDIR, 'tmp_Information.tmp'), 'w')
tmp.close()
    
def load_image(path):
    return pyglet.image.load(os.path.join(DATADIR, path))
