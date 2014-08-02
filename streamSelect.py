"""
/***************************************************************************
Name		     : streamSelect
Description          : 
Date                 : 2/Aug/2014/ 
copyright            : (C) 2011 by Ruggero Valentinotti
email                : valruggero@gmail.com 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis.utils

import os


class StreamSelect:
    
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
	       
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/streamSelect/icon.png"), "StreamSlelect", self.iface.mainWindow())
        #Add toolbar button and menu item
        #self.iface.addPluginToVectorMenu("&StreamSelect", self.action)
        self.iface.addPluginToMenu("&SBM-Tools", self.action)
        #self.iface.addToolBarIcon(self.action)
        
        #load the form
        path = os.path.dirname(os.path.abspath(__file__))
        self.dock = uic.loadUi(os.path.join(path, "ui_streamSelect.ui"))
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        
        self.sourceIdEmitPoint = QgsMapToolEmitPoint(self.iface.mapCanvas())
        #self.sourceIdEmitPoint.setButton(buttonSelectSourceId)
        self.targetIdEmitPoint = QgsMapToolEmitPoint(self.iface.mapCanvas())
        #self.targetIdEmitPoint.setButton(buttonSelectTargetId)

        
        #connect the action to each method
        QObject.connect(self.action, SIGNAL("triggered()"), self.show)
        QObject.connect(self.dock.comboLayers, SIGNAL("currentIndexChanged(int)"), self.updateComboFields)
        QObject.connect(self.dock.buttonSelectSourceId, SIGNAL("clicked(bool)"), self.selectSourceId)
        QObject.connect(self.sourceIdEmitPoint, SIGNAL("canvasClicked(const QgsPoint&, Qt::MouseButton)"), self.setSourceId)
        QObject.connect(self.dock.buttonSelectTargetId, SIGNAL("clicked(bool)"), self.selectTargetId)
        QObject.connect(self.targetIdEmitPoint, SIGNAL("canvasClicked(const QgsPoint&, Qt::MouseButton)"), self.setTargetId)
        QObject.connect(self.dock.buttonRun, SIGNAL("clicked()"), self.run)
        QObject.connect(self.dock.buttonClear, SIGNAL("clicked()"), self.clear)
	QObject.connect(self.dock.buttonHelp, SIGNAL("clicked()"), self.call_help)
	QObject.connect(self.dock.lineEditSourceId,SIGNAL("editingFinished ()"),self.setSourceIdByExp)
	
	self.sourceFeatID = None
             
        #self.dock.lineEditSourceId.setValidator(QIntValidator())
        #self.dock.lineEditTargetId.setValidator(QIntValidator())
        
        
    def show(self):
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&SBM-Tools", self.action)
        self.iface.removeDockWidget(self.dock)

    def updateComboLayers(self):
	self.dock.comboLayers.clear()
#	self.dock.comboLayers.addItem("")
#        layer = self.iface.mapCanvas().layer(index)
        #populate the combo with vector layers
        mapCanvas = self.iface.mapCanvas()
        for i in range(mapCanvas.layerCount()):
	    layer = mapCanvas.layer(i)
	    if ( layer.type() == layer.VectorLayer  ) and (layer.geometryType() == QGis.Line):
		self.dock.comboLayers.addItem(layer.name(),layer.id())
        
    def updateComboFields(self, index):		
	self.dock.comboFields.clear()
	self.dock.comboFields.addItem("")
#        layer = self.iface.mapCanvas().layer(index)
	activeLayerID = str(self.dock.comboLayers.itemData(index))
	layer = QgsMapLayerRegistry.instance().mapLayer(activeLayerID)
	if layer:
		fields = layer.pendingFields()
		for field in fields:
			if field.typeName() == 'String':
				self.dock.comboFields.addItem(field.name())
        
    def selectSourceId(self, checked):
        if checked:
            self.toggleSelectButton(self.dock.buttonSelectSourceId)
            self.dock.lineEditSourceId.setText("")
            self.iface.mapCanvas().setMapTool(self.sourceIdEmitPoint)
        else:
            self.iface.mapCanvas().unsetMapTool(self.sourceIdEmitPoint)
        
    def setSourceId(self, pt):
	if self.dock.comboLayers.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select a layer and the id field!\n')
        	return   
	if self.dock.comboFields.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select the id field!\n')
        	return
        activeLayerID = str(self.dock.comboLayers.itemData(self.dock.comboLayers.currentIndex()))
	layer = QgsMapLayerRegistry.instance().mapLayer(activeLayerID)
	layer.removeSelection()	
	width = self.iface.mapCanvas().mapUnitsPerPixel() * 2
  	rect = QgsRectangle(pt.x() - width,
                      	    pt.y() - width,
                            pt.x() + width,
                            pt.y() + width)
	layer.select(rect,True)
	selected_features = layer.selectedFeatures()

	if layer.selectedFeatureCount()>1:
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: more than one feature selected!\n')
        	return
	if layer.selectedFeatureCount()==0:
        	return
	for feat in selected_features:
		sourceID=feat[str(self.dock.comboFields.currentText())]
		self.sourceFeatID=feat.id()
	self.dock.lineEditSourceId.setText(sourceID)

    def setSourceIdByExp(self):
	if self.dock.comboLayers.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select a layer and the id field!\n')
        	return   
	if self.dock.comboFields.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select the id field!\n')
        	return  
        activeLayerID = str(self.dock.comboLayers.itemData(self.dock.comboLayers.currentIndex()))
	layer = QgsMapLayerRegistry.instance().mapLayer(activeLayerID)
	layer.removeSelection()
	source=self.dock.lineEditSourceId.text()
	sourceExp='"'+self.dock.comboFields.currentText()+'" = \''+source+'\''
	req = QgsFeatureRequest().setFilterExpression(sourceExp)
	fea = layer.getFeatures(req)
	if fea:
		for feai in fea:	
			self.sourceFeatID=feai.id()
			layer.select(self.sourceFeatID)
			break	

      
    def selectTargetId(self, checked):

	self.dock.lineEditTargetId.setText(str(id))

        if checked:
            self.toggleSelectButton(self.dock.buttonSelectTargetId)
            self.dock.lineEditTargetId.setText("")
            self.iface.mapCanvas().setMapTool(self.targetIdEmitPoint)
        else:
            self.iface.mapCanvas().unsetMapTool(self.targetIdEmitPoint)
        
    def setTargetId(self, pt):
	if self.dock.comboLayers.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select a layer and the id field!\n')
        	return   
	if self.dock.comboFields.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select the id field!\n')
        	return
        activeLayerID = str(self.dock.comboLayers.itemData(self.dock.comboLayers.currentIndex()))
	layer = QgsMapLayerRegistry.instance().mapLayer(activeLayerID)
	layer.removeSelection()	
	width = self.iface.mapCanvas().mapUnitsPerPixel() * 2
  	rect = QgsRectangle(pt.x() - width,
                      	    pt.y() - width,
                            pt.x() + width,
                            pt.y() + width)
	layer.select(rect,True)

	selected_features = layer.selectedFeatures()
	if layer.selectedFeatureCount()>1:
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: more than one feature selected!\n')
        	return
	if layer.selectedFeatureCount()==0:
        	return
	for feat in selected_features:
		sourceID=feat[str(self.dock.comboFields.currentText())]
        self.dock.lineEditTargetId.setText(sourceID)
    
    def getLength(self):
    	activeLayerID = str(self.dock.comboLayers.itemData(self.dock.comboLayers.currentIndex()))
	layer = QgsMapLayerRegistry.instance().mapLayer(activeLayerID)
    	totalLen = 0
	count = 0
    	for feature in layer.selectedFeatures():
        	geom = feature.geometry()
        	totalLen = totalLen + geom.length()
		count = count + 1
    	return totalLen, count
    
    def run(self):
    	self.dock.textEditLog.clear()
        
	if self.dock.comboLayers.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select a layer and the id field!\n')
        	return        
	if self.dock.comboFields.currentText()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Select the id field!\n')
        	return
	if self.dock.lineEditTargetId.text()=='' or self.dock.lineEditSourceId.text()=='':
		QMessageBox.warning(self.dock, self.dock.windowTitle(),
                'WARNING: Define a source and a target id!\n')
        	return 
	QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

	final_list = []
	selection_list = []
	tol = self.dock.spinBoxTol.value()
	self.dock.textEditLog.append("Starting...")

	activeLayerID = str(self.dock.comboLayers.itemData(self.dock.comboLayers.currentIndex()))
	layer = QgsMapLayerRegistry.instance().mapLayer(activeLayerID)
	layer.removeSelection()       
	
	layer.select(self.sourceFeatID)
	provider = layer.dataProvider()
	selection_list.append(self.sourceFeatID)
	final_list.append(self.sourceFeatID)
	
	# this part based on flowTrace (modified by "Ed B"
	while selection_list:
		request = QgsFeatureRequest().setFilterFid(selection_list[0])
		feature = layer.getFeatures(request).next()
		# get list of nodes
		nodes = feature.geometry().asPolyline()
		
		#self.dock.textEditLog.append(str(self.dock.comboFields.currentText())+ ": " + feature[str(self.dock.comboFields.currentText())]+" - N. vertex: " + str(len(nodes)))
		# get end node upstream 
		up_end_node = nodes[-1]        
		#print(str(len(nodes)-1)+" "+str(up_end_node))
		# select all features around upstream coordinate using a bounding box
		rectangle = QgsRectangle(up_end_node.x() - tol, up_end_node.y() - tol, up_end_node.x() + tol, up_end_node.y() + tol)
		request = QgsFeatureRequest().setFilterRect(rectangle)
		features = layer.getFeatures(request)

		# start nodes into tolerance		
		n_start_node=0

		features = layer.getFeatures(request)
		#iterate thru requested features
		for feature in features:
			
			#get list of nodes
			nodes = feature.geometry().asPolyline()
	
			#get start node downstream
			down_start_node = nodes[0]
			#print(str(0)+" "+str(down_start_node))	
			
			#setup distance
			distance = QgsDistanceArea()				
			#get distance from up_end_node to down_start_node
			dist = distance.measureLine(up_end_node, down_start_node)
			
			if dist < tol:
				n_start_node=n_start_node+1
				#add feature to final list
				final_list.append(feature.id())
					
				#add feature to selection list to keep selecting upstream line segments
				#selection_list.append(feature.id())
										
				if feature.id() not in selection_list:
					#add feature to selection list
					selection_list.append(feature.id())
			#if feature is the target, break
			if feature[str(self.dock.comboFields.currentText())]==str(self.dock.lineEditTargetId.text()):
				break	


		if n_start_node > 1:
			self.dock.textEditLog.append("Bifurcation at end of: "+	feature[str(self.dock.comboFields.currentText())])
		if n_start_node > 1 and self.dock.checkBifurcat.isChecked():
			#remove last n_start_node items from final_list				
			final_list[len(final_list)-n_start_node:len(final_list)] = []					
			self.dock.textEditLog.append("Stop at bifurcation!")			
			break	
		if feature[str(self.dock.comboFields.currentText())]==str(self.dock.lineEditTargetId.text()):
			break		
		#remove feature from selection list
		selection_list.pop(0)
			
			
	#select features using final_list			
	layer.setSelectedFeatures(final_list)				
	
	tot = self.getLength()
	
	self.dock.textEditLog.append("")
	self.dock.textEditLog.append("N. of selected feature(s): " + str(tot[1]))
	self.dock.textEditLog.append("Length of selected feature(s): " + str(round(tot[0],3)))
	

#if feat[str(self.dock.comboFields.currentText())]==str(self.dock.lineEditTargetId.text()):
#stop=1
	QApplication.restoreOverrideCursor()
        
    def call_help(self):
	qgis.utils.showPluginHelp()
        
    def clear(self):
	self.updateComboLayers()
        self.dock.lineEditSourceId.setText("")
        self.dock.lineEditTargetId.setText("")
        self.dock.textEditLog.clear()
	QApplication.restoreOverrideCursor()

        
    def toggleSelectButton(self, button):
        selectButtons = [
            self.dock.buttonSelectSourceId,
            self.dock.buttonSelectTargetId
        ]
        for selectButton in selectButtons:
            if selectButton != button:
                if selectButton.isChecked():
                    selectButton.click()
        

