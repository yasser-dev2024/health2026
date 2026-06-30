from django import forms


class HeroChallengeForm(forms.Form):
    participant_name = forms.CharField(
        label='الاسم على الشهادة',
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'اكتب اسمك كما تريد ظهوره في الشهادة'}),
    )
    phone = forms.RegexField(
        label='رقم الجوال',
        max_length=30,
        regex=r'^[0-9+\-\s]{8,20}$',
        error_messages={'invalid': 'أدخل رقم جوال صحيح للتواصل.'},
        widget=forms.TextInput(attrs={'inputmode': 'tel', 'placeholder': '05xxxxxxxx'}),
    )
