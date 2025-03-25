[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
![PyInstaller](https://img.shields.io/badge/-PyInstaller-464646?style=flat-square)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat-square&logo=pandas&logoColor=white)
## VKstats
Приложение собирает статистику всех обьявлений во всех рекламных компаниях клиента и преобразует ее в csv-файл. 
### Содержание
- [Актуальность](#актуальность)
- [Выгружаемые данные](#выгружаемые-данные)
- [Инструкция](#инструкция)

## Выгружаемые данные
По умолчанию данные можно получить по дням за указанный период. 
В выгрузке вы найдете следующие поля:
- __campaign_id__ - ID рекламной компании
- __campaign_name__ - название компании
-  __ad_id__ - ID рекламного обьявления
- __impressions__ - просмотры
- __clicks__ - клики
- __spent__ - потраченные средства
- __date__ - дата
- __reach__ - охват
- __link_external_clicks__ - количество уникальных переходов по ссылкам
- __join_rate__ - вступления в группу

Полный список полей, представленных методом [ads.getStatistics](https://dev.vk.com/method/ads.getStatistics)

## Инструкция
1. Зарегистрируйте приложение в ВК.
   - Следуя [ссылке](https://vk.com/apps?act=manage), создайте приложение. ID этого приложения будет необходим для запросов.
2. Получение access token
   - добавьте ID_APP в ссылку
   ```
      https://oauth.vk.com/authorize?client_id=ВАШ ID_APP&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=ads&response_type=token&v=5.131
   ```
   - пройдите авторизацию и скопируйте значение ?access_token= из строки запроса, добавьте его в .env
4. Заполните .env настройками личного кабинета ВК. Пример для заполнения доступен в файле [.env.example](https://github.com/number92/loadfromVK/blob/main/.env.example).
   
3. После выполнения в текущей директории будет создан csv-файл.
