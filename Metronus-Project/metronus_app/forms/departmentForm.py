from django import forms

class DepartmentForm(forms.Form):
    name = forms.CharField(max_length=30)
    department_id=forms.IntegerField()
