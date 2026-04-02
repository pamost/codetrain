from django import forms
from app.models import Card, Language

class CardForm(forms.ModelForm):
    language = forms.ModelChoiceField(
        queryset=Language.objects.all().order_by('name'),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Card
        fields = ['language', 'term', 'definition', 'image_url', 'notes']
        widgets = {
            'term': forms.TextInput(attrs={'class': 'form-input'}),
            'definition': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5}),
            'image_url': forms.URLInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }
        labels = {
            'language': 'Язык',
            'term': 'Термин',
            'definition': 'Определение',
            'image_url': 'URL иллюстрации (необязательно)',
            'notes': 'Заметки (необязательно)',
        }