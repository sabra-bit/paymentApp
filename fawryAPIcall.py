# importing the requests library
import requests
# importing Hash Library
import hashlib
import json
# FawryPayAPI Endpoint
URL = "https://fakefawry.onrender.com/your_api_endpoint"

# Payment Data
def call(cnumber , exYear , exMonth , CVV , value ):
    merchantCode    = '4543474002249996'
    merchantRefNum  = '000'
    merchant_cust_prof_id  = '777777'
    payment_method = 'PayUsingCC'
    amount = value
    cardNumber = cnumber
    cardExpiryYear = exYear
    cardExpiryMonth = exMonth
    cvv = CVV
    returnUrl = "https://developer.fawrystaging.com"
    merchant_sec_key =  '4d6c1f7c-fdcd-433c-b649-f53e790163d4' # For the sake of demonstration
    #signature = hashlib.sha256(merchantCode + (merchantRefNum) + (merchant_cust_prof_id) + (payment_method) +
    #                (amount) + (cardNumber) + (cardExpiryYear) + (cardExpiryMonth) + (cvv) + (merchant_sec_key)).hexdigest()
    #card_info= (merchantCode + merchantRefNum + merchant_cust_prof_id + payment_method +
    #                amount + cardNumber + cardExpiryYear + cardExpiryMonth + cvv + merchant_sec_key)
    card_info = ""
    card_info=card_info +  (merchantCode  + merchantRefNum + payment_method +
                    amount + cardNumber + cardExpiryYear + cardExpiryMonth + cvv +returnUrl+ merchant_sec_key)
    print (card_info.encode())
    signature = hashlib.sha256(str(card_info).encode('utf-8')).hexdigest()
    #signature =hashlib.sha256(card_info.encode()).hexdigest()
    print(signature)
    # defining a params dict for the parameters to be sent to the API
    PaymentData = {
        "merchantCode":merchantCode,
        "merchantRefNum":merchantRefNum,
        "cardNumber": cardNumber,
        "cardExpiryYear": cardExpiryYear,
        "cardExpiryMonth": cardExpiryMonth,
        "cvv": cvv,
        "customerMobile": "01111111111",
        "customerEmail": "a@gmail.com",
        "amount": value,
        "currencyCode": "EGP",
        "language" : "en-gb",
        "returnUrl": returnUrl,
        "chargeItems" : [
            {
                "itemId":"184",
                "price":value,
                "quantity":1
            }
        ],
        "enable3DS":True,
        "paymentMethod": "CARD",
        "signature":signature

    }
    # print (json.dumps(PaymentData))
    headers = {'Content-Type': 'application/json', 'Accept' : 'application/json'}
    # sending post request and saving the response as response object
    status_request = requests.post(URL,  json.dumps(PaymentData),headers=headers)
    print ('sent')
    print (status_request.status_code)
    print (status_request.text)
    return status_request
# extracting data in json format
#status_response = status_request.json()
