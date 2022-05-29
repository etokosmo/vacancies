from environs import Env
from terminaltables import SingleTable

from hhru import create_language_info_hhru
from superjob import create_language_info_superjob


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

    SUPERJOB_API_TOKEN = env("SUPERJOB_API_TOKEN")
    languages = ['Python', 'Java', 'JavaScript', 'C', 'C#', 'C++', 'Ruby', 'Go', '1C']
    services = {
        'hhru': create_language_info_hhru(languages),
        'superjob': create_language_info_superjob(languages, SUPERJOB_API_TOKEN)
    }
    for service, content in services.items():
        print_table(content, service)


if __name__ == "__main__":
    main()
