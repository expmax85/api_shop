from django import forms
from django.forms import FileInput

from goods.models import ProductImportFile


class ImportForm(forms.ModelForm):
    file = forms.FileField(label='Your csv file', required=True,
                           widget=FileInput(attrs={
                               'class': 'import_row',
                               'accept': '.csv',
                               }))

    class Meta:
        model = ProductImportFile
        fields = ['file', ]
