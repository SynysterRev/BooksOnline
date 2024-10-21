import csv
import re
from bs4 import BeautifulSoup
import requests
from datetime import date

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
    review_rating = review_rating_paragraph["class"][1]
    book_info["rating"] = review_rating

def extract_description(soup, book_info):
    product_description = soup.find(id="product_description")
    description = product_description.find_next("p")
    book_info["product_description"] = description.string

def extract_image(soup, book_info):
    image_div = soup.find("div", class_="item active")
    image = image_div.find("img")
    book_info["image_url"] = image["src"]

def extract_all_info(soup, book_info):
    extract_title_and_category(soup, book_info)
    extract_product_info(soup, book_info)
    extract_rating(soup, book_info)
    extract_description(soup, book_info)
    extract_image(soup, book_info)

def load(book_info):
    today_date = date.today().strftime("%d-%m-%Y")
    file_name = "books_to_scrape_info_" + today_date + ".csv"
    with open(file_name, "w") as output_csv:
        writer = csv.writer(output_csv, lineterminator= '\n')
        header = []
        info = []
        for key in book_info.keys():
            header.append(key)
        for value in book_info.values():
            info.append(value)
        print(info)
        writer.writerow(header)
        writer.writerow(info)



def main():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    book_info = {"url": url}
    extract_all_info(soup, book_info)

    load(book_info)

    # print(book_info["image_url"])

if __name__ == "__main__":
    main()
