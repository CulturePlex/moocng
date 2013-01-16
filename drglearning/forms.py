from django import forms
from django.utils.translation import ugettext_lazy as _


class ImportPlayerForm(forms.Form):
    code = forms.CharField(label=_(u"Code"), required=True)
