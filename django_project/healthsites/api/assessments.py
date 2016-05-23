__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '17/05/16'

from rest_framework.response import Response
from rest_framework import authentication, permissions

from rest_framework.decorators import api_view


from healthsites.models.assessment import HealthsiteAssessment
from healthsites.serializers.assessments_serializer import AssessmentSerializer


@api_view()
def assessments(request):
    healthsite_assessments = HealthsiteAssessment.objects.filter(current=True)
    return Response(AssessmentSerializer(healthsite_assessments))


@api_view()
def assessments_details(request, assessment_id):

    return Response({"message": "Hello, world!"})