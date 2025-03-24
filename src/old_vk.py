import os
import sys
import requests
import logging
import time

from http import HTTPStatus

from dotenv import load_dotenv, set_key

from pandas import DataFrame

from datetime import datetime, timedelta

dotenv_path = ".env"

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION", default="5.131")
ACCOUNT_ID: int = os.getenv("ACCOUNT_ID")
ID_CLIENT = os.getenv("ID_CLIENT")
ID_APP: int = os.getenv("ID_APP")
TODAY = datetime.today().strftime("%Y-%m-%d")
YESTERDAY = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
TIME = datetime.today().strftime("%H-%M-%S")
URL = (
    "https://oauth.vk.com/authorize?client_id="
    + f"{os.getenv('ID_APP')}&display=page&redirect_uri="
    + "https://oauth.vk.com/blank.html&scope="
    + f"ads&response_type=token&v={VERSION}"
)
help_text = [
    ", для пропуска шага нажмите Enter или введите новый ID: ",
    "ID приложения должен состоять цифр длиной 8 символов",
    "ID клиента должен состоять цифр длиной 10 символов",
    "ID рекламного кабинета должен состоять цифр длиной 10 символов",
]


class InvalidToken(Exception):
    pass


def read_input(arg):
    if arg == "ID_APP":
        new_id_app = ["ID_APP", f'{input("Вставьте ID приложения: ").strip()}']
        return new_id_app
    if arg == "ACCOUNT_ID":
        new_id_acc = ["ACCOUNT_ID", f'{input("Вставьте ID рекламного аккаунта: ").strip()}']
        return new_id_acc
    if arg == "ID_CLIENT":
        read = input("Вставьте ID клиента: ").strip()
        new_id_client = ["ID_CLIENT", f"{read}"]
        return new_id_client


def check_input(value):
    if value[0] == "ID_APP":
        return value[1].isdigit() and len(value[1]) == 8
    if value[0] == "ID_CLIENT" or "ACCOUNT_ID":
        return value[1].isdigit() and len(value[1]) == 10


def check_settings():
    print("Нужно ли изменить настройки личного кабинета?")
    yes_or_no = input('Введите "yes" или "no" : ').strip().lower()
    if yes_or_no == "yes":
        new_id_app = ["ID_APP", f'{input(f"ID приложения: {ID_APP}{help_text[0]}").strip()}']
        if len(new_id_app[1]) != 0:
            while check_input(new_id_app) is False:
                print(help_text[1])
                time.sleep(0.4)
                new_id_app = read_input("ID_APP")
            set_key(dotenv_path, "ID_APP", new_id_app[1])

        mess = f"ID рекламного аккаунта: {ACCOUNT_ID}{help_text[0]}"
        new_id_acc = ["ACCOUNT_ID", f"{input(mess).strip()}"]
        if len(new_id_acc[1]) != 0:
            while check_input(new_id_acc) is False:
                print(help_text[2])
                time.sleep(0.4)
                new_id_acc = read_input("ACCOUNT_ID")
            set_key(dotenv_path, "ACCOUNT_ID", new_id_acc[1])

        new_id_client = ["ID_CLIENT", f'{input(f"ID клиента: {ID_CLIENT}{help_text[0]}").strip()}']
        if len(new_id_client[1]) != 0:
            while check_input(new_id_client) is False:
                print(help_text[3])
                time.sleep(0.4)
                new_id_client = read_input("ID_CLIENT")
            set_key(dotenv_path, "ID_CLIENT", new_id_client[1])
    elif yes_or_no == "no":
        return
    else:
        check_settings()


def refresh_token():
    print(f"Перейдите по ссылке и авторизуйтесь \n \n {URL}")
    time.sleep(0.3)
    print('\n Скопируйте адресную строку от "access_token=" до "&expires_in"')
    token = input("Вставьте строку сюда: ")
    print("Срок жизни токена 24 часа")
    set_key(dotenv_path, "ACCESS_TOKEN", token)
    time.sleep(0.4)
    r = requests.get(
        "https://api.vk.com/method/ads.getAds",
        params={
            "access_token": token,
            "client_id": ID_CLIENT,
            "v": VERSION,
            "account_id": ACCOUNT_ID,
        },
    )
    if r.json().get("error"):
        print(f'Ошибка: {r.json()["error"]["error_msg"]}')
        time.sleep(3)
    data = r.json()["response"]
    return data


def get_api_answer():
    try:
        if ACCESS_TOKEN == "None":
            refresh_token()
        logging.info("Запрос данных...")
        r = requests.get(
            "https://api.vk.com/method/ads.getAds",
            params={
                "access_token": os.getenv("ACCESS_TOKEN"),
                "client_id": ID_CLIENT,
                "v": VERSION,
                "account_id": ACCOUNT_ID,
            },
        )
        if r.json().get("error"):
            print(f'Ошибка: {r.json()["error"]["error_msg"]}')
            try:
                return refresh_token()
            except InvalidToken(f'Ошибка: {r.json()["error"]["error_msg"]}'):
                return
    except OSError as err:
        if r.status_code != HTTPStatus.OK:
            logging.error(f"Статус запроса {r.status_code}")
            raise ConnectionError(f"Статус запроса {r.status_code}")
        logging.error(f"Ошибка в запросе API{err}")
        raise ConnectionError("Не удалось установить соединение с сервером") from err
    else:
        logging.debug("Ответ от Api получен")
        data = r.json()["response"]
        return data


def get_campaign_id(data):
    ad_campaign_dict = {}
    try:
        logging.info("Получение id компаний...")
        for i in range(len(data)):
            ad_campaign_dict[data[i]["id"]] = data[i]["campaign_id"]
    except KeyError as err:
        logging.error(f"Ошибка{err}, {i}")
        raise KeyError(f"Ошибка при получение id компаний: {err}")
    return ad_campaign_dict


def data_proccesing(ad_campaign_dict):
    ads_campaign_list = []
    ads_id_list = []
    ads_impressions_list = []
    ads_clicks_list = []
    ads_spent_list = []
    ads_day_list = []
    ads_reach_list = []
    ads_join_rate_list = []
    ads_link_to_clicks = []
    period = {
        "date_from": input('Введите дату начала периода в формате "2023-06-25": '),
        "date_to": input('Введите дату конца периода в формате "2023-06-25": '),
    }
    logging.debug("Запрос API: статистика компании...")
    try:
        for ad_id in ad_campaign_dict:
            r = requests.get(
                "https://api.vk.com/method/ads.getStatistics",
                params={
                    "access_token": ACCESS_TOKEN,
                    "client_id": ID_CLIENT,
                    "v": VERSION,
                    "account_id": ACCOUNT_ID,
                    "ids_type": "ad",
                    "ids": ad_id,
                    "period": "day",
                    "date_from": period["date_from"],
                    "date_to": period["date_to"],
                },
            )
            try:
                data_stats = r.json()["response"]
                for i in range(len(data_stats)):
                    for j in range(len(data_stats[i]["stats"])):
                        if len(data_stats[i]["stats"]) == 0:
                            return
                        ads_campaign_list.append(ad_campaign_dict[ad_id])
                        ads_id_list.append(data_stats[i]["id"])
                        ads_impressions_list.append(data_stats[i]["stats"][j].get("impressions", 0))
                        ads_clicks_list.append(data_stats[i]["stats"][j].get("clicks", 0))
                        spent = data_stats[i]["stats"][j].get("spent", "0")
                        ads_spent_list.append(spent.replace(".", ","))
                        ads_day_list.append(data_stats[i]["stats"][j]["day"])
                        ads_reach_list.append(data_stats[i]["stats"][j].get("reach", 0))
                        ads_link_to_clicks.append(data_stats[i]["stats"][j].get("link_external_clicks", 0))
                        ads_join_rate_list.append(data_stats[i]["stats"][j].get("join_rate", 0))
                time.sleep(0.6)
            except KeyError:
                logging.error(f'Ошибка в запросе API{r["content"]["error"]}')
                continue
    except OSError as err:
        logging.error(f"Ошибка в запросе API{err}")
        raise ConnectionError("Не удалось установить соединение с сервером") from err
    if r.status_code != HTTPStatus.OK:
        logging.error(f"Статус запроса {r.status_code}")
        raise ConnectionError(f"Статус запроса {r.status_code}")

    result = (
        ads_campaign_list,
        ads_id_list,
        ads_impressions_list,
        ads_clicks_list,
        ads_spent_list,
        ads_day_list,
        ads_reach_list,
        ads_link_to_clicks,
        ads_join_rate_list,
    )
    if len(result[1]) == 0:
        logging.info("Список данных пуст")
        sys.exit(0)
    return result


def dataframe_formation(process):
    try:
        logging.info("Формирование датафреймов")
        df = DataFrame()
        df["campaign_id"] = process[0]
        df["ad_id"] = process[1]
        df["impressions"] = process[2]
        df["clicks"] = process[3]
        df["spent"] = process[4]
        df["date"] = process[5]
        df["reach"] = process[6]
        df["link_external_clicks"] = process[7]
        df["join_rate"] = process[8]

    except KeyError as err:
        logging.error(err)
        ("Ошибка формирования датафрейма")
    return df


# def main():
#     try:
#         check_settings()
#         response = get_api_answer()
#         camp_id = get_campaign_id(response)
#         process = data_proccesing(camp_id)
#         dataframe = dataframe_formation(process)
#         dataframe.to_csv(f"loading_({TODAY})_{TIME}.csv")
#         logging.info("Выгрузка завершена, csv-файл создан")
#     except Exception as err:
#         print(err)


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO,
#         stream=sys.stdout,
#         encoding="utf-8",
#         format="%(asctime)s, %(levelname)s, %(message)s",
#     )
#     main()
