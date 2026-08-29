from django import forms

from .models import PlatformOrganization
from .services import EDITABLE_FIELDS
from .validators import normalize_cnpj, validate_cnpj


class PlatformOrganizationAdminForm(forms.ModelForm):
    cnpj = forms.CharField(label="CNPJ", max_length=18, required=False)
    expected_version = forms.IntegerField(widget=forms.HiddenInput, required=False, initial=0)

    class Meta:
        model = PlatformOrganization
        fields = (*EDITABLE_FIELDS, "expected_version")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["expected_version"].initial = self.instance.version

    def clean_cnpj(self):
        value = normalize_cnpj(self.cleaned_data.get("cnpj"))
        validate_cnpj(value)
        return value
