from flask_restful import Resource, Api
from flask import request, jsonify
from flask_security import login_user, logout_user
from application.models import User
from werkzeug.security import check_password_hash

api = Api()

class LoginAPI(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        
        if not user:
            return {'message': 'User not found'}, 404
            
        if user.check_password(data.get('password')):
            login_user(user)
            role = user.roles[0].name if user.roles else None
            return {
                'username': user.username,
                'email': user.email,
                'role': role
            }, 200
        return {'message': 'Invalid credentials'}, 401

class LogoutAPI(Resource):
    def post(self):
        logout_user()
        return {'message': 'Logged out successfully'}, 200

api.add_resource(LoginAPI, '/api/login')
api.add_resource(LogoutAPI, '/api/logout')
