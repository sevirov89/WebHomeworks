from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.db.session import db
from app.errors import APIError
from app.models import User


def hash_password(plain: str) -> str:
    return generate_password_hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)


def issue_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode(
        {'sub': str(user_id), 'exp': exp},
        current_app.config['SECRET_KEY'],
        algorithm='HS256',
    )


def current_user_from_token() -> User:
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        raise APIError('Требуется авторизация', 401)
    token = header[7:].strip()
    if not token:
        raise APIError('Требуется авторизация', 401)
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256'],
        )
        user_id = int(payload['sub'])
    except jwt.PyJWTError:
        raise APIError('Недействительный токен', 401)
    user = db.session.get(User, user_id)
    if user is None:
        raise APIError('Недействительный токен', 401)
    return user
