from statistics import mean


def predict_rub_salary(currency: str,
                       min_salary: int | None,
                       max_salary: int | None) -> float | None:
    """Получаем среднюю зарплату по профессии"""
    if currency not in ('rub', 'RUR'):
        return None
    if min_salary and max_salary:
        return mean([max_salary, max_salary])
    if min_salary:
        return min_salary * 1.2
    if max_salary:
        return max_salary * 0.8
