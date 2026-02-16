from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Perfil
from datetime import date
from django.utils import timezone
from .models import (
    EstadoAnimo,
    RegistroEstadoAnimo,
    Habito,
    RegistroHabito
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

from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    estados_animo = EstadoAnimo.objects.all()
    habitos = Habito.objects.all()

    if request.method == "POST":

        # ===============================
        # GUARDAR ESTADO DE ÁNIMO
        # ===============================
        if "guardar_animo" in request.POST:
            estado_id = request.POST.get("estado_animo")

            if estado_id:
                estado = EstadoAnimo.objects.filter(id=estado_id).first()
                if estado:
                    RegistroEstadoAnimo.objects.create(
                        usuario=request.user,
                        estado_animo=estado
                    )

            return redirect("dashboard")

        # ===============================
        # GUARDAR HÁBITO
        # ===============================
        if "guardar_habito" in request.POST:
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

            return redirect("dashboard")

    context = {
        "estados_animo": estados_animo,
        "habitos": habitos
    }

    return render(request, "dashboard.html", context)