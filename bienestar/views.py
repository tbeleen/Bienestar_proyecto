from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Perfil
from datetime import date
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    Habito,
    RegistroEmocion,
    RegistroHabito,
    Diario,
    Emocion
)

User = get_user_model()


def registro_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        genero = request.POST.get("genero")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")

        # 🔒 Validar dominio DUOC
        if not email.endswith("@duocuc.cl"):
            messages.error(request, "Debes usar tu correo institucional @duocuc.cl")
            return redirect("registro")

        # 🔒 Validar email único
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está registrado")
            return redirect("registro")

        # 🔒 Validar contraseñas iguales
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect("registro")

        # 🔒 Validar fecha realista
        try:
            fecha_nac = date.fromisoformat(fecha_nacimiento)
        except ValueError:
            messages.error(request, "Fecha de nacimiento inválida")
            return redirect("registro")

        hoy = date.today()
        edad = hoy.year - fecha_nac.year - (
            (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day)
        )

        if fecha_nac.year < 1920:
            messages.error(request, "Fecha de nacimiento no válida")
            return redirect("registro")

        if edad < 18:
            messages.error(request, "Debes ser mayor de 18 años")
            return redirect("registro")

        # ✅ Crear usuario
        user = User.objects.create_user(
            email=email,
            password=password1
        )

        # ✅ Crear perfil
        Perfil.objects.create(
            usuario=user,
            genero=genero,
            fecha_nacimiento=fecha_nac
        )

        login(request, user)
        messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
        return redirect("login")

    return render(request, "registro.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "login.html")

@login_required
def dashboard_view(request):
    # Obtener emociones desde la BD (o usar datos de ejemplo si no tienes BD)
    emociones = Emocion.objects.all()
    
    # Si no tienes BD aún, usa esto temporalmente:
    # emociones = [
    #     {'id': 1, 'nombre': 'Feliz'},
    #     {'id': 2, 'nombre': 'Triste'},
    #     {'id': 3, 'nombre': 'Emocionado/a'},
    #     {'id': 4, 'nombre': 'Angustiado/a'},
    #     {'id': 5, 'nombre': 'Decepcionado/a'},
    #     {'id': 6, 'nombre': 'Extraño/a'},
    # ]

    if request.method == "POST":
        # ===============================
        # GUARDAR EMOCIÓN
        # ===============================
        if "guardar_emocion" in request.POST:
            emocion_id = request.POST.get("emocion")
            intensidad = request.POST.get("intensidad")
            comentario = request.POST.get("comentario", "")

            # Validaciones
            if not emocion_id or emocion_id == "":
                messages.error(request, "Por favor selecciona una emoción")
            elif not intensidad or intensidad == "":
                messages.error(request, "Por favor selecciona una intensidad")
            else:
                try:
                    # Descomentar cuando tengas BD lista:
                    RegistroEmocion.objects.create(
                        usuario=request.user,
                        emocion_id=int(emocion_id),
                        intensidad=int(intensidad),
                        comentario=comentario
                    )
                    messages.success(request, "¡Emoción registrada exitosamente! 💚")
                    
                    # Para modo demo sin BD:
                    # messages.info(request, "Modo demo - La emoción no se guardó (sin BD)")
                    
                except Exception as e:
                    messages.error(request, f"Error al guardar: {str(e)}")

            return redirect("dashboard")

    return render(request, "dashboard.html", {
        "emociones": emociones,
    })

@login_required
def registro_habitos(request):
    habitos = Habito.objects.all()

    if request.method == "POST":
        habito_id = request.POST.get("habito")
        valor = request.POST.get("valor")

        if habito_id and valor:
            habito = Habito.objects.filter(id=habito_id).first()

            if habito:
                RegistroHabito.objects.create(
                    usuario=request.user,
                    habito=habito,
                    fecha=date.today(),
                    valor=int(valor)
                )

        return redirect("registro_habitos")

    return render(request, "habitos.html", {
        "habitos": habitos
    })

@login_required
def estadistica_view(request):
    return render(request, "estadistica.html")


@login_required
def recursos_view(request):
    return render(request, "recursos.html")


@login_required
def diario(request):
    if request.method == 'POST':
        texto = request.POST.get('contenido')

        if texto:
            Diario.objects.create(
                usuario=request.user,
                contenido=texto
            )
            return redirect('diario')  # vuelve al diario

    return render(request, 'diario.html')


@login_required
def perfil(request):
    return render(request, 'perfil.html')