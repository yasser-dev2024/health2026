from django import forms

from .models import HealthEvent


class HealthEventForm(forms.ModelForm):
    class Meta:
        model = HealthEvent
        fields = [
            'title', 'description', 'city', 'location',
            'date', 'time', 'activity_type', 'audience',
            'category', 'map_url', 'order', 'show_on_home', 'active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان الفعالية'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'وصف الفعالية'}),
            'city': forms.TextInput(attrs={'placeholder': 'أبها، خميس مشيط...'}),
            'location': forms.TextInput(attrs={'placeholder': 'اسم المكان أو العنوان'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TextInput(attrs={'placeholder': '9:00 صباحاً - 1:00 ظهراً'}),
            'activity_type': forms.TextInput(attrs={'placeholder': 'مثال: ماراثون، محاضرة، ورشة...'}),
            'audience': forms.TextInput(attrs={'placeholder': 'مثال: عائلات، أطفال، جميع الفئات...'}),
            'category': forms.TextInput(attrs={'placeholder': 'مثال: توعية، رياضة، صحة...'}),
            'map_url': forms.URLInput(attrs={'placeholder': 'رابط خرائط جوجل (اختياري)'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
