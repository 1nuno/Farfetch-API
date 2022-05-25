from dateutil.parser import parse

class Farfetch_Api:
  
  def __init__(self,session):
    self.ids_base_url = "https://www.farfetch.com/pt/plpslice/listing-api/products-facets"
    self.product_base_url = "https://www.farfetch.com/pt/pdpslice/product/"
    self.session = session
    self.page = 0
    self.page_type = "Shopping"
    self.price_type = "FullPrice"
    self.scale = 282
    self.view = 90

  def request_page_data(self,proxies:dict=None,headers:dict=None):
    """this function sends a request to the current page data url and returns its json content.

    :param proxies: This parameter is usefull in case you want to use an external proxie to send the request.
                    Usually is used when atempting to do proxy rotation. 
                    defaults to None.
    :type proxies: dict, optional


    :param headers: This parameter is usefull in case you want to use a different header to send the request.
                    Usually is used when atempting to do header rotation. 
                    defaults to None., defaults to None
    :type headers: dict, optional


    :return: Json content of the request made.
    :rtype: dict
    """
    self.request = self.session.get(self.page_data_url,headers=headers,proxies=proxies, timeout=10)
    return self.request.json()

  def get_page_ids(self,page_data:dict):
    """this function gets all the product id's that are present in the dictionary returned by the function "request_page_data" and returns a list with them.

    :param page_data: dictionary returned by the function "request_page_data"
    :type page_data: dict


    :return: list of product id's
    :rtype: list
    """
    page_ids = []
    for i,id_ in enumerate(page_data['listingItems']['items']):
      try:
        page_ids.append(id_['id'])
      except:
        if i+1 != len(page_data['listingItems']['items']):
          continue
        else:
          break
    return page_ids

  def get_product_links(self,sort:int=None,
                        c_category:int=None,
                        category:int=None,
                        gender:str=None,
                        designer:int=None,
                        pages:int=0,
                        proxies:dict=None,
                        headers:dict=None,
                        save:bool=False):

    """this function creates all the product links that we intend to scrape and returns them in a list.

    :param sort: Atribute of the link. It sorts the links and can have the following values:
                 1 - high price to low price
                 2 - newest first
                 3 - their own picks
                 4 - low price to high price
                 None - it defaults to 3
    :type sort: int, optional


    :param c_category: Atribute of the link. It filters the links to only get items within the specified categories.
                       There is many possible values to this parameter and to see how to get them refer to the demo
                       package in the github repo. if None, it wont filter the results by category.
    :type c_category: int, optional


    :param category: Atribute of the link. It filters the links to only get items within the specified sub-categories.
                     There is many possible values to this parameter and to see how to get them refer to the demo
                     package in the github repo. if None, it wont filter the results by sub-category.
    :type category: int, optional


    :param gender: Atribute of the link. It filters the links to only get items within the specified gender.
                   It can have the following values:
                   'men' - only men products
                   'women' - only women products
                   'kids' - only kids products
                   None - it wont filter the results by gender
    :type gender: str, optional


    :param category: Atribute of the link. It filters the links to only get items within the specified brand.
                     There is many possible values to this parameter and to see how to get them refer to the demo
                     package in the github repo. if None, it wont filter the results by sub-category.
    :type category: int, optional


    :param pages: Atribute of the link. The number of pages thats desired to scrape.
    :type pages: int, optional


    :param proxies: This parameter is usefull in case you want to use an external proxie to send the request.
                    Usually is used when atempting to do proxy rotation. 
                    defaults to None.
    :type proxies: dict, optional


    :param headers: This parameter is usefull in case you want to use a different header to send the request.
                    Usually is used when atempting to do header rotation. 
                    defaults to None., defaults to None
    :type headers: dict, optional


    :param save: if True it saves all the scraped links to a csv file (named product_links.csv) in the data folder.
                 Defaults to False.
    :type save: bool, optional


    :return: Returns a list with all the product links
    :rtype: list
    """
    self.sort = sort
    self.designer = designer
    self.category = category
    self.c_category = c_category
    self.gender = gender
    self.params = {'page':self.page,
                  'pagetype':self.page_type,
                  'pricetype':self.price_type,
                  'scale':self.scale,
                  'sort':self.sort,
                  'view':self.view,
                  'rootCategory':self.gender,
                  'c_category':self.c_category,
                  'category':self.category,
                  'designer':self.designer}
    self.params_str = '?' + '&'.join([f'{k}={v}' for k,v in self.params.items() if v])
    self.page_data_url = self.ids_base_url + self.params_str

    if not pages: pages = self.request_page_data(proxies=proxies,headers=headers)["listingPagination"]["totalPages"]
    product_links = []
    for i in range(1,pages+1):
      self.params['page'] = i
      page_data = self.request_page_data(proxies=proxies,headers=headers)
      page_i_ids = self.get_page_ids(page_data)
      page_product_links = [f'https://www.farfetch.com/pt/pdpslice/product/{product_id}' for product_id in page_i_ids]
      product_links.extend(page_product_links)
      if save:
        with open('data//product_links.csv','a') as f:
          for link in page_product_links:
            f.write(link + "\n")
    return product_links

  def get_sizes(self,product_data:dict):
    """This function will get the sizes of the given product.

    :param product_data: Its a dictionary derived from a request made to one of the product links that can be
                         generated by the "get_product_links" function.
    :type product_data: dict


    :return: Returns a dictinary containing the sizes.
    :rtype: dict
    """
    try:
      sizes_data = product_data['productViewModel']['sizes']
      self.sizes = {'scale':sizes_data['cleanScaleDescription']}
      for s in sizes_data['available'].values():
        size_id = s['sizeId']
        size = s['description']
        self.sizes[f'{size_id}'] = size
    except:
        self.sizes[''] = '0'
    return self.sizes

  def get_prices(self,product_data:dict,sizes:dict):
    """This function will get the prices of the given product.

    :param product_data: Its a dictionary derived from a request made to one of the product links that can be
                         generated by the "get_product_links" function.
    :type product_data: dict


    :param sizes: Its a dictionary derived from the "get_sizes" function.
    :type sizes: dict


    :return: Returns a dictionary containing the prices.
    :rtype: dict
    """    
    try:
      prices_data = product_data['productViewModel']['priceInfo']
      self.prices = {}
      for size_id, size in sizes.items():
        if size_id in prices_data:
          info = prices_data[size_id]
          price_info = [info['finalPrice'],info['currencyCode'],sizes['scale']]
          self.prices[size] = price_info

      info = prices_data['default']
      price_info = [info['finalPrice'],info['currencyCode'],sizes['scale']]
      self.prices['default'] = price_info
    except:
      self.prices = {'0':[None,None,None]}
    return self.prices

  def get_description(self,product_data:dict):
    """This function will get the descriptions of the given product.

    :param product_data: Its a dictionary derived from a request made to one of the product links that can be
                         generated by the "get_product_links" function.
    :type product_data: dict


    :return: Returns a dictinary containing the descriptions.
    :rtype: dict
    """
    try:
      details_data = product_data['productViewModel']['details']
      designer_details = product_data['productViewModel']['designerDetails']
      brand = designer_details['name']
      model = details_data['shortDescription']
      descriptions = [details_data['description'],designer_details['description']]
      category = product_data['productViewModel']['categoriesTree'][0]['subCategories'][0]['name']
    except:
      brand = None
      model = None
      descriptions = None
      category = None

    self.description = {'brand':brand,
                'model':model,
                'descriptions':descriptions,
                'category':category}
    return self.description

  def get_shipping_info(self,product_data:dict):
    """This function will get the shipping info of the given product.

    :param product_data: Its a dictionary derived from a request made to one of the product links that can be
                         generated by the "get_product_links" function.
    :type product_data: dict


    :return: Returns a dictinary containing the shipping info.
    :rtype: dict
    """
    try:
      shipping_data = product_data['productViewModel']['shippingInformations']['details']['default']
      shipping_from = shipping_data['shippingFromMessage']
      arrival_date = shipping_data['eddStandard']
      time_period = [parse(time) for time in arrival_date.split(' - ')]
      time_period = time_period[-1] - time_period[0]
    except:
      time_period = None

    self.shipping_info = {'shipping_from':shipping_from,'time_period':time_period}
    return self.shipping_info     

  def get_images(self,product_data:dict):
    """This function will get the images of the given product.

    :param product_data: Its a dictionary derived from a request made to one of the product links that can be
                         generated by the "get_product_links" function.
    :type product_data: dict


    :return: Returns a dictinary containing the images.
    :rtype: dict
    """
    try:
      images_data = product_data['productViewModel']['images']['main']
      self.images = {}
      for p,image in enumerate(images_data):
          small = image['small']
          medium = image['medium']
          large = image['large']
          self.images[p] = {}
          self.images[p]['small'] = small
          self.images[p]['medium'] = medium
          self.images[p]['large'] = large
    except:
      self.images = {'':{'':None}}
    return self.images