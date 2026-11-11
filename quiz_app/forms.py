from django import forms
from django.contrib.auth.models import User
from .models import Participant, Moderator, Quiz

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    ROLE_CHOICES = [('participant', 'Participant'), ('moderator', 'Moderator')]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'student_class', 'age', 'gender', 'institution']

class ModeratorForm(forms.ModelForm):
    class Meta:
        model = Moderator
        fields = ['name', 'department']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
