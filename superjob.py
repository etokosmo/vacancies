from statistics import mean

import requests

URL_SUPERJOB = 'https://api.superjob.ru/2.0/vacancies/'
HEADERS_SUPERJOB = {}
PAYLOAD_SUPERJOB = {
    'town': 'Москва',
    'page': 0,
    'count': 100
}


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


def get_language_superjob(lang: str) -> dict:
    """Получаем характеристики вакансий по языку программирования"""
    processed_response = get_response_superjob(lang).json()
    vacancies = get_all_vacancies_superjob(processed_response)
    salaries = []
    for vacancy in vacancies:
        if salary := predict_rub_salary_for_superjob(vacancy):
            salaries.append(salary)
    language = {'vacancies_found': get_count_vacancies(processed_response),
                "vacancies_processed": len(salaries),
                "average_salary": int(mean(salaries))
                }
    return language


def get_response_superjob(lang: str) -> requests.models.Response:
    """Отправляем запрос на hh.ru для получения вакансий для языка, в которых указана зарплата"""
    PAYLOAD_SUPERJOB['keyword'] = f'Программист {lang}'
    response = requests.get(URL_SUPERJOB, headers=HEADERS_SUPERJOB, params=PAYLOAD_SUPERJOB)
    response.raise_for_status()
    return response


def get_all_vacancies_superjob(content: dict) -> list:
    """Возвращаем список всех вакансий для языка, в которых указана зарплата"""
    vacancies = []
    PAYLOAD_SUPERJOB['page'] = 0
    while True:
        vacancies_on_page = content.get('objects')
        for vacancy in vacancies_on_page:
            vacancies.append(vacancy)

        if content.get('more'):
            PAYLOAD_SUPERJOB['page'] += 1
            response = requests.get(URL_SUPERJOB, headers=HEADERS_SUPERJOB, params=PAYLOAD_SUPERJOB)
            response.raise_for_status()
            content = response.json()
        else:
            break
    return vacancies


def create_language_info_superjob(langs: list, api_token: str) -> dict:
    """Создаем словарь с информацией о вакансиях по языкам программирования"""
    HEADERS_SUPERJOB['X-Api-App-Id'] = api_token
    result = {}
    for lang in langs:
        result[lang] = get_language_superjob(lang)
    return result
