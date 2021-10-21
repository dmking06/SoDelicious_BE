from django import forms


class SubscribeForm(forms.Form):
    """
    Form for Subscribe.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus'  : 'True',
                                                            'placeholder': "Enter Email Address..."
                                                            }))
