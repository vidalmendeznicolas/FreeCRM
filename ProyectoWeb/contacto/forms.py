from django import forms

class FormularioContacto(forms.Form):
    nombre = forms.CharField(
        label="Nombre completo",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre completo',
            'autocomplete': 'name'
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email'
        })
    )
    
    telefono = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+34 600 000 000',
            'autocomplete': 'tel'
        })
    )
    
    asunto = forms.CharField(
        label="Asunto",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '¿En qué podemos ayudarte?'
        })
    )
    
    contenido = forms.CharField(
        label="Mensaje",
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu mensaje aquí...',
            'rows': 5,
            'style': 'resize: vertical;'
        })
    )
    
    # Campo oculto para protección anti-spam
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=""
    )