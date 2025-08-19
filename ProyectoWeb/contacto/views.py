from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormularioContacto
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
# Create your views here.
def contacto(request):
    if request.method == 'POST':
        formulario_contacto = FormularioContacto(request.POST)
        if formulario_contacto.is_valid():
            # Verificar honeypot (protección anti-spam)
            if formulario_contacto.cleaned_data.get('honeypot'):
                messages.error(request, 'Error en el formulario. Por favor, inténtalo de nuevo.')
                return redirect('Contacto')
            
            # Aquí puedes agregar la lógica para enviar el email
            # Por ejemplo, usando Django's send_mail o un servicio externo
            # infForm=formulario_contacto.cleaned_data
            # send_mail(infForm['asunto'], infForm['contenido'], infForm.get('email', 'nicoingenieroinf@gmail.com'), ['vidalmendeznicolas@gmail.com'],)
            ######    1º asunto  |    2º mensaje | 3º get(1º email que el user introdujo | 2º email del servidor | 3º email al que va a llegar el mensaje)
            # Obtener datos del formulario
            nombre = formulario_contacto.cleaned_data['nombre']
            email_usuario = formulario_contacto.cleaned_data['email']
            asunto = formulario_contacto.cleaned_data['asunto']
            contenido = formulario_contacto.cleaned_data['contenido']
            
            # Crear el mensaje de email
            email_message = EmailMessage(
                subject=f"Nuevo mensaje de contacto: {asunto}",
                body=f"""
                Has recibido un nuevo mensaje desde el formulario de contacto:
                
                Nombre: {nombre}
                Email: {email_usuario}
                Asunto: {asunto}
                
                Mensaje:
                {contenido}
                
                ---
                Este mensaje fue enviado desde el formulario de contacto de Esquemas Centro de Estudios.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_usuario],
                reply_to=['nicoingenieroinf@gmail.com']
            )
            
            # Envío del email
            try:
                email_message.send()
                messages.success(request, f'¡Gracias {nombre}! Tu mensaje ha sido enviado correctamente. Te responderemos pronto.')
            except Exception as e:
                messages.error(request, f'Error al enviar el email: {e}')            
           
            return redirect('Contacto')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        formulario_contacto = FormularioContacto()
    
    return render(request, "contacto/contacto.html", {"miFormulario": formulario_contacto})