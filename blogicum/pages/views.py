from django.shortcuts import render
from django.views.generic import TemplateView

"""CBV для обработки Статичных страниц"""


class RulesTemplateView(TemplateView):
    template_name = 'pages/rules.html'


class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'


"""Функции для обработки ошибок"""


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)
