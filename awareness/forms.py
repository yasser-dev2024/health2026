from django import forms

from .models import AwarenessContent, AwarenessMessage


class AwarenessContentForm(forms.ModelForm):
    class Meta:
        model = AwarenessContent
        fields = [
            'title', 'content_type', 'category', 'summary',
            'action_label', 'order', 'active',
            'file_upload', 'file_url',
            'thumbnail_upload', 'thumbnail_url',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان المادة التوعوية'}),
            'category': forms.TextInput(attrs={'placeholder': 'مثال: توعية، تغذية، قلب...'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'placeholder': 'وصف مختصر للمادة'}),
            'action_label': forms.TextInput(attrs={'placeholder': 'مثال: تحميل، عرض، قراءة...'}),
            'file_url': forms.URLInput(attrs={'placeholder': 'https://... رابط خارجي للملف (اختياري)'}),
            'thumbnail_url': forms.URLInput(attrs={'placeholder': 'https://... رابط خارجي للصورة (اختياري)'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }


class AwarenessMessageForm(forms.ModelForm):
    class Meta:
        model = AwarenessMessage
        fields = ['title', 'text', 'category', 'icon', 'order', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان الرسالة'}),
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'نص الرسالة التوعوية'}),
            'category': forms.TextInput(attrs={'placeholder': 'مثال: نصيحة، تحذير، معلومة...'}),
            'icon': forms.TextInput(attrs={'placeholder': 'رمز اختياري مثال: 💧 أو 🏃'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
