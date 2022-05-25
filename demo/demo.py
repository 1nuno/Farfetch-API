from requests_html import HTMLSession
import os
import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from api.Farfetch import Farfetch_Api

session = HTMLSession()
api = Farfetch_Api(session)

#get the desired products urls
urls = api.get_product_links(save=False,
                             sort=4,
                             c_category=135968,
                             category=137174,
                             pages=1)

#get the data from the first url
request = api.session.get(urls[0],timeout=10)
print(request.status_code)
data = request.json()

#get the links for the images of the product (copy and paste one of them on your browser to view it)
images = api.get_images(data)
print(images)


