# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:01:02 2013

@author: dporro
"""

import pyglet
debug = False
pyglet.options['debug_gl'] = debug
pyglet.options['debug_gl_trace'] = debug
pyglet.options['debug_gl_trace_args'] = debug
pyglet.options['debug_lib'] = debug
pyglet.options['debug_media'] = debug
pyglet.options['debug_trace'] = debug
pyglet.options['debug_trace_args'] = debug
pyglet.options['debug_trace_depth'] = 1
pyglet.options['debug_font'] = debug
pyglet.options['debug_x11'] = debug
pyglet.options['debug_trace'] = debug

import numpy as np
import nibabel as nib
from streamshow import StreamlineLabeler
from streamwindow import Window
from guillotine import Guillotine
from dipy.io.dpy import Dpy
from fos import Scene
import pickle
from streamshow import compute_buffers, mbkm_wrapper
from dipy.tracking.distances import bundles_distances_mam
from dissimilarity_common import compute_disimilarity


if __name__ == '__main__':
    
    