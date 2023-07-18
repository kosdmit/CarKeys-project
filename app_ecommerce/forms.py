from django import forms

from app_ecommerce.models import Customer, Message


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


class MessageForm(forms.ModelForm):
    text = forms.CharField(
        label='Сообщение:',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': '3',
                                     'placeholder': 'Добавьте дополнительную информацию'})
    )

    class Meta:
        model = Message
        fields = ['text']