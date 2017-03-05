from django import forms

class ProjectForm(forms.Form):
    name = forms.CharField(max_length=30)
    project_id=forms.IntegerField()