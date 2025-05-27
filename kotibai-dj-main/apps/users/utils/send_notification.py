import firebase_admin
from firebase_admin import credentials, messaging

# Yangi xizmat ko'rsatish hisobining JSON faylini yuklash
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)


def send_firebase_notification(token, title, body, res_id):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            "id": f"{res_id}"
        },
        token=token,
    )

    response = messaging.send(message)
    print('Successfully sent message:', response)

# # Test ma'lumotlar
# device_token = 'fOKbxbIXQCKiMqJOOUP4Ur:APA91bEZCHiWYYErXXTLgI-NNGzsLP3gFW8mFvE_hjZNrsHUwrPgo-9_JGFj0JZ0T8qiyE2ahpjReed7OfahjTAhm995SM01P8hWM_8ct1MNPvJVdCbsi57DeQ1dv0-0dCVW7PljxVGV'
# notification_title = 'Salom'
# notification_body = 'Bu test bildirishnomasi'
#
# send_firebase_notification(device_token, notification_title, notification_body)
