from flask import Blueprint, jsonify
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.auth import hash_password, issue_token, verify_password
from app.db.session import db
from app.errors import APIError
from app.models import User
from app.request_utils import parse_json_body
from app.schemas import UserLoginSchema, UserRegisterSchema

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        raw = parse_json_body()
        data = UserRegisterSchema.model_validate(raw).model_dump()
    except ValidationError as e:
        raise APIError(str(e), 400)

    user = User(
        email=data['email'].strip().lower(),
        password_hash=hash_password(data['password']),
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIError('Пользователь с такой почтой уже существует', 409)
    except SQLAlchemyError:
        db.session.rollback()
        raise APIError('Ошибка базы данных', 500)

    return jsonify({'id': user.id, 'email': user.email}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        raw = parse_json_body()
        data = UserLoginSchema.model_validate(raw).model_dump()
    except ValidationError as e:
        raise APIError(str(e), 400)

    email = data['email'].strip().lower()
    user = db.session.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(
            data['password'], user.password_hash):
        raise APIError('Неверная почта или пароль', 401)

    return jsonify({'token': issue_token(user.id)})
