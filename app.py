import requests
from bs4 import BeautifulSoup as bs
import logging
import pandas as pd
from pymongo import MongoClient

logging.basicConfig(filename="logs_scrapper.log" , level=logging.INFO)  
lst=[]
#Function for extracting information about the book

def get_book_titles(html_data,prod_url):
    try:
        lst=[]
        upc=html_data.find(attrs={"class":"table table-striped"}).td.text
        book_title = html_data.find("div",{"class":"col-sm-6 product_main"}).h1.text
        stock=html_data.find(attrs={"class":"instock availability"}).text.strip()
        rating=-1
        price=html_data.find(attrs={"class":"price_color"}).text
        #To check the rating of the product
        if html_data.find("p",{"class": "star-rating One"}) is not None:
            rating=1
        elif html_data.find("p",{"class": "star-rating Two"}) is not None:
            rating=2
        elif html_data.find("p",{"class": "star-rating Three"}) is not None:
            rating=3
        elif html_data.find("p",{"class": "star-rating Four"}) is not None:
            rating=4
        elif html_data.find("p",{"class": "star-rating Five"}) is not None:
            rating=5
        else:
            rating="Not found"
        #Storing information in a dictionary
        book_info = {
                    'UPC':upc,
                    'BOOK TITLE':book_title,
                    'PRICE':price,
                    'STOCK AVAILABILTY':stock,
                    'RATING':rating,
                    'URL':prod_url
                    }
        return book_info
    except Exception as e:
        logging.info("Error in Function for extracting information about the book::"+ e)
        

#Function for mongoDB connection
def send_data_mongo(df):
    try:
        from pymongo import MongoClient
        client=MongoClient('mongodb+srv://pseudo0862:Neelabro9@cluster0.dn64x4h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        db=client['ScrapedData']
        collection=db['Data']
        df.reset_index(inplace=True)
        dict_data=df.to_dict("records")
        collection.insert_many(dict_data)
    except Exception as e:
        logging.info("Error in Function for mongoDB connection::"+ e)

try:
    no_of_pages=int(input("Enter number of pages to scrape from website::"))    #Input from the user for the number pages to scrape
    for pg in range(1,no_of_pages+1):
        book_url="https://books.toscrape.com/catalogue/page-"+str(pg)+'.html' 
        urlclient=requests.get(book_url)     #Request URL
        urlclient.encoding='utf-8'
        book_html=bs(urlclient.text,'html.parser')   #Parsing the content to HTML
        all_products_in_a_page=book_html.findAll("li",{"class":"col-xs-6 col-sm-4 col-md-3 col-lg-3"})
        for i in range(0,len(all_products_in_a_page)):
            productLink="https://books.toscrape.com/catalogue/"+all_products_in_a_page[i].article.h3.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            lst.append(get_book_titles(prod_html,productLink))
except Exception as e:
        logging.info("Error in driver function::"+ e)

df=pd.DataFrame(lst)
df.to_csv("Scraped_Data.csv", sep=',', index=False, encoding='utf-8')   #Saving data in csv format
send_data_mongo(df) #Saving data in MongoDB    
