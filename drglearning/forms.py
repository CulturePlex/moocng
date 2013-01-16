from django import forms

from drglearning.models import Player


class ImportPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ("code", )
