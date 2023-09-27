from datetime import datetime, timedelta
import jwt
from settings import setting
import smtplib
from email.message import EmailMessage


def encode_jwt(user_id):
    """
    Description: Encode a JWT token with user_id and expiration time.
    Parameter: user_id: int from the db
    Return: [jwt_token: Encoded JWT Token]
    """
    token_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=4)  # Token expiration time
    }
    jwt_token = jwt.encode(token_payload, key=setting.JWT_KEY, algorithm=setting.ALGORITHM)
    return jwt_token


def decode_token(token):
    """
    Description: Decode a JWT token and return the payload.
    Parameter: token: str
    Return: payload consisting of user_id
    """
    try:
        payload = jwt.decode(token, key=setting.JWT_KEY, algorithms=[setting.ALGORITHM])
        return payload
    except jwt.PyJWTError as ex:
        raise ex


def send_email(email, link):
    """
    Description:
        Sends an email containing link to user to complete verification process
    Parameters:
        Param 1: email= recipient email ID to whom mail has to be sent.
        Param 2: link = verification link to be sent in the body of email .
    Return:
        None
    """
    EMAIL_ADDRESS = setting.EMAIL_USER  # os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = setting.EMAIL_PASS  # os.getenv('EMAIL_PASS')

    msg = EmailMessage()
    msg['Subject'] = 'Account Verification '
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content(f'{link}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:   # port 587 is recommended .
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
