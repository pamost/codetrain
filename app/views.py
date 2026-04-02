import json
import random
from datetime import datetime

import markdown
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from app.forms import CardForm
from app.models import User, Language, Topic, Card, RememberedCard, QuizAttempt

def home_page(request):
    languages = Language.objects.all()
    all_topics  = Topic.objects.all()
    users_count = User.objects.count()
    context = {
        'app_name': 'СodeTrain',
        'app_description': 'тренажер языков программирования',
        'current_year': datetime.now().year,
        'languages': languages,
        'topics': all_topics,
        'users_count': users_count
    }
    return render(request, 'app/home.html', context)

def topics(request, lang_slug): # pylint: disable=too-many-return-statements
    language = get_object_or_404(Language, slug=lang_slug)
    all_topics = language.topics.all().order_by('order', 'name')

    # --- Получение карточек языка с автором ---
    # Базовый запрос: только одобренные карточки, подгружаем автора (created_by)
    cards_qs = language.cards.filter(is_approved=True).select_related('created_by')

    user_id = request.session.get('user_id')
    if user_id:
        # Исключаем карточки, которые пользователь уже запомнил
        remembered_ids = RememberedCard.objects.filter(user_id=user_id).values_list('card_id', flat=True)
        cards = cards_qs.exclude(id__in=remembered_ids)
    else:
        cards = cards_qs

    # --- Навигация по темам ---
    topics_list = list(all_topics)
    selected_topic_id = request.GET.get('topic_id')
    selected_topic = None
    prev_topic = None
    next_topic = None

    if selected_topic_id:
        selected_topic = get_object_or_404(Topic, id=selected_topic_id, language=language)
        try:
            index = topics_list.index(selected_topic)
            if index > 0:
                prev_topic = topics_list[index - 1]
            if index < len(topics_list) - 1:
                next_topic = topics_list[index + 1]
        except ValueError:
            pass
    elif topics_list:
        selected_topic = topics_list[0]
        if len(topics_list) > 1:
            next_topic = topics_list[1]

    # --- Преобразование Markdown в HTML для выбранной темы ---
    if selected_topic:
        selected_topic.html_description = markdown.markdown(
            selected_topic.description or '',
            extensions=['fenced_code', 'codehilite']
        )

    # --- Контекст ---
    context = {
        'title': f'{language.name} - темы',
        'current_year': datetime.now().year,
        'language': language,
        'topics': all_topics ,
        'selected_topic': selected_topic,
        'prev_topic': prev_topic,
        'next_topic': next_topic,
        'cards': cards,
        'user_id': user_id,
    }
    return render(request, 'app/topics.html', context)

def card_create(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.is_approved = False
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    card.created_by = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    pass
            card.save()
            messages.success(request, 'Карточка отправлена на модерацию.')
            return redirect('topics', lang_slug=card.language.slug)
    else:
        initial = {}
        language_id = request.GET.get('language')
        if language_id:
            initial['language'] = language_id
        form = CardForm(initial=initial)

    context = {
        'form': form,
        'title': 'Добавить карточку',
        'current_year': datetime.now().year,
    }
    return render(request, 'app/card_form.html', context)

@csrf_exempt
def remember_card(request): # pylint: disable=too-many-return-statements
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            card_id = data.get('card_id')
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

        try:
            user = User.objects.get(id=user_id)
            card = Card.objects.get(id=card_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        except Card.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Card not found'}, status=404)

        _, created = RememberedCard.objects.get_or_create(user=user, card=card)
        if created:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Already remembered'}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def unremember_card(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            card_id = data.get('card_id')
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error'}, status=401)

        RememberedCard.objects.filter(user_id=user_id, card_id=card_id).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

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
        }
        return render(request, 'app/set_user.html', context)

def user_stats(request):
    if 'user_id' not in request.session:
        return redirect('set_user')
    user = get_object_or_404(User, id=request.session['user_id'])
    attempts = QuizAttempt.objects.filter(user=user).select_related('topic').order_by('-created_at')
    remembered_cards = RememberedCard.objects.filter(user=user).select_related('card').order_by('-created_at')
    context = {
        'title': 'Моя статистика',
        'current_year': datetime.now().year,
        'attempts': attempts,
        'remembered_cards': remembered_cards,
        'remembered_cards_count': remembered_cards.count(),
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

def topic_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    questions = list(topic.questions.all())
    if not questions:
        messages.warning(request, 'В этой теме пока нет вопросов.')
        return redirect('topics', lang_slug=topic.language.slug)

    # Преобразуем Markdown в HTML для текста вопроса и вариантов ответов
    md_extensions = ['fenced_code', 'codehilite']
    for q in questions:
        q.html_text = markdown.markdown(q.text, extensions=md_extensions)
        q.html_option1 = markdown.markdown(q.option1, extensions=md_extensions)
        q.html_option2 = markdown.markdown(q.option2, extensions=md_extensions)
        q.html_option3 = markdown.markdown(q.option3, extensions=md_extensions)
        q.html_option4 = markdown.markdown(q.option4, extensions=md_extensions)

    # Проверка авторизации
    if 'user_id' not in request.session:
        return redirect(f"{reverse('set_user')}?next={request.path}")

    user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        score = 0
        for q in questions:
            selected = request.POST.get(f'q_{q.id}')
            if selected == str(q.correct_option):
                score += 1
        # Сохраняем попытку
        QuizAttempt.objects.create(
            user=user,
            topic=topic,
            score=score,
            total=len(questions)
        )
        request.session['quiz_result'] = {
            'score': score,
            'total': len(questions),
            'topic_id': topic.id,
        }
        return redirect('quiz_result')
    else:
        # Перемешиваем вопросы для разнообразия (опционально)
        random.shuffle(questions)
        context = {
            'title': f'Тест: {topic.name}',
            'topic': topic,
            'questions': questions,
        }
        return render(request, 'app/quiz_take.html', context)

def quiz_result(request):
    result = request.session.get('quiz_result')
    if not result:
        return redirect('home')
    topic = get_object_or_404(Topic, id=result['topic_id'])
    context = {
        'title': 'Результат теста',
        'score': result['score'],
        'total': result['total'],
        'topic': topic,
    }
    return render(request, 'app/quiz_result.html', context)
