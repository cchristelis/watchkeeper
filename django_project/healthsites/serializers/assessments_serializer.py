__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '17/05/16'

from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis
# from healthsites.models.assessment import (
#     HealthsiteAssessment, AssessmentGroup, AssessmentCriteria)


class HealthsiteSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=100)
    point_geometry = serializers_gis.GeometryField()


class AssessmentSerializer(serializers.Serializer):

    healthsite = HealthsiteSerializer()
