# main.py
import time
import requests
import xml.etree.ElementTree as ET
from ngrams import extract_ngrams_from_snippets, save_counter_csv

HH_URL = "https://api.hh.ru/vacancies"
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

CITY_IDS = {
    "Москва": 1,
    "Санкт-Петербург": 2,
    "Екатеринбург": 66,
    "Пермь": 69,
    "Россия": 113
}


def get_cbr_rates():
    resp = requests.get(CBR_URL, timeout=10)
    resp.encoding = "windows-1251"
    root = ET.fromstring(resp.text)
    rates = {"RUB": 1.0, "RUR": 1.0}
    for valute in root.findall("Valute"):
        code = valute.find("CharCode").text
        nominal = int(valute.find("Nominal").text)
        value = float(valute.find("Value").text.replace(",", "."))
        rates[code] = value / nominal
    return rates


def fetch_all_vacancies(text, per_page=100, max_pages=None, sleep_between=0.2, area=None):
    params = {"text": text, "per_page": per_page, "page": 0}
    if area:
        params["area"] = area

    resp = requests.get(HH_URL, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()

    total = j.get("found", 0)
    pages = j.get("pages", 0)
    if max_pages is not None:
        pages = min(pages, max_pages)

    all_items = j.get("items", [])

    for page in range(1, pages):
        params["page"] = page
        time.sleep(sleep_between)
        resp = requests.get(HH_URL, params=params, timeout=10)
        resp.raise_for_status()
        j = resp.json()
        all_items.extend(j.get("items", []))

    return all_items, total


def convert_to_rub(amount, currency, rates):
    if currency is None or currency not in rates:
        return None
    return amount * rates[currency]


def extract_salary_rub(salary_obj, rates):
    if not salary_obj:
        return None
    s_from = salary_obj.get("from")
    s_to = salary_obj.get("to")
    cur = salary_obj.get("currency")
    if s_from is not None and s_to is not None:
        value = (s_from + s_to) / 2.0
    elif s_from is not None:
        value = s_from
    elif s_to is not None:
        value = s_to
    else:
        return None
    return convert_to_rub(value, cur, rates)


def compute_average_from_list(values):
    if not values:
        return None
    return sum(values) / len(values)


def task_a(rates):
    query = input("Введите название вакансии: ").strip()
    if not query:
        print("Пустой запрос. Отмена.")
        return

    print(f"Ищу вакансии: {query} ...")
    vacancies, total_found = fetch_all_vacancies(query, per_page=100, max_pages=None)
    print(f"Всего вакансий найдено по запросу: {total_found}")

    salaries_rub = []
    for v in vacancies:
        s_rub = extract_salary_rub(v.get("salary"), rates)
        if s_rub is not None:
            salaries_rub.append(s_rub)

    avg = compute_average_from_list(salaries_rub)
    if avg is None:
        print("Не найдено вакансий с конвертируемой зарплатой.")
    else:
        print(f"\nСредняя зарплата по вакансии '{query}': {avg:,.2f} RUB")
        print(f"Учтено вакансий с зарплатой: {len(salaries_rub)}")


def task_b(rates):
    print("\nСредняя зарплата Python-разработчика по городам:")
    for city, area_id in CITY_IDS.items():
        vacs, _ = fetch_all_vacancies("Python", per_page=100, max_pages=None, area=area_id)
        salaries = [extract_salary_rub(v.get("salary"), rates) for v in vacs if extract_salary_rub(v.get("salary"), rates) is not None]
        avg = compute_average_from_list(salaries)
        if avg is None:
            print(f"{city}: нет данных")
        else:
            print(f"{city}: {avg:,.2f} RUB (учтено {len(salaries)} вакансий)")


def task_c():
    query = input("Введите вакансию для анализа n-грамм (обязательно): ").strip()
    if not query:
        print("Нужно ввести название вакансии для извлечения n-грамм.")
        return

    print(f"\nИзвлекаю n-граммы для вакансий: {query} ...")
    vacancies, _ = fetch_all_vacancies(query, per_page=100, max_pages=1)
    if not vacancies:
        print("Вакансии не найдены.")
        return

    # ВСЕ n-граммы (для сохранения)
    all_ngrams = extract_ngrams_from_snippets(vacancies, top_k=None)

    # ТОЛЬКО ТОП-10 (для вывода)
    top_ngrams = extract_ngrams_from_snippets(vacancies, top_k=10)

    for n in (1, 2, 3):
        print(f"\nТоп-10 {n}-грамм:")
        for gram, count in top_ngrams[n]:
            print(f"{gram}: {count}")

    # Сохраняем ВСЕ n-граммы в csv
    save_counter_csv(all_ngrams[1], "ngrams_1.csv")
    save_counter_csv(all_ngrams[2], "ngrams_2.csv")
    save_counter_csv(all_ngrams[3], "ngrams_3.csv")

    print("\nЧастотные словари сохранены в файлы ngrams_1.csv, ngrams_2.csv, ngrams_3.csv")


def main():
    rates = get_cbr_rates()

    while True:
        print("\nВыберите действие:")
        print("1 — Средняя зарплата по вакансии (задача a)")
        print("2 — Средняя зарплата Python-разработчика по городам (задача b)")
        print("3 — Построение частотного словаря N-грамм (задача c)")
        print("0 — Выход")

        choice = input("Введите номер: ").strip()

        if choice == "1":
            task_a(rates)
        elif choice == "2":
            task_b(rates)
        elif choice == "3":
            task_c()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()
