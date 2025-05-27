import requests
from loguru import logger

from root.settings import TIME_PRICES, TELEGRAM_BOT_TOKEN
from users.models import OrderPayment, PromoCodeUsage
from users.utils import loaded_yaml, send_message
from .click import ClickPay


def convert_credits_to_time(credits, lang):
    hours = int(credits // 3600)
    minutes = int((credits % 3600) // 60)
    seconds = int(credits % 60)

    translations = {
        'uz': {'hours': 'soat', 'minutes': 'daqiqa', 'seconds': 'soniya'},
        'en': {'hours': 'hours', 'minutes': 'minutes', 'seconds': 'seconds'},
        'ru': {'hours': 'часов', 'minutes': 'минут', 'seconds': 'секунд'}
    }

    lang_translations = translations.get(lang, translations['en'])

    time_parts = []
    if hours:
        time_parts.append(f"{hours} {lang_translations['hours']}")
    if minutes:
        time_parts.append(f"{minutes} {lang_translations['minutes']}")
    if seconds or not time_parts:
        time_parts.append(f"{seconds} {lang_translations['seconds']}")

    formatted_time = " ".join(time_parts)
    return formatted_time


@logger.catch
def payment_status_approval(transaction_id: str = None, payment_id: int | None = None,
                            current_date: str | None = None, sleep: int | None = None):
    logger.info(f'Payment waiting started for {transaction_id}')
    click = ClickPay()
    if transaction_id:
        order = OrderPayment.objects.filter(transaction_id=transaction_id).first()
    elif payment_id:
        order = OrderPayment.objects.filter(payment_id=payment_id).first()
    if not order:
        return
    user = order.user
    logger.info(f'Payment checking started for {transaction_id} from: {user}')
    if order.status == OrderPayment.StatusChoices.PAID:
        logger.error(f'status Fail for {transaction_id} cause: {order.status}')
        return True, 'Payment has already been paid successfully'
    if payment_id:
        payment_status = click.payment_status_payment_id(payment_id)
    else:
        payment_status = click.payment_status_by_merchant_trans_id(transaction_id, current_date)
    if int(payment_status.get("error_code")) < 0 or int(payment_status.get("payment_status")) < 0:
        order.status = OrderPayment.StatusChoices.CANCEL
        order.save()
        logger.error(payment_status)
        logger.error(f'status Fail for {transaction_id} cause: {order.status}')
        return False, payment_status
    elif int(payment_status.get("payment_status")) == 2:
        order.status = OrderPayment.StatusChoices.PAID
        if order.amount < 36000:
            user.credit_seconds = user.credit_seconds + (order.amount / TIME_PRICES['second'])
            user.credit_sums += int(order.amount)
        elif order.amount == 36000:
            user.credit_seconds += 3600
            user.credit_sums += 36000
        elif order.amount == 100000:
            user.credit_seconds += 10800
            user.credit_sums += 1080000

        elif order.amount == 200000:
            user.credit_seconds += 25200
            user.credit_sums += 252000

        elif order.amount == 500000:
            user.credit_seconds += 61200
            user.credit_sums += 612000
        else:
            user.credit_seconds += (order.amount / TIME_PRICES['second'])
        user.save()
        order.save()
        if order.promocode:
            promocode_usage = PromoCodeUsage.objects.filter(id=order.promocode.id).first()
            if promocode_usage:
                promocode_usage.usage_count = promocode_usage.usage_count + 1
                promocode_usage.save()
            else:
                promocode_usage = PromoCodeUsage.objects.create(promo_code=order.promocode, user=user,
                                                                usage_count=1)
        time_traffic = convert_credits_to_time(user.credit_seconds, user.lang)
        message_template = loaded_yaml['payment_confirmation'].get(user.lang)
        text = message_template['message'].format(
            payment_date=str(order.updated_at).split('.')[0], payment_amount=int(order.amount),
            time_traffic=time_traffic)

        send_message(user.telegram_id,
                     text
                     )
    logger.error(f'status Success for {transaction_id} cause: {payment_status}')
    return True, payment_status
