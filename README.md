# layer-sorting
Sort all layers open in QGIS according to geometry in the QGIS layer list: points, lines and then polygons. Rasters will be sorted to the bottom of the list.
Group and subgroup sorting can also be performed, using either feature count or alphabetically. An option is also avaiable to remove groups.

## Installation
1) Download the zip file stored here: https://github.com/vermeulendivan/layer-sorting/tree/main/plugin:
   1) Use the QGIS plugin installer to install the plugin: Plugins > Manage and install plugins;
   2) Select the Install from ZIP tab; and
   3) Select the zip file and click Install Plugin.
2) Make a clone using the git:
   1) git clone https://github.com/vermeulendivan/layer-sorting;
   2) Go to the QGIS plugin folder: C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins;
   3) Create a folder "layer_sorting"; and
   4) Paste the cloned/downloaded files into the folder.

## Plugin information
Sorting will be done as follows:
1) Points;
2) Lines;
3) Polygons; and
4) Rasters.

Opening the plugin:
1) Go to Plugins > Layer sorting > Layer sorting;
2) Click on the layer sorting toolbar button:
![Icon](https://github.com/vermeulendivan/layer-sorting/blob/main/data/icon.png)

The plugin window:

![Plugin](https://github.com/vermeulendivan/layer-sorting/blob/main/data/plugin_window.png)

The user has two parameters to set:
1) Sort type:
   1) Alphabetic: Layers in the root, groups, and subgroups will be sorted alphabetically (A to Z);
   2) Feature count: Sorts the layers according to feature count, with the layer with the least number of features at the top.
2) Group by:
   1) Keep groups: All groups and subgroups will be used, with sorting applied within each of the groups;
   2) Remove groups: All layers within groups and subgroups will be moved to the root, and the groups will be removed.

Sort type will be applied to each type of geometry, and rasters individually. Geometry sorting is therefore preserved.
