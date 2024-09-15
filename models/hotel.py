import sys
sys.path.append('c:\\Users\\Raquel\\Documents\\VSCode\\Rest API')
from sql_alchemy import banco

class HotelModel(banco.Model):
    __tablename__ = 'hoteis'

    id_hotel = banco.Column(banco.String, primary_key=True)
    nome = banco.Column(banco.String(80))
    estrelas = banco.Column(banco.Float(precision=1))
    diaria = banco.Column(banco.Float(precision=2))
    cidade = banco.Column(banco.String(80))
    id_site = banco.Column(banco.Integer(), banco.ForeignKey('sites.id_site')) # sites = tabela sites

    def __init__(self, id_hotel, nome, estrelas, diaria, cidade, id_site):
        self.id_hotel = id_hotel
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.id_site = id_site

    def json(self):
        return {
            'id_hotel': self.id_hotel,
            'nome': self.nome,
            'estrelas': self.estrelas,
            'diaria': self.diaria,
            'cidade': self.cidade,
            # 'id_site': self.id_site
        }

    @classmethod
    def find_hotel(cls, id_hotel):
        hotel = cls.query.filter_by(id_hotel=id_hotel).first()
        if hotel:
            return hotel
        return None
    
    def save_hotel(self):
        banco.session.add(self)
        banco.session.commit()
            
    def update_hotel(self, nome, estrelas, diaria, cidade, id_site) :
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.id_site = id_site

    def delete_hotel(self):
        banco.session.delete(self)
        banco.session.commit()