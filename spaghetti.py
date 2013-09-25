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
#from streamwindow import Window
from guillotine import Guillotine
from dipy.io.dpy import Dpy
import pickle
from streamshow import compute_buffers, mbkm_wrapper
from dipy.tracking.distances import bundles_distances_mam
from dissimilarity_common import compute_disimilarity


class Spaghetti():

    def __init__(self, structpath=None, tracpath=None, segmpath=None):
        
        
        if segmpath == None:
            
            subject = '05'
            num_M_seeds = 1
                    
            self.t1_filename = structpath +'/data/subj_'+subject+'/MPRAGE_32/T1_flirt_out.nii.gz'
            self.tracpath=tracpath[0]
                        
        else:
            print "Loading saved session file"
            segmpath=segmpath[0]
            segm_info = pickle.load(open(segmpath)) 
            state = segm_info['segmsession']  
            self.t1_filename=segm_info['structfilename']
            self.tracpath=segm_info['tractfilename']   
            
            
      #load T1 volume registered in MNI space
        print "Loading structural information file"
        img = nib.load(self.t1_filename)
        data = img.get_data()
        affine = img.get_affine()

    #load the tracks registered in MNI space
        tracks_basename = self.tracpath[:self.tracpath.find(".")]
        tracks_format = self.tracpath[self.tracpath.find("."):]   
        
        if tracks_format == '.spa':
            self.LoadInfo(self.tracpath)
            
        elif tracks_format == '.dpy' or tracks_format == '.trk':
#            
            general_info_filename = tracks_basename + '.spa'
            #Check if there is the .spa file that contains all the computed information from the tractography anyway and try to load it
            try:
                print "Looking for general information file"
                self.LoadInfo(general_info_filename)
            #show a message box
            
            except IOError:
                print "General information not found, loading tractography to recompute buffers and dissimilarity matrix."
                dpr = Dpy(self.tracpath, 'r')
                print "Loading", self.tracpath
                T = dpr.read_tracks()
                dpr.close()
                T = np.array(T, dtype=np.object)
            
                print "Computing buffers."
                self.buffers = compute_buffers(T, alpha=1.0, save=False)
                
                print "Computing dissimilarity representation."
                self.num_prototypes = 40
                self.full_dissimilarity_matrix = compute_disimilarity(T, distance=bundles_distances_mam, prototype_policy='sff', num_prototypes=self.num_prototypes)
                
                # compute initial MBKM with given n_clusters
                print "Computing MBKM"
                n_clusters = 150
                streamlines_ids = np.arange(self.full_dissimilarity_matrix.shape[0], dtype=np.int)
                self.clusters = mbkm_wrapper(self.full_dissimilarity_matrix, n_clusters, streamlines_ids)
                
                
                print "Saving computed information from tractography"
                self.SaveInfo(general_info_filename)
#                
           
    # create the interaction system for tracks 
        self.tl = StreamlineLabeler('Bundle Picker',
                           self.buffers, self.clusters,
                           vol_shape=data.shape[:3], 
                           affine=affine,
                           clustering_parameter=len(self.clusters),
                           clustering_parameter_max=len(self.clusters),
                           full_dissimilarity_matrix=self.full_dissimilarity_matrix)
                              
        data = np.interp(data, [data.min(), data.max()], [0, 255])    
        self.guil = Guillotine('Volume Slicer', data, affine)    
            
        try:
            state
            self.tl.set_state(state)
        except NameError:
            pass
            
            
    def SaveInfo(self,filepath):
        """
        Saves all the information from the tractography required for the whole segmentation procedure
        """
        info = {'initclusters':self.clusters, 'buff':self.buffers, 'dismatrix':self.full_dissimilarity_matrix,'nprot':self.num_prototypes}
        print "Saving information of the tractography for the segmentation"
        print filepath
        pickle.dump(info, open(filepath,'w'), protocol=pickle.HIGHEST_PROTOCOL)
        
    
    def LoadInfo(self,filepath):
        """
        Loads all the information from the tractography required for the whole segmentation procedure
        """
        print "Loading general information file"
        general_info = pickle.load(open(filepath))
        self.buffers = general_info['buff']
        self.clusters = general_info['initclusters']
        self.full_dissimilarity_matrix = general_info['dismatrix']
        self.num_prototypes = general_info['nprot']
        
    def SaveSegmentation(self, filename):
        """
        Saves the information of the segmentation result from the current session
        """
        
        print "Save segmentation result from current session"
        filename=filename[0]+'.seg'
        state = self.tl.get_state()
        seg_info={'structfilename':self.t1_filename, 'tractfilename':self.tracpath, 'segmsession':state}
        pickle.dump(seg_info, open(filename,'w'), protocol=pickle.HIGHEST_PROTOCOL)
        
    
        
        
        
#        filepath= self.tracpath[:myString.find(".")]
        
                               



