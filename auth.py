from random import choices
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText


def init_service(client_secrets_file: str):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    flow = InstalledAppFlow.from_client_secrets_file(
        'data/client_secret_620369742470-9kv0kkroc2n54llap78f8uj8h7850ed7.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=0)

    return build('gmail', 'v1', credentials=creds)

def generate_auth_code(length: int=6) -> str:
    return ''.join(choices('0123456789', k=length))

def generate_verification_message(to: str, content: dict):
    message = MIMEText(f'''
        Здравствуйте!
        Вы запрашивали код подтверждения для входа на сайт LEMFOODS.
                               
        Ваш код:
        🔢 {content['code']}
        
        
        Пожалуйста, введите этот код на сайте, чтобы завершить авторизацию.
        Код действителен в течение 10 минут.
        
        Если вы не запрашивали этот код, просто проигнорируйте это письмо.
        
        С уважением,
        Команда IT4World
    ''')
    message['to'] = to
    message['subject'] = '🔐 Код подтверждения для входа на сайт LEMFOODS'
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, message):
    try:
        service.users().messages().send(userId='me', body=message).execute()
    
        return 0
    except Exception as err:
        return 1