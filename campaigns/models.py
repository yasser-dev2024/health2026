from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.validators import validate_safe_url


class Campaign(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'مسودة'),
        (STATUS_ACTIVE, 'نشطة'),
        (STATUS_DISABLED, 'معطلة'),
        (STATUS_ARCHIVED, 'مؤرشفة'),
    ]

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    archived_at = models.DateTimeField(null=True, blank=True)

    logo = models.ImageField(upload_to='campaigns/logos/', blank=True, null=True)
    logo_static_path = models.CharField(max_length=220, blank=True, default='')
    splash_image = models.ImageField(upload_to='campaigns/splash/', blank=True, null=True)
    splash_static_path = models.CharField(max_length=220, blank=True, default='')
    background_image = models.ImageField(upload_to='campaigns/backgrounds/', blank=True, null=True)
    background_static_path = models.CharField(max_length=220, blank=True, default='')

    primary_color = models.CharField(max_length=20, default='#15508A')
    secondary_color = models.CharField(max_length=20, default='#283A83')
    accent_color = models.CharField(max_length=20, default='#D4AF37')
    color_settings = models.JSONField(default=dict, blank=True)

    main_title = models.CharField(max_length=180, blank=True)
    main_description = models.TextField(blank=True)
    welcome_text = models.CharField(max_length=220, blank=True)

    doctor_settings = models.JSONField(default=dict, blank=True)
    qr_settings = models.JSONField(default=dict, blank=True)
    deep_link_settings = models.JSONField(default=dict, blank=True)
    page_settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', 'name']
        verbose_name = 'حملة'
        verbose_name_plural = 'إدارة الحملات'
        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                condition=models.Q(is_active=True),
                name='campaign_single_active_true',
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def logo_src(self):
        if self.logo:
            return self.logo.url
        return self.logo_static_path

    @property
    def splash_src(self):
        if self.splash_image:
            return self.splash_image.url
        return self.splash_static_path

    @property
    def background_src(self):
        if self.background_image:
            return self.background_image.url
        return self.background_static_path

    def clean(self):
        if self.is_active and self.status == self.STATUS_ARCHIVED:
            raise ValidationError('لا يمكن تفعيل حملة مؤرشفة.')
        if self.status == self.STATUS_ACTIVE:
            self.is_active = True
        if self.is_active:
            self.status = self.STATUS_ACTIVE
            self.archived_at = None

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_active:
            Campaign.objects.exclude(pk=self.pk).filter(is_active=True).update(
                is_active=False,
                status=self.STATUS_DISABLED,
            )
        self.full_clean(validate_constraints=False)
        super().save(*args, **kwargs)

    def activate(self):
        self.is_active = True
        self.status = self.STATUS_ACTIVE
        self.archived_at = None
        self.save(update_fields=['is_active', 'status', 'archived_at', 'updated_at'])

    def disable(self):
        self.is_active = False
        if self.status != self.STATUS_ARCHIVED:
            self.status = self.STATUS_DISABLED
        self.save(update_fields=['is_active', 'status', 'updated_at'])

    def archive(self):
        self.is_active = False
        self.status = self.STATUS_ARCHIVED
        self.archived_at = timezone.now()
        self.save(update_fields=['is_active', 'status', 'archived_at', 'updated_at'])

    def duplicate(self, suffix='copy'):
        base_slug = f'{self.slug}-{suffix}'
        slug = base_slug
        counter = 2
        while Campaign.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        duplicate = Campaign.objects.create(
            name=f'نسخة من {self.name}',
            slug=slug,
            description=self.description,
            status=self.STATUS_DRAFT,
            is_active=False,
            logo=self.logo,
            logo_static_path=self.logo_static_path,
            splash_image=self.splash_image,
            splash_static_path=self.splash_static_path,
            background_image=self.background_image,
            background_static_path=self.background_static_path,
            primary_color=self.primary_color,
            secondary_color=self.secondary_color,
            accent_color=self.accent_color,
            color_settings=self.color_settings,
            main_title=self.main_title,
            main_description=self.main_description,
            welcome_text=self.welcome_text,
            doctor_settings=self.doctor_settings,
            qr_settings=self.qr_settings,
            deep_link_settings=self.deep_link_settings,
            page_settings=self.page_settings,
        )
        page_map = {}
        for page in self.pages.all():
            new_page = page.duplicate_to(duplicate)
            page_map[page.pk] = new_page
        for button in self.buttons.all():
            button.duplicate_to(duplicate, page_map=page_map)
        return duplicate


class CampaignPage(models.Model):
    PAGE_HOME = 'home'

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='pages')
    key = models.SlugField(max_length=80)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    banner = models.ImageField(upload_to='campaigns/pages/', blank=True, null=True)
    banner_static_path = models.CharField(max_length=220, blank=True, default='')
    content = models.TextField(blank=True)
    settings = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'key']
        unique_together = ('campaign', 'key')
        verbose_name = 'صفحة حملة'
        verbose_name_plural = 'صفحات الحملات'

    def __str__(self):
        return f'{self.campaign} - {self.title}'

    @property
    def banner_src(self):
        if self.banner:
            return self.banner.url
        return self.banner_static_path

    def duplicate_to(self, campaign):
        return CampaignPage.objects.create(
            campaign=campaign,
            key=self.key,
            title=self.title,
            description=self.description,
            banner=self.banner,
            banner_static_path=self.banner_static_path,
            content=self.content,
            settings=self.settings,
            active=self.active,
            order=self.order,
        )


class CampaignButton(models.Model):
    ACTION_PAGE = 'page'
    ACTION_DEEP_LINK = 'deep_link'
    ACTION_EXTERNAL = 'external'
    ACTION_ASSISTANT = 'assistant'
    ACTION_CHOICES = [
        (ACTION_PAGE, 'فتح صفحة'),
        (ACTION_DEEP_LINK, 'فتح رابط عميق'),
        (ACTION_EXTERNAL, 'فتح رابط خارجي'),
        (ACTION_ASSISTANT, 'فتح الدكتور مساعد'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='buttons')
    page = models.ForeignKey(CampaignPage, null=True, blank=True, on_delete=models.CASCADE, related_name='buttons')
    label = models.CharField(max_length=90)
    icon = models.CharField(max_length=40, blank=True)
    color = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_PAGE)
    target_page = models.ForeignKey(
        CampaignPage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='targeted_buttons',
    )
    url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    deep_link = models.CharField(max_length=240, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'زر حملة'
        verbose_name_plural = 'أزرار الحملات'

    def __str__(self):
        return self.label

    def clean(self):
        if self.page and self.page.campaign_id != self.campaign_id:
            raise ValidationError('يجب أن تكون صفحة الزر من نفس الحملة.')
        if self.target_page and self.target_page.campaign_id != self.campaign_id:
            raise ValidationError('يجب أن تكون الصفحة المستهدفة من نفس الحملة.')

    def get_url(self):
        if self.action_type == self.ACTION_ASSISTANT:
            return reverse('assistant')
        if self.action_type == self.ACTION_DEEP_LINK:
            return self.deep_link or self.url or '#'
        if self.action_type == self.ACTION_EXTERNAL:
            return self.url or '#'
        if self.target_page:
            if self.target_page.key == CampaignPage.PAGE_HOME:
                return reverse('core:home')
            return reverse('campaign_page', kwargs={'page_key': self.target_page.key})
        return self.url or '#'

    def duplicate_to(self, campaign, page_map=None):
        page_map = page_map or {}
        return CampaignButton.objects.create(
            campaign=campaign,
            page=page_map.get(self.page_id),
            label=self.label,
            icon=self.icon,
            color=self.color,
            order=self.order,
            action_type=self.action_type,
            target_page=page_map.get(self.target_page_id),
            url=self.url,
            deep_link=self.deep_link,
            active=self.active,
        )


class CampaignInteraction(models.Model):
    TYPE_VISIT = 'visit'
    TYPE_QR_SCAN = 'qr_scan'
    TYPE_ASSISTANT_OPEN = 'assistant_open'
    TYPE_ASSISTANT_QUERY = 'assistant_query'
    TYPE_INTERACTION = 'interaction'
    TYPE_CHOICES = [
        (TYPE_VISIT, 'زائر'),
        (TYPE_QR_SCAN, 'مسح QR'),
        (TYPE_ASSISTANT_OPEN, 'فتح الدكتور مساعد'),
        (TYPE_ASSISTANT_QUERY, 'سؤال الدكتور مساعد'),
        (TYPE_INTERACTION, 'تفاعل'),
    ]

    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    event_type = models.CharField(max_length=30, choices=TYPE_CHOICES, db_index=True)
    visitor_id = models.CharField(max_length=64, blank=True, db_index=True)
    path = models.CharField(max_length=240, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تفاعل حملة'
        verbose_name_plural = 'تفاعلات الحملات'

    def __str__(self):
        return f'{self.get_event_type_display()} - {self.campaign or "بدون حملة"}'
