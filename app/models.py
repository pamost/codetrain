from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, verbose_name="Имя пользователя")
    email = models.EmailField(blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return str(self.username)


class Language(models.Model):
    name = models.CharField(max_length=50, verbose_name="Язык программирования")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    description = models.TextField(blank=True, verbose_name="Описание")
    logo_url = models.URLField(blank=True, verbose_name="URL логотипа")

    class Meta:
        verbose_name = "Язык"
        verbose_name_plural = "Языки"

    def __str__(self):
        return str(self.name)


class Topic(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=100, verbose_name="Название темы")
    slug = models.SlugField(verbose_name="Слаг")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        unique_together = ('language', 'slug')
        ordering = ['order', 'name']
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self):
        return str(self.name)


class Card(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='cards')
    term = models.CharField(max_length=200, verbose_name="Термин")
    definition = models.TextField(verbose_name="Определение")   # изменено с CharField на TextField
    image_url = models.URLField(blank=True, verbose_name="URL иллюстрации")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Создатель")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        ordering = ['-created_at']

    def __str__(self):
        return str(self.term)
    
class RememberedCard(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='remembered_cards')
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='remembered_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'card')
        verbose_name = "Запомненная карточка"
        verbose_name_plural = "Запомненные карточки"