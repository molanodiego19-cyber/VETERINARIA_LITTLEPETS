from django.shortcuts import render, redirect
from .forms import *

def crear_horario(request):

    if request.method == 'POST':
        form = HorarioVeterinarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = HorarioVeterinarioForm()

    return render(request,'crear_horario.html',{'form':form})

def crear_especialidad(request):

    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = EspecialidadForm()

    return render(request,'crear_especialidad.html',{'form':form})

def crear_bloqueo_agenda(request):

    if request.method == 'POST':
        form = BloqueoAgendaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BloqueoAgendaForm()

    return render(request,'bloquear_agenda.html',{'form':form})