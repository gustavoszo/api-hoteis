import sys
sys.path.append('c:\\Users\\Raquel\\Documents\\VSCode\\Rest API')
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.site import SiteModel
from models.hotel import HotelModel

class Sites(Resource): # métodos de /sites
    
    def get(self):
        return {'sites': [site.json() for site in SiteModel.query.all()] }, 200

    @jwt_required()
    def post(self):
        parametro = reqparse.RequestParser()
        parametro.add_argument('url')
        url = parametro.parse_args()['url']
        site = SiteModel.find_site(url)
        if site:
            return {'message': f'the site {url} already exists'}, 400 

        site = SiteModel(url)
        try:
            site.save_site()
        except:
            return {'message': 'an internal error ocurred trying to creat a new site'}
        return site.json(), 201
    
class Site(Resource): # metodos de sites/{url}

    def get(self, url):
        site = SiteModel.find_site(url)
        if site:
            return site.json(), 200
        return {'message': 'Site not found.'}
    
    @jwt_required()
    def delete(self, url):
        site = SiteModel.find_site(url)
        if not site:
            return {'message': 'site not found'}, 404
        try:
            site.delete_site()
        except:
            return {'message': 'an internal error ocurred trying to delete the site'}
        return {'message': 'Site deleted'}, 200