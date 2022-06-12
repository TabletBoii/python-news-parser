import datetime
import time
import numpy
from requests_html import HTMLSession
from db_connection import connection
from urllib.parse import urlparse
import dateparser


def date_converter(raw_date_string):
    replace_list = ['Сегодня', 'Вчера']
    for forbidden_word in replace_list:
        raw_date_string = raw_date_string.replace(forbidden_word, "")
    return raw_date_string


db_cursor = connection.cursor()

parsing_session = HTMLSession()

site_info = ""
info_array = []

db_cursor.execute("SELECT * FROM resource")

for x in db_cursor:
    info_array.append(numpy.asarray(x))

for i in range(len(info_array)):
    get_parent = parsing_session.get(info_array[i][2])

    parsed_parent_uri = urlparse(info_array[i][2])
    parent_uri = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_parent_uri)

    news_link = get_parent.html.xpath(info_array[i][3])
    for j in range(15):
        parsed_uri_path = urlparse(news_link[j]).path
        res_uri = parent_uri + parsed_uri_path

        get_news_info = parsing_session.get(res_uri)

        news_title = get_news_info.html.find(info_array[i][5], first=True)
        news_content_list = get_news_info.html.find(info_array[i][4], first=True)
        
        news_date_raw = get_news_info.html.find(info_array[i][6], first=True)
        news_date_raw = news_date_raw.text

        news_date_formatted = news_date_raw.replace(".", "-")

        news_date_formatted = date_converter(news_date_formatted)
        news_date_converted = dateparser.parse(date_converter(news_date_formatted), settings={'DATE_ORDER': 'YMD'})

        news_unix_datetime = time.mktime(news_date_converted.timetuple()) * 1000

        current_date = datetime.datetime.now()
        add_unix_datetime = time.mktime(current_date.timetuple()) * 1000
        try:
            db_cursor.execute(
                "INSERT INTO items(res_id, link, title, content, nd_date, s_date, not_date) VALUES(%s, %s, %s, %s, "
                "%s, %s, %s)", (info_array[i][0], res_uri, news_title.text, news_content_list.text,
                                news_unix_datetime, add_unix_datetime, news_date_converted))
            connection.commit()
        except Exception as e:
            print(e)

connection.close()
