from statistics import mean, StatisticsError

import requests
from loguru import logger

URL_SUPERJOB = 'https://api.superjob.ru/2.0/vacancies/'


def predict_rub_salary_for_superjob(vac: dict) -> int | None:
    """Получаем среднюю зарплату по профессии"""
    if vac.get('currency') != 'rub':
        return None
    min_salary = vac.get('payment_from')
    max_salary = vac.get('payment_to')
    if min_salary and max_salary:
        return mean([max_salary, max_salary])
    if min_salary:
        return min_salary * 1.2
    if max_salary:
        return max_salary * 0.8


def get_count_vacancies(content: dict) -> int:
    """Получаем количество вакансий по языку"""
    return content.get('total')


def get_language_superjob(lang: str, headers_superjob: dict, payload_superjob: dict) -> dict:
    """Получаем характеристики вакансий по языку программирования"""
    processed_response = get_response_superjob(lang, headers_superjob, payload_superjob).json()
    vacancies = get_all_vacancies_superjob(processed_response, headers_superjob, payload_superjob)
    salaries = []
    for vacancy in vacancies:
        if salary := predict_rub_salary_for_superjob(vacancy):
            salaries.append(salary)
    try:
        svg_lang_salary = int(mean(salaries))
    except StatisticsError:
        logger.debug(f'Язык={lang}. Вакансий с зарплатой не найдено')
        svg_lang_salary = 0
    language = {'vacancies_found': get_count_vacancies(processed_response),
                "vacancies_processed": len(salaries),
                "average_salary": svg_lang_salary
                }
    logger.info(f'Language={lang}, info={language}')
    return language


def get_response_superjob(lang: str, headers_superjob: dict, payload_superjob: dict) -> requests.models.Response:
    """Отправляем запрос на hh.ru для получения вакансий для языка, в которых указана зарплата"""
    payload_superjob['keyword'] = f'Программист {lang}'
    response = requests.get(URL_SUPERJOB, headers=headers_superjob, params=payload_superjob)
    response.raise_for_status()
    return response


def get_all_vacancies_superjob(content: dict, headers_superjob: dict, payload_superjob: dict) -> list:
    """Возвращаем список всех вакансий для языка, в которых указана зарплата"""
    vacancies = []
    payload_superjob['page'] = 0
    while True:
        vacancies_on_page = content.get('objects')
        for vacancy in vacancies_on_page:
            vacancies.append(vacancy)

        if content.get('more'):
            payload_superjob['page'] += 1
            response = requests.get(URL_SUPERJOB, headers=headers_superjob, params=payload_superjob)
            response.raise_for_status()
            content = response.json()
        else:
            break
    return vacancies


def create_language_info_superjob(langs: list, api_token: str, city: str) -> dict:
    """Создаем словарь с информацией о вакансиях по языкам программирования"""
    logger.info(f'Отправляем запросы к superjob.ru')
    headers_superjob = {'X-Api-App-Id': api_token}
    payload_superjob = {'page': 0,
                        'count': 100,
                        'town': city
                        }
    result = {}
    for lang in langs:
        result[lang] = get_language_superjob(lang, headers_superjob, payload_superjob)
    return result
