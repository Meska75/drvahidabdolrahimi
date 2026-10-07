import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    digest = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(plain):
    if not plain:
        return ''
    return _fernet().encrypt(plain.encode('utf-8')).decode('ascii')


def decrypt_secret(token):
    if not token:
        return ''
    try:
        return _fernet().decrypt(token.encode('ascii')).decode('utf-8')
    except (InvalidToken, ValueError, TypeError):
        return ''


def mask_secret(plain):
    if not plain:
        return ''
    if len(plain) <= 4:
        return '••••'
    return '••••' + plain[-4:]
