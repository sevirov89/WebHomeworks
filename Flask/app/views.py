from flask import Blueprint, jsonify
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.auth import current_user_from_token
from app.db.session import db
from app.errors import APIError, handle_api_error
from app.models import Advertisement
from app.request_utils import parse_json_body
from app.schemas import AdvertisementCreateSchema, AdvertisementUpdateSchema

ads_bp = Blueprint('ads', __name__, url_prefix='/api/v1/ads')


@ads_bp.route('', methods=['POST'])
def create_ad():
    user = current_user_from_token()

    try:
        raw = parse_json_body()
        data = AdvertisementCreateSchema.model_validate(raw).model_dump()
    except ValidationError as e:
        raise APIError(str(e), 400)

    try:
        ad = Advertisement(owner_id=user.id, **data)
        db.session.add(ad)
        db.session.commit()
        return jsonify(ad.dict), 201
    except SQLAlchemyError:
        db.session.rollback()
        raise APIError('Ошибка базы данных', 500)


@ads_bp.route('/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = db.session.get(Advertisement, ad_id)
    if not ad:
        raise APIError('Объявление не найдено', 404)
    return jsonify(ad.dict)


@ads_bp.route('/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    user = current_user_from_token()

    ad = db.session.get(Advertisement, ad_id)
    if not ad:
        raise APIError('Объявление не найдено', 404)
    if ad.owner_id != user.id:
        raise APIError('Нет прав на изменение объявления', 403)

    try:
        raw = parse_json_body()
        payload = AdvertisementUpdateSchema.model_validate(
            raw).model_dump(exclude_unset=True)
    except ValidationError as e:
        raise APIError(str(e), 400)

    try:
        for key, value in payload.items():
            setattr(ad, key, value)
        db.session.commit()
        return jsonify(ad.dict)
    except SQLAlchemyError:
        db.session.rollback()
        raise APIError('Ошибка базы данных', 500)


@ads_bp.route('/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    user = current_user_from_token()

    ad = db.session.get(Advertisement, ad_id)
    if not ad:
        raise APIError('Объявление не найдено', 404)
    if ad.owner_id != user.id:
        raise APIError('Нет прав на удаление объявления', 403)

    try:
        db.session.delete(ad)
        db.session.commit()
        return '', 204
    except SQLAlchemyError:
        db.session.rollback()
        raise APIError('Ошибка базы данных', 500)


def register_error_handlers(app):
    app.register_error_handler(APIError, handle_api_error)
