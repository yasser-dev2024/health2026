from django import forms

from .models import HealthLocation


class HealthLocationForm(forms.ModelForm):
    class Meta:
        model = HealthLocation
        fields = [
            'name', 'location_type', 'city', 'address',
            'distance_label', 'availability', 'phone',
            'map_url', 'order', 'active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'اسم الموقع أو المرفق'}),
            'city': forms.TextInput(attrs={'placeholder': 'أبها، خميس مشيط...'}),
            'address': forms.TextInput(attrs={'placeholder': 'العنوان التفصيلي'}),
            'distance_label': forms.TextInput(attrs={'placeholder': 'مثال: 2 كم من وسط المدينة'}),
            'availability': forms.TextInput(attrs={'placeholder': 'مثال: 24 ساعة، 8 ص - 8 م'}),
            'phone': forms.TextInput(attrs={'placeholder': '05xxxxxxxx أو 0172xxxxxx'}),
            'map_url': forms.URLInput(attrs={'placeholder': 'رابط خرائط جوجل (اختياري)'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
