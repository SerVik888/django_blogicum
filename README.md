# Блогикум

### Описание проекта
Блогикум - это сайт, на котором пользователь может создать свою страницу и публиковать на ней сообщения («посты»).
Для каждого поста нужно указать категорию — например «путешествия», «кулинария» или «python-разработка», а также опционально локацию, с которой связан пост, например «Остров отчаянья» или «Караганда». 
Пользователь может перейти на страницу любой категории и увидеть все посты, которые к ней относятся.
Пользователи смогут заходить на чужие страницы, читать и комментировать чужие посты.
Для своей страницы автор может задать имя и уникальный адрес. 

### Cписок используемых технологий
- Django
- django-bootstrap5
- pytest

### Как запустить проект:
`git clone git@github.com:SerVik888/django_blogicum.git` -> клонировать репозиторий

* Если у вас Linux/macOS\
    `python3 -m venv env` -> создать виртуальное окружение\
    `source env/bin/activate` -> активировать виртуальное окружение\
    `python3 -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `python3 manage.py migrate` -> выполнить миграции\
    `python3 manage.py createsuperuser` -> создать суперпользователя\
    `python3 manage.py runserver` -> запустить проект

* Если у вас windows\
    `python -m venv venv` -> создать виртуальное окружение\
    `source venv/Scripts/activate` -> активировать виртуальное окружение\
    `python -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `python manage.py migrate` -> выполнить миграции\
    `python manage.py createsuperuser` -> создать суперпользователя\
    `python manage.py runserver` -> запустить проект

### Как запускать тесты
После активации виртуального окружения находясь в корне проекта, в консоли ввидите `pytest`

Автор:
Сафонов Сергей https://github.com/SerVik888 [sergey_safonov86@inbox.ru](mailto:sergey_safonov86@inbox.ru)