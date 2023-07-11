from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    # пути для бработки Списков
    path('', views.PostListView.as_view(), name='index'),
    path(
        'category/<slug:post_category>/',
        views.category_posts,
        name='category_posts'
    ),

    # пути для бработки Профиля
    path(
        'profile/<str:username>/',
        views.profile_detail,
        name='profile'
    ),
    path(
        'edit_profile/<slug:pk>/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),

    # пути для бработки Поста
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),

    # пути для бработки Коментариев
    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:pk>',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:pk>',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]
