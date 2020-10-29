from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import date
import time
from database import DbCluj


cluj_db = DbCluj()


def main():
    num_of_processed_pages = 1
    # Instantiate webdriver using headless Chrome broswer
    options = Options()
    # options.headless = True
    dr = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    # URL for real estate headers in Cluj-Napoca, Romania
    dr.get('https://www.imobiliare.ro/vanzare-apartamente/cluj-napoca')
    # Wait for cookie pop-up then click OK
    time.sleep(7)
    dr.find_element_by_css_selector("#modalCookies > div > div > div > div.explicatie > div.row.butoane-actiune.vizibil-informare > div:nth-child(2) > a").click()
    # Get page source and pass it to beautifulsoup
    source = dr.page_source
    soup = BeautifulSoup(source, "html.parser")
    # Get location, characteristics and price from each header as list and insert it into db
    for rec_list in get_all_info(soup):
        try:
            cluj_db.insert_cluj_estate_record(rec_list)
        except:
            print('Could not insert record')
    # Get the last page number and crawl through all the pages to insert header information into db
    for page in range(2, get_last_page_number(soup)):
        time.sleep(5)
        base_url = 'https://www.imobiliare.ro/vanzare-apartamente/cluj-napoca?pagina='
        dr.get(base_url + str(page))
        source_page = dr.page_source
        soup_page = BeautifulSoup(source_page, "html.parser")
        for record_list in get_all_info(soup_page):
            try:
                cluj_db.insert_cluj_estate_record(record_list)
            except:
                print('Could not insert record')
        num_of_processed_pages += 1
        print(num_of_processed_pages)


# Get location as "Region, City" Ex: "Manastur, Cluj-Napoca"
def get_location_list(soupObj):
    localisations_list = []
    localisations_div = soupObj.find_all('div', {'class': 'localizare'})
    for item in localisations_div:
        localisations_list.append(list(item.text.split('\n')))
    localisations_list_formatted = [(list(int(x) if x.isdigit() else x.strip().replace(' zona ', '') for x in _ if x)) for _ in
                                    localisations_list]

    return localisations_list_formatted


# Get characteristics: number of rooms, dimension, level, architecture
def get_characteristics_list(soupObj):
    characteristics_list = []
    characteristics_ul = soupObj.find_all('ul', {'class': 'caracteristici'})
    for item in characteristics_ul:
        characteristics_list.append(list(item.text.split('\n')))
    characteristics_list_formatted = [(list(int(x) if x.isdigit() else x.strip().replace(' camere', '').replace('o camera', '1').replace(' mp utili', '').replace('o cameră', '1') for x in _ if x)) for _ in
                                      characteristics_list]
    # Remove duplicate and irrelevant data for this analysis
    for elem in characteristics_list_formatted:
        if len(elem) == 7:
            elem.pop(1)
            elem.pop(4)
        if 'Bloc nou' in elem:
            elem.remove('Bloc nou')

    return characteristics_list_formatted


# Get price number and currency type
def get_prices_list(soupObj):
    prices_list = []
    prices_div = soupObj.find_all('div', {'class': 'pret'})
    for item in prices_div:
        prices_list.append(list(item.text.split('\n')))
    prices_list_formatted = [(list(int(x) if x.isdigit() else x.strip() for x in _ if x)) for _ in prices_list]

    return prices_list_formatted


# Get location, characteristics, price plus the date when the information was scraped as list of lists
def get_all_info(soupObj):
    local = get_location_list(soupObj)
    charact = get_characteristics_list(soupObj)
    prices = get_prices_list(soupObj)
    scraped_date = [date.today().strftime("%Y/%m/%d")]
    all_info = []
    for (l, c ,p) in zip(local, charact, prices):
        all_info.append(l + c + p + scraped_date)

    return all_info


def get_last_page_number(soupObj):
    pages = soupObj.find_all('a', {'class': 'butonpaginare'})[-2]

    return int(pages.text)


main()





