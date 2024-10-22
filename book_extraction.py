import csv
import re
from bs4 import BeautifulSoup
import requests
from datetime import date
from urllib.parse import urljoin

# use to get the correct url for the images
URL = "https://books.toscrape.com/index.html"

# use to get the correct url for the books
url_catalogue = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"

def extract_title_and_category(soup, book_info):
    link_list = soup.find("ul", class_="breadcrumb")
    text_list = link_list.find_all("li")
    book_info["title"] = text_list[3].string
    book_info["category"] = text_list[2].find("a").string

def extract_product_info(soup, book_info):
    table_product_info = soup.find("table", class_="table table-striped")
    trs = table_product_info.find_all("tr")
    book_info["universal_product_code"] = trs[0].find("td").string
    book_info["price_excluding_tax"] = trs[2].find("td").string
    book_info["price_including_tax"] = trs[3].find("td").string
    available_string = trs[5].find("td").string
    number_available = re.findall(r'\d+', available_string)
    book_info["number_available"] = number_available[0]

def extract_rating(soup, book_info):
    review_rating_paragraph = soup.find("p", class_="star-rating")
    # string contains 2 parts "star-rating" and a number, [1] to only get the number
    review_rating = review_rating_paragraph["class"][1]
    book_info["rating"] = review_rating

def extract_description(soup, book_info):
    product_description = soup.find(id="product_description")
    description = product_description.find_next("p")
    book_info["product_description"] = description.string

def extract_image(soup, book_info):
    image_div = soup.find("div", class_="item active")
    image = image_div.find("img")
    book_info["image_url"] = image.get("src")

def extract_all_info(soup, book_info):
    extract_title_and_category(soup, book_info)
    extract_description(soup, book_info)
    extract_product_info(soup, book_info)
    extract_rating(soup, book_info)
    extract_image(soup, book_info)

def extract_all_books_from_page(soup, books_info):
    for article in soup.find_all("article", class_="product_pod"):
        link_book = article.find("a")
        absolute_url = urljoin(url_catalogue, link_book.get("href"))
        current_page = requests.get(absolute_url)
        if current_page.ok:
            current_soup = BeautifulSoup(current_page.content, "html.parser")
            current_book = {"url": absolute_url}
            extract_all_info(current_soup, current_book)
            transform(current_book)
            books_info.append(current_book)

def transform(book_info):
    transform_rating(book_info)
    transform_image_url(book_info)
    transform_to_euros(book_info)

def transform_rating(book_info):
    match book_info["rating"]:
        case "Zero":
            book_info["rating"] = "0"
        case "One":
            book_info["rating"] = "1"
        case "Two":
            book_info["rating"] = "2"
        case "Three":
            book_info["rating"] = "3"
        case "Four":
            book_info["rating"] = "4"
        case "Five":
            book_info["rating"] = "5"
        case _:
            print("Error: rating is not between 0 and 5")
    book_info["rating"] += " stars"

def transform_image_url(book_info):
    absolute_url = urljoin(URL, book_info["image_url"])
    book_info["image_url"] = absolute_url

def convert_to_euros(price_sterling):
    return str(round(float(price_sterling) * 1.15, 2)) + "€"

def transform_to_euros(book_info):
    price_excluding_tax_cleaned = ''.join(filter(lambda x: x.isdigit() or x == ".", book_info["price_excluding_tax"]))
    book_info["price_excluding_tax"] = convert_to_euros(price_excluding_tax_cleaned)
    price_including_tax_cleaned = ''.join(filter(lambda x: x.isdigit() or x == ".", book_info["price_including_tax"]))
    book_info["price_including_tax"] = convert_to_euros(price_including_tax_cleaned)

def load(books_info):
    today_date = date.today().strftime("%d-%m-%Y")
    file_name = "books_to_scrape_info_" + today_date + ".csv"
    with open(file_name, "w") as output_csv:
        writer = csv.writer(output_csv, lineterminator='\n')
        header = ["url", "title", "category", "description", "universal_product_code", "price_excluding_tax",
                  "price_including_tax", "number_available", "rating", "image_url"]
        writer.writerow(header)
        for book in books_info:
            writer.writerow(book.values())

def main():
    page = requests.get(url_catalogue)

    if page.ok:
        soup = BeautifulSoup(page.content, "html.parser")
        books_info = []
        extract_all_books_from_page(soup, books_info)
        next_page = soup.find("li", class_="next")
        while next_page :
            next_page_link = next_page.find("a").get("href")
            new_url = urljoin(url_catalogue, next_page_link)
            page = requests.get(new_url)
            if page.ok:
                soup = BeautifulSoup(page.content, "html.parser")
                extract_all_books_from_page(soup, books_info)
                next_page = soup.find("li", class_="next")
        load(books_info)

if __name__ == "__main__":
    main()
