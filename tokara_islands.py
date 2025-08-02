import pandas as pd
import os
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup


list_page_url_template = "https://earthquake.tenki.jp/bousai/earthquake/center/798/"
def create_list_page_url(page_number: int) -> str:
    if page_number == 1:
        return list_page_url_template
    else:
        return list_page_url_template + f"page-{page_number}.html"


def tr_happened_time(ht: str) -> datetime:
    return datetime.strptime(ht, "%Y-%m-%d-%H-%M-%S.html")


def tr_lat(lat: str) -> float:
    ptn = re.compile(r"北緯(.*)度")
    lat = re.findall(ptn, lat)[0].strip()
    return float(lat)


def tr_lon(lon: str) -> float:
    ptn = re.compile(r"東経(.*)度")
    lon = re.findall(ptn, lon)[0].strip()
    return float(lon)


def tr_i_scale(i_scale: str) -> int:
    ptn = re.compile(r"震度([0-9].*?)")
    i_scale = re.findall(ptn, i_scale)[0].strip()
    return int(i_scale)


def tr_m_scale(m_scale: str) -> float:
    ptn = re.compile(r"M(.*)")
    m_scale = re.findall(ptn, m_scale)[0].strip()
    return float(m_scale)


if __name__ == "__main__":

    PAGES = 21
    all_list_page_url = [create_list_page_url(_) for _ in range(1, PAGES+1)]

    df_coll = []

    for list_page_url in all_list_page_url:
        print(f"PROCESSING: {list_page_url}")

        df = pd.read_html(list_page_url, encoding="utf-8")[0]
        df = df.iloc[:, 2:-1]
        df.columns = ["center", "magnitude"]

        response = requests.get(list_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.findAll('table')[0]

        links = []
        for tri, tr in enumerate(table.findAll('tr')):
            if tri == 0:  # テーブルのコラム名行は飛ばします
                continue
            link_td = tr.findAll('td')[1]  # 2列目のリンクのみが解析対象とします
            try:
                link = link_td.find('a')['href']
            except Exception:
                continue
            links.append("https://earthquake.tenki.jp" + link)

        print(f"START DETAIL CONVERT ...")
        happened_time, lat, lon, i_scale, m_scale, depth = [], [], [], [], [], []
        for link in links:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.findAll('table')[0]

            tr_coll = table.findAll('tr')
            happened_time.append(tr_happened_time(os.path.basename(link)))
            i_scale.append(tr_i_scale(tr_coll[2].find('td').text))
            lat.append(tr_lat(tr_coll[3].find('td').text))
            lon.append(tr_lon(tr_coll[4].find('td').text))
            m_scale.append(tr_m_scale(tr_coll[5].find('td').text))
            depth.append(tr_coll[6].find('td').text)

        df["happened_time"] = happened_time
        df["lat"] = lat
        df["lon"] = lon
        df["intensity_scale"] = i_scale
        df["magnitude_scale"] = m_scale
        df["depth"] = depth

        df_coll.append(df)

    df_all = pd.concat(df_coll, axis=0)

    df_all.to_csv(os.path.join("data", "data_in_21pages.csv"), index=False, encoding="cp932")
