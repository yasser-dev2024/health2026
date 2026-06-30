from django import forms

from campaigns.services import get_active_campaign

from .models import QrItem, QrLocation
from .services import unique_location_slug


class QrLocationForm(forms.ModelForm):
    active = forms.TypedChoiceField(
        label='الحالة',
        choices=((True, 'نشط'), (False, 'غير نشط')),
        coerce=lambda value: value in (True, 'True', 'true', '1', 'on'),
        widget=forms.Select,
    )

    class Meta:
        model = QrLocation
        fields = ['name', 'description', 'active']
        labels = {
            'name': 'اسم الموقع',
            'description': 'وصف اختياري',
        }
        help_texts = {
            'name': 'مثال: شارع الفن، مطار أبها، ممشى الضباب.',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'مثال: شارع الفن'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'وصف اختياري يظهر داخل لوحة التحكم'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.campaign_id:
            instance.campaign = get_active_campaign()
        if not instance.slug:
            instance.slug = unique_location_slug(instance.name, instance, campaign=instance.campaign)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class QrItemForm(forms.ModelForm):
    class Meta:
        model = QrItem
        fields = ['title', 'item_type', 'description', 'target_url', 'stamp', 'active']
