import requests
from requests.auth import HTTPBasicAuth
from fastapi import FastAPI, Path, Request, HTTPException
from pydantic import BaseSettings
from fastapi.templating import Jinja2Templates


class Settings(BaseSettings):
    consumer_key: str
    consumer_secret: str

    class Config:
        env_file = ".env"

settings = Settings()
mpesa = FastAPI()
templates = Jinja2Templates(directory="templates")

@mpesa.get("/token/{access_token}")
def generate_token(access_token: str = Path(...)):
    auth = HTTPBasicAuth(settings.consumer_key, settings.consumer_secret)
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=auth)
    response_json = response.json()
    access_token = response_json["access_token"]
    return access_token


@mpesa.get("/qr/{qr_code}")
def generate_qr(qr_code: str = Path(...)):
    access_token = generate_token()
    payment_details = {
        "MerchantName": "TEST SUPERMARKET",
        "RefNo": "Invoice Test",
        "Amount": 10,
        "TrxCode": "BG",
        "CPI": "373132",
        "Size": "300"
    }
    qr_url = "https://sandbox.safaricom.co.ke/mpesa/qrcode/v1/generate"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(qr_url, json=payment_details, headers=headers)
    response_json = response.json()
    qr_code = response_json["QRCode"]
    return {"qr_code": qr_code}

@mpesa.post("/callbackdata")
async def call_back(request: Request):
    json_data = await request.json()


    # Extract the desired fields
    merchant_request_id = json_data['Body']['stkCallback']['MerchantRequestID']
    checkout_request_id = json_data['Body']['stkCallback']['CheckoutRequestID']
    result_code = json_data['Body']['stkCallback']['ResultCode']
    result_desc = json_data['Body']['stkCallback']['ResultDesc']
    amount = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
    mpesa_receipt_number = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
    transaction_date = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][2]['Value']
    phone_number = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']

    # Print the extracted values
    print("MerchantRequestID:", merchant_request_id)
    print("CheckoutRequestID:", checkout_request_id)
    print("ResultCode:", result_code)
    print("ResultDesc:", result_desc)
    print("Amount:", amount)
    print("MpesaReceiptNumber:", mpesa_receipt_number)
    print("TransactionDate:", transaction_date)
    print("PhoneNumber:", phone_number)


@mpesa.get("/stkpush")
def payment_status():
    access_token = generate_token()
    transaction_details = {
        "BusinessShortCode": "174379",
        "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3",
        "Timestamp":"20160216165627",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",
        "PartyA":"254719259795",
        "PartyB":"174379",
        "PhoneNumber":"254719259795",
        "CallBackURL": "https://114b-197-248-202-33.ngrok-free.app/callbackdata",
        "AccountReference":"Test",
        "TransactionDesc":"Test"
    }
    status_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(status_url, json=transaction_details, headers=headers)
    response_json = response.json()
    return response_json
