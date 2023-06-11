import requests
from requests.auth import HTTPBasicAuth
from fastapi import FastAPI, Path, Request
from pydantic import BaseSettings
from fastapi.templating import Jinja2Templates
from database import create_table, populate_table


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
async def callback(request: Request):
    json_data = await request.json()

    transactions = []
    for i in json_data:
        merchant_request_id = json_data['Body']['stkCallback']['MerchantRequestID']
        checkout_request_id = json_data['Body']['stkCallback']['CheckoutRequestID']
        result_code = json_data['Body']['stkCallback']['ResultCode']
        result_desc = json_data['Body']['stkCallback']['ResultDesc']
        amount = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        mpesa_receipt_number = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        transaction_date = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][2]['Value']
        phone_number = json_data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']
        transactions.append((merchant_request_id, checkout_request_id, result_code, result_desc, amount, mpesa_receipt_number, transaction_date, phone_number))

    create_table("Mpesa", ["merchant_request_id VARCHAR(255)","checkout_request_id VARCHAR(255)","result_code INTEGER","result_desc VARCHAR(255)","amount INTEGER","mpesa_receipt_number VARCHAR(255)","transaction_date DATE","phone_number VARCHAR(255)"])
    populate_table("Mpesa", transactions)

@mpesa.get("/stkpush")
def make_payment():
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
