from django import forms
from .models import Result, Unit


class ResultForm(forms.ModelForm):
    """Form for entering/updating grades with validation."""
    class Meta:
        model = Result
        fields = ['student', 'unit', 'score']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.01,
                'placeholder': 'Score (0-100)',
                'required': True
            }),
        }
    
    def clean_score(self):
        """Validate score is between 0 and 100."""
        score = self.cleaned_data.get('score')
        if score is not None:
            if score < 0 or score > 100:
                raise forms.ValidationError('Score must be between 0 and 100.')
        return score
    
    def clean(self):
        """Validate student-unit uniqueness."""
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        unit = cleaned_data.get('unit')
        
        if student and unit:
            # Check if result already exists for this student-unit combination
            existing = Result.objects.filter(student=student, unit=unit)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'{student.user.get_full_name()} already has a grade for {unit.code}.'
                )
        
        return cleaned_data


class ProjectionForm(forms.Form):
    """Form for GPA projection calculations with validation."""
    HONORS_CHOICES = [
        (70, 'First Class Honours (70%)'),
        (60, 'Second Class Honours - Upper Division (60%)'),
        (50, 'Second Class Honours - Lower Division (50%)'),
        (40, 'Pass (40%)'),
    ]
    
    target_honors = forms.ChoiceField(
        choices=HONORS_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Target Honors Level"
    )
    
    remaining_units = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of remaining units',
            'min': 1,
            'max': 20
        })
    )
    
    def clean_remaining_units(self):
        """Validate remaining units."""
        units = self.cleaned_data.get('remaining_units')
        if units and (units < 1 or units > 20):
            raise forms.ValidationError('Remaining units must be between 1 and 20.')
        return units
    
    def clean_target_honors(self):
        """Validate target honors selection."""
        target = self.cleaned_data.get('target_honors')
        if target:
            try:
                int(target)
            except ValueError:
                raise forms.ValidationError('Invalid target honors selection.')
        return target
