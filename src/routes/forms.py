"""Validate the HTTP login form without revealing account existence."""

from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Adresse e-mail",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"autocomplete": "username", "autocapitalize": "none"}
        ),
    )
    password = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
