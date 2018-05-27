import shopify
import os

SOURCE_SHOP_URL = ''
SOURCE_SHOP_API = ''
SOURCE_SHOP_PASSWORD = ''

DESTINATION_SHOP_URL = ''
DESTINATION_SHOP_API = ''
DESTINATION_SHOP_PASSWORD = ''

source_shop = None
destination_shop = None

replace_information = {}


def start(shop_url, api_key, secret_key):
    try:
        # shopify.ShopifyResource.set_site = __shop_url
        if "https://" in shop_url:
            shop_url = "https://%s:%s@%s/admin" % (api_key, secret_key, str(shop_url).split('/')[2])
        else:
            shop_url = "https://%s:%s@%s/admin" % (api_key, secret_key, shop_url)
        shopify.ShopifyResource.set_site(shop_url)
        # shopify.Session.api_key = __api_key
        # shopify.Session.secret = __secret_key
        shopify.Shop.current()
        return shopify
    except Exception as e:
        print(e)
        return None


def __is_empty(string):
    if string and str(string).strip():
        return False
    return True


while True:
    print('---------------- SOURCE SHOP INFORMATION ----------------')
    while __is_empty(SOURCE_SHOP_URL):
        SOURCE_SHOP_URL = input('Input your source shop URL: ').strip()
    while __is_empty(SOURCE_SHOP_API):
        SOURCE_SHOP_API = input('Input your source shop API: ').strip()
    while __is_empty(SOURCE_SHOP_PASSWORD):
        SOURCE_SHOP_PASSWORD = input('Input your source shop password: ').strip()
    source_shop = start(SOURCE_SHOP_URL, SOURCE_SHOP_API, SOURCE_SHOP_PASSWORD)
    if source_shop is not None:
        break
    print('Your source shop input is wrong, please re-input')
    SOURCE_SHOP_URL = ''
    SOURCE_SHOP_API = ''
    SOURCE_SHOP_PASSWORD = ''

while True:
    print('---------------- DESTINATION SHOP INFORMATION ----------------')
    while __is_empty(DESTINATION_SHOP_URL):
        DESTINATION_SHOP_URL = input('Input your destination shop URL: ').strip()
    while __is_empty(DESTINATION_SHOP_API):
        DESTINATION_SHOP_API = input('Input your destination shop API: ').strip()
    while __is_empty(DESTINATION_SHOP_PASSWORD):
        DESTINATION_SHOP_PASSWORD = input('Input your destination shop password: ').strip()
    destination_shop = start(DESTINATION_SHOP_URL, DESTINATION_SHOP_API, DESTINATION_SHOP_PASSWORD)
    if destination_shop is not None:
        break
    print('Your destination shop input is wrong, please re-input')
    DESTINATION_SHOP_URL = ''
    DESTINATION_SHOP_API = ''
    DESTINATION_SHOP_PASSWORD = ''

print('---------------- READING INFORMATION_MAPPING.TXT FILE ----------------')
try:
    with open('information_mapping.txt') as information_mapping:
        for line in information_mapping:
            pair = line.split('|')
            if len(pair) == 2:
                try:
                    replace_information[pair[0].strip()] = pair[1].strip()
                except Exception as e:
                    print(e)
            else:
                print('Your information_mapping file contains error. Please fix it!')
except IOError:
    print('It looks like information_mapping.txt file is not exist. No value will be changed from source shop')

# Get pages from source shop

# Firstly need to activate source shop

source_shop = start(SOURCE_SHOP_URL, SOURCE_SHOP_API, SOURCE_SHOP_PASSWORD)
pages_array = []

print('---------------- STARTING GETTING PAGES FROM SOURCE SHOP ----------------')

for page in source_shop.Page.find():
    try:
        print('Getting page: ' + page.title)
        push_page = shopify.Page()
        push_page.title = page.title
        body_html = str(page.body_html)
        for key in replace_information.keys():
            try:
                if key in body_html:
                    body_html = body_html.replace(key, replace_information[key])
                else:
                    # It could contain 160 ASCII (non-breaking) char instead of 32 ASCII (space), so let's replace it
                    replace_string = replace_information[key].replace(' ', u"\u00A0")
                    key = key.replace(' ', u"\u00A0")
                    body_html = body_html.replace(key, replace_string)
            except Exception as e:
                print(e)
        push_page.body_html = body_html
        push_page.template_suffix = page.template_suffix
        pages_array.append(push_page)
    except Exception as e:
        print(e)

# Secondly push page to destination shop
# Active destination shop
destination_shop = start(DESTINATION_SHOP_URL, DESTINATION_SHOP_API, DESTINATION_SHOP_PASSWORD)

count_pages_cloned = 0
print('---------------- START PUSHING PAGES TO DESTINATION SHOP ----------------')
for page in pages_array:
    try:
        print('Cloning page: ' + page.title)
        to_push_page = destination_shop.Page()
        to_push_page.title = page.title
        to_push_page.body_html = page.body_html
        to_push_page.template_suffix = page.template_suffix
        to_push_page.save()
        count_pages_cloned = count_pages_cloned + 1
    except Exception as e:
        print(e)
    finally:
        import time
        time.sleep(0.5)

print('---------------- REPORT ----------------')
print('Clone %s page(s) successfully!' % str(count_pages_cloned))
