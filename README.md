# Zalando-Presta-scraper
Semester 5 - Electronic Business
---
The Zalando-Presta-scraper is a Python web scraper designed to extract information about products from the Zalando e-commerce website. This scraper retrieves data such as the product's name, price, brand, photo, description, and category.

### Usage
You can use the scraper by running the scraper.py script. Before running the script, you can customize the following parameters according to your needs:
```
num_of_categories = 5
num_of_products_from_category = 110
sizes = ['S', 'M', 'L', 'XL']
colors = ['Szary', 'Szarobrązowy', 'Beżowy']
```
- *num_of_categories*: The number of categories to scrape. Set it to None to scrape all categories.
- *num_of_products_from_category*: The number of products to scrape from each category.
- *sizes*: A list of available sizes for the products.
- *colors*: A list of available colors for the products.  

You can also specify if you want to download the pictures of scraped products in *get_products* function:
```
get_products(category, num_of_products, save_images=False, img_path='')
```
  
Once you have configured the parameters, you can run the script. The script will scrape the specified categories, retrieve product information and save the data in CSV format compatible with PrestaShop import files in the Polish version. The resulting files will be saved in the same directory. Sample CSV files of scraping results have been uploaded to the [csv](https://github.com/Jacenty-And/Zalando-Presta-scraper/tree/main/csv) directory.
