# Daraja-API Experience
Engage Daraja API to generate payment details qr code, stkpush prompt for online payments (C2B) and store the transaction details on postgres database. In this project, I use fast api to create scripts and ngrok to create callback urls for data consumption.

## Access Token
To use consume any of the apis, access token is generated and parsed to each call made to daraja apis endpoints.

## QR Code
Generate qr code that captures payment details. With Mpesa App, you can scan the qr code to authorize payment to a till number.

## STKPush
The stkpush prompt to users' phone initiates C2B payment, only requiring them to input Mpesa PIN to confirm transactions. 

## Database
The stkpush transaction is confirmed, a json response is forwarded to the callback url from where I pick relevant data and store it on a database.
