from django import forms
from home.models import CodeSubmission, Profile
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import test_cases, problems

class ProblemsForm(forms.ModelForm):
    class Meta:
        model = problems
        fields = ['prblmname', 'statement','sip','sop', 'difficulty']
        widgets = {
            'prblmname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter problem name'}),
            'statement': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter problem statement'}),
            'sip': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Sample Input Format'}),
            'sop': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Sample Output Format'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
        }

class TestCasesForm(forms.ModelForm):
    class Meta:
        model = test_cases
        fields = ['Test_Name', 'input_data', 'output_data']
        widgets = {
            'Test_Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter test case name'}),
            'input_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Input Data in One line for one case and separate using commas'}),
            'output_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Output Data in One line for one case and separate using commas'}),
        }

class TestCasesFormWID(forms.ModelForm):
    class Meta:
        model = test_cases
        fields = ['Test_Name', 'input_data', 'output_data', 'prblm_id']
        widgets = {
            'Test_Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter test case name'}),
            'input_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Input Data in One line for one case and separate using commas'}),
            'output_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Output Data in One line for one case and separate using commas'}),
            'prblm_id': forms.Select(attrs={'class': 'form-control'}),
        }



LANGUAGE_CHOICES = [
    ("py", "Python"),
    ("c", "C"),
    ("cpp", "C++"),
]

class CodeSubmissionForm(forms.ModelForm):
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES)
    code = forms.CharField(
        required=False,  # Disable browser-side required validation
        widget=forms.Textarea(attrs={
            'placeholder': 'Write Code here',
            'class': 'code-editor',  # For CodeMirror targeting
            'rows': 20,
            'cols': 80,
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].widget.attrs.update({'class': 'custom-select'})
    
    class Meta:
        model = CodeSubmission
        fields = ["language", "code", "input_data"]


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    # avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    class Meta:
        model = Profile
        fields = ['bio']

