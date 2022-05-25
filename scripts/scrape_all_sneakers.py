import time
import random
import pandas as pd
import numpy as np
from requests_html import HTMLSession
import os
import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from api.Farfetch import Farfetch_Api

def scrape_it(url:str,proxies:dict,headers:dict,status_code:bool=True):
    request = api.session.get(url,proxies=proxies,headers=headers,verify=False,timeout=10)
    if status_code: print(request.status_code) 
    product_data = request.json()

    sizes = api.get_sizes(product_data)
    prices = api.get_prices(product_data,sizes)
    description = api.get_description(product_data)
    shipping_info = api.get_shipping_info(product_data)
    images = api.get_images(product_data)

    images_str=''
    for image in images.values():
        for image in image.values():
            images_str += '\n' + str(image)
    images_str = images_str.strip('\n')

    id_ = url.split('/')[-1]
    shoe_prices = np.zeros([len(prices.keys()),7], dtype=object)
    shoe_prices[:,0] = id_
    shoe_prices[:,1] = description['brand']
    shoe_prices[:,2] = description['model']
    shoe_prices[:,3] = list(prices.keys())
    shoe_prices[:,4:] = list(prices.values())

    shoes_descriptions = np.zeros([1,7], dtype=object)
    shoes_descriptions[:,0] = id_
    shoes_descriptions[:,1] = description['brand']
    shoes_descriptions[:,2] = description['model']
    shoes_descriptions[:,3] = f"{description['descriptions'][0]}\n{description['descriptions'][1]}"
    shoes_descriptions[:,4] = shipping_info['time_period']
    shoes_descriptions[:,5] = shipping_info['shipping_from']
    shoes_descriptions[:,6] = images_str
      
    return shoe_prices,shoes_descriptions

user_agents = [{ 
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
              "Accept": "application/json, text/plain, */*",
              "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
              "Accept-Encoding": "gzip, deflate, br",
              "Referer": "https://www.farfetch.com/pt/shopping/men/shoes-2/items.aspx?page=1&view=90&sort=1&scale=282",
              "x-requested-with": "XMLHttpRequest",
              "Cache-Control": "no-cache, no-store, must-revalidate",
              "Connection": "keep-alive"
            },{ 
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
              "Accept": "application/json, text/plain, */*",
              "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
              "Accept-Encoding": "gzip, deflate, br",
              "Referer": "https://www.farfetch.com/pt/shopping/men/shoes-2/items.aspx?page=1&view=90&sort=1&scale=282",
              "x-requested-with": "XMLHttpRequest",
              "Cache-Control": "no-cache, no-store, must-revalidate",
              "Connection": "keep-alive"
            },{ 
              "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
              "Accept": "application/json, text/plain, */*",
              "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
              "Accept-Encoding": "gzip, deflate, br",
              "Referer": "https://www.farfetch.com/pt/shopping/men/shoes-2/items.aspx?page=1&view=90&sort=1&scale=282",
              "x-requested-with": "XMLHttpRequest",
              "Cache-Control": "no-cache, no-store, must-revalidate",
              "Connection": "keep-alive"
            }]

proxies = [{'http': 'http://scraperapi:365d128d3619d75597d9e5bfa31862a5@proxy-server.scraperapi.com:8001'},
          {'http': 'http://scraperapi:89cff43104f011358f1a9890696bf7a9@proxy-server.scraperapi.com:8001'},
          {'http': 'http://scraperapi:6fc5fbc74d3839fed104a1cc89700a31@proxy-server.scraperapi.com:8001'},
          {'http': 'http://scraperapi:4a03bcdd6f4aad2afe9d3f49bf55e22b@proxy-server.scraperapi.com:8001'}]

map_agents_proxies = {i:random.randint(0,len(user_agents)-1) for i in range(len(proxies))}
session = HTMLSession()
api = Farfetch_Api(session)
urls = api.get_product_links(save=False,
                             sort=4,
                             c_category=135968,
                             category=137174,
                             proxies=proxies[0],
                             headers=user_agents[0]
                            )
random_proxie = list(range(len(proxies)))
random.shuffle(random_proxie)

c = 0
for i,url in enumerate(urls):
    proxie_index = random_proxie[c]
    agent_index = map_agents_proxies[proxie_index]
    try:
      #scrape
      results = scrape_it(url,proxies[proxie_index],user_agents[agent_index])

      #save the results
      pd.DataFrame(results[0]).to_csv('data//prices.csv', mode='a', index=False, header=False)
      pd.DataFrame(results[1]).to_csv('data//details.csv', mode='a', index=False, header=False)

      print(results)
      print()
      print(f'Finished! - {i}')

  
    except Exception:
      #save urls that it didnt scrape
      with open('data//didnt_scrape.csv','a') as f:
            f.write(url + "\n")

      print(f'error - {proxie_index}\n')
      print(Exception)
      print()
    print('--------------------------------------------------')    
    if c == len(proxies)-1:
        random.shuffle(random_proxie)
        minutes = round(random.uniform(6,8),2)
        time.sleep(minutes * 60)
        c = -1
    c+=1

