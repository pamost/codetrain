from app.models import User, Language

def user_context(request):
    user_id = request.session.get('user_id')
    username = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            username = user.username
        except User.DoesNotExist:
            # Если пользователь удалён из БД, очистим сессию
            del request.session['user_id']
            user_id = None
    return {
        'user_id': user_id,
        'username': username,
    }

def languages_context(request):
    return {'languages': Language.objects.all()}

def app_info(request):
    return {
        'app_name': 'CodeTrain',
        'app_description': 'тренажер для программистов',
    }