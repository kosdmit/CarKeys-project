from django import forms

from app_ecommerce.models import Customer


class CustomerForm(forms.ModelForm):
    name = forms.CharField(
        label='Имя:',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    phone_number = forms.CharField(
        label='Телефон:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'value': '+7',
                                      'placeholder': '+7'}),
        required=False
    )

    class Meta:
        model = Customer
        fields = ['name', 'phone_number']