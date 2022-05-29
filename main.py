from environs import Env
from terminaltables import SingleTable

from hhru import create_language_info_hhru
from superjob import create_language_info_superjob

CITIES = {"Москва": {
    "town": "Москва",
    "area": 1
    }
}


def print_table(content: dict, title: str, city: str = 'Moscow') -> None:
    """Выводим красивую информативную таблицу"""
    header = ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
    body = [[lang, content.get(lang).get("vacancies_found"), content.get(lang).get("vacancies_processed"),
             content.get(lang).get("average_salary")] for lang in content]
    body.insert(0, header)

    table_instance = SingleTable(body, f'{title} {city}')
    print(table_instance.table)
    print()


def main() -> None:
    """Парсим вакансии по Москве на hh.ru и superjob и выводим их в консоль"""
    env = Env()
    env.read_env()
    superjob_api_token = env("SUPERJOB_API_TOKEN")
    city = env("CITY", "Москва")
    hh_city = CITIES.get(city).get("area")
    sj_city = CITIES.get(city).get("town")
    languages = ['Python', 'Java', 'JavaScript', 'C', 'C#', 'C++', 'Ruby', 'Go', '1C']
    services = {
        'hhru': create_language_info_hhru(languages, hh_city),
        'superjob': create_language_info_superjob(languages, superjob_api_token, sj_city)
    }
    for service, content in services.items():
        print_table(content, service, city)


if __name__ == "__main__":
    main()
