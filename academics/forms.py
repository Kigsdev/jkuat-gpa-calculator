from django import forms
from .models import Result, Unit


class ResultForm(forms.ModelForm):
    """Form for entering/updating grades."""
    class Meta:
        model = Result
        fields = ['student', 'unit', 'score']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'placeholder': 'Score (0-100)'
            }),
        }


class ProjectionForm(forms.Form):
    """Form for GPA projection calculations."""
    HONORS_CHOICES = [
        (70, 'First Class Honours (70%)'),
        (60, 'Second Class Honours - Upper Division (60%)'),
        (50, 'Second Class Honours - Lower Division (50%)'),
        (40, 'Pass (40%)'),
    ]
    
    target_honors = forms.ChoiceField(
        choices=HONORS_CHOICES,
        widget=forms.RadioSelect(),
        label="Target Honors Level"
    )
    
    remaining_units = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of remaining units'
        })
    )
