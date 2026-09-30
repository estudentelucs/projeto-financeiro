from django.shortcuts import render


def home(request):
    """Página inicial do sistema."""
    return render(request, 'core/home.html')
