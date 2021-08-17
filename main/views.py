from django.shortcuts import render
from .models import Food

def index(request):
    foods = Food.objects.prefetch_related('image_set').order_by('-rating')
    context = {
        "foods": foods
    }
    return render(request, 'index.html', context)
