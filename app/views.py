import json

from datetime import datetime
from django.urls import reverse

from django.shortcuts import render, get_object_or_404, redirect
import random
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import User, Language, Topic

def home_page(request):
    languages = Language.objects.all()
    topics = Topic.objects.all()
    context = {
        'app_name': 'СodeTrain',
        'app_description': 'тренажер для изучения языков программирования',
        'current_year': datetime.now().year,
        'languages': languages,
        'topics': topics
    }
    return render(request, 'app/home.html', context)

@csrf_exempt
def set_user(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX запрос из модального окна
            try:
                data = json.loads(request.body)
                username = data.get('username')
                email = data.get('email')
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Неверный формат данных'}, status=400)

            if not username:
                return JsonResponse({'status': 'error', 'message': 'Имя обязательно'}, status=400)

            # Ищем или создаём пользователя
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if not created and email and not user.email:
                user.email = email
                user.save()
            request.session['user_id'] = user.id
            return JsonResponse({'status': 'ok'})
        else:
            # Обычный POST (например, если форма отправлена без AJAX)
            username = request.POST.get('username')
            email = request.POST.get('email')
            next_url = request.GET.get('next', reverse('home'))
            if username:
                user, created = User.objects.get_or_create(username=username, defaults={'email': email})
                request.session['user_id'] = user.id
                return redirect(next_url)
            else:
                messages.error(request, 'Имя обязательно.')
                return redirect('set_user')
    else:
        # GET – показываем форму
        context = {
            'title': 'Представьтесь',
            'current_year': datetime.now().year,
            'next': request.GET.get('next', ''),
            'app_name': 'CodeTrain',
            'app_description': 'тренажер для программистов',
        }
        return render(request, 'app/set_user.html', context)
    
def user_stats(request):
    if 'user_id' not in request.session:
        return redirect('home')
    # user = get_object_or_404(User, id=request.session['user_id'])
    # attempts = QuizAttempt.objects.filter(user=user).select_related('topic')
    context = {
        'title': 'Моя статистика',
        'current_year': datetime.now().year,
        # 'attempts': attempts,
        'app_name': 'CodeTrain',
        'app_description': 'тренажер для программистов',
    }
    return render(request, 'app/user_stats.html', context)

def logout_user(request):
    if request.method == 'POST':
        request.session.flush()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def get_user_data(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    user = get_object_or_404(User, id=request.session['user_id'])
    return JsonResponse({'username': user.username, 'email': user.email})

def update_user(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    if 'user_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')
    if not username:
        return JsonResponse({'status': 'error', 'message': 'Имя обязательно'}, status=400)
    user = get_object_or_404(User, id=request.session['user_id'])
    user.username = username
    user.email = email
    user.save()
    return JsonResponse({'status': 'ok'})