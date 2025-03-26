import sys
import time
import requests
from requests.exceptions import HTTPError
from loguru import logger
from src.ads_df import AdStatistics, StatRow
from core.config import URL
from src.utils import ResponseEmptyException, raise_err_by_code


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

    def get_ads(self) -> dict[int, int]:
        """Возвращает соварь где ключ id обьявления , значение id campaign"""

        logger.info("Запрос данных...")
        auth_params = self._get_auth_params()
        req = requests.get("https://api.vk.com/method/ads.getAds", params=auth_params)
        response = req.json()
        if er := response.get("error"):
            raise_err_by_code(er)
        id_ads = {item["id"]: item["campaign_id"] for item in response.get("response")}
        if not id_ads:
            logger.error(response.get("response"))
            raise ResponseEmptyException(detail="Список обьявлений пуст")
        return id_ads

    def get_campaign_names(self) -> dict[int, str]:
        """Получение словаря id кампании : имя кампании"""

        logger.info("Получение имен компаний...")
        req = requests.get(
            "https://api.vk.com/method/ads.getCampaigns",
            params=self._get_auth_params(),
        )
        response = req.json()
        if er := response.get("error"):
            raise_err_by_code(er)
        company_dict = {item["id"]: item["name"] for item in response.get("response")}
        if not company_dict:
            raise ResponseEmptyException(detail="Список кампаний пуст")
        return company_dict

    def data_proccesing(self, date_from: str, date_to: str):
        df = AdStatistics()
        logger.debug("Запрос API: статистика компании...")
        ad_ids = self.get_ads()
        compaign_names = self.get_campaign_names()
        try:
            ads_list = self._split_keys_to_parts(list(ad_ids.keys()))
            q_params = {
                "ids_type": "ad",
                "period": "day",
                "date_from": date_from,
                "date_to": date_to,
            }
            q_params.update(self._get_auth_params())
            for part in ads_list:
                try:
                    time.sleep(1)
                    q_params.update({"ids": part})
                    r = requests.get(
                        "https://api.vk.com/method/ads.getStatistics", params=q_params
                    )
                    if er := r.json().get("error"):
                        raise_err_by_code(er)
                    data_stats = r.json().get("response")
                    if data_stats:

                        for ad in data_stats:
                            ad_stats = ad.get("stats", None)
                            if ad_stats:
                                for day in ad_stats:
                                    cmp_id = ad_ids.get(ad.get("id"))
                                    df_row = StatRow(
                                        ad_id=ad.get("id"),
                                        campaign_id=cmp_id,
                                        campaign_name=compaign_names.get(cmp_id),
                                    ).__dict__
                                    for key in day:
                                        if key in df_row:
                                            df_row.update({key: day[key]})
                                    df.add_rows(df_row)
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
        logger.info("Формирование датафрейма завершено")
        return dataframe
