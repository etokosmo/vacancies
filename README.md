# Скрипт для просмотра средней зарплаты программистов

## Цели проекта

* Скачать вакансии разработчиков с HeadHunter и SuperJob
* Посчитать среднюю зарплату для каждого языка программирования

> Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).

## Конфигурации

* Python version: 3.10
* Libraries: requirements.txt

## Запуск

- Скачайте код
- Установите библиотеки командой:

```bash
pip install -r requirements.txt
```

- Запишите переменные окружения в файле `.env`

```bash
SUPERJOB_API_TOKEN=... #Токен полученный на https://api.superjob.ru/
CITY=... #Город, например Москва, Санкт-Петербург или Екатеринбург
```

- Запустить скрипт

```bash
python3 main.py
```

## Пример работы программы

![пример](https://dvmn.org/filer/canonical/1567490703/266/)