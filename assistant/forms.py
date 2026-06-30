from django import forms


class AssistantQueryForm(forms.Form):
    query = forms.CharField(
        label='اكتب سؤالك الصحي',
        max_length=400,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'مثال: أين أقرب مركز صحي؟'}),
    )
