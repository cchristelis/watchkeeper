__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '10/04/16'

import uuid
from django import forms
from django.contrib.gis.geos import Point
from healthsites.models.healthsite import Healthsite
from healthsites.tasks.regenerate_cache import regenerate_cache
from healthsites.models.assessment import (
    AssessmentCriteria, ResultOption, AssessmentGroup, HealthsiteAssessment,
    HealthsiteAssessmentEntryDropDown, HealthsiteAssessmentEntryInteger,
    HealthsiteAssessmentEntryReal)



class GroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        assessment_group = kwargs.pop('assessment_group', None)
        super(GroupForm, self).__init__(*args, **kwargs)
        criteria = AssessmentCriteria.objects.filter(
            assessment_group=assessment_group)
        for criterium in criteria:
            if criterium.result_type == 'Integer':
                self.fields[criterium.name] = forms.IntegerField(
                    required=True
                )
            elif criterium.result_type == 'Decimal':
                self.fields[criterium.name] = forms.DecimalField(
                    decimal_places=2, max_digits=9, required=True)
            elif criterium.result_type == 'DropDown':
                self.fields[criterium.name] = forms.ModelChoiceField(
                    ResultOption.objects.filter(assessment_criteria=criterium),
                    required=True)
            # elif criterium.result_type == 'MultipleChoice':
            #     self.fields[criterium.name] = forms.ModelMultipleChoiceField(
            #         queryset=ResultOption.objects.filter(
            #             assessment_criteria=criterium))


class Group(object):
    def __init__(self, name, group_form):
        self.name = name
        self.group_form = group_form


class AssessmentForm(forms.Form):
    name = forms.CharField(max_length=100, min_length=3)
    latitude = forms.CharField()
    longitude = forms.CharField()
    reference_url = forms.URLField(max_length=200, required=False)
    reference_file = forms.FileField(required=False)

    def save_form(self):
        name = self.cleaned_data.get('name')
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')

        geom = Point(
            float(latitude), float(longitude)
        )
        # find the healthsite
        try:
            healthsite = Healthsite.objects.get(name=name, point_geometry=geom)
            self.create_assessment(healthsite)
        except Healthsite.DoesNotExist:
            # generate new uuid
            tmp_uuid = uuid.uuid4().hex
            healthsite = Healthsite(name=name, point_geometry=geom, uuid=tmp_uuid, version=1)
            healthsite.save()
            # regenerate_cache.delay()
            self.create_assessment(healthsite)

    def create_assessment(self, healthsite):
        if 'update_button' in self.data:
            healthsite_assessment = HealthsiteAssessment.objects.filter(
                healthsite=healthsite,
                current=True)
        else:
            for healthsite_assessment in HealthsiteAssessment.objects.all():
                healthsite_assessment.current = False
                healthsite_assessment.save()
            healthsite_assessment = HealthsiteAssessment(
                healthsite=healthsite)
            healthsite_assessment.save()

        criteria = AssessmentCriteria.objects.all()
        for criterium in criteria:
            entry_class = None
            selected_option = None
            if criterium.result_type == 'Integer':
                entry_class = HealthsiteAssessmentEntryInteger
                selected_option = self.cleaned_data.get(
                    chriterium.name)
            elif criterium.result_type == 'Decimal':
                entry_class = HealthsiteAssessmentEntryReal
                selected_option = self.cleaned_data.get(
                    chriterium.name)
            elif criterium.result_type == 'DropDown':
                entry_class = HealthsiteAssessmentEntryDropDown
                selected_option = self.cleaned_data.get(
                    criterium.name)
            # elif criterium.result_type == 'MultipleChoice':
            #     self.fields[criterium.name] = forms.ModelMultipleChoiceField(
            #         queryset=ResultOption.objects.filter(
            #             assessment_criteria=criterium))
            if not entry_class or not selected_option:
                continue
            try:
                entry = entry_class.objects.get(
                    healthsite_assessment=healthsite_assessment,
                    assessment_criteria=criterium)
                entry.selected_option = selected_option
                entry.save()
            except entry_class.DoesNotExist:
                entry_class.objects.create(
                    healthsite_assessment=healthsite_assessment,
                    assessment_criteria=criterium,
                    selected_option=selected_option)

    def groups(self):
        groups = [Group('General', self)]
        for assessment_group in AssessmentGroup.objects.all():
            group_form = GroupForm(assessment_group=assessment_group)
            group = Group(assessment_group.name, group_form)
            groups.append(group)
        return groups
