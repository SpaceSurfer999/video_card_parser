import re
import csv
import json
import time
import datetime
import math
from selenium import webdriver
# from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


def get_card_link(search='rtx3080'):
    # --- получаем время и создаем хром драйвер ---
    currtime = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    option = webdriver.ChromeOptions()
    # useragent = UserAgent(verify_ssl=False)
    option.headless = True

    option.add_argument('--disable-notifications')
    option.add_argument("disable-popup-blocking")
    # option.add_argument('--no-sandbox')
    option.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/103.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(
        service=Service(r'G:\Coding\Python_project\Scraping\venv\Chromedriver\chromedriver.exe'),
        options=option
    )  # driver.fullscreen_window()
    num = 1
    url = f'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?q={search}&p={num}'
    driver.get(url=url)
    driver.implicitly_wait(10)

    items = driver.find_element(By.CSS_SELECTOR, '[class="products-count"]').text  #Получаем количество найденных товаров
    items_di = ' '.join(re.findall(r'\d+', items))       #переводим в цифры

    page_count = math.ceil(int(items_di)/18) # получаем количество страниц

    # --- получаем данные, если с товарами всего 1 странца ---
    new_new_name = []
    new_new_price = []
    if page_count == 1:

        new_new_price = driver.find_elements(By.CSS_SELECTOR, value='[class="product-buy__price"]')
        new_new_name = driver.find_elements(By.CSS_SELECTOR, value='[class="catalog-product__name ui-link ui-link_black"]')

        # print('Страниц с товаром = ', page_count)

    # --- получаем данные, если с товарами несколько страниц ---
    else:

        num = 1
        while num < page_count+1:
            time.sleep(3)
            driver = webdriver.Chrome(
                service=Service(r'G:\Coding\Python_project\Scraping\venv\Chromedriver\chromedriver.exe'),
                options=option
            )
            url = f'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?q={search}&p={num}'
            driver.get(url=url)
            driver.implicitly_wait(10)

            new_price = driver.find_elements(By.CSS_SELECTOR,
                                             value='[class="product-buy__price"]')
            new_new_price.append(new_price)
            new_name = driver.find_elements(By.CSS_SELECTOR,
                                            value='[class="catalog-product__name ui-link ui-link_black"]')
            new_new_name.append(new_name)

            num += 1
        new_new_price = [x for l in new_new_price for x in l]
        new_new_name = [x for l in new_new_name for x in l]
        # print('Страниц с товаром = ',page_count)

    # --- создаем словарь ---
    dic = {}
    new_price_txt = []
    for i in new_new_price:
        w = i.text
        new_price_txt.append(w)
        # print(new_price_txt)
    new_name_txt = []
    for i in new_new_name:
        n = i.text
        part = n.partition('[')[0]
        new_name_txt.append(part)
    # print(new_name_txt)
    for i in range(0, len(new_new_price)):
        dic = dict(zip(new_name_txt, new_price_txt))

    # --- записываем данные в json файл и в файл CSV, что бы потом отправлять через TG бота ---
    with open('../venv/result_txt.json', 'w', encoding="utf-8") as file:
        json.dump(dic, file, indent=4, ensure_ascii=False)

    with open(f'{search}_{currtime}.csv', 'w', encoding='utf-16') as file:
        writer = csv.writer(file, delimiter='\t')

        for key, value in dic.items():
            writer.writerow([key, value])
    print(f'Найдено {items_di} видеокарт')


    return f'{search}_{currtime}.csv'


def main():
    get_card_link()


if __name__ == '__main__':
   main()