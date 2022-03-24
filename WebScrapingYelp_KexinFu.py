#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import time
import random
import re


# ### Question 1
# Yelp uses GET requests for its search. Using Python or Java (Selenium is OK to use but not required
# and may be more cumbersome here; I didn't use Selenium), write a program that searches on yelp.com
# for the top-40 “Donut Shop” in the San Francisco area (no need to verify that the shop is actually selling
# donuts, just search for “Donut Shop”, top 40 shops according to Yelp's "Recommended" sorting). Save
# each search result page to disk, “sf_donut_shop_search_page_[PN].htm” (replace [PN] with the page
# number). Please make sure to pause after loading each page. (25 points)

# In[2]:


fixed_URL = "https://www.yelp.com/search?find_desc=donut+shop&find_loc=san+francisco&ns=1&start="
for i in ["0","10","20","30"]:
    print(fixed_URL + i)


# In[3]:


def saveString(html,i):
    try:
        filename = "sf_donut_shop_search_page_" + str(i) + ".html"
        file = open(filename,"w", encoding = 'utf-8')
        file.write(str(html))
        file.close()
    except Exception as ex:
        print('Error: ' + str(ex))


# #### Save to webpages

# In[5]:


HEADERS = {'User-Agent':  
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}  

page_range = ["0", "10", "20", "30"]
for i in range(4):
    page = requests.get(fixed_URL + page_range[i], headers = HEADERS)
    soup = BeautifulSoup(page.text, 'lxml')
    saveString(soup, i)
    
    t = random.randint(5,10)
    time.sleep(t)
    


# ### Question 2
# Using Python or Java, write new code that opens the search result pages saved in (1) and parses out
# all shop information (search rank, name, linked URL [this store’s Yelp URL], star rating, number of
# reviews, store tags, “$” signs, delivery / dine-in tags, and whether you can order through Yelp). Please
# be sure to skip all “Sponsored Results”. (15 points)

# In[4]:


def loadString(f):
    try:
        html = open(f, "r", encoding='utf-8').read()
        return(html)
    except Exception as ex:
        print('Error: ' + str(ex))


# #### Main Code

# In[51]:


rank_list = []
name_list = []
whole_href = []
star_list = []
num_review_list = []
store_tag_list = []
price_tag_list = []
delivery_list = []
order_via_yelp_list = []

for i in range(0,4):
    name = "sf_donut_shop_search_page_" + str(i) + ".html"
    content = loadString(f = name)
    soup = BeautifulSoup(content, "lxml")
    
    # Rank and Name
    rnk_name = soup.select(".css-1uq0cfn")
    for i in rnk_name:
        if i.text[0].isdigit():
            rank = int(i.text.split('.')[0])
            name = i.text.split('.')[1]
            rank_list.append(rank)
            name_list.append(name)
    
    # Store URL
    store_url = soup.select("a.css-1422juy")
    for item in store_url:
        href = item.get('href')
        whole_href.append(href)
        
    # Star
    star = soup.select("div > div > div > div > span > div") # This returns 13 items for each page
    for j in star[2:12]: # First 2 and last 1 are sponsored, so remove them
        star_list.append(j['aria-label'])
    
    # Number of Reviews
    num_review = soup.select("span.reviewCount__09f24__tnBk4")
    for review in num_review[2:12]:
        num_review_list.append(review.text)

    # Store Tags
    store_tag = soup.select("span.css-epvm6")
    for tag in store_tag[2:12]:
        store_tag_list.append(tag.text)
        
    # Price Tags
    price_tag = soup.select("p.css-1gfe39a")
    for price in price_tag[2:12]:
        price_tag_list.append(price.text)
    
    # delivery tags
    delivery_list_page = []
    for item in soup.select('[class*=container]'):
        try:
            name_rnk = item.find_all("span", {"class" : "css-1uq0cfn"})
            if name_rnk:
                delivery_soup = item.find("li",
                                              {"class":"border-color--default__09f24__NPAKY"}) # Return the div content or []
                if delivery_soup:
                    delivery_list_page.append(delivery_soup.text)
                else:
                    delivery_list_page.append(None)
 
        except Exception as e:
            raise e
            print('')
    delivery_list_page = delivery_list_page[2:12]
    delivery_list += delivery_list_page

    # Start Order Tag
    order_via_yelp_list_page = []
    for item in soup.select('[class*=container]'):
        try:
            name_rnk = item.find_all("span", {"class" : "css-1uq0cfn"})
            if name_rnk:
                order_button_soup = item.find_all(
                                                    "div",
                                                    {"class":"dontTriggerCardClick__09f24__nH1kt border-color--default__09f24__NPAKY"}
                                                )
                order_via_yelp = len(order_button_soup) > 0
                order_via_yelp_list_page.append(order_via_yelp)     
        except Exception as e:
            raise e
            print('')
    order_via_yelp_list_page = order_via_yelp_list_page[2:12]
    order_via_yelp_list += order_via_yelp_list_page
print(len(order_via_yelp_list))
print(len(delivery_list))


# #### Price Tag List Cleaning

# In[52]:


x = re.findall(r"\$+", str(price_tag_list))

with_price_index = []
for i in range(len(price_tag_list)):
    if "$" in price_tag_list[i]:
        with_price_index.append(i)

price_tag_list_clean = [None] * 40
x_reverse = x[::-1]

for i in with_price_index:
    price_tag_list_clean[i] = x_reverse.pop()


# #### Store Link Cleaning

# In[53]:


biz_href = []
for i in whole_href:
    if i.startswith('/biz/'):
        biz_href.append(i)

for i in range(len(biz_href)):
    biz_href[i] = "https://www.yelp.com" + biz_href[i]


# #### Combined DataFrame

# In[54]:


import pandas as pd
combined_df = pd.DataFrame({"rank":rank_list,
                            "name":name_list,
                           "link": biz_href,
                           "star": star_list,
                           "num_review": num_review_list,
                           "store_tag": store_tag_list,
                           "price_tag": price_tag_list_clean,
                           "delivery_tag": delivery_list,
                           "order_via_yelp": order_via_yelp_list})
combined_df


# ### Question 3
# Adjust your code in (2) to create a MongoDB collection called “sf_donut_shops” that stores all the
# extracted shop information, one document for each shop. (10 points)

# In[56]:


# from pymongo import MongoClient
import pymongo
import bson

# connect to the mongoclient
client = pymongo.MongoClient('mongodb://localhost:27017')

# get the database
database = client['local']

database.create_collection("sf_donut_shops")

sf_donut_shops = database.get_collection("sf_donut_shops")
sf_donut_shops.insert_many(combined_df.to_dict('records'))


# In[57]:


cursor = sf_donut_shops.find({})
for document in cursor:
    print(document)


# ### Question 4
# Using Python or Java, write a _new_ piece of code that reads all URLs stored in “sf_donut_shops”
# and download each shop page. Store the page to disk, “sf_donut_shop_[SR].htm” (replace [SR] with the
# search rank). (15 points)

# In[263]:


def saveString2(html,i):
    try:
        filename = "sf_donut_shop_" + str(i) + ".html"
        file = open(filename,"w", encoding = 'utf-8')
        file.write(str(html))
        file.close()
    except Exception as ex:
        print('Error: ' + str(ex))


# In[266]:


cursor2 = database.sf_donut_shops.find({},{"link":1,"_id":0})

counter = 0
for document in cursor2:
    counter += 1
    yelp_link = document['link']
    page = requests.get(yelp_link, headers = HEADERS)
    soup = BeautifulSoup(page.text, 'lxml')
    saveString2(soup, counter)
    print("Saved Successfully" + str(counter))
    time.sleep(5)


# ### Question 5
# Using Python or Java, write new code that reads the 40 shop pages saved in (4) and parses each
# shop’s address, phone number, and website. (15 points)

# In[58]:


web_list = []
address_list = []
phone_list = []

for i in range(1,41):
    name = "sf_donut_shop_" + str(i) + ".html"
    content = loadString(f = name)
    soup = BeautifulSoup(content, "lxml")
    all_info = soup.select("div.css-1vhakgw")
    x_container = []
    y_container = []
    for j in all_info:
        
        # Find Website
        x = re.findall(r"http.*", j.text)
        if x:
            x_container.append(x[0])
        
        # Find Phone Number
        pat = re.compile(r'(\(\d{3}\)\s*\d{3}-\d{4})')
        y = pat.findall(j.text)
        if y:
            y_container.append(y[0])
    
    web_list.append(x_container)
    phone_list.append(y_container)     
    
    # Find Address
    address = soup.select("p.css-qyp8bo")
    if address:
        for j in address:
            address_list.append(j.text)
#         print("Address Exists")
    else:
        address_list.append(None)
#         print("Address Not Exists")


# In[60]:


def format_list(old_list):
    new_list = []
    for i in old_list:
        if i:
            new_list.append(i[0])
        else:
            new_list.append(None)
    return new_list

phone_list = format_list(phone_list)
web_list = format_list(web_list)


# ### Question 6
# Sign up for a free account with https://positionstack.com/ Adjust your code in (5) to query each
# shop address’ geolocation (long, lat). Update each shop document on the MongoDB collection
# “sf_donut_shops” to contain the shop’s address, phone number, website, and geolocation. Lastly, place
# an index on the shop’s search rank. (20 points)

# In[13]:


access_key = "8e18c99933726be90e3ed229fd54ecf1"
import json
# Forward Geocoding API Endpoint
base_url = "http://api.positionstack.com/v1/forward?access_key=8e18c99933726be90e3ed229fd54ecf1&query="

lat_list = []
long_list = []
for i in address_list:
    if i:
        address_url = i.replace(" ","%20")
        whole_url = base_url + address_url
        page = requests.get(whole_url, headers = HEADERS)
        doc = BeautifulSoup(page.content, 'html.parser')
        json_dict = json.loads(str(doc))
        lat = json_dict['data'][0]['latitude']
        long = json_dict['data'][0]['longitude']
        lat_list.append(lat)
        long_list.append(long)
    else:
        lat_list.append(None)
        long_list.append(None)
print(lat_list)
print(long_list)


# In[65]:


combined_df['lat'] = lat_list
combined_df['long'] = long_list
combined_df['geolocation'] = combined_df[["lat","long"]].apply(tuple, axis=1)

geolocation_list = combined_df[["lat","long"]].apply(tuple, axis=1)


# #### Before Updating

# In[61]:


sf_donut_shops.find_one()


# #### Update each entry: address, website, phone number and geolocation

# In[69]:


for i in range(0,40):
    sf_donut_shops.update_one({'rank': i+1},{"$set": {"address": address_list[i],
                                                      "website": web_list[i],
                                                      "phone number":phone_list[i],
                                                      "geolocation": geolocation_list[i]}})


# In[70]:


cursor = sf_donut_shops.find({})
for document in cursor:
    print(document)


# #### Create Index on Rank

# In[71]:


sf_donut_shops.create_index("rank")

