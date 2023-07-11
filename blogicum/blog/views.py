

import datetime

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from blog.constants import NUM_OF_POSTS
from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post

User = get_user_model()


"""Обработка списков"""


class PostListView(ListView):
    """Список постов на главной странице"""

    model = Post
    template_name = 'blog/index.html'

    """Параметры фильтрации"""
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )

    """Cортируем сначала новые потом старые посты"""
    ordering = '-pub_date'
    paginate_by = 10


def category_posts(request, post_category):
    """Обрабатывает запрос на получение постов определённой категории."""
    category_posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
        category__slug=post_category
    ).order_by('-pub_date')
    paginator = Paginator(category_posts, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    category_posts = paginator.get_page(page_number)
    context = {
        'category': get_object_or_404(
            Category,
            slug=post_category,
            is_published=True
        ),
        'page_obj': category_posts
    }
    return render(request, 'blog/category.html', context)

# ??? Как получить post_category в СBV

# class CategoryListView(ListView):
#     """Обрабатывает запрос на получение постов определённой категории."""

#     model = Post
#     template_name = 'blog/category.html'

#     """Параметры фильтрации"""
#     queryset = Post.objects.filter(
#         is_published=True,
#         category__is_published=True,
#         pub_date__lte=timezone.now(),
#         category__slug=post_category
#     )

#     """Cортируем сначала новые потом старые посты"""
#     ordering = '-pub_date'
#     paginate_by = 10


"""Обработка профиля"""


def profile_detail(request, username):
    """Обрабатывает запрос на получение полного описания юзера."""
    profile_posts = Post.objects.filter(
        author__username=username
    ).order_by('-pub_date')
    paginator = Paginator(profile_posts, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': get_object_or_404(
            User,
            username=username
        ),
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)

# ??? Как получить список нужных постов в СBV

# class ProfileDetailView(DetailView):
#     """Обрабатывает запрос на получение полного описания юзера."""

    # model = Post

    # def get_context_data(self, **kwargs):
    #     # Получаем словарь контекста:
    #     context = super().get_context_data(**kwargs)
    #     # Добавляем в словарь новый ключ:
    #     context['profile'] = get_object_or_404(
    #         User,
    #         username=self.get_object().author
    #     ),
    #     context['page_obj'] = (
    #         # Дополнительно подгружаем авторов комментариев,
    #         # чтобы избежать множества запросов к БД.
    #         self.object.posts.select_related('author')
    #     )
    #     # Возвращаем словарь контекста.
    #     return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')


"""Обработка поста"""


class PostDetailView(DetailView):
    """Обрабатывает запрос на получение полного описания поста."""

    model = Post
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        """Проверяем опубликован ли пост, или категория, и дату публикации
        если это не автор ставим ограничения на просмотр публикаций
        """
        post = self.get_object()
        if (
                post.author != self.request.user
                and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > datetime.datetime.now(pytz.utc)
                )
        ):
            raise Http404(
                "Страница не опубликована."
            )
        return super(PostDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        """Записываем в переменную form пустой объект формы."""
        context['form'] = CommentForm()
        """Запрашиваем все комментарии для выбранного поста."""
        context['comments'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comment.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin,  CreateView):
    """Обрабатывает запрос на Создание нового поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Присвоить полю author объект пользователя из запроса."""
        form.instance.author = self.request.user
        """Продолжить валидацию, описанную в форме."""
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляем пользователя после создания поста на его страницу."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class PostUpdateView(UserPassesTestMixin, UpdateView):
    """Обрабатывает запрос на Редактирование поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.get_object().author == self.request.user
        )

    def get_redirect_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def handle_no_permission(self):
        return redirect(self.get_redirect_url())

    def get_success_url(self):
        """Перенаправляем пользователя после обновления поста на его страницу.
        """
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(DeleteView):
    """Обрабатывает запрос на Удаление поста"""
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            raise Http404("Вам не разрешается удалять этот пост.")
        return super(PostDeleteView, self).dispatch(request, *args, **kwargs)


"""Обработка комментария"""


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    user_post = None
    model = Comment
    form_class = CommentForm
    template_name = 'comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.user_post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.user_post
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляем пользователя после создания формы на страницу поста.
        """
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление коментария"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Комментарий может изменить только автор иначе показываем ошибку"""
        if self.get_object().author != self.request.user:
            raise Http404("Вам не разрешается редактировать этот комментарий.")
        return super(
            CommentUpdateView, self
        ).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(DeleteView):
    """Удаление комментария"""

    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Комментарий может удалить только автор иначе показываем ошибку"""
        if self.get_object().author != self.request.user:
            raise Http404("Вам не разрешается удалять этот комментарий.")
        return super(
            CommentDeleteView, self
        ).dispatch(request, *args, **kwargs)

    #
    def get_success_url(self):
        """Перенаправляем пользователя после удаления комментария
        на страницу поста."""
        return reverse('blog:post_detail', kwargs={'pk': self.object.post_id})
