import sys
sys.path.append('c:\\Users\\Raquel\\Documents\\VSCode\\Rest API')
from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from secrets import compare_digest
from blacklist import BLACKLIST
import traceback
from flask import render_template, make_response

argumentos = reqparse.RequestParser()
argumentos.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank")
argumentos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be left blank")
argumentos.add_argument('email', type=str)
argumentos.add_argument('ativado', type=bool, default=False)

class User(Resource):

    def get(self, id_user):
        user = UserModel.find_user(id_user)
        if user:
            return user.json(), 200
        return {'message': f'user id {id_user} not found'}, 404

    @jwt_required() # precisa estar logado para fazer a requisição
    def delete(self, id_user):
        user = UserModel.find_user(id_user)
        if user:
            try:
                user.delete_user()
            except:
                return {'message': 'An internal error ocurred trying to delete user'}
            return {'message': 'User deleted.'}, 200
        return {'message': 'User not found.'}, 404

class UserRegister(Resource):

    def post(self):
        dados = argumentos.parse_args()
        if not dados.get('email') or dados.get('email') is None:
            return {'message': "The field 'email' cannot be left blank"}, 400

        if UserModel.find_by_email(dados['email']):
            return {'message': f'The email {dados["email"]} already exists.'}, 400
        
        if UserModel.find_by_login(dados['login']):
            return {'message': f'The login {dados["login"]} already exists.'}, 400
        
        user = UserModel(**dados)
        user.ativado = False
        try:
            user.save_user()
            user.send_confirm_email()
        except:
            user.delete_user()
            traceback.print_exc()
            return {'message': 'An internal server error has ocurred'}, 500
        return {'message': 'User created successfully'}, 201

class UserLogin(Resource):

    @staticmethod
    def post():
        dados = argumentos.parse_args()
        user = UserModel.find_by_login(dados['login'])
        if user and compare_digest(user.senha, dados['senha']):
            if user.ativado:
                token_de_acesso = create_access_token(identity=user.id_user) # token que recebe uma identidade
                return {'Token de acesso': token_de_acesso}, 200
            return {'message': f"user 'id {user.id_user}' is not activated"}
        return {'message': 'The Username or password is incorrect'}, 401 # unauthorized
    
class UserLogOut(Resource):
    
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # jti = JWT Token Indentifier && 'jti' pega o identificador do jwt(id do token)
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged Out successfully'}, 401

class UserConfirm(Resource):

    @staticmethod
    def get(id_user):
        user = UserModel.find_user(id_user)
        if not user:
            return {'message': f"user '{id_user}' not found" }, 404
        
        user.ativado = True
        user.save_user()
        # return {'message': f"user '{id_user}' activate successfully"}

        # Muda o headers padrao (json) do restful para o retorno ser a pagina html
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('user_confirm.html', email=user.email, usuario=user.login), 200, headers)