from lxml import html  
import requests
from exceptions import ValueError
import time
from time import sleep
from sinchsms import SinchSMS
import sched

s = sched.scheduler(time.time, time.sleep)
 
def AmazonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/42.0.2311.90'}
    page = requests.get(url,headers=headers)
    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
 
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
            
            
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None

            
 
            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code is not 200:
                raise ValueError('captha')

            data = {
                    'NAME':NAME,
                    'SALE_PRICE':SALE_PRICE,
                    'CATEGORY':CATEGORY,
                    'ORIGINAL_PRICE':ORIGINAL_PRICE,
                    'AVAILABILITY':AVAILABILITY,
                    'URL':url,
                    }
 
            return data
        except Exception as e:
            print e

# send SMS
def sendSMS(data):
    number = 'your_mobile_number'
    app_key = 'your_app_key'
    app_secret = 'your_secret_key'
    message = "current price of "+data['NAME']+" is Rs. "+ data['SALE_PRICE']
    client = SinchSMS(app_key, app_secret)
    print("Sending '%s' to %s" % (message, number))

    response = client.send_message(number, message)
    message_id = response['messageId']
    response = client.check_status(message_id)

    while response['status'] != 'Successful':
        print(response['status'])
        time.sleep(1)
        response = client.check_status(message_id)

    print(response['status'])

def ReadUrl(sc):
    url = "https://www.amazon.in/Rockerz-510-Wireless-Bluetooth-Headphones/dp/B06Y5LK5QJ/ref=sr_1_omk_4?keywords=boat%2Bheadphones&qid=1651037696&sr=8-4&th=1"
    data = AmazonParser(url)
    # print data['SALE_PRICE'] 
    if data['SALE_PRICE'] <= "1,099.00":
        print "price in expected range!"
        print "sending message to +917217XXXXXX"
        sendSMS(data)
        print "message sent"
    else:
        print "price not in expected range, continuing..."
        s.enter(5, 1, ReadUrl, (sc,))
 
 
if __name__ == "__main__":
    print "starting script"
    s.enter(5, 1, ReadUrl, (s,))
    s.run()
