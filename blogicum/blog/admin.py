from django.contrib import admin
from blog.constants import NUM_OF_WORDS_OF_TEXT, NUM_OF_WORDS_OF_TITLE
from blog.models import Category, Comment, Location, Post
from django.utils.html import format_html

admin.site.empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Класс для настройки интерфейса админ-зоны модели Post."""

    list_display = (
        'get_short_title',
        'get_short_text',
        'pub_date',
        'category',
        'is_published',
        'get_comment_count',
        'image_tag',
    )
    list_editable = (
        'is_published',
        'pub_date',
        'category'
    )
    search_fields = ('title', 'text',)
    list_filter = ('category', 'location',)

    @admin.display(description='Заголовок')
    def get_short_title(self, obj):
        """Получаем начальные слова заголовка поста."""
        return " ".join(obj.title.split()[:NUM_OF_WORDS_OF_TITLE])

    @admin.display(description='Описание')
    def get_short_text(self, obj):
        """Получаем начальные слова текста описания поста."""
        return f'{" ".join(obj.text.split()[:NUM_OF_WORDS_OF_TEXT])} ...'

    @admin.display(description='Комментарии')
    def get_comment_count(self, obj):
        """Получаем колличество комментариев в посте."""
        return obj.comments.count()

    @admin.display(description='Изображение')
    def image_tag(self, obj):
        """Получаем картинку к посту."""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" />'.format(obj.image.url)
            )
        return 'Не найдено'


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Comment)
