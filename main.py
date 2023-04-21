import json
import time
import requests
from bs4 import BeautifulSoup
import re

file_name = "house_data.json"
headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

def read_data():
    try:
        house_data_file = open(file_name, "r")
        house_data = json.load(house_data_file)
    except FileNotFoundError:
        house_data = {}
    return house_data

def write_data(house_data):
    house_data_file = open(file_name, "w")
    json.dump(house_data, house_data_file, indent=4, ensure_ascii=False)
    house_data_file.close()

def find_housing_estate_detail(href, house_data):
    response = requests.get(href, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    name_info = soup.find("h1", attrs={"class":"main"})
    name = name_info.text.strip()
    all_infos = soup.find_all("span", attrs={"class":"xiaoquInfoContent"})
    for info in all_infos:
        if "户" in info.text:
            house_num = int(info.text[:-1])
            house_data[name] = house_num
    return house_data


def find_housing_estate_list(house_data, page):
    print(f"in page {page}\n")
    url = f"https://cd.ke.com/xiaoqu/pg{page}/"
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    all_links = soup.findAll("a", attrs={"class":"maidian-detail"})
    for link in all_links:
        link_class = link.get('class')
        if 'img' in link_class:
            continue
        #print(link_class)
        href = link.get('href')
        #print(href)
        time.sleep(1)
        house_data = find_housing_estate_detail(href, house_data)
    return house_data

# 城市一共有多少小区
def find_housing_estate_total_num():
    url = f"https://cd.ke.com/xiaoqu/pg1/"
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    total_h2 = soup.find("h2", attrs={"class":"total fl"})
    print(total_h2.text)
    ret = re.search('[0-9]+', total_h2.text)
    total = ret.group()
    return int(total)

def collect_data():
    # 读取文件
    house_data = read_data()
    print(house_data)
    for i in range(1, 101):
        house_data_new = find_housing_estate_list(house_data, i)
        # 写入文件
        write_data(house_data_new)

def cal_data():
    # 城市总社区数量
    housing_estate_total_num = find_housing_estate_total_num()
    house_data = read_data()
    data_estate_total = 0
    data_house_total = 0
    for value in house_data.values():
        data_estate_total += 1
        data_house_total += value
    print(f"城市中小区总数: {housing_estate_total_num}\n")
    print(f"统计的小区总数: {data_estate_total}\n")
    print(f"统计的总户数: {data_house_total}")

    if data_estate_total > 0:
        print(f"估计城市总套数: {int(housing_estate_total_num * data_house_total / data_estate_total)}")
    else:
        print("数据不足，无法估计")

if __name__ == "__main__":
    while(True):
        command = input("请输入命令\n 1. 爬取小区详细信息 \n2. 统计结果\nq. 离开")
        if command == 'q':
            break
        elif command == '1':
            collect_data()
        elif command == '2':
            cal_data()
        else:
            print("input error\n")



