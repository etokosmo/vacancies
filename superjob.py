from statistics import mean, StatisticsError

import requests
from loguru import logger


def predict_rub_salary(currency: str, min_salary: int | None, max_salary: int | None) -> float | None:
    """Получаем среднюю зарплату по профессии"""
    if currency not in ('rub', 'RUR'):
        return None
    if min_salary and max_salary:
        return mean([max_salary, max_salary])
    if min_salary:
        return min_salary * 1.2
    if max_salary:
        return max_salary * 0.8


def get_language_superjob(lang: str, headers_superjob: dict, payload_superjob: dict) -> dict:
    """Получаем характеристики вакансий по языку программирования"""
    url_superjob = 'https://api.superjob.ru/2.0/vacancies/'
    payload_superjob['keyword'] = f'Программист {lang}'
    response = requests.get(url_superjob, headers=headers_superjob, params=payload_superjob)
    response.raise_for_status()
    processed_response = response.json()

    vacancies = get_all_vacancies_superjob(processed_response, url_superjob, headers_superjob, payload_superjob)
    salaries = []
    for vacancy in vacancies:
        currency = vacancy.get('currency')
        payment_from = vacancy.get('payment_from')
        payment_to = vacancy.get('payment_to')
        if salary := predict_rub_salary(currency, payment_from, payment_to):
            salaries.append(salary)
    try:
        svg_lang_salary = int(mean(salaries))
    except StatisticsError:
        logger.debug(f'Язык={lang}. Вакансий с зарплатой не найдено')
        svg_lang_salary = 0
    language = {'vacancies_found': processed_response.get('total'),
                "vacancies_processed": len(salaries),
                "average_salary": svg_lang_salary
                }
    logger.info(f'Language={lang}, info={language}')
    return language


def get_all_vacancies_superjob(content: dict,
                               url_superjob: str,
                               headers_superjob: dict,
                               payload_superjob: dict) -> list:
    """Возвращаем список всех вакансий для языка, в которых указана зарплата"""
    vacancies = []
    payload_superjob['page'] = 0
    while True:
        vacancies_on_page = content.get('objects')
        for vacancy in vacancies_on_page:
            vacancies.append(vacancy)

        if content.get('more'):
            payload_superjob['page'] += 1
            response = requests.get(url_superjob, headers=headers_superjob, params=payload_superjob)
            response.raise_for_status()
            content = response.json()
        else:
            break
    return vacancies


def create_language_info_superjob(langs: list, api_token: str, city: str) -> dict:
    """Создаем словарь с информацией о вакансиях по языкам программирования"""
    logger.info(f'Отправляем запросы к superjob.ru')
    headers_superjob = {'X-Api-App-Id': api_token}
    payload_superjob = {'page': 0, 'count': 100, 'town': city}
    result = {}
    for lang in langs:
        result[lang] = get_language_superjob(lang, headers_superjob, payload_superjob)
    return result
