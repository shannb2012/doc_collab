from django import forms

class PinForm(forms.Form):
    pin = forms.IntegerField()
