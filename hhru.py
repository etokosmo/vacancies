from statistics import mean, StatisticsError

import requests
from loguru import logger

from superjob import predict_rub_salary


def get_language_hhru(lang: str, payload_hhru: dict) -> dict:
    """Получаем характеристики вакансий по языку программирования"""
    url_hhru = 'https://api.hh.ru/vacancies'
    headers_hhru = {
        'User-Agent': 'api-test-agent'
    }
    payload_hhru['text'] = f'Программист {lang}'
    payload_hhru['only_with_salary'] = True

    response = requests.get(url_hhru, headers=headers_hhru, params=payload_hhru)
    response.raise_for_status()
    processed_response = response.json()

    vacancies = get_all_vacancies_hhru(processed_response, url_hhru, headers_hhru, payload_hhru)
    salaries = []
    for vacancy in vacancies:
        salary = vacancy.get('salary')
        if not salary:
            continue
        currency = salary.get('currency')
        payment_from = salary.get('from')
        payment_to = salary.get('to')
        if salary := predict_rub_salary(currency, payment_from, payment_to):
            salaries.append(salary)
    try:
        svg_lang_salary = int(mean(salaries))
    except StatisticsError:
        logger.debug(f'Язык={lang}. Вакансий с зарплатой не найдено')
        svg_lang_salary = 0
    language = {'vacancies_found': processed_response.get('found'),
                "vacancies_processed": len(salaries),
                "average_salary": svg_lang_salary
                }
    logger.info(f'Language={lang}, info={language}')
    return language


def get_all_vacancies_hhru(content: dict, url_hhru: str, headers_hhru: dict, payload_hhru: dict) -> list:
    """Возвращаем список всех вакансий для языка, в которых указана зарплата"""
    pages = content.get('pages')
    vacancies = []
    for page in range(pages + 1):
        payload_hhru['page'] = page
        response = requests.get(url_hhru, headers=headers_hhru, params=payload_hhru)
        response.raise_for_status()
        vacancies_on_page = response.json().get('items')
        for vac in vacancies_on_page:
            vacancies.append(vac)
    return vacancies


def create_language_info_hhru(langs: list, city: int) -> dict:
    """Создаем словарь с информацией о вакансиях по языкам программирования"""
    logger.info(f'Отправляем запросы к hh.ru')
    payload_hhru = {"area": city}
    result = {}
    for lang in langs:
        result[lang] = get_language_hhru(lang, payload_hhru)
    return result
