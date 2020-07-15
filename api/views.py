# coding=utf-8
""""
    API views fro eleprofile app.
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2020-07-14'
__copyright__ = 'Copyright 2015 - 2020, Gis3w'

from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from qgis.core import QgsFeatureRequest
from core.api.base.views import G3WAPIView
from core.utils.qgisapi import get_qgis_layer, get_qgs_project
from eleprofile.models import EleProDTM

from eleprofile.vendor.qprof.gis_utils.qgs_tools import \
    multipolyline_to_xytuple_list2, \
    polyline_to_xytuple_list, \
    raster_qgis_params, \
    QGisRasterParameters

from eleprofile.vendor.qprof.gis_utils.features import \
    xytuple_list_to_Line, \
    xytuple_l2_to_MultiLine, \
    MultiLine

from eleprofile.utils.profile import topoline_from_dem


class ProfileCalculateApiView(G3WAPIView):
    """
    Make calculation
    """

    # authentication_classes = (
    #     CsrfExemptSessionAuthentication,
    # )
    #
    # permission_classes = (
    #     MakeCDUPermission,
    # )

    def get(self, request, **kwargs):

        # try to use qprof api
        # ====================

        # try to load layer
        try:
            epp = EleProDTM.objects.get(pk=kwargs['eleprodtm_pk'])
            layer = epp.layers.filter(
                qgs_layer_id=kwargs['qgs_layer_id'])[0]
            dem = epp.dtm_layer
        except ObjectDoesNotExist as e:
            raise e
        except IndexError as e:
            raise

        # try to get qgis_layer
        qgis_project = get_qgs_project(dem.project.qgis_file.path)
        qgis_dem = get_qgis_layer(dem)
        qgis_layer = get_qgis_layer(layer)

        # get single feature
        feature = qgis_layer.getFeature(kwargs['fid'])
        geom = feature.geometry()
        if not geom:
            raise Exception('Fid not found into layer')

        if geom.isMultipart():
            line = multipolyline_to_xytuple_list2(geom.asMultiPolyline())  # typedef QVector<QgsPolyline>
            # now it's a list of list of (x,y) tuples
            path_line = xytuple_l2_to_MultiLine(line).to_line()

        else:
            line = polyline_to_xytuple_list(geom.asPolyline())  # typedef QVector<QgsPointXY>
            path_line = xytuple_list_to_Line(line)

        multi_path_line = MultiLine([path_line]).to_line().remove_coincident_points()

        # TODO: check for reproject layer by project crs

        # line resampled by sample distance
        resampled_line = multi_path_line.densify_2d_line(epp.dtm_delta)

        profile = topoline_from_dem(
            resampled_line,
            True,
            qgis_project.crs(),
            qgis_dem,
            QGisRasterParameters(*raster_qgis_params(qgis_dem)),
            epp.dtm_delta
        )

        return JsonResponse({'profile': profile})