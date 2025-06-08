from flask import Blueprint, request, jsonify
from .models import Result, db


# Создание Blueprint для API
api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/ping', methods=['GET'])
def ping():
    """Эндпоинт для проверки работоспособности сервиса."""
    return jsonify({"status": "ok"}), 200


@api_bp.route('/submit', methods=['POST'])
def submit():
    """Принимает данные в формате JSON и сохраняет их в БД."""
    data = request.get_json()
    if not data or 'name' not in data or 'score' not in data:
        return jsonify({"error": "Missing name or score"}), 400

    try:
        name = data['name']
        score = int(data['score'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format"}), 400

    new_result = Result(name=name, score=score)
    db.session.add(new_result)
    db.session.commit()

    return jsonify({
        "message": "Result submitted successfully",
        "id": new_result.id
    }), 201


@api_bp.route('/results', methods=['GET'])
def get_results():
    """Возвращает все записи из базы данных."""
    all_results = Result.query.order_by(Result.timestamp.desc()).all()
    return jsonify([result.to_dict() for result in all_results]), 200