import sys
sys.path.append('c:\\Users\\Raquel\\Documents\\VSCode\\Rest API')
from sql_alchemy import banco
from flask import request, url_for
from requests import post

mailgun_domain = 'sandbox3ffdd90a20d1443694a01dbd76156ff5.mailgun.org'
mailgun_api_key = '3b2e9696bee4833cf0b93a54a7c90663-5e3f36f5-f9a73e07'
from_title = 'NO-REPLY'
from_email = 'no-reply@restapi.com'

class UserModel(banco.Model):
    __tablename__ = 'usuarios'

    id_user = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40), nullable=False, unique=True)
    senha = banco.Column(banco.String(40), nullable=False)
    email = banco.Column(banco.String(80), nullable=False, unique=True)
    ativado = banco.Column(banco.Boolean)

    def __init__(self, login, senha, email, ativado):
        self.login = login
        self.senha = senha
        self.email = email
        self.ativado = ativado

    def json(self):
        return {
            'id_user': self.id_user,
            'login': self.login,
            'email': self.email,
            'ativado': self.ativado
        }
    
    def send_confirm_email(self):            #class UserConfirm
        link = request.url_root[:-1] + url_for('userconfirm', id_user=self.id_user)  # http://127.0.0.1:5000/confirmacao/{id_user}
        
        return post(
		    f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
		    auth=("api", mailgun_api_key),
		    data={"from": f"{from_title} <{from_email}>",
		    	"to": self.email,
		    	"subject": "Confirmação de cadastro",
		    	"text": f"Confirme seu cadastro clicando no link a seguir: {link}"}
        )

    @classmethod
    def find_user(cls, id_user):
        user = cls.query.filter_by(id_user=id_user).first()
        if user:
            return user
        return None
    
    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None
    
    @classmethod
    def find_by_email(cls, email):
        user = cls.query.filter_by(email=email).first()
        if user:
            return user
        return None
    
    def save_user(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()