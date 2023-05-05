from django import forms


class login(forms.Form):
    user_name = forms.CharField(label="User name", max_length=30)
    password = forms.PasswordInput(label="Password", min_length=8)
