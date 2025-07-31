from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Application, CustomUser, EducationalQualification, Job

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company_name', 'location', 'description']

from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        widget=forms.FileInput(attrs={'accept': 'application/pdf'}),
        label="Resume (PDF only)"
    )

    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # File extension check
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Resume file must be in PDF format.")
            # MIME type check (for extra security)
            if hasattr(resume, 'content_type') and resume.content_type != 'application/pdf':
                raise forms.ValidationError("Uploaded file is not a valid PDF.")
        return resume



# class ApplicationForm(forms.ModelForm):
# 
    # resume = forms.FileField(
        # widget=forms.FileInput(attrs={'accept': 'application/pdf'}),
        # label="Resume (PDF only)"
    # )
    # class Meta:
        # model = Application
        # fields = ['resume', 'cover_letter']
# 
    # def clean_resume(self):
        # resume = self.cleaned_data.get('resume')
        # if resume:
            # if not resume.name.lower().endswith('.pdf'):
                # raise forms.ValidationError("Resume file must be in PDF format.")
            # Optionally, check MIME type:
            # if resume.content_type != 'application/pdf':
                # raise forms.ValidationError("Uploaded file is not a valid PDF.")
        # return resume
# 


# class ApplicationForm(forms.ModelForm):
    # class Meta:
        # model = Application
        # fields = ['resume', 'cover_letter']


class EducationalQualificationForm(forms.ModelForm):
    class Meta:
        model = EducationalQualification
        fields = ['degree', 'result', 'institution', 'year']    