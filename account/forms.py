from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter password'}))

    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm password'}))

    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Account
        fields = ['first_name', 'last_name',
                  'phone_number', 'email', 'password']

    def __init__(self, *args, **kargs):
        super(RegistrationForm, self).__init__(*args, **kargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                {'password': "Passwords don't match"}
            )


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kargs):
        super(UserForm, self).__init__(*args, **kargs)        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False,error_messages={'invalid': ('Image files only',)},widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1',
                  'address_line_2',
                  'profile_picture',
                  'city',
                  'state',
                  'country']
    def __init__(self, *args, **kargs):
        super(UserProfileForm, self).__init__(*args, **kargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
