# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PySide.QtCore import Slot
from PySide.QtGui import QMainWindow

from Ui_mainwindow import *
from fos.vsml import vsml
from fos.actor import *
from fos.world import *
from glwidget import GLWidget
from spaghetti import Spaghetti
import os
import sys
import pp


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        #calling base initializers
        super(MainWindow, self).__init__(parent)
        
         #calling base setupUi for ui configuration
        self.setupUi(self)
        
        #setting up the gui
        self.setup_gui()
        
    def setup_gui(self):
        
        self.glWidget = GLWidget(parent = self.gridWidget_4, 
                                    width = 1508, 
                                    height = 713, 
                                    bgcolor = (.5, .5, 0.9), 
                                    enable_light = False)
                                    
        self.gridLayout_4.addWidget(self.glWidget) 
        
        #adding the editing items to ROI table
       
        #double spinbox for x,y and z coordinates
        self.dspbxcoord = QtGui.QDoubleSpinBox()
        self.tblROI.setCellWidget(3, 1,  self.dspbxcoord)
        
        self.dspbycoord = QtGui.QDoubleSpinBox()
        self.tblROI.setCellWidget(4, 1,  self.dspbycoord)
        
        self.dspbzcoord = QtGui.QDoubleSpinBox()
        self.tblROI.setCellWidget(5, 1,  self.dspbzcoord)
        
        self.spbrad = QtGui.QSpinBox()
        self.tblROI.setCellWidget(6, 1,  self.spbrad)
         #define method ROI
        self.roimethod = 1 #tractome inside
               
        #color button
        self.colorlist = [QtGui.QColor('red'), QtGui.QColor('blue'), QtGui.QColor('green'), QtGui.QColor('yellow'), QtGui.QColor('cyan'), QtGui.QColor('black')]
        self.btncolor = QtGui.QPushButton()
        self.tblROI.setCellWidget(2, 1,  self.btncolor)
        self.btncolor.setAutoFillBackground(True)
        #connect button with QColorDialog
        self.connect(self.btncolor, QtCore.SIGNAL("clicked()"), 
                        self.on_btncolor_clicked)
                
        #visibility checkbox
        self.chkbvis = QtGui.QCheckBox()
        self.chkbvis.setCheckState(QtCore.Qt.Checked)
        self.connect(self.chkbvis, QtCore.SIGNAL("stateChanged(int)"), self.on_chkbvis_stateChanged)
        self.tblROI.setCellWidget(1, 1,  self.chkbvis)
        
#        self.show_hide_rows(True)
        
        #creating the main Scene
        self.spaghetti= Spaghetti()
        self.add_scene(self.spaghetti.scene)
        
                
    def changenumstreamlines_handler(self, n_stream):
       
        if (n_stream< 1e5) and (n_stream>= 50):
            default = 50
        else:
            default = n_stream
            
        self.spbRecluster.setValue(default)
        self.spbRecluster.setRange(1, n_stream)
        self.hSlReCluster.setValue(default)
#        self.hSlReCluster.setSingleStep() 
        self.hSlReCluster.setMinimum(1)
        self.hSlReCluster.setMaximum(n_stream)
        self.tblTract.item(1, 1).setText(str(n_stream))
        

    @Slot()
    def on_dspbxcoord_valueChanged(self, value):
        self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  coordx = value,  rebuild= True)
        self.glWidget.updateGL()
            
    @Slot()
    def on_dspbycoord_valueChanged(self, value):
        self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  coordy = value, rebuild= True)
        self.glWidget.updateGL()
            
    @Slot()
    def on_dspbzcoord_valueChanged(self, value): 
        self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  coordz = value, rebuild= True)
        self.glWidget.updateGL()
            
    @Slot()
    def on_spbrad_valueChanged(self, value): 
        
        self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(), radius=value, rebuild= True)
        self.glWidget.updateGL()
    
    @Slot()
    def on_chkbvis_stateChanged(self, state): 
        """
        Shows or hides the ROI if the visibility checkbox is checked or not correspondingly
        """
        self.spaghetti.show_hide_actor(self.tblROI.item(0, 1).text(), state)
        if self.list_chkROIS[self.activeROI].isChecked():
            self.list_chkROIS[self.activeROI].setChecked(False)
        self.glWidget.updateGL()
        
    @Slot(QtGui.QTreeWidgetItem, int)
    def on_treeObject_itemClicked(self, item, column):
        """
        If the item selected is a ROI, the corresponding information will be shown in the tableROI
        """
        name = str(item.text(0))
        xcoord, ycoord, zcoord, radius, color= self.spaghetti.information_from_ROI(name)
        index= self.treeObject.indexFromItem(item)
        self.activeROI = index.row()
        self.disconnect(self.tblROI, QtCore.SIGNAL("itemChanged(QtGui.QTableWidgetItem)"), self.on_tblROI_itemChanged)
        self.updateROItable(name, xcoord, ycoord, zcoord, radius, color)
        self.connect(self.tblROI, QtCore.SIGNAL("itemChanged(QtGui.QTableWidgetItem)"), self.on_tblROI_itemChanged)
        
    def on_btncolor_clicked(self):
        color = QtGui.QColorDialog().getColor()
        self.btncolor.setStyleSheet( u'background-color:%s' % color.name()) 
        self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  color = color.getRgbF())
#        self.glWidget.updateGL()
#        
    @Slot(int)
    def on_chkbShowTract_stateChanged(self, state):
        """
        Shows or hides the tractography if the Checkbox is checked or not correspondingly
        """
        self.spaghetti.show_hide_actor('Bundle Picker', state)
        self.glWidget.updateGL()
        
    @Slot(int)
    def on_chkbShowStruct_stateChanged(self, state):
        """
        Shows or hides the structural image if the Checkbox is checked or not correspondingly
        """
        self.spaghetti.show_hide_actor('Volume Slicer', state)
        self.glWidget.updateGL()
#    
#    @Slot(bool)
#    def on_rdbTrackvis_toggled(self, checked):
#        """
#        Use method of Trackvis to compute the ROI
#        """
#        pdb.set_trace()
#        if checked:
#            self.roimethod = 0
#            self.grb_tractomeroi.setEnabled(False)
 
#            if len(self.list_chkROIS)>0:
#                self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  method = self.roimethod, rebuild= True)
#            
#    
#    @Slot(bool)
#    def on_rdbTract_toggled(self, checked):
#        """
#        To change ROI method to tractome's version
#        """
#        if checked:
#            self.grb_tractomeroi.setEnabled(True)
#            self.rdbInsSphere.toggle()
#               
#       
    @Slot(bool)
    def on_rdbInsSphere_toggled(self, checked):
        """
        Use method of Tractome inside sphere to compute the ROI
        """
        if checked:
            self.roimethod = 1
                       
            if len(self.list_chkROIS)>0:
               self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  method = self.roimethod, rebuild= True)
    
#       
#    @Slot(bool)
#    def on_rdbIntSphere_toggled(self, checked):
#        """
#        Use method of Tractome intersect sphere to compute the ROI.
#        """
#        if checked:
#            self.roimethod = 2
#                        
#            if len(self.list_chkROIS)>0:
#               self.spaghetti.update_ROI(self.tblROI.item(0, 1).text(),  method = self.roimethod, rebuild= True)
#    
    
    @Slot(int)
    def on_spbRecluster_valueChanged(self, p0):
        """
        Update slider Recluster
        """
        self.hSlReCluster.setValue(p0)
   
    @Slot(int)
    def on_hSlReCluster_valueChanged(self, value):
        """
        Update spbRecluster
        """
        self.spbRecluster.setValue(value)
        
    @Slot()
    def on_pbRecluster_clicked(self):
        """
        Call re-cluster function from spaghetti and update values of possible number of clusters for related objects.
        """
        self.spaghetti.recluster(self.spbRecluster.value())
    
#    @Slot()
#    def on_spbExtClust_editingFinished(self):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError
#    
#    @Slot(int)
#    def on_spbExtClust_valueChanged(self, p0):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError
#    
#    @Slot(int)
#    def on_vSlExtClust_valueChanged(self, value):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError
#    
    @Slot()
    def on_actionLoad_Structural_Image_triggered(self):
        """
        Opens a dialog to allow the user to choose the structural file.
        """
        #Creating filedialog to search for the structural file
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("((*.gz *.nii *.img)"))
        self.fileStruct= filedialog.getOpenFileName(self,"Open Structural file", os.getcwd(), str("(*.gz *.nii *.img)"))
        struct_basename = os.path.basename(self.fileStruct[0])

        self.create_update_Item('slicer')
        self.spaghetti.loading_structural(self.fileStruct[0])
        self.structnameitem.setText(0, struct_basename) 
        self.refocus_camera()  
    
    @Slot()
    def on_actionLoad_MASk_triggered(self):
        """
        Opens a dialog to allow the user to choose the mask file.
        """
        #Creating filedialog to search for the structural file
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("((*.gz *.nii *.img)"))
        self.fileMask= filedialog.getOpenFileName(self,"Open Mask file", os.getcwd(), str("(*.gz *.nii *.img)"))
        mask_basename = os.path.basename(self.fileMask[0])
        self.prepare_interface_ROI('mask',  nameroi = mask_basename)
        self.spaghetti.loading_mask(self.fileMask[0], self.roi_color)
        self.updateROItable(mask_basename, color = self.roi_color.name())
        self.refocus_camera()  
   
          
    @Slot()
    def on_actionLoad_Tractography_triggered(self):
        """
        Opens a dialog to allow the user to choose the tractography file 
        """
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("(*.dpy *.trk *.vtk)"))
        self.fileTract = filedialog.getOpenFileName(self,"Open Tractography file", os.getcwd(), str("(*.dpy *.trk *.vtk)"))
        tracks_basename = os.path.basename(self.fileTract[0])
        
        self.create_update_Item('tractography') 
        self.spaghetti.loading_full_tractograpy(tracpath=self.fileTract[0]) 
        self.set_clustering_values()
        self.tractnameitem.setText(0, tracks_basename)
        
        # connecting event that is fired when number of streamlines is changed after some action on the streamlinelabeler actor
        
        self.spaghetti.streamlab.numstream_handler += self.changenumstreamlines_handler
    
        #add information to tab in Table
        self.tblTract.item(0, 1).setText(tracks_basename)
        trackcount = len(self.spaghetti.T)
        self.tblTract.item(1, 1).setText(str(trackcount))
    
        if hasattr(self.spaghetti, 'hdr'):
            hdr = self.spaghetti.hdr
            self.tblTract.item(2, 1).setText(str(hdr['voxel_size']))
            self.tblTract.item(3, 1).setText(str(hdr['dim']))
            self.tblTract.item(4, 1).setText(str(hdr['voxel_order']))
                         
                
        else:
            self.tblTract.item(2, 1).setText('No info')
            self.tblTract.item(3, 1).setText('No info')
            self.tblTract.item(4, 1).setText('LAS')
     
        self.refocus_camera() 
                
   
    def create_update_Item(self,  object):
        """
        Creates or updates the specified item in the TreeObject and the corresponding actor in the Scene (if neccesary)
        """
        if object == 'tractography':
            #checking if there is already a tractography open to substitute it
            try:
                self.tractnameitem
                self.spaghetti.clear_actor('Bundle Picker')
                self.clear_all_session()
                                
            #if there is no tractography open 
            except AttributeError: 
                self.tractnameitem =  QtGui.QTreeWidgetItem(self.treeObject) 
                self.chkbShowTract.setEnabled(True)
                self.tblTract.setEnabled(True)
                self.actionSave_Segmentation.setEnabled(True) 
                self.actionSave_as_trackvis_file.setEnabled(True)
                self.menuROI.setEnabled(True)
                self.menuFunctions.setEnabled(True)
                
                            
        if object == 'slicer':
            try:
                self.structnameitem
                self.treeObject.clear()
                self.spaghetti.clear_all()
                self.clear_all_session()
            
            except AttributeError:
             #If this is the first opening we create the tree item
                self.actionLoad_Tractography.setEnabled(True)
                self.chkbShowStruct.setEnabled(True)
            
            self.structnameitem =  QtGui.QTreeWidgetItem(self.treeObject)    
            
        
        
    
    @Slot()
    def on_actionLoad_Saved_Segmentation_triggered(self):
        """
        Opens a dialog to allow the user to choose a file of a previously saved session
        """
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("(*.seg)"))
        fileSeg = filedialog.getOpenFileName(self,"Open Segmentation file", os.getcwd(), str("(*.seg)"))
               
        #checking if there is already a tractography open to substitute it
        try:
            self.structnameitem
            self.tractnameitem
            self.treeObject.clear()
            self.spaghetti.clear_all()
            self.clear_all_session()

                
        #if there is no tractography open 
        except AttributeError: 
            self.chkbShowStruct.setEnabled(True)
            self.chkbShowTract.setEnabled(True)
            self.tblTract.setEnabled(True)
            self.menuROI.setEnabled(True)
            self.menuFunctions.setEnabled(True)
            
        self.structnameitem =  QtGui.QTreeWidgetItem(self.treeObject)   
        self.tractnameitem =  QtGui.QTreeWidgetItem(self.treeObject) 
        self.spaghetti.load_segmentation(fileSeg[0])
         
         #add structural and tractography file names to the treeview
        struct_basename = os.path.basename(self.spaghetti.structpath)
        self.structnameitem.setText(0, struct_basename) 
         
        tracks_basename = os.path.basename(self.spaghetti.tracpath)  
        self.tractnameitem.setText(0, tracks_basename)
        
        #add information to tab in Table
        self.tblTract.item(0, 1).setText(tracks_basename)
        trackcount = len(self.spaghetti.T)
        self.tblTract.item(1, 1).setText(str(trackcount))
        
        try:
            hdr = self.spaghetti.hdr
            self.tblTract.item(2, 1).setText(str(hdr['voxel_size']))
            self.tblTract.item(3, 1).setText(str(hdr['dim']))
            self.tblTract.item(4, 1).setText(str(hdr['voxel_order']))
                     
            
        except AttributeError:
            self.tblTract.item(2, 1).setText('No info')
            self.tblTract.item(3, 1).setText('No info')
            self.tblTract.item(4, 1).setText('LAS')
        
        self.refocus_camera()  

    def clear_all_session(self):
        """
        Clear all the objects related to ROIs
        """
        self.list_chkROIS = []
        self.list_ands = []
        self.list_ors = []
        self.tblROISlist.clear()
        
        
#    
    @Slot()
    def on_actionSave_as_trackvis_file_triggered(self):
        """
        Save streamlines of actual session in .trk file
        """
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Segmentation in .trk', os.getcwd(), str("(*.trk)"))
        self.spaghetti.save_trk(filename)
        
    
    @Slot()
    def on_actionSave_Segmentation_triggered(self):
        """
        Saves the current session.
        """
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Segmentation', os.getcwd(), str("(*.seg)"))
        self.spaghetti.save_segmentation(filename)
        
    
    @Slot()
    def on_actionClose_triggered(self):
        """
        Close application
        """
        self.close()
    
    def disconnect_signals(self):
        '''
        Disconnect signal of spinboxes in ROI tables. If they are connected when updating min_max values of spinbox, the valueChanged signal is unnecessarily called. 
        '''
        self.disconnect(self.spbrad, QtCore.SIGNAL("valueChanged(int)"), self.on_spbrad_valueChanged)
        self.disconnect(self.dspbxcoord, QtCore.SIGNAL("valueChanged(double)"), self.on_dspbxcoord_valueChanged)
        self.disconnect(self.dspbycoord, QtCore.SIGNAL("valueChanged(double)"), self.on_dspbycoord_valueChanged)
        self.disconnect(self.dspbzcoord, QtCore.SIGNAL("valueChanged(double)"), self.on_dspbzcoord_valueChanged)
        
    def connect_signals(self):
        '''
        Reconnect signals of spinboxes in ROI tables, after min_max values have been updated
        '''
        self.connect(self.spbrad, QtCore.SIGNAL("valueChanged(int)"), self.on_spbrad_valueChanged)
        self.connect(self.dspbxcoord, QtCore.SIGNAL("valueChanged(double)"), self.on_dspbxcoord_valueChanged)
        self.connect(self.dspbycoord, QtCore.SIGNAL("valueChanged(double)"), self.on_dspbycoord_valueChanged)
        self.connect(self.dspbzcoord, QtCore.SIGNAL("valueChanged(double)"), self.on_dspbzcoord_valueChanged)
    
    @Slot()
    def on_actionCreate_Sphere_triggered(self):
        """
        Create a ROI and plot sphere
        """
        maxcoord = self.spaghetti.max_coordinates()
        xmax = maxcoord[0]
        ymax = maxcoord[1]
        zmax = maxcoord[2]
        self.grb_tractomeroi.setEnabled(True)
        self.rdbInsSphere.toggle()
        cantrois = 0
        
        if hasattr(self, 'list_chkROIS'):
            cantrois = len(self.list_chkROIS) 
    
        number =cantrois + 1 #to define the name of the ROI depending on the number of available ROIs
        nameroi = 'ROI'+ str(number)
        
        self.prepare_interface_ROI('sphere', coords=maxcoord,  nameroi = nameroi)    
        self.spaghetti.create_ROI_sphere(nameroi, xmax/2, ymax/2, zmax/2, 2, self.roimethod, self.roi_color)
             
        #add info of the ROI to ROI table
        self.updateROItable(nameroi, xmax/2, ymax/2, zmax/2, 2, self.roi_color.name())
        self.tabProps_4.setCurrentIndex(1) 

        self.refocus_camera()  

    def prepare_interface_ROI(self, roi_type,  coords=None,  nameroi = None):
        """
        Set values and status of all interface elementes related to ROI
        """
        self.tblROI.setEnabled(True)
        self.tblROISlist.setEnabled(True)
        self.show_hide_rows(roi_type == 'mask')
        try:
            self.list_chkROIS
                                   
        except AttributeError:
            self.list_chkROIS = []
            self.list_ands = []
            self.list_ors = []
            #add some fixed information to ROI table
            if roi_type == 'sphere':
                maxcoord = coords
                self.radmax = np.amax(maxcoord)  
                self.grbROImethod.setEnabled(True)
                
                #setting some fixed values in the table
                self.dspbxcoord.setRange(0, maxcoord[0])
                self.dspbycoord.setRange(0,maxcoord[1])
                self.dspbzcoord.setRange(0, maxcoord[2])
                self.spbrad.setRange(1, self.radmax)
                self.connect_signals()
#      
        cantrois = len(self.list_chkROIS)           
        self.activeROI = cantrois #to know which is the ROI shown in the table, in case some information needs to be changed
        
        #define color
        if  cantrois < len(self.colorlist):
            self.roi_color = self.colorlist[self.activeROI]
        else:
            poscolor = self.activeROI%len(self.colorlist)
            self.roi_color = self.colorlist[poscolor]
#               
       #add item to tractography in tree
        roinameitem =  QtGui.QTreeWidgetItem(self.tractnameitem) 
        roinameitem.setText(0, nameroi) #should we add the whole file path?
##        roinameitem.setSelected(True)
        self.treeObject.expandAll()
        
        #create checkbox for applying ROI, add to list and to table for applied ROIs
        newchkroi = QtGui.QCheckBox()
        newchkroi.setText(nameroi)
        self.connect(newchkroi, QtCore.SIGNAL("stateChanged(int)"), self.on_chkroi_stateChanged)
        self.list_chkROIS.append(newchkroi)
#        
        #create rdbuttons for operators and add checkbox for ROI
        cantchk = cantrois
        if cantchk==0:
            self.tblROISlist.insertRow(0)
            self.tblROISlist.setCellWidget(0, 0, newchkroi)
        else:
            self.tblROISlist.insertRow((2*cantchk)-1)
            #create groupbox
            grb_roi_operators= QtGui.QGroupBox()
                       
            #create radio buttons 
            rdband = QtGui.QRadioButton("AND")
            rdbor = QtGui.QRadioButton("OR")
            rdbor.setText('OR')
            
            #add radio button to groupbox
            horizontalLayout_roiop = QtGui.QHBoxLayout()
            horizontalLayout_roiop.addWidget(rdband)
            horizontalLayout_roiop.addWidget(rdbor)
            horizontalLayout_roiop.addStretch(1)
            grb_roi_operators.setLayout(horizontalLayout_roiop)
            
            self.connect(rdband, QtCore.SIGNAL("toggled(bool)"), self.on_chkroi_stateChanged)
            self.connect(rdbor, QtCore.SIGNAL("toggled(bool)"), self.on_chkroi_stateChanged)
#            
            self.tblROISlist.setCellWidget((2*cantchk)-1, 0, grb_roi_operators)
            self.list_ands.append(rdband)
            self.list_ors.append(rdbor)
            self.tblROISlist.insertRow(2*cantchk)
            self.tblROISlist.setCellWidget(2*cantchk, 0, newchkroi)
            self.tblROISlist.resizeRowsToContents()
        

        
    def updateROItable(self, name,coordx=None, coordy=None, coordz=None, radius=None, color=None):
        """
        Information of ROI  is inserted in table when new ROI is created or when ROI selection changes in treeview
        """
        #show info of ROI in the table
        self.tblROI.item(0, 1).setText(name)


        if coordx is not None:
            self.disconnect_signals()
            self.dspbxcoord.setValue(coordx) 
            self.dspbycoord.setValue(coordy)
            self.dspbzcoord.setValue(coordz)
            self.spbrad.setValue(radius)
            self.connect_signals()
        self.btncolor.setStyleSheet( u'background-color:%s' % color)
        
    def show_hide_rows(self,  hide):
        """
        Hides or shows rows from TableROI, depending on the type of ROI is selected on the tree. 
        """
        for i in range(3, self.tblROI.rowCount()):
            self.tblROI.setRowHidden(i, hide)
        self.tblROI.resizeRowsToContents()
        
    @Slot()
    def on_chkroi_stateChanged(self, checked):
        '''
        Computing streamlines to show according to ROIs that are checked and their operators
        '''
        streamlines_ROIs = []
        last_chkd = 0
        for pos in range(0, len(self.list_chkROIS)):
            if self.list_chkROIS[pos].isChecked():
                self.spaghetti.activation_ROIs(pos, True)
                if pos!=(len(self.list_chkROIS)-1) and ((self.list_ands[pos].isChecked()==False) and (self.list_ors[pos].isChecked()==False)):
                     self.list_ands[pos].setChecked(True)
                
                if not pos==0:
                    if self.list_ands[last_chkd].isChecked():
                        self.spaghetti.activation_ROIs(pos,  True, operator = 'and')
                    if self.list_ors[last_chkd].isChecked():
                        self.spaghetti.activation_ROIs(pos,  True, operator = 'or')
              
            else:
                self.spaghetti.activation_ROIs(pos, False)
                if pos!=(len(self.list_chkROIS)-1):
                     if self.list_ands[pos].isChecked():
                         self.list_ands[pos].setAutoExclusive(False)
                         self.list_ands[pos].setChecked(False)
                         self.list_ands[pos].setAutoExclusive(True)
                     if self.list_ors[pos].isChecked():
                         self.list_ors[pos].setAutoExclusive(False)
                         self.list_ors[pos].setChecked(False)
                         self.list_ors[pos].setAutoExclusive(True)
                         
                
                        
        self.spaghetti.compute_streamlines_ROIS()
        self.glWidget.updateGL()
                    
           
            
        
    @Slot(QtGui.QTableWidgetItem)   
    def on_tblROI_itemChanged(self, item):
        """
        Will change name of ROI if this is edited in the table
        """
        treeitem = self.tractnameitem.child(self.activeROI)
        if item is self.tblROI.item(0, 1):
            prev_name_roi = str(treeitem.text(0))
            
            index = self.treeObject.indexFromItem(treeitem, 0)            
            if index.isValid():
                self.spaghetti.update_ROI(prev_name_roi,  newname = item.text(), pos_activeroi = self.activeROI)
                treeitem.setText(0, item.text()) 
    
#    @Slot()
#    def on_actionExpand_ROI_triggered(self):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError
#    
    
    @Slot()
    def on_actionRe_Cluster_triggered(self):
        """
        Re-cluster
        """
        self.groupBox_12.setEnabled(True)
        self.spbRecluster.setEnabled(True)
        self.hSlReCluster.setEnabled(True)
        self.pbRecluster.setEnabled(True)
        
    def set_clustering_values(self):
        
        max,  default = self.spaghetti.max_num_clusters()
        self.spbRecluster. setValue(default)
        self.spbRecluster.setRange(1, max)
        self.hSlReCluster.setValue(default)
        self.hSlReCluster.setMinimum(1)
        self.hSlReCluster.setMaximum(max)
#    
#    @Slot()
#    def on_actionExpand_Clusters_triggered(self):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError
#        
        
    def initSpincamera(self, angle = 0.007 ):

        if self._spinCameraTimerInit:
            self.spinCameraTimer.timeout.disconnect()
        
        def rotate_camera():
            self.glWidget.world.camera.rotate_around_focal( angle, "yup" )
            self.glWidget.updateGL()
        
        self.spinCameraTimer.timeout.connect(rotate_camera)
        self._spinCameraTimerInit = True

    def spinCameraToggle(self):
        if not self.spinCameraTimer.isActive():
            self.spinCameraTimer.start()
        else:
            self.spinCameraTimer.stop()

    def timerInit(self, interval = 30):
        timer = QtCore.QTimer(self)
        timer.setInterval( interval )
        return timer

    def add_scene(self, scene):
        self.glWidget.world.add_scene(scene)
        
    def set_camera(self, camera):
        self.glWidget.world.camera = camera

    def refocus_camera(self):
        self.glWidget.world.refocus_camera()

    def update_light_position(self, x, y, z):
        if not self.glWidget.world.light is None:
            self.glWidget.world.update_lightposition(x, y, z)

    def screenshot(self, filename):
        """ Store current OpenGL context as image
        """
        self.glWidget.updateGL()
        self.glWidget.grabFrameBuffer().save( filename )

    
    def keyPressEvent(self, event):
        """ Handle all key press events
        """
        #print 'key pressed', event.key()   
        key = event.key()
        #self.messages=empty_messages.copy()
        #self.messages['key_pressed']=key
        #self.glWidget.world.send_all_messages(self.messages)       
        # F1: fullscreen
        # F2: next frame
        # F3: previous frame
        # F4: start rotating
        # F12: reset camera
        # Esc: close window
        if key == QtCore.Qt.Key_F1:
            if self.fullscreen:
                self.showNormal()
            else:
                self.showFullScreen()
            self.fullscreen = not self.fullscreen
        elif key == QtCore.Qt.Key_F2:
            self.glWidget.world.nextTimeFrame()
        elif key == QtCore.Qt.Key_F3:
            self.glWidget.world.previousTimeFrame()
        elif key == QtCore.Qt.Key_F12:
            self.glWidget.world.refocus_camera()
            self.glWidget.world.camera.update()
            self.glWidget.updateGL()
        elif key == QtCore.Qt.Key_F4:
            if (event.modifiers() & QtCore.Qt.ShiftModifier):
                self.initSpincamera( angle = -0.01 )
                self.spinCameraToggle()
            else:
                self.initSpincamera( angle = 0.01 )
                self.spinCameraToggle()
        elif key == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super(MainWindow, self).keyPressEvent( event )
        self.glWidget.updateGL()
        

if __name__ == "__main__":
    #import sys
    #app = QtGui.QApplication(sys.argv)
    #mainWindow= MainWindow()
    #mainWindow.show()
    #sys.exit(app.exec_())
	
    mainWindow= MainWindow()
    mainWindow.show()
    
    