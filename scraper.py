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
            if key == 'Materiał':
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
    keys_material_care = ['Materiał', 'Struktura/rodzaj materiału', 'Zawiera elementy skórzane',
                          'Wskazówki pielęgnacyjne']
    description += get_key_values_from(text_material_care, keys_material_care)

    text_details = text[index_details:index_size_fit]
    keys_details = ['Rodzaj dekoltu', 'Kształt kołnierza', 'Kaptur', 'Stan', 'Zapięcie', 'Kieszenie', 'Przezroczystość',
                    'Wzór', 'Szczegóły', 'Numer produktu']
    description += get_key_values_from(text_details, keys_details)

    text_size_fit = text[index_size_fit:index_sustainability]
    keys_size_fit = ['Wzrost modela', 'Fason', 'Kształt', 'Długość', 'Długość rękawa', 'Cała długość']
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
                price = price.text.replace(',', '.').replace('zł', '').replace('od', '').strip()
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
                'ID reguły podatku': 1,
                'Koszt własny': round((price / 1.23) / 1.1),
                'W sprzedaży(0 lub 1)': 1,
                'Wartość rabatu': '',
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
                'Szerokość': '',
                'Wysokość': '',
                'Głębokość': '',
                'Waga': str(round(random.random() + 0.01, 2)).replace('.', ','),
                'Czas dostawy produktów dostępnych w magazynie:': '',
                'Czas dostawy wyprzedanych produktów z możliwością rezerwacji:': '',
                'Ilość': random.randint(3, 100),
                'Minimalna ilość': '',
                'Niski poziom produktów w magazynie': '',
                'Otrzymuj powiadomienie o niskim stanie magazynów przez e-mail': '',
                'Widoczność': '',
                'Dodatkowe koszty przesyłki': '',
                'Jednostka dla ceny za jednostkę': '',
                'Cena za jednostkę': '',
                'Podsumowanie': '',
                'Opis': description,
                'Tagi(x, y, z...)': '',
                'Meta - tytuł': '',
                'Słowa kluczowe meta': '',
                'Opis meta': '',
                'Przepisany URL': '',
                'Etykieta, gdy w magazynie': '',
                'Etykieta kiedy dozwolone ponowne zamówienie': '',
                'Dostępne do zamówienia(0 = Nie, 1 = Tak)': 1,
                'Data dostępności produktu': '',
                'Data wytworzenia produktu': '',
                'Pokaż cenę(0 = Nie, 1 = Tak)': 1,
                'Adresy URL zdjęcia(x, y, z...)': img_url,
                'Tekst alternatywny dla zdjęć(x, y, z...)': '',
                'Usuń istniejące zdjęcia(0 = Nie, 1 = Tak)': 1,
                'Cecha(Nazwa:Wartość:Pozycja:Indywidualne)': '',
                'Dostępne tylko online(0 = Nie, 1 = Tak)': '',
                'Stan:': '',
                'Konfigurowalny(0 = Nie, 1 = Tak)': '',
                'Można wgrywać pliki(0 = Nie, 1 = Tak)': '',
                'Pola tekstowe(0 = Nie, 1 = Tak)': '',
                'Akcja kiedy brak na stanie': '',
                'Wirtualny produkt(0 = No, 1 = Yes)': '',
                'Adres URL pliku': '',
                'Ilość dozwolonych pobrań': '',
                'Data wygaśnięcia(rrrr-mm-dd)': '',
                'Liczba dni': '',
                'ID / Nazwa sklepu': '',
                'Zaawansowane zarządzanie magazynem': '',
                'Zależny od stanu magazynowego': '',
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
                'Wartość (Wartość:Pozycja)*': f'{color}:0, {size}:1',
                'Identyfikator dostawcy': '',
                'Indeks': '',
                'kod EAN13': '',
                'Kod kreskowy UPC': '',
                'MPN': '',
                'Koszt własny': '',
                'Wpływ na cenę': '',
                'Podatek ekologiczny': '',
                'Ilość': random.randint(1, 13),
                'Minimalna ilość': '',
                'Niski poziom produktów w magazynie': '',
                'Otrzymuj powiadomienie o niskim stanie magazynów przez e-mail': '',
                'Wpływ na wagę': '',
                'Domyślny (0 = Nie, 1 = Tak)': '',
                'Data dostępności kombinacji': '',
                'Wybierz z pośród zdjęć produktów wg pozycji (1,2,3...)': '',
                'Adresy URL zdjęcia (x,y,z...)': '',
                'Tekst alternatywny dla zdjęć (x,y,z...)': '',
                'ID / Nazwa sklepu': '',
                'Zaawansowane zarządzanie magazynem': '',
                'Zależny od stanu magazynowego': '',
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
            'Krótki opis': '',
            'Meta - tytuł': '',
            'Słowa kluczowe meta': '',
            'Opis meta': '',
            'URL zdjęcia': product['Adresy URL zdjęcia(x, y, z...)'],
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
    colors = ['Szary', 'Szarobrązowy', 'Beżowy']

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
            'Kategoria nadrzędna': '',
            'Główna kategoria(0 / 1)': 0,
            'Opis': 'Opis kategorii - jakiś będzie trzeba wymyślić, bo nie ma na Zalando',
            'Meta - tytuł': '',
            'Słowa kluczowe meta': '',
            'Opis meta': '',
            'Przepisany URL': '',
            'URL zdjęcia': '',
            'ID / Nazwa sklepu': '',
        }
        categories_list.append(category)
    save_as_csv(categories_list, 'categories')
    save_as_csv(products, 'products')
    save_as_csv(combinations, 'combinations')
    save_as_csv(brands, 'brands')
