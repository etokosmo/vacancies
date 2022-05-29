from statistics import mean, StatisticsError

import requests

URL_HHRU = 'https://api.hh.ru/vacancies'
HEADERS_HHRU = {
    'User-Agent': 'api-test-agent'
}
PAYLOAD_HHRU = {}


def predict_rub_salary_hhru(vac: dict) -> int | None:
    """Получаем среднюю зарплату по профессии"""
    salary = vac.get('salary')
    if salary.get('currency') != 'RUR':
        return None
    min_salary = salary.get('from')
    max_salary = salary.get('to')
    if min_salary and max_salary:
        return mean([max_salary, max_salary])
    if min_salary:
        return min_salary * 1.2
    if max_salary:
        return max_salary * 0.8


def get_count_vacancies_hhru(content: dict) -> int:
    """Получаем количество вакансий по языку"""
    return content.get('found')


def get_language_hhru(lang: str) -> dict:
    """Получаем характеристики вакансий по языку программирования"""
    processed_response = get_response_hhru(lang).json()
    vacancies = get_all_vacancies_hhru(processed_response)
    salaries = []
    for vacancy in vacancies:
        if salary := predict_rub_salary_hhru(vacancy):
            salaries.append(salary)
    try:
        svg_lang_salary = int(mean(salaries))
    except StatisticsError:
        svg_lang_salary = 0
    language = {'vacancies_found': get_count_vacancies_hhru(processed_response),
                "vacancies_processed": len(salaries),
                "average_salary": svg_lang_salary
                }
    return language


def get_response_hhru(lang: str) -> requests.models.Response:
    """Отправляем запрос на hh.ru для получения вакансий для языка, в которых указана зарплата"""
    PAYLOAD_HHRU['text'] = f'Программист {lang}'
    PAYLOAD_HHRU['only_with_salary'] = True
    response = requests.get(URL_HHRU, headers=HEADERS_HHRU, params=PAYLOAD_HHRU)
    response.raise_for_status()
    return response


def get_all_vacancies_hhru(content: dict) -> list:
    """Возвращаем список всех вакансий для языка, в которых указана зарплата"""
    pages = content.get('pages')
    vacancies = []
    for page in range(pages + 1):
        PAYLOAD_HHRU['page'] = page
        response = requests.get(URL_HHRU, headers=HEADERS_HHRU, params=PAYLOAD_HHRU)
        response.raise_for_status()
        vac_list = response.json().get('items')
        for vac in vac_list:
            vacancies.append(vac)
    return vacancies


def create_language_info_hhru(langs: list, city: int) -> dict:
    """Создаем словарь с информацией о вакансиях по языкам программирования"""
    PAYLOAD_HHRU["area"] = city
    result = {}
    for lang in langs:
        result[lang] = get_language_hhru(lang)
    return result
