# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerSorting
                                 A QGIS plugin
 Sorts QGIS layers according to geometry type
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-24
        copyright            : (C) 2021 by Kartoza
        email                : vermeulendivan@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LayerSorting class from file LayerSorting.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .layer_sorting import LayerSorting
    return LayerSorting(iface)
