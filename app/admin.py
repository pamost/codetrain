from django.contrib import admin
from app.models import User, Language, Topic, Card, Question

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'logo_url')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'slug', 'order')
    list_filter = ('language',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('term', 'language', 'created_by', 'is_approved', 'created_at')
    list_filter = ('language', 'is_approved', 'created_at')
    search_fields = ('term', 'definition')
    actions = ['approve_cards']

    def approve_cards(self, request, queryset):
        queryset.update(is_approved=True)
    approve_cards.short_description = "Одобрить выбранные карточки"

    def save_model(self, request, obj, form, change):
        if not change:  # новая карточка через админку
            obj.is_approved = True
        super().save_model(request, obj, form, change)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'correct_option')
    list_filter = ('topic__language', 'topic')
    search_fields = ('text',)
    fieldsets = (
        (None, {
            'fields': ('topic', 'text', 
                ('option1', 'option2'),
                ('option3', 'option4'),
            'correct_option', 'explanation')
        }),
    )
