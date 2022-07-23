from django import forms
from numpy import require
from .models import CSR

class CSRForm(forms.ModelForm):
    common_name = forms.CharField(max_length=264, required=True)
    validity_time = forms.IntegerField(label='(Validity period in years)')
    country_code = forms.CharField(max_length=2, required=False)
    state = forms.CharField(max_length=256, required=False)
    org_name = forms.CharField(max_length=264) 
    org_unit = forms.CharField(max_length=264)
    email = forms.EmailField()
    passphrase = forms.CharField(max_length=48, required=True, label='Enter passphrase to encrypt key :')
    class Meta:
        model = CSR
        exclude = ['csr', 'key', 'certificate']

class CSSRForm(forms.ModelForm):
    validity_time = forms.IntegerField(label='(Validity period in years)')
    class Meta:
        model = CSR
        exclude = ['key', 'certificate'] 