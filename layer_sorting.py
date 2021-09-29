<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerSorting
                                 A QGIS plugin
 Sorts QGIS layers according to geometry type
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-09-24
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Kartoza
        email                : vermeulendivan@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsProject, QgsMapLayerType, QgsGeometry, QgsWkbTypes, QgsLayerTreeGroup, QgsLayerTreeLayer

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .layer_sorting_dialog import LayerSortingDialog
import sys, os.path


class LayerSorting:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LayerSorting_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Layer sorting')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LayerSorting', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/layer_sorting/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Layer sorting'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Layer sorting'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = LayerSortingDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # OK has been pressed
        if result:
            sort_type = self.dlg.cbSortType.currentText()
            grouping_type = self.dlg.cbGrouping.currentText()
            project_root = QgsProject.instance().layerTreeRoot()
            list_tree_layers = project_root.children()
            
            list_groups = []  # Stores the QgsLayerTreeGroup objects
            dict_layers = {}  # Store layers according to geometry type
            for tree_layer in list_tree_layers:  # Loops through all of the layers
                if type(tree_layer) == QgsLayerTreeLayer:
                    layer = tree_layer.layer()  # QgsVectorLayer object
                    
                    # Reads all of the information from the layer objects
                    layer_id, layer_type, layer_name, layer_feature_cnt, layer_geom = self.get_layer_info(tree_layer, layer)
                
                    # Stores the information for a layer in a dictionary
                    # Lowercase used for layer name for when alphabetic sorting is performed
                    if layer_geom not in dict_layers:
                        dict_layers.update({layer_geom:[[layer_name.lower(), layer_id, tree_layer, layer_type, layer_feature_cnt]]})
                    else:
                        dict_layers[layer_geom].append([layer_name.lower(), layer_id, tree_layer, layer_type, layer_feature_cnt])
                elif type(tree_layer) == QgsLayerTreeGroup:
                    if grouping_type == "Remove groups":
                        group_layers = tree_layer.findLayers()
                        list_groups.append(tree_layer)
                        
                        for group_layer in group_layers:
                            layer = group_layer.layer()  # QgsVectorLayer object
                        
                            # Reads all of the information from the layer objects
                            layer_id, layer_type, layer_name, layer_feature_cnt, layer_geom = self.get_layer_info(group_layer, layer)
                        
                            # Stores the information for a layer in a dictionary
                            # Lowercase used for layer name for when alphabetic sorting is performed
                            if layer_geom not in dict_layers:
                                dict_layers.update({layer_geom:[[layer_name.lower(), layer_id, group_layer, layer_type, layer_feature_cnt]]})
                            else:
                                dict_layers[layer_geom].append([layer_name.lower(), layer_id, group_layer, layer_type, layer_feature_cnt])
                        #list_groups.append()
                    elif grouping_type == "Keep groups":
                        print("keep groups")
                else:
                    print("UNKNOWN LAYER TYPE")
            
            # Performs sorting for each geometry alphabetically or by feature count
            rasters, polygons, polylines, points = self.sort_type_groups(dict_layers, sort_type)
            
            # Adds the reordered layers to QGIS
            # Removes the no longer needed unordered layers from QGIS
            self.update_layers(project_root, rasters, polygons, polylines, points)
            
            if grouping_type == "Remove groups":
                self.remove_groups(project_root, list_groups)


    # Removes all group layers (QgsLayerTreeGroup) provided in a list
    def remove_groups(self, project_root, groups):
        for group in groups:
            project_root.removeChildNode(group)


    # Gets information of the layer from the tree_layer and layer objects
    # Layer ID, type, name, feature count, and geometry type
    def get_layer_info(self, tree_layer, layer):
        layer_id = tree_layer.layerId()
        layer_type = self.get_layer_type(layer)  # Raster or vector
                
        # Check whether the layer is vector or raster
        if layer_type == "vector":
            layer_name = tree_layer.name()
            layer_feature_cnt = layer.featureCount()
            layer_geom = self.get_geometry_type(layer)
        elif layer_type == "raster":
            layer_name = tree_layer.name()
            layer_feature_cnt = None
            layer_geom = "pixel"
        
        return layer_id, layer_type, layer_name, layer_feature_cnt, layer_geom


    # Determines the layer type and returns a string
    def get_layer_type(self, layer):
        layer_type = layer.type()
        if layer_type == QgsMapLayerType.RasterLayer:
            return "raster"
        elif layer_type == QgsMapLayerType.VectorLayer:
            return "vector"
        
        return "UNKNOWN LAYER TYPE"
    
    # Gets the geometry type from a layer feature
    def get_geometry_type(self, layer):
        geom = layer.geometryType()
        if geom == 0:  # Point vectors
            return "point"
        elif geom == 1:  # Polyline vectors
            return "line"
        elif geom == 2:  # Polygon vectors
            return "polygon"
            
        return "UNKNOWN GEOMETRY TYPE"
    
    
    # Adds the sorted layers to QGIS
    # Points, polylines, polygons, and then rasters
    def update_layers(self, project_root, rasters, polygons, polylines, points):
        # Adds reordered rasters to QGIS
        for raster in rasters:
                orig_layer_tree = raster[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)
        
        # Adds reordered polygons to QGIS
        for polygon in polygons:
                orig_layer_tree = polygon[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)
        
        # Adds reordered polylines to QGIS
        for line in polylines:
                orig_layer_tree = line[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)
        
        # Adds reordered points to QGIS
        for point in points:
                orig_layer_tree = point[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)


    # Sorts the layers for each geometry type
    # Two cases: sorts according to layer name (alphabetically) or feature count
    def sort_type_groups(self, dict_layers, sort_type):
        # Alphabetical sorting. A to Z
        if sort_type == "Alphabetic":
            rasters = sorted(dict_layers.get("pixel"), key=lambda x: x[0], reverse=True)
            polygons = sorted(dict_layers.get("polygon"), key=lambda x: x[0], reverse=True)
            polylines = sorted(dict_layers.get("line"), key=lambda x: x[0], reverse=True)
            points = sorted(dict_layers.get("point"), key=lambda x: x[0], reverse=True)
            
            return rasters, polygons, polylines, points
        # Feature count sorting. Low to high
        elif sort_type == "Feature count":
            rasters = sorted(dict_layers.get("pixel"), key=lambda x: x[0], reverse=True)
            polygons = sorted(dict_layers.get("polygon"), key=lambda x: x[4], reverse=True)
            polylines = sorted(dict_layers.get("line"), key=lambda x: x[4], reverse=True)
            points = sorted(dict_layers.get("point"), key=lambda x: x[4], reverse=True)
        
            return rasters, polygons, polylines, points
=======
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerSorting
                                 A QGIS plugin
 Sorts QGIS layers according to geometry type
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-09-24
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Kartoza
        email                : vermeulendivan@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsProject, QgsMapLayerType, QgsGeometry, QgsWkbTypes

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .layer_sorting_dialog import LayerSortingDialog
import sys, os.path


class LayerSorting:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LayerSorting_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Layer sorting')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LayerSorting', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/layer_sorting/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Layer sorting'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Layer sorting'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = LayerSortingDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # OK has been pressed
        if result:
            sort_type = self.dlg.cbSortType.currentText()
            project_root = QgsProject.instance().layerTreeRoot()
            list_tree_layers = project_root.children()
            
            list_layers = []  # Stores the QgsVectorLayers
            dict_layers = {}  # Store layers according to geometry type
            for tree_layer in list_tree_layers:  # Loops through all of the layers
                layer = tree_layer.layer()  # QgsVectorLayer object
                
                # Reads all of the information from the layer objects
                layer_id, layer_type, layer_name, layer_feature_cnt, layer_geom = self.get_layer_info(tree_layer, layer)
            
                # Stores the information for a layer in a dictionary
                # Lowercase used for layer name for when alphabetic sorting is performed
                if layer_geom not in dict_layers:
                    dict_layers.update({layer_geom:[[layer_name.lower(), layer_id, tree_layer, layer_type, layer_feature_cnt]]})
                else:
                    dict_layers[layer_geom].append([layer_name.lower(), layer_id, tree_layer, layer_type, layer_feature_cnt])
            
            # Performs sorting for each geometry alphabetically or by feature count
            rasters, polygons, polylines, points = self.sort_type_groups(dict_layers, sort_type)
            
            # Adds the reordered layers to QGIS
            # Removes the no longer needed unordered layers from QGIS
            self.update_layers(project_root, rasters, polygons, polylines, points)
        

    # Gets information of the layer from the tree_layer and layer objects
    # Layer ID, type, name, feature count, and geometry type
    def get_layer_info(self, tree_layer, layer):
        layer_id = tree_layer.layerId()
        layer_type = self.get_layer_type(layer)  # Raster or vector
                
        # Check whether the layer is vector or raster
        if layer_type == "vector":
            layer_name = tree_layer.name()
            layer_feature_cnt = layer.featureCount()
            layer_geom = self.get_geometry_type(layer)
        elif layer_type == "raster":
            layer_name = tree_layer.name()
            layer_feature_cnt = None
            layer_geom = "pixel"
        
        return layer_id, layer_type, layer_name, layer_feature_cnt, layer_geom


    # Determines the layer type and returns a string
    def get_layer_type(self, layer):
        layer_type = layer.type()
        if layer_type == QgsMapLayerType.RasterLayer:
            return "raster"
        elif layer_type == QgsMapLayerType.VectorLayer:
            return "vector"
        
        return "UNKNOWN LAYER TYPE"
    
    # Gets the geometry type from a layer feature
    def get_geometry_type(self, layer):
        geom = layer.geometryType()
        if geom == 0:  # Point vectors
            return "point"
        elif geom == 1:  # Polyline vectors
            return "line"
        elif geom == 2:  # Polygon vectors
            return "polygon"
            
        return "UNKNOWN GEOMETRY TYPE"
    
    
    # Adds the sorted layers to QGIS
    # Points, polylines, polygons, and then rasters
    def update_layers(self, project_root, rasters, polygons, polylines, points):
        # Adds reordered rasters to QGIS
        for raster in rasters:
                orig_layer_tree = raster[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)
        
        # Adds reordered polygons to QGIS
        for polygon in polygons:
                orig_layer_tree = polygon[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)
        
        # Adds reordered polylines to QGIS
        for line in polylines:
                orig_layer_tree = line[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)
        
        # Adds reordered points to QGIS
        for point in points:
                orig_layer_tree = point[2]
                clone_layer_tree = orig_layer_tree.clone()
                
                project_root.insertChildNodes(0, [clone_layer_tree])
                project_root.removeChildNode(orig_layer_tree)


    # Sorts the layers for each geometry type
    # Two cases: sorts according to layer name (alphabetically) or feature count
    def sort_type_groups(self, dict_layers, sort_type):
        # Alphabetical sorting. A to Z
        if sort_type == "Alphabetic":
            rasters = sorted(dict_layers.get("pixel"), key=lambda x: x[0], reverse=True)
            polygons = sorted(dict_layers.get("polygon"), key=lambda x: x[0], reverse=True)
            polylines = sorted(dict_layers.get("line"), key=lambda x: x[0], reverse=True)
            points = sorted(dict_layers.get("point"), key=lambda x: x[0], reverse=True)
            
            return rasters, polygons, polylines, points
        # Feature count sorting. Low to high
        elif sort_type == "Feature count":
            rasters = sorted(dict_layers.get("pixel"), key=lambda x: x[0], reverse=True)
            polygons = sorted(dict_layers.get("polygon"), key=lambda x: x[4], reverse=True)
            polylines = sorted(dict_layers.get("line"), key=lambda x: x[4], reverse=True)
            points = sorted(dict_layers.get("point"), key=lambda x: x[4], reverse=True)
        
            return rasters, polygons, polylines, points
>>>>>>> origin
