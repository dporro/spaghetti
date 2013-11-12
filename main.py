# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 12:13:01 2013

@author: dporro
"""
import os
import sys
from PyQt4 import  QtGui
from spaghetti import Spaghetti


class MainForm(QtGui.QMainWindow):

    def __init__(self):
        super(MainForm, self).__init__()

        widget = QtGui.QWidget()
        self.setCentralWidget(widget)
        
        title = 'Streamline Interaction and Segmentation'
        self.setWindowTitle(self.tr(title))      
        self.createActions()
        self.createMenus()

              
    def saveFile(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', os.getenv('./'))
        f = open(filename, 'w')
        filedata = self.text.toPlainText()
        f.write(filedata)
        f.close()
        
    def openStructFile(self):
        """
        Opens a dialog to allow user to choose a directory
        """
        flags = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        self.directorystruct = QtGui.QFileDialog.getExistingDirectory(self,"Open Directory", os.getcwd(),flags)
        print self.directorystruct
   
    def openTractFile(self):
        """
        Opens a dialog to allow user to choose a directory
        """
        flags = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        self.directoryTract = QtGui.QFileDialog.getExistingDirectory(self,"Open Directory", os.getcwd(),flags)
        print self.directoryTract
        spa= Spaghetti(str(self.directorystruct), str(self.directoryTract))
        
        
        
            
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openStruct)
        self.fileMenu.addAction(self.openTract)
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
        self.openStruct = QtGui.QAction("&Open Structure...", self,
                shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.openStructFile)
                
        self.openTract = QtGui.QAction("&Open Tractography...", self,
                shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.openTractFile)

        self.saveAct = QtGui.QAction("&Save", self,
                shortcut=QtGui.QKeySequence.Save,
                statusTip="Save the document to disk", triggered=self.saveFile)

#        self.printAct = QtGui.QAction("&Print...", self,
#                shortcut=QtGui.QKeySequence.Print,
#                statusTip="Print the document", triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)
#
#        self.undoAct = QtGui.QAction("&Undo", self,
#                shortcut=QtGui.QKeySequence.Undo,
#                statusTip="Undo the last operation", triggered=self.undo)
#
#        self.redoAct = QtGui.QAction("&Redo", self,
#                shortcut=QtGui.QKeySequence.Redo,
#                statusTip="Redo the last operation", triggered=self.redo)

#        self.aboutQtAct = QtGui.QAction("About &Spaghetti", self,
#                statusTip="Show the Qt library's About box",
#                triggered=self.aboutQt)
#        self.aboutQtAct.triggered.connect(QtGui.qApp.aboutQt)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = MainForm()
    window.show()
    sys.exit(app.exec_())   
   