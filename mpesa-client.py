import requests
from requests.auth import HTTPBasicAuth
from fastapi import FastAPI, Path
from pydantic import BaseSettings

class Settings(BaseSettings):
    consumer_key: str
    consumer_secret: str

    class Config:
        env_file = ".env"

settings = Settings()
mpesa = FastAPI()

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

@mpesa.get("/result/{ResultCode}")
def payment_status(result_code: str = Path(...)):
    access_token = generate_token()
    transaction_details = {
        "BusinessShortCode":"174379",    
        "Password": "MTc0Mzc5YmZiMjc5TliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3",    
        "Timestamp":"20160216165627",    
        "CheckoutRequestID": "ws_CO_260520211133524545",    
    }
    status_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(status_url, json=transaction_details, headers=headers)
    response_json = response.json()
    result_code = response_json["ResultCode"]
    return result_code


