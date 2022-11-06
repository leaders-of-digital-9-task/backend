# ЛЦТ 9 задача, Magnum Opus backend

### Запуск
```shell
$ docker-compose -f local.yml up
```

###### API на http://127.0.0.1:8000/api/

### Стек
- Django
- Postgresql
- Celery
- DRF
- django-polymorphic
- pydicom


### Особенности

- полиморфные модели для рисунков(позволяет легко добавлять новые типы фигур)
- celery + [celery flower](http://127.0.0.1:5555) для асинхронной обработки STL и просмотра задач
- документация API в [swagger](http://127.0.0.1:8000/api/docs/) и [redoc](http://127.0.0.1:8000/api/redoc/)
- линтеры и workflow-ы для разработки


### Докуменатция
https://dev3.akarpov.ru/api/redoc/

### ML
https://drive.google.com/drive/folders/1aLcZFkOKFeUNMcROPKAFr5EwRgw3FpSC?usp=sharing
