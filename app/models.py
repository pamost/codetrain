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

