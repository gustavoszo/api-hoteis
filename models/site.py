import sys
sys.path.append('c:\\Users\\Raquel\\Documents\\VSCode\\Rest API')
from sql_alchemy import banco

class SiteModel(banco.Model):
    __tablename__ = 'sites'

    id_site = banco.Column(banco.Integer, primary_key=True)
    url = banco.Column(banco.String(80))
    hoteis = banco.relationship('HotelModel') # Lista de objetos hoteis // hoteis instancias da classe hoteis

    def __init__(self, url):
        self.url = url

    def json(self):
        return {
            'id_site': self.id_site,
            'url': self.url,
            'hoteis': [hotel.json() for hotel in self.hoteis]
        }

    @classmethod
    def find_site(cls, url):
        site = cls.query.filter_by(url=url).first()
        if site:
            return site
        return None
    
    @classmethod
    def find_by_id(cls, id):
        site = cls.query.filter_by(id_site=id).first()
        if site:
            return True
        return None
    
    def save_site(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_site(self):
        [hotel.delete_hotel() for hotel in self.hoteis]
        banco.session.delete(self)
        banco.session.commit()
