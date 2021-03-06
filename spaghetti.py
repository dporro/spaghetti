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
from streamshow import compute_buffers, compute_buffers_representatives, mbkm_wrapper
from dipy.tracking.distances import bundles_distances_mam
from dissimilarity_common import compute_disimilarity


if __name__ == '__main__':
    
    subject = '05'
    num_M_seeds = 1
    directory_name='./'

    #load T1 volume registered in MNI space
    t1_filename = directory_name+'data/subj_'+subject+'/MPRAGE_32/T1_flirt_out.nii.gz'
    print "Loading", t1_filename
    img = nib.load(t1_filename)
    data = img.get_data()
    affine = img.get_affine()

    #load the tracks registered in MNI space
    tracks_basenane = directory_name+'data/subj_'+subject+'/101_32/DTI/tracks_gqi_'+str(num_M_seeds)+'M_linear'
    buffers_filename = tracks_basenane+'_buffers.npz'
    try:
        print "Loading", buffers_filename
        buffers = np.load(buffers_filename)
    except IOError:
        print "Buffers not found, recomputing."
        fdpyw = tracks_basenane+'.dpy'    
        dpr = Dpy(fdpyw, 'r')
        print "Loading", fdpyw
        T = dpr.read_tracks()
        dpr.close()
    
        T = np.array(T, dtype=np.object)
        print "Computing buffers."
        buffers = compute_buffers(T, alpha=1.0, save=True, filename=buffers_filename)
        
    num_prototypes = 40
    full_dissimilarity_matrix_filename = tracks_basenane+'_dissimilarity'+str(num_prototypes)+'.npy'
    try:
        print "Loading dissimilarity representation:", full_dissimilarity_matrix_filename
        full_dissimilarity_matrix = np.load(full_dissimilarity_matrix_filename)
    except IOError:
        print "Dissimilarity matrix not found."
        print "Computing dissimilarity representation."
        try:
            T
        except NameError:
            fdpyw = tracks_basenane+'.dpy'    
            dpr = Dpy(fdpyw, 'r')
            print "Loading", fdpyw
            T = dpr.read_tracks()
            dpr.close()
    
            # T = T[:5000]
            T = np.array(T, dtype=np.object)
        
        full_dissimilarity_matrix = compute_disimilarity(T, distance=bundles_distances_mam, prototype_policy='sff', num_prototypes=num_prototypes)
        print "Saving", full_dissimilarity_matrix_filename
        np.save(full_dissimilarity_matrix_filename, full_dissimilarity_matrix)
        

    # load initial MBKM with given n_clusters
    n_clusters = 150
    clusters_filename = directory_name+'data/subj_'+subject+'/101_32/DTI/mbkm_gqi_'+str(num_M_seeds)+'M_linear_'+str(n_clusters)+'_clusters.pickle'
    try:
        print "Loading", clusters_filename
        clusters = pickle.load(open(clusters_filename))
    except IOError:
        print "MBKM clustering not found."
        print "Computing MBKM."
        streamlines_ids = np.arange(full_dissimilarity_matrix.shape[0], dtype=np.int)
        clusters = mbkm_wrapper(full_dissimilarity_matrix, n_clusters, streamlines_ids)
        print "Saving", clusters_filename
        pickle.dump(clusters, open(clusters_filename,'w'))

            
    # create the interaction system for tracks 
    tl = StreamlineLabeler('Bundle Picker',
                           buffers, clusters,
                           vol_shape=data.shape[:3], 
                           affine=affine,
                           clustering_parameter=len(clusters),
                           clustering_parameter_max=len(clusters),
                           full_dissimilarity_matrix=full_dissimilarity_matrix)
    
    title = 'Streamline Interaction and Segmentation'
    w = Window(caption = title, 
                width = 1200, 
                height = 800, 
                bgcolor = (.5, .5, 0.9) )

    scene = Scene(scenename = 'Main Scene', activate_aabb = False)

    data = np.interp(data, [data.min(), data.max()], [0, 255])    
    guil = Guillotine('Volume Slicer', data, affine)

    scene.add_actor(guil)
    scene.add_actor(tl)

    w.add_scene(scene)
    w.refocus_camera()


