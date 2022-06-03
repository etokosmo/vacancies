import os

from environs import Env
from loguru import logger
from terminaltables import SingleTable

from hhru import create_language_info_hhru
from superjob import create_language_info_superjob

CITIES = {
    "Москва": 1,
    "Санкт-Петербург": 2,
    "Екатеринбург": 3,
}
BASE_DIR = os.path.dirname(__file__) or '.'
PATH_TO_LOGS = os.path.join(BASE_DIR, 'logs', 'logs.log')


def print_table(content: dict, title: str, city: str) -> None:
    """Выводим красивую информативную таблицу"""
    header = [
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата"
    ]
    body = [
        [
            lang,
            content.get(lang).get("vacancies_found"),
            content.get(lang).get("vacancies_processed"),
            content.get(lang).get("average_salary")
        ] for lang in content
    ]
    body.insert(0, header)

    table_instance = SingleTable(body, f'{title} {city}')
    print(table_instance.table)
    print()


def main() -> None:
    """Парсим вакансии по Москве на hh.ru и superjob и выводим их в консоль"""
    logger.add(PATH_TO_LOGS, level='DEBUG')
    env = Env()
    env.read_env()
    superjob_api_token = env("SUPERJOB_API_TOKEN")
    city = env("CITY", "Москва")
    try:
        area = CITIES.get(city)
    except AttributeError:
        logger.error(f'Неправильно передан город')
        return None
    logger.info(
        f'Прием аргументов: city={city}, hh_city={area}, sj_city={city}')

    languages = [
        'Python',
        'Java',
        'JavaScript',
        'C',
        'C#',
        'C++',
        'Ruby',
        'Go',
        '1C'
    ]
    services = {
        'hhru': create_language_info_hhru(languages, area),
        'superjob': create_language_info_superjob(
            languages,
            superjob_api_token,
            city
        )
    }

    for service, content in services.items():
        print_table(content, service, city)


if __name__ == "__main__":
    main()
