from django import forms
from recipes.models import Recipe, Image


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'prep_time', 'cook_time', 'total_time',
                  'servings', 'ingredients', 'steps', 'nutrition']
        widgets = {
            'ingredients': forms.Textarea(attrs={'rows': 5, 'cols': 60}),
            'steps': forms.Textarea(attrs={'rows': 5, 'cols': 60}),
            'nutrition': forms.Textarea(attrs={'rows': 2, 'cols': 60}),
            }
        labels = {
            'name': 'Recipe name',
            'prep_time': "Prep time (mins)",
            'cook_time': "Cook time (mins)",
            'total_time': "Total time (mins)",
            }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class SubscribeForm(forms.Form):
    """
    Form for Subscribe.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus'  : 'True',
                                                            'placeholder': "Enter Email Address..."
                                                            }))
