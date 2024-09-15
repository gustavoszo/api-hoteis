import sys
sys.path.append('c:\\Users\\Raquel\\Documents\\VSCode\\Rest API')
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.hotel import HotelModel
from models.site import SiteModel
from resources.filtros import query_sem_cidade, query_com_cidade
from secrets import compare_digest
import sqlite3

path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str, default='', location="args")
path_params.add_argument('estrelas_min', type=float, default=0, location="args")
path_params.add_argument('estrelas_max', type=float, default=5, location="args")
path_params.add_argument('diaria_min', type=float, default=0, location="args")
path_params.add_argument('diaria_max', type=float, default=1000, location="args")
path_params.add_argument('limit', type=int, default=50, location="args")
path_params.add_argument('setoff', type=int, default=0, location="args")
    
hoteis = [
    {
        'id_hotel': 'alpha',
        'nome': 'Hotel Alpha',
        'estrelas': 4.4,
        'diaria': 460.0,
        'cidade': 'Rio de Janeiro'
    },
    {
        'id_hotel': 'bravo',
        'nome': 'Hotel Bravo',
        'estrelas': 4.2,
        'diaria': 430.0,
        'cidade': 'Santa Catarina'
    },
    {
        'id_hotel': 'charlie',
        'nome': 'Hotel Charlie',
        'estrelas': 3.8,
        'diaria': 360.0,
        'cidade': 'Santa Catarina'
    }
]

class Hoteis(Resource):

    def get(self):
        con = sqlite3.connect('instance/banco.db')
        c = con.cursor()

        parametros = path_params.parse_args()

        # query = HotelModel.query
 
        # if parametros["cidade"] != '':
        #     query = query.filter(HotelModel.cidade == parametros["cidade"])
        # query = query.filter(HotelModel.estrelas >= parametros["estrelas_min"])
        # query = query.filter(HotelModel.estrelas <= parametros["estrelas_max"])
        # query = query.filter(HotelModel.diaria >= parametros["diaria_min"])
        # query = query.filter(HotelModel.diaria <= parametros["diaria_max"])
        # query = query.limit(parametros["limit"])
        # query = query.offset(parametros["offset"])
 
        # return {"hoteis": [hotel.json() for hotel in query]}

        if compare_digest(parametros.get('cidade'), ''):   # if parametros['cidade'] == '':
            tupla = tuple([parametros[chave] for chave in parametros if chave != 'cidade'])
            resultado = c.execute(query_sem_cidade, tupla)
        else:
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = c.execute(query_com_cidade, tupla)

        hoteis = list()
        for hotel in resultado:
            hoteis.append({
                'id_hotel': hotel[0],
                'nome': hotel[1],
                'estrelas': hotel[2],
                'diaria': hotel[3],
                'cidade': hotel[4],
                'id_site': hotel[5]
            })
            
        con.close()
        return {'Hoteis': hoteis}, 200
    
class Hotel(Resource):
    
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank")
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('id_site', required=True, help='Every hotel needs to be linked with a site')

    def get(self, id_hotel):
        hotel = HotelModel.find_hotel(id_hotel)
        if hotel:
            return hotel.json(), 200
        return {'message': 'Hotel not found.'}, 404 # not found

    @jwt_required()
    def post(self, id_hotel):
        if HotelModel.find_hotel(id_hotel):
            return {'message': f'hotel id {id_hotel} already exist.'}, 400 # bad request
        
        dados = Hotel.argumentos.parse_args()
        site = SiteModel.find_by_id(dados['id_site'])
        if site:
            hotel = HotelModel(id_hotel, **dados)
            try:
                hotel.save_hotel()
            except:
                return {'message': 'An internal error ocurred trying to save hotel'}
            return hotel.json(), 201
        return {'message': f"id site {dados['id_site']} not found"}
    
    @jwt_required()
    def put(self, id_hotel):
    
        dados = Hotel.argumentos.parse_args()
        site = SiteModel.find_by_id(dados['id_site'])
        hotel_encontrado = HotelModel.find_hotel(id_hotel)

        if not site:
            return {'message': f"id site {dados['id_site']} not found"}, 404
        
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            try:
                hotel_encontrado.save_hotel()
            except:
                return {'message': 'An internal error ocurred trying to save hotel'}
            return hotel_encontrado.json(), 200
        hotel = HotelModel(id_hotel, **dados)
        try:
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to save hotel'}
        return hotel.json(), 201
    
    @jwt_required()
    def delete(self, id_hotel):
        hotel = HotelModel.find_hotel(id_hotel)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An internal error ocurred trying to delete hotel'}
            return {'message': 'Hotel deleted.'}, 200
        return {'message': 'Hotel not found.'}, 404 

