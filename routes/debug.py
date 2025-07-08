from flask import Blueprint, jsonify, request
from models.admin import Admin

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/admins')
def debug_admins():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'username required as query param'}), 400
    admins = Admin.query.filter_by(username=username).all()
    return jsonify([
        {
            'id': a.id,
            'username': a.username,
            'password_hash': a.password_hash,
            'is_active': a.is_active
        } for a in admins
    ])
