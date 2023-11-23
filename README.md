# Foodrgam

Foodrgam - web-приложение для обмена рецептами между пользователями.

Foodgram позволяет:
- делиться собственными рецептами;
- подписываться на страницы других пользователей;
- сохранять чужие рецепты к себе в Избранное;
- добавлять рецепты в Список покупок;


## Используемые технологии

- python 3.9.6;
- Django 4.2.5;
- DjangoRestFramework 3.14.0;
<!-- - Docker; -->
 

## Особенности реализации

Проект состоит из 2 приложений:
- recipes;
- users;

Документация к API доступна по адресу: <http://localhost/api/docs/redoc.html>


## Для локального запуска

- склонировать репозиторий:

```bash
git clone git@github.com:ekblb/foodgram-project-react.git
```

- установить и активировать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

- установить зависимости:
```bash
pip install -r requirements.txt
```

- применить миграции:
```bash
python manage.py migrate
```

- применить команду запуска на локальном сервере:
```bash
python manage.py runserver
```

## Сборка контейнеров:

- перейти в папку проекта infra, развернуть контейнеры:
```bash
docker-compose up -d --build
```

- выполнить миграции:
```bash
docker-compose exec backend python manage.py migrate
```

- создать суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

- собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

- используя интерфейс администратора создать теги, загрузить ингредиенты;

## Автор

Екатерина Балабаева
balabaeva.e.yu@yandex.ru