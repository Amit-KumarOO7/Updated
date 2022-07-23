from django import forms
from .models import RootCAIM

class RootCAIMForm(forms.ModelForm):
    common_name = forms.CharField(max_length=264, required=True)
    validity_time = forms.IntegerField(label='(Validity period in years)')
    country_code = forms.CharField(max_length=2, required=False)
    state = forms.CharField(max_length=256, required=False)
    org_name = forms.CharField(max_length=264) 
    org_unit = forms.CharField(max_length=264)
    class Meta:
        model = RootCAIM
        exclude = ['certificate', 'key']