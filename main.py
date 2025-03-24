from src.old_vk_client import VkHelper
from core import config

vk_client = VkHelper(config.ID_APP, config.VERSION, config.ACCOUNT_ID, config.ACCESS_TOKEN, config.ID_CLIENT)


def main():
    try:

        companies: dict = vk_client.get_campaign_names()
        process = vk_client.data_proccesing(companies, config.DATE_FROM, config.DATE_TO)
        # dataframe = vk_client.dataframe_formation(process)
        # dataframe.to_csv(f"loading_({TODAY})_{TIME}.csv")

    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
