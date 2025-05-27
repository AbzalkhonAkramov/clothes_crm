from hashlib import sha1
from time import time

import httpx

from root.settings import CLICK_MERCHANT_ID, CLICK_SERVICE_ID, CLICK_SECRET_KEY, CLICK_MERCHANT_USER_ID


class Click:
    BASE_URL = 'https://api.click.uz/v2/merchant/'

    CREATE_INVOICE_URL = BASE_URL + 'invoice/create'
    INVOICE_URL = BASE_URL + 'invoice/status/{}/{}'
    CARD_TOKEN_URL = BASE_URL + 'card_token/request'
    CARD_TOKEN_VERIFY = BASE_URL + 'card_token/verify'
    CARD_PAYMENT = BASE_URL + 'card_token/payment'
    PAYMENT_STATUS_BY_PAYMENT_ID = BASE_URL + f'payment/status/{CLICK_SERVICE_ID}'
    PAYMENT_STATUS_BY_TRANSACTION_TID = BASE_URL + f'payment/status_by_mti/{CLICK_SERVICE_ID}'

    @staticmethod
    def generate_auth_token():
        timestamp = str(time())[:10]
        digest = sha1(f'{timestamp}{CLICK_SECRET_KEY}'.encode()).hexdigest()
        return f'{CLICK_MERCHANT_USER_ID}:{digest}:{timestamp}'

    @staticmethod
    def make_payload(amount, phone_number, merchant_trans_id):
        payload = {
            'service_id': CLICK_SERVICE_ID,
            'amount': amount,
            'phone_number': phone_number,
            'merchant_trans_id': merchant_trans_id
        }
        return payload

    def make_headers(self):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Auth': self.generate_auth_token()
        }

        return headers

    def make_invoice_url(self, invoice_id):
        return self.INVOICE_URL.format(CLICK_SERVICE_ID, invoice_id)


class ClickPay(Click):
    def create_invoice(self, amount, phone_number, merchant_trans_id):
        headers = self.make_headers()
        payload = self.make_payload(amount, phone_number, merchant_trans_id)
        res = httpx.post(self.CREATE_INVOICE_URL, json=payload, headers=headers)
        return res.json(), res.status_code

    def check_invoice_status(self, invoice_id):
        headers = self.make_headers()
        url = self.make_invoice_url(invoice_id)

        res = httpx.get(url, headers=headers)
        return res.json(), res.status_code

    def create_card_token(self, card_number, expire_date):
        payload = {
            'card_number': card_number,
            'expire_date': expire_date,
            'service_id': CLICK_SERVICE_ID,
            'temporary': 1
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = httpx.post(self.CARD_TOKEN_URL, json=payload, headers=headers)
        return res.json(), res.status_code

    def verify_card_token(self, card_token, sms_code):
        headers = self.make_headers()
        payload = {
            'service_id': CLICK_SERVICE_ID,
            'card_token': card_token,
            'sms_code': sms_code,
        }
        res = httpx.post(self.CARD_TOKEN_VERIFY, json=payload, headers=headers)
        return res.json(), res.status_code

    def card_payment(self, card_token, amount, merchant_trans_id):
        headers = self.make_headers()
        payload = {
            'service_id': CLICK_SERVICE_ID,
            'card_token': card_token,
            'amount': amount,
            'merchant_trans_id': merchant_trans_id
        }
        res = httpx.post(self.CARD_PAYMENT, json=payload, headers=headers)
        return res.json()

    @staticmethod
    def create_redirect_payment(amount, card_type, return_url, transaction_param):
        url = f"""https://my.click.uz/services/pay?service_id={CLICK_SERVICE_ID}&merchant_id={CLICK_MERCHANT_ID}&amount={
        amount}&transaction_param={transaction_param}&return_url={return_url}&card_type={card_type}"""
        return url

    def payment_status_payment_id(self, payment_id):
        headers = self.make_headers()
        res = httpx.get(f'{self.PAYMENT_STATUS_BY_PAYMENT_ID}/{payment_id}', headers=headers)
        return res.json()

    def payment_status_by_merchant_trans_id(self, merchant_trans_id, date=None):
        headers = self.make_headers()
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        res = httpx.get(
            f'{self.PAYMENT_STATUS_BY_TRANSACTION_TID}/{merchant_trans_id}/{date}',
            headers=headers)
        return res.json()
