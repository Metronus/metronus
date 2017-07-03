from django import forms
from django.utils.translation import ugettext_lazy as _
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.core.validators import MinValueValidator, MaxValueValidator

class TaskForm(forms.Form):
    """Form for Task model class"""
    name = forms.CharField(label=_("name"), max_length=30, initial="")
    description = forms.CharField(label=_("description"), max_length=200, initial="")
    task_id = forms.IntegerField(widget=forms.HiddenInput(), initial="0")
    project_id = forms.ModelChoiceField(queryset=Project.objects.all())
    department_id = forms.ModelChoiceField(queryset=Department.objects.all())
    production_goal = forms.FloatField(label=_("production_goal"), required=False, initial="", validators=[MinValueValidator(0.0), MaxValueValidator(1000000.0)])
    goal_description = forms.CharField(label=_("goal_description"), max_length=100, required=False, initial="")

    price_per_unit = forms.FloatField(label=_("price_per_unit"), required=False, initial="", validators=[MinValueValidator(0.0), MaxValueValidator(1000000.0)])
    price_per_hour = forms.FloatField(label=_("price_per_hour"), required=False, initial="", validators=[MinValueValidator(0.0), MaxValueValidator(1000000.0)])
