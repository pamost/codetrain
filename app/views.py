from datetime import datetime
from django.shortcuts import render

def home_page(request):
    context = {
        'title': 'СodeTrain - тренажер для изучения языков программирования',
        'current_year': datetime.now().year
    }
    return render(request, 'app/home.html', context)
