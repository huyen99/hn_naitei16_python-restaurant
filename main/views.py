from django.shortcuts import render
from .models import Food

def index(request):
    foods = Food.objects.prefetch_related('image_set').order_by('-rating')
    query = ''

    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET['query'].strip()
        foods = Food.objects.filter(name__icontains=query)

    context = {
        "foods": foods,
        "keyword": query
    }
    return render(request, 'index.html', context)
