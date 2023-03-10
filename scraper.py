import random
from datetime import date

from bs4 import BeautifulSoup
import csv
import requests

product_id = 0


def get_soup_init(url, print_response=True):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"}
    request = requests.get(url, headers=headers)
    if print_response:
        print(f'{request}: {url}')
    html_text = request.text
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup


def get_categories(num_of_categories=None):
    url = 'https://www.zalando.pl/odziez-meska/'
    soup = get_soup_init(url)
    category_list = soup.find('ul', class_='_0AtdH3')
    categories_from_list = category_list.find_all('li', class_='_4oK5GO')
    categories = []
    for category in categories_from_list:
        category_url = category.find('a')['href']
        category_name = category.find('span').text
        categories.append({'name': category_name, 'url': category_url})
        if num_of_categories is not None and len(categories) == num_of_categories:
            break

    return categories


def get_product_description(product_url):

    def find_in_string(string, label_start, label_end):
        index_start = string.find(label_start)
        if index_start == -1:  # string not found
            return ''
        index_start += len(label_start)
        index_end = index_start + string[index_start:].find(label_end)
        return string[index_start:index_end].strip('"')

    def get_label(string):
        label = find_in_string(string, '"label":', ',')
        return label

    def get_key_value(string, key):
        value = find_in_string(string, f'"key":"{key}","value":', '}')
        return value

    def get_key_values_from(string, key_list):
        description = ''
        label = get_label(string)
        if label != '':
            description += f'<br /><b>{label}</b><br />'
        for key in key_list:
            value = get_key_value(string, key)
            if key == 'Materia??':
                value = value.replace('%25', '%')
            if value != '':
                description += f'{key}: {value}<br />'
        return description

    description = ''

    product_soup = get_soup_init(product_url)
    text = product_soup.prettify()

    index_material_care = text.find('{"id":"material_care"')
    index_details = text.find('{"id":"details"')
    index_size_fit = text.find('{"id":"size_fit"')
    index_sustainability = text.find('{"id":"sustainability"')

    text_material_care = text[index_material_care:index_details]
    keys_material_care = ['Materia??', 'Struktura/rodzaj materia??u', 'Zawiera elementy sk??rzane',
                          'Wskaz??wki piel??gnacyjne']
    description += get_key_values_from(text_material_care, keys_material_care)

    text_details = text[index_details:index_size_fit]
    keys_details = ['Rodzaj dekoltu', 'Kszta??t ko??nierza', 'Kaptur', 'Stan', 'Zapi??cie', 'Kieszenie', 'Przezroczysto????',
                    'Wz??r', 'Szczeg????y', 'Numer produktu']
    description += get_key_values_from(text_details, keys_details)

    text_size_fit = text[index_size_fit:index_sustainability]
    keys_size_fit = ['Wzrost modela', 'Fason', 'Kszta??t', 'D??ugo????', 'D??ugo???? r??kawa', 'Ca??a d??ugo????']
    description += get_key_values_from(text_size_fit, keys_size_fit)

    return description


def get_products(category, num_of_products, save_images=False, img_path=''):
    products = []
    max_pages = 20
    for page in range(1, max_pages):
        if page > 1:
            url = f'https://www.zalando.pl{category["url"]}?p={page}'
        else:
            url = f'https://www.zalando.pl{category["url"]}'
        soup = get_soup_init(url)
        divs = soup.find_all('div', class_='DT5BTM w8MdNG cYylcv _1FGXgy _75qWlu iOzucJ JT3_zV vut4p9')
        for div in divs:
            try:
                product_url = div.find('a')['href']
                img_url = div.find('img')['src']
                brand = div.find_all('h3')[0].text
                name = div.find_all('h3')[1].text
                price = div.find('p')
                price = price.text.replace(',', '.').replace('z??', '').replace('od', '').strip()
                price = float(price)
                # description = get_product_description(product_url)
                description = ''
            except:
                continue

            global product_id
            product_id += 1

            if save_images:
                img_data = requests.get(img_url).content
                with open(f'{img_path}{product_id}.jpg', 'wb') as handler:
                    handler.write(img_data)

            if category['name'] == 'Bluzy':
                discount = 10
            elif category['name'] == 'Koszule':
                discount = 25
            else:
                discount = 0

            product = {
                'ID': product_id,
                'Aktywny(0 lub 1)': 1,
                'Nazwa': name,
                'Kategorie(x, y, z...)': category['name'],
                'Cena bez podatku. (netto)': round(price / 1.23),
                # 'Cena zawiera podatek. (brutto)': price,
                'ID regu??y podatku': 1,
                'Koszt w??asny': round((price / 1.23) / 1.1),
                'W sprzeda??y(0 lub 1)': 1,
                'Warto???? rabatu': '',
                'Procent rabatu': discount,
                'Rabat od dnia(rrrr-mm-dd)': date.today(),
                'Rabat do dnia(rrrr-mm-dd)': date(2022, 12, 24),
                'Indeks #': '',
                'Kod dostawcy': '',
                'Dostawca': '',
                'Marka': brand,
                'Kod EAN13': '',
                'Kod kreskowy': '',
                'UPC': '',
                # 'MPN': '',
                'Podatek ekologiczny': '',
                'Szeroko????': '',
                'Wysoko????': '',
                'G????boko????': '',
                'Waga': str(round(random.random() + 0.01, 2)).replace('.', ','),
                'Czas dostawy produkt??w dost??pnych w magazynie:': '',
                'Czas dostawy wyprzedanych produkt??w z mo??liwo??ci?? rezerwacji:': '',
                'Ilo????': random.randint(3, 100),
                'Minimalna ilo????': '',
                'Niski poziom produkt??w w magazynie': '',
                'Otrzymuj powiadomienie o niskim stanie magazyn??w przez e-mail': '',
                'Widoczno????': '',
                'Dodatkowe koszty przesy??ki': '',
                'Jednostka dla ceny za jednostk??': '',
                'Cena za jednostk??': '',
                'Podsumowanie': '',
                'Opis': description,
                'Tagi(x, y, z...)': '',
                'Meta - tytu??': '',
                'S??owa kluczowe meta': '',
                'Opis meta': '',
                'Przepisany URL': '',
                'Etykieta, gdy w magazynie': '',
                'Etykieta kiedy dozwolone ponowne zam??wienie': '',
                'Dost??pne do zam??wienia(0 = Nie, 1 = Tak)': 1,
                'Data dost??pno??ci produktu': '',
                'Data wytworzenia produktu': '',
                'Poka?? cen??(0 = Nie, 1 = Tak)': 1,
                'Adresy URL zdj??cia(x, y, z...)': img_url,
                'Tekst alternatywny dla zdj????(x, y, z...)': '',
                'Usu?? istniej??ce zdj??cia(0 = Nie, 1 = Tak)': 1,
                'Cecha(Nazwa:Warto????:Pozycja:Indywidualne)': '',
                'Dost??pne tylko online(0 = Nie, 1 = Tak)': '',
                'Stan:': '',
                'Konfigurowalny(0 = Nie, 1 = Tak)': '',
                'Mo??na wgrywa?? pliki(0 = Nie, 1 = Tak)': '',
                'Pola tekstowe(0 = Nie, 1 = Tak)': '',
                'Akcja kiedy brak na stanie': '',
                'Wirtualny produkt(0 = No, 1 = Yes)': '',
                'Adres URL pliku': '',
                'Ilo???? dozwolonych pobra??': '',
                'Data wyga??ni??cia(rrrr-mm-dd)': '',
                'Liczba dni': '',
                'ID / Nazwa sklepu': '',
                'Zaawansowane zarz??dzanie magazynem': '',
                'Zale??ny od stanu magazynowego': '',
                'Magazyn': '',
                'Akcesoria(x, y, z...)': '',
            }

            products.append(product)
            if len(products) == num_of_products:
                return products

    return products


def get_combinations(id, sizes, colors):
    combinations = []
    for color in colors:
        for size in sizes:
            combination = {
                'Identyfikator Produktu (ID)': id,
                'Indeks produktu': '',
                'Atrybut (Nazwa:Typ:Pozycja)*': 'Kolor:kolor:0, Rozmiar:rozmiar:1',
                'Warto???? (Warto????:Pozycja)*': f'{color}:0, {size}:1',
                'Identyfikator dostawcy': '',
                'Indeks': '',
                'kod EAN13': '',
                'Kod kreskowy UPC': '',
                'MPN': '',
                'Koszt w??asny': '',
                'Wp??yw na cen??': '',
                'Podatek ekologiczny': '',
                'Ilo????': random.randint(1, 13),
                'Minimalna ilo????': '',
                'Niski poziom produkt??w w magazynie': '',
                'Otrzymuj powiadomienie o niskim stanie magazyn??w przez e-mail': '',
                'Wp??yw na wag??': '',
                'Domy??lny (0 = Nie, 1 = Tak)': '',
                'Data dost??pno??ci kombinacji': '',
                'Wybierz z po??r??d zdj???? produkt??w wg pozycji (1,2,3...)': '',
                'Adresy URL zdj??cia (x,y,z...)': '',
                'Tekst alternatywny dla zdj???? (x,y,z...)': '',
                'ID / Nazwa sklepu': '',
                'Zaawansowane zarz??dzanie magazynem': '',
                'Zale??ny od stanu magazynowego': '',
                'Magazyn': '',
            }
            combinations.append(combination)

    return combinations


def get_brands(products):
    brands = []
    id = 1
    for product in products:
        brand = {
            'ID': id,
            'Aktywny(0 lub 1)': 1,
            'Nazwa *': product['Marka'],
            'Opis': f'Super marka {product["Marka"]}',
            'Kr??tki opis': '',
            'Meta - tytu??': '',
            'S??owa kluczowe meta': '',
            'Opis meta': '',
            'URL zdj??cia': product['Adresy URL zdj??cia(x, y, z...)'],
            'ID / Nazwa sklepu grupy': '',
        }
        for x in brands:
            if brand['Nazwa *'] == x['Nazwa *']:
                break
        else:
            brands.append(brand)
            id += 1

    return brands


def save_as_csv(list_of_dicts, file_name, path=''):
    header = list(list_of_dicts[0].keys())
    with open(f'{path}{file_name}.csv', 'w', encoding='UTF8', newline='') as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=header, delimiter=';', dialect='excel')
        writer.writeheader()
        writer.writerows(list_of_dicts)
    print(f'{path}{file_name} saved')


if __name__ == "__main__":
    num_of_categories = 5
    num_of_products_from_category = 110
    sizes = ['S', 'M', 'L', 'XL']
    colors = ['Szary', 'Szarobr??zowy', 'Be??owy']

    categories = []
    products = []
    combinations = []
    brands = []

    categories = get_categories(num_of_categories)  # defined number of categories
    # categories = get_categories()  # all categories
    for category in categories:
        products_in_category = get_products(category, num_of_products_from_category)
        if category['name'] == 'Bluzy':
            for product in products_in_category:
                combinations_of_product = get_combinations(product['ID'], sizes, colors)
                combinations.extend(combinations_of_product)
        products.extend(products_in_category)
    brands = get_brands(products)

    categories_list = []
    for id, category in enumerate(categories, start=1):
        category = {
            # 'ID': id,
            'ID': '',
            'Aktywny(0 lub 1)': 1,
            'Nazwa *': category['name'],
            'Kategoria nadrz??dna': '',
            'G????wna kategoria(0 / 1)': 0,
            'Opis': 'Opis kategorii - jaki?? b??dzie trzeba wymy??li??, bo nie ma na Zalando',
            'Meta - tytu??': '',
            'S??owa kluczowe meta': '',
            'Opis meta': '',
            'Przepisany URL': '',
            'URL zdj??cia': '',
            'ID / Nazwa sklepu': '',
        }
        categories_list.append(category)
    save_as_csv(categories_list, 'categories')
    save_as_csv(products, 'products')
    save_as_csv(combinations, 'combinations')
    save_as_csv(brands, 'brands')
