# Тестовый проект интернет-магазина - тестовое задание Skillbox
 - автор: Максим Семенюк

##Установка
```
git clone https://github.com
cd Skill_testshop
pip install requirements.txt
```
Исправить или заполнить файл `.env`
Создание базы данных:
```
python manage.py makemigrations
python manage.py migrate

```
Создать суперпользователя:
```
python manage.py createsuperuser
```
## Создание тестовых данныx:
```
python manage.py create_products
```
##Запуск
```
python manage.py runserver
```

##API
Доступна по адресу `/api/products`. Доступны поиск по категориям: имени(`category`) или id категории(`category_id`).
Примеры:
```
/api/products/?category_id=1
/api/products/?category=test_category
```
Поиск по названию через параметр `search` или при ручном вводе
Пример:
```
/api/products/?search=test
```

## Админ-панель
Доступно создание категорий и продуктов, управление покупками и корзинами
Чтобы загрузить продукты из csv, необходимо зайти в `products` -> `import`
Чтобы посмотреть отчет о покупках: `purchases` -> `show purchases report`