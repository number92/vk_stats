import sys
import time
import requests
from requests.exceptions import HTTPError
from loguru import logger
from dataclasses import asdict
from src.ads_df import AdStatistics, StatRow
from core.config import URL


class VkHelper:
    def __init__(self, app, version, acc_id, long_token, client_id):
        self.app = app
        self.version = version
        self.acc_id = acc_id
        self.token = long_token
        self.client_id = client_id
        # self.df = AdStatistics()

    def _get_auth_params(self) -> dict:
        """Параметры для успешного запроса"""
        return {
            "access_token": self.token,
            "client_id": self.client_id,
            "v": self.version,
            "account_id": self.acc_id,
        }

    def _split_keys_to_parts(self, keys: list, part_size=500) -> list:
        """Разделение списка ключей на части по 1000 элементов"""
        parts = []
        for i in range(0, len(keys), part_size):
            end_slice = i + part_size
            part = keys[i:end_slice]
            parts.append(",".join(map(str, part)))
        return parts

    def get_ads(self) -> dict[int, StatRow]:
        """Возвращает соварь где ключ id компании , значение обьект StatRow"""

        logger.info("Запрос данных...")
        auth_params = self._get_auth_params()
        res = requests.get("https://api.vk.com/method/ads.getAds", params=auth_params)
        res.raise_for_status()
        response = res.json()
        if er := response.get("error"):
            if er.get("error_code") == 5:
                logger.error(f"HTTP ошибка: {er.get('error_msg')}")
                print(f"link for update token:\n {URL}")
                raise ConnectionError(er.get("error_msg"))
        ad_campaign_dict = {}
        for ad in response.get("response"):
            ad_campaign_dict[ad.get("campaign_id")] = StatRow(
                ad_id=ad.get("id"), campaign_id=ad.get("campaign_id")
            )
        return ad_campaign_dict

    def get_campaign_names(self) -> dict[int, dict]:

        try:
            comp_ids_stat = self.get_ads()
            logger.info("Получение имен компаний...")
            result_stat_rows = {}
            res = requests.get(
                "https://api.vk.com/method/ads.getCampaigns",
                params=self._get_auth_params(),
            )
            response = res.json().get("response")
            company_dict = {item["id"]: item["name"] for item in response}
            for com_id, company in comp_ids_stat.items():
                row = company.__dict__
                row.update({"campaign_name": company_dict.get(company.campaign_id)})
                company.campaign_name = company_dict.get(company.campaign_id)
                result_stat_rows[row.get("ad_id")] = row

        except Exception as err:
            logger.error(f"Ошибка{err}")
            raise KeyError(f"Ошибка при получение id компаний: {err}")
        return result_stat_rows

    def data_proccesing(self, stat_rows: dict[int, dict], date_from: str, date_to: str):
        df = AdStatistics()
        logger.debug("Запрос API: статистика компании...")
        try:
            ads_list = self._split_keys_to_parts(list(stat_rows.keys()))
            q_params = {
                "ids_type": "ad",
                "period": "day",
                "date_from": date_from,
                "date_to": date_to,
            }
            q_params.update(self._get_auth_params())
            for part in ads_list:
                try:
                    q_params.update({"ids": part})
                    r = requests.get(
                        "https://api.vk.com/method/ads.getStatistics", params=q_params
                    )
                    data_stats = r.json().get("response")
                    for ad in data_stats:
                        for stat in ad.get("stats"):
                            if not stat:
                                break
                            row = stat_rows.get(ad.get("id"))
                            for key in stat:
                                if key in row:
                                    row[key] = stat[key]
                                df.add_rows(row)
                    r.raise_for_status()
                    time.sleep(0.3)
                except HTTPError as er:
                    logger.error(f"Ошибка в запросе API {er}")

        except ConnectionError as err:
            logger.error(f"Ошибка в запросе API{err}")
            raise ConnectionError(
                "Не удалось установить соединение с сервером"
            ) from err

        dataframe = df.get_dataframe()

        if dataframe.empty:
            logger.info("Список данных пуст")
            sys.exit(0)

        return dataframe
