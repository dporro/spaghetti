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
import vtk
import nibabel as nib
from streamshow import StreamlineLabeler
from guillotine import Guillotine
from dipy.io.dpy import Dpy
import pickle
from streamshow import compute_buffers, mbkm_wrapper
from dipy.tracking.distances import bundles_distances_mam
from dissimilarity_common import compute_disimilarity




class Spaghetti():

    def __init__(self, structpath=None, tracpath=None, segmpath=None):
        
        
        if segmpath == None:
            
            self.structpath = structpath
            self.tracpath=tracpath
                        
        else:
            print "Loading saved session file"
            segm_info = pickle.load(open(segmpath)) 
            state = segm_info['segmsession']  
            
            self.structpath=segm_info['structfilename']
            self.tracpath=segm_info['tractfilename']   
            
            
      #load T1 volume registered in MNI space
        print "Loading structural information file"
        self.img = nib.load(self.structpath)
        data = self.img.get_data()
        affine = self.img.get_affine()
        
        
    #load the tracks registered in MNI space
#        tracks_basename = self.tracpath[:self.tracpath.find(".")]
        tracks_basename, addext, tracks_format = nib.filename_parser.splitext_addext(self.tracpath,addexts=('.trk', '.dpy', '.vtk'),match_case=False)
#        tracks_format = self.tracpath[self.tracpath.find("."):]   
        
        general_info_filename = tracks_basename + '.spa'
            #Check if there is the .spa file that contains all the computed information from the tractography anyway and try to load it
        
        try:
            print "Looking for general information file"
            self.LoadInfo(general_info_filename)
            #show a message box
          
        except IOError:
            print "General information not found, loading tractography to recompute buffers and dissimilarity matrix."
            if tracks_format == '.dpy': 
                dpr = Dpy(self.tracpath, 'r')
                print "Loading", self.tracpath
                T = dpr.read_tracks()
                dpr.close()
                T = np.array(T, dtype=np.object)
                
            elif tracks_format == '.trk': 
                streams, hdr = nib.trackvis.read(self.tracpath, points_space='voxel')
                print "Loading", self.tracpath
                T = np.array([s[0] for s in streams], dtype=np.object)
                
            elif tracks_format == '.vtk': 
                T = self.ReadingVTKTract()
             
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
        
        #remove the singleton dimension in case of files (.trk for example) in which t=1, but still the data has 4 dimensions 
        data = (np.interp(np.squeeze(data), [data.min(), data.max()], [0, 255]))
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
        seg_info={'structfilename':self.structpath, 'tractfilename':self.tracpath, 'segmsession':state}
        pickle.dump(seg_info, open(filename,'w'), protocol=pickle.HIGHEST_PROTOCOL)
        
    
    def ReadingVTKTract(self):
        """
        Read Entire Tractography from .vtk file
        """
        #Reading tractography which is stored as Polydata in .vtk file
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(self.tracpath)
        
        #Releasing memory
        reader.ReleaseDataFlagOn()
        reader.GetOutput().ReleaseDataFlagOn()
        reader.Update()
        
       
        data=reader.GetOutput()
        #read header if there is...we'll see how to use it later
#        hdr=reader.GetHeader()
        
        del reader
        nstreamlines=data.GetNumberOfLines()
      
        T=[]
        #Obtaining the points corresponding to the ith streamline, which are associated to the Ids in the ith cell. 
        for i in range(nstreamlines-1):
             pts = data.GetCell(i).GetPoints()    
             T.append(np.array([pts.GetPoint(j) for j in range(pts.GetNumberOfPoints())],dtype=np.float32))
             
        T = np.array(T, dtype=np.object)
        
       
        return T
        
        
        
        
        
      
                               



