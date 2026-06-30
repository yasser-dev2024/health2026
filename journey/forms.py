from django import forms


class JourneyForm(forms.Form):
    LOCATION_CHOICES = [
        ('abha', 'أبها'),
        ('soudah', 'السودة'),
        ('airport', 'مطار أبها'),
        ('khamis', 'خميس مشيط'),
        ('other', 'وجهة أخرى في عسير'),
    ]
    AGE_CHOICES = [
        ('under_18', 'أقل من 18'),
        ('adult', '18 إلى 49'),
        ('senior', '50 إلى 64'),
        ('elderly', '65 فأكثر'),
    ]
    PARTY_CHOICES = [
        ('individual', 'فرد'),
        ('family', 'عائلة'),
    ]
    PURPOSE_CHOICES = [
        ('tourism', 'سياحة وتنزه'),
        ('sport', 'نشاط بدني'),
        ('hiking', 'هايكنج ومسارات'),
        ('family', 'فعالية عائلية'),
        ('relax', 'استرخاء وزيارة خفيفة'),
        ('urgent', 'حاجة صحية عاجلة'),
    ]

    current_location = forms.ChoiceField(label='الوجهة الحالية', choices=LOCATION_CHOICES)
    age_group = forms.ChoiceField(label='الفئة العمرية', choices=AGE_CHOICES)
    party_type = forms.ChoiceField(label='نوع الزيارة', choices=PARTY_CHOICES, widget=forms.RadioSelect)
    visit_purpose = forms.ChoiceField(label='الغرض من الزيارة', choices=PURPOSE_CHOICES)
    has_health_condition = forms.BooleanField(
        label='توجد حالة صحية أو أعراض تحتاج انتباها',
        required=False,
    )
