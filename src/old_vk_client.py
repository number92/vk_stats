import sys
import time
import requests
from loguru import logger

from src.ads_df import AdStatistics, StatRow


class VkHelper:
    def __init__(self, app, version, acc_id, long_token, client_id):
        self.app = app
        self.version = version
        self.acc_id = acc_id
        self.token = long_token
        self.client_id = client_id
        self.df = AdStatistics()

    def _get_auth_params(self) -> dict:
        """Параметры для успешного запроса"""
        return {"access_token": self.token, "client_id": self.client_id, "v": self.version, "account_id": self.acc_id}

    def _split_keys_to_parts(self, keys: list, part_size=500) -> list:
        """Разделение списка ключей на части по 1000 элементов"""
        parts = []
        for i in range(0, len(keys), part_size):
            part = keys[i : i + part_size]
            parts.append(",".join(map(str, part)))
        return parts

    def get_ads(self) -> dict:
        try:
            logger.info("Запрос данных...")
            auth_params = self._get_auth_params()
            res = requests.get("https://api.vk.com/method/ads.getAds", params=auth_params)
            res.raise_for_status()
            response = res.json()
            ad_campaign_dict = {}
            for ad in response.get("response"):
                ad_campaign_dict[ad.get("campaign_id")] = StatRow(ad_id=ad.get("id"), compaign_id=ad.get("campaign_id"))
            return ad_campaign_dict
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP ошибка: {http_err}")
            raise ConnectionError("Ошибка при запросе к API") from http_err
        except Exception as err:
            logger.error(f"Ошибка: {err}")
            raise ConnectionError("Произошла ошибка") from err

    def get_campaign_names(self) -> tuple[dict, dict]:

        try:
            comp_ids_stat: dict[int, StatRow] = self.get_ads()
            logger.info("Получение имен компаний...")
            res = requests.get("https://api.vk.com/method/ads.getCampaigns", params=self._get_auth_params())
            response = res.json().get("response")
            company_dict = {item["id"]: item["name"] for item in response}
            for com_id, company in comp_ids_stat.items():
                company.compaign_name = company_dict.get(company.compaign_id)
            # stopped_here: нужно сопоставить id компаний из запроса и и comp_ids и записать
            # сделать полноценный dataclass с мапом полей и типов

        except Exception as err:
            logger.error(f"Ошибка{err}, {i}")
            raise KeyError(f"Ошибка при получение id компаний: {err}")
        return cmp_name_dict, ad_campaign_dict

    def data_proccesing(self, ad_campaign_dict: dict, date_from: str, date_to: str):
        ads_campaign_list = []
        ads_id_list = []
        ads_impressions_list = []
        ads_clicks_list = []
        ads_spent_list = []
        ads_day_list = []
        ads_reach_list = []
        ads_join_rate_list = []
        ads_link_to_clicks = []

        logger.debug("Запрос API: статистика компании...")
        try:
            ads_list = self._split_keys_to_parts(list(ad_campaign_dict.keys()))
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
                    r = requests.get("https://api.vk.com/method/ads.getStatistics", params=q_params)
                    data_stats = r.json().get("response")
                    for ad_id in data_stats:
                        for stat in ad_id.get("stats"):
                            if not stat:
                                return
                            ads_campaign_list.append(ad_campaign_dict[ad_id.get("id")])
                            ads_id_list.append(ad_id.get("id"))
                            ads_impressions_list.append(stat.get("impressions", 0))
                            ads_clicks_list.append(stat.get("clicks", 0))
                            spent = stat.get("spent", "0")
                            ads_spent_list.append(spent.replace(".", ","))
                            ads_day_list.append(stat.get("day"))
                            ads_reach_list.append(stat.get("reach", 0))
                            ads_link_to_clicks.append(stat.get("link_external_clicks", 0))
                            ads_join_rate_list.append(stat.get("join_rate", 0))
                    time.sleep(0.3)
                except KeyError:
                    logger.error(f'Ошибка в запросе API{r["content"]["error"]}')
                    continue
        except OSError as err:
            logger.error(f"Ошибка в запросе API{err}")
            raise ConnectionError("Не удалось установить соединение с сервером") from err
        if r.status_code != 200:
            logger.error(f"Статус запроса {r.status_code}")
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
            logger.info("Список данных пуст")
            sys.exit(0)

        return result
