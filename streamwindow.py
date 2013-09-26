import os
import sys
from PySide import QtCore, QtGui, QtOpenGL

from fos.vsml import vsml
from fos.world import *
from fos.actor import *
from spaghetti import Spaghetti

try:
    from pyglet.gl import *
except ImportError:
    print("Need pyglet for OpenGL rendering")

empty_messages={ 'key_pressed':None,
                    'mouse_pressed':None,
                    'mouse_position':None,
                    'mouse_moved':None,
                    'mod_key_pressed':None}


class RightPanel(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
       
        self.parent = parent
        
        self.SpinBoxi = QtGui.QSpinBox()
        self.SpinBoxi.setRange(0, 255)
        self.SpinBoxi.setSingleStep(1)

        self.SpinBoxj = QtGui.QSpinBox()
        self.SpinBoxj.setRange(0, 255)
        self.SpinBoxj.setSingleStep(1)

        self.SpinBoxk = QtGui.QSpinBox()
        self.SpinBoxk.setRange(0, 255)
        self.SpinBoxk.setSingleStep(1)

        spinLayoutijk = QtGui.QHBoxLayout()
        spinLayoutijk.addWidget(self.SpinBoxi)
        spinLayoutijk.addWidget(self.SpinBoxj)
        spinLayoutijk.addWidget(self.SpinBoxk)

        showi = QtGui.QPushButton("Saggital")
        showi.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Normal))
        showj = QtGui.QPushButton("Axial")
        showj.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Normal))
        showk = QtGui.QPushButton("Coronal")
        showk.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Normal))

        self.connect(showi, QtCore.SIGNAL("clicked()"), 
                        self, QtCore.SLOT("show_i()"))
        
        self.connect(showj, QtCore.SIGNAL("clicked()"), 
                        self, QtCore.SLOT("show_j()"))

        self.connect(showk, QtCore.SIGNAL("clicked()"), 
                        self, QtCore.SLOT("show_k()"))

        pushLayout = QtGui.QHBoxLayout()
        pushLayout.addWidget(showi)
        pushLayout.addWidget(showj)
        pushLayout.addWidget(showk)

        dial1 = QtGui.QDial()
        dial1.setMinimum(0)
        dial1.setMaximum(90)

        dial2 = QtGui.QDial()
        dial2.setMinimum(0)
        dial2.setMaximum(90)
        
        dial3 = QtGui.QDial()
        dial3.setMinimum(0)
        dial3.setMaximum(90)


        dialLayout = QtGui.QHBoxLayout()
        dialLayout.addWidget(dial1)
        dialLayout.addWidget(dial2)
        dialLayout.addWidget(dial3)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(spinLayoutijk)
        vbox.addLayout(pushLayout)
        vbox.addLayout(dialLayout)

        self.setLayout(vbox)

        #groupBox = QtGui.QGroupBox("Volume Slicer")
        #groupBox.setLayout(vbox)

        #self.groupBox = groupBox

    def access_vol(self):
        self.vol = self.parent.glWidget.world.scenes['Main Scene'].actors['Volume Slicer']

    def show_i(self):
        self.access_vol()
        self.vol.show_i = not self.vol.show_i
        self.parent.glWidget.updateGL()
        self.parent.glWidget.setFocus()

    def show_j(self):
        self.access_vol()
        self.vol.show_j = not self.vol.show_j
        self.parent.glWidget.updateGL()
        self.parent.glWidget.setFocus()
    
    def show_k(self):
        self.access_vol()
        self.vol.show_k = not self.vol.show_k
        self.parent.glWidget.updateGL()
        self.parent.glWidget.setFocus()
        



class Window(QtGui.QMainWindow):


    def __init__(self, parent = None,
                    width=600,
                    height=400,
                    bgcolor = (0,0,0), 
                    fullscreen = False, 
                    dynamic = False, 
                    enable_light = False, right_panel=False):
        """ Create a window

        Parameters
        ----------
        `caption` : str or unicode
            Initial caption (title) of the window.
        `width` : int
            Width of the window, in pixels.  Defaults to 640, or the
            screen width if `fullscreen` is True.
        `height` : int
            Height of the window, in pixels.  Defaults to 480, or the
            screen height if `fullscreen` is True.
        `bgcolor` : tuple
            Specify the background RGB color as 3-tuple with values
            between 0 and 1
        """
        # TODO: add PySide.QtOpenGL.QGLFormat to configure the OpenGL context
        QtGui.QMainWindow.__init__(self, parent)
#        screenSize= QtGui.qApp.desktop().availableGeometry().size()
        self.glWidget = GLWidget(parent = self, 
                                    width = width, 
                                    height = height,
                                    bgcolor = (.5, .5, 0.9), 
                                    enable_light = enable_light)
                                    
             
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)

        if right_panel:
            rightPanel = RightPanel(self)
            mainLayout.addWidget(rightPanel)
            
        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

#        self.setLayout(mainLayout)
        title = 'Streamline Interaction and Segmentation'
        self.setWindowTitle(self.tr(title))      
        self.createActions()
        self.createMenus()
      
        self.spinCameraTimer = self.timerInit(interval = 30)
        self._spinCameraTimerInit = False

        self.messages=empty_messages
        self.last_key=None
        
        if dynamic:
            self.dynamicWindowTimer = self.timerInit(interval = 30)
            self.dynamicWindowTimer.timeout.connect(self.glWidget.updateGL)
            self.dynamicWindowTimer.start()

        if fullscreen:
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.show()
            self.fullscreen = False
            
            
    def saveFile(self):
        """
        Saves the current session"
        """
#        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Segmentation', self.spaghetti.tracpath, str("(*.seg)"))
#        seg_basename = filename[:filename.find(".")]
#        self.spaghetti.SaveSegmentation(seg_basename)
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Segmentation', os.getcwd(), str("(*.seg)"))
        self.spaghetti.SaveSegmentation(filename)
        

    def openStructFile(self):
        """
        Opens a dialog to allow the user to choose the structural file
        """
#        flags = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
#        self.directorystruct = QtGui.QFileDialog.getExistingDirectory(self,"Open Directory", os.getcwd(),flags)
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("(*.dpy *.trk)"))
        self.fileStruct= filedialog.getOpenFileName(self,"Open Structural file", os.getcwd(), str("(*.gz)"))
           
   
    def openTractFile(self):
        """
        Opens a dialog to allow the user to choose the tractography file 
        """
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("(*.dpy *.trk)"))
        self.fileTract = filedialog.getOpenFileName(self,"Open Tractography file", os.getcwd(), str("(*.dpy *.trk)"))
        self.spaghetti= Spaghetti(self.fileStruct[0], self.fileTract[0])
              
        try:
             self.scene
             self.scene.actors['Volume Slicer'] = self.spaghetti.guil
             self.scene.actors['Bundle Picker'] = self.spaghetti.tl
             self.scene.update()
            
        except AttributeError:
            #If this is the first opening we create the spaghetti class and the scene with actors
            self.scene = Scene(scenename = 'Main Scene', activate_aabb = False)
            self.scene.add_actor(self.spaghetti.guil)
            self.scene.add_actor(self.spaghetti.tl)
            self.add_scene(self.scene)
            
        self.refocus_camera()
        
    def OpenSegmSession(self):
        """
        Opens a dialog to allow the user to choose a file of a previously saved session
        """
        filedialog=QtGui.QFileDialog()
        filedialog.setNameFilter(str("(*.seg)"))
        fileSeg = filedialog.getOpenFileName(self,"Open Tractography file", os.getcwd(), str("(*.seg)"))
        self.spaghetti= Spaghetti(segmpath=fileSeg[0])
        
        try:
           self.scene
           self.scene.actors['Volume Slicer'] = self.spaghetti.guil
           self.scene.actors['Bundle Picker'] = self.spaghetti.tl
           self.scene.update()
        
        except AttributeError:
            self.scene = Scene(scenename = 'Main Scene', activate_aabb = False)
            self.scene.add_actor(self.spaghetti.guil)
            self.scene.add_actor(self.spaghetti.tl)
            self.add_scene(self.scene)
            
        self.refocus_camera()
        
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openStruct)
        self.fileMenu.addAction(self.openTract)
        self.fileMenu.addAction(self.openSeg)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        
        self.editMenu = self.menuBar().addMenu("&Edit")
#        self.editMenu.addAction(self.undoAct)
#        self.editMenu.addAction(self.redoAct)
#        self.editMenu.addSeparator()
#        self.editMenu.addAction(self.cutAct)
#        self.editMenu.addAction(self.copyAct)
#        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()
    
    def createActions(self):
        self.openStruct = QtGui.QAction("&Open Structural...", self,
                shortcut=QtGui.QKeySequence("Ctrl+G"),
                statusTip="Open an existing structural file", triggered=self.openStructFile)
                
        self.openTract = QtGui.QAction("&Open Tractography...", self,
                shortcut=QtGui.QKeySequence("Ctrl+T"),
                statusTip="Open an existing tractography file", triggered=self.openTractFile)
                
        self.openSeg = QtGui.QAction("&Open Segmentation result...", self,
                shortcut=QtGui.QKeySequence("Ctrl+N"),
                statusTip="Open an existing segmentation session file", triggered=self.OpenSegmSession)        

        self.saveAct = QtGui.QAction("&Save segmentation", self,
                shortcut=QtGui.QKeySequence.Save,
                statusTip="Save the current segmentation session to disk", triggered=self.saveFile)

#        self.printAct = QtGui.QAction("&Print...", self,
#                shortcut=QtGui.QKeySequence.Print,
#                statusTip="Print the document", triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

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
            super(Window, self).keyPressEvent( event )
        self.glWidget.updateGL()
        
        
        

# if event.key() == Qt.Key_O and ( event.modifiers() & Qt.ControlModifier ): 
# & == bit wise "and"!

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None, 
                        width = None, 
                        height = None, 
                        bgcolor = None, 
                        enable_light = False, 
                        ortho = False):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.lastPos = QtCore.QPoint()
        self.bgcolor = QtGui.QColor.fromRgbF(bgcolor[0], bgcolor[1], bgcolor[2], 1.0)
        self.width = width
        self.height = height
        self.enable_light = enable_light
        self.world = World()
        self.ortho = ortho
        self.messages = empty_messages
        self.setMouseTracking(True)
        # camera rotation speed
        self.ang_step = 0.02
        # necessary to grab key events
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.parent = parent

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.width, self.height)

    def initializeGL(self):
        self.qglClearColor(self.bgcolor)
        glShadeModel(GL_SMOOTH)
        #glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        if self.enable_light:
            self.world.setup_light()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.world.draw_all()

    def resizeGL(self, width, height):
        #side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)
        if height == 0:
            height = 1
        vsml.setSize( width, height )
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        if self.ortho:
            self.width_ortho = self.width
            self.height_ortho = self.height
        self.update_projection()

    def update_projection(self, factor = 1.0):
        vsml.loadIdentity(vsml.MatrixTypes.PROJECTION)
        ratio =  abs(self.width * 1.0 / self.height)
        if self.ortho:
            self.width_ortho += -factor * ratio
            self.height_ortho += -factor
            vsml.ortho(-(self.width_ortho)/2.,(self.width_ortho)/2.,
                (self.height_ortho)/2.,(self.height_ortho)/-2.,-500,8000)
        else:
            vsml.perspective(60., ratio, .1, 8000)
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(vsml.get_projection())
        glMatrixMode(GL_MODELVIEW)

    def ortho_zoom(self, zoom_level = 1.0):
        if not self.ortho:
            print('Not on orthogonal projection mode')
            return
        vsml.loadIdentity(vsml.MatrixTypes.PROJECTION)
        ratio =  abs(self.width * 1.0 / self.height)
        self.width_ortho = self.width * zoom_level * ratio
        self.height_ortho = self.width * zoom_level
        vsml.ortho(-(self.width_ortho)/2.,(self.width_ortho)/2.,
            (self.height_ortho)/2.,(self.height_ortho)/-2.,-500,8000)
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(vsml.get_projection())
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            x, y = event.x(), event.y()
            self.world.pick_all(x, self.height - y)

    def mouseMoveEvent(self, event):
        self.messages=empty_messages.copy()
        self.messages['mouse_position']=(event.x(),self.height - event.y())
        self.world.send_all_messages(self.messages)
        self.messages=empty_messages
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            shift = True
        else:
            shift = False
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            ctrl = True
        else:
            ctrl = False
        if event.buttons() & QtCore.Qt.LeftButton:
            if not ctrl:
                # should rotate
                if dx != 0:
                    # rotate around yup
                    if dx > 0: angle = -self.ang_step #0.01
                    else: angle = self.ang_step #0.01
                    if shift: angle *= 2
                    self.world.camera.rotate_around_focal(angle, "yup")
                if dy != 0:
                    # rotate around right
                    if dy > 0: angle = -self.ang_step #0.01
                    else: angle = self.ang_step #0.01
                    if shift: angle *= 2
                    self.world.camera.rotate_around_focal(angle, "right")
                self.updateGL()
            else:
                # with control, do many selects!
                x, y = event.x(), event.y()
                self.world.pick_all( x, self.height - y)

        elif event.buttons() & QtCore.Qt.RightButton:
            # should pan
            if dx > 0: pandx = -1.0
            elif dx < 0: pandx = 1.0
            else: pandx = 0.0
            if dy > 0: pandy = 0.5
            elif dy < 0: pandy = -0.5
            else: pandy = 0.0
            if shift:
                pandx *= 4
                pandy *= 4
            self.world.camera.pan( pandx, pandy )
            self.updateGL()
            
        self.lastPos = QtCore.QPoint(event.pos())

    def wheelEvent(self, e):
        numSteps = e.delta() / 15 / 8
        #print "numsteps", numSteps
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            ctrl = True
        else:
            ctrl = False
        if (e.modifiers() & QtCore.Qt.ShiftModifier):
            shift = True
        else:
            shift = False
        if self.ortho:
            if shift:
                numSteps *= 10
            self.update_projection( 10.*numSteps )
            self.updateGL()
            return
        if ctrl:
            if shift:
                self.world.camera.move_forward_all( numSteps * 10 )
            else:
                self.world.camera.move_forward_all( numSteps )
        else:
            if shift:
                self.world.camera.move_forward( numSteps * 10 )
            else:
                self.world.camera.move_forward( numSteps )
        self.updateGL()


    def keyPressEvent(self, event):
        """ Handle all key press events
        """
        #print 'key pressed GLWidget', event.key()   
        key = event.key()
        self.messages=empty_messages.copy()
        self.messages['key_pressed']=key
        self.world.send_all_messages(self.messages)       
        self.updateGL()
        self.parent.keyPressEvent(event)
        
        
if __name__ == '__main__':

#    app = QtGui.QApplication(sys.argv)
    screenSize= QtGui.QApplication.desktop().availableGeometry (screen = -1).size()
    wind = Window(width=screenSize.width(),height=screenSize.height())
    wind.show()
#    sys.exit(app.exec_()) 
        
