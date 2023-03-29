from flask import Flask, jsonify, request
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
import requests

app = Flask(__name__)

# Configuración de la conexión a la base de datos MongoDB

client = MongoClient("MONGO_URI")
db = client.pokedex
collection = db.pokemons




# Función de controlador para obtener los nombres y ids de todos los Pokémon
@app.route('/pokemons/names', methods=['GET'])
def get_pokemon_names():
    try:
        # Realizamos una petición GET a la API pública de Pokemon
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=1000')
        # Convertimos la respuesta JSON en un diccionario de Python
        data = response.json()
        # Obtenemos la lista de resultados de la respuesta
        results = data['results']
        # Creamos una lista de diccionarios que contienen el nombre y el id de cada Pokémon
        pokemon_names = [{'name': result['name'], 'id': int(result['url'].split('/')[-2])} for result in results]
        # Retornamos la lista de Pokémon como una respuesta JSON con un código de estado 200
        return jsonify(pokemon_names), 200
    except requests.exceptions.RequestException as e:
        # En caso de un error al hacer la petición GET, retornamos una respuesta JSON con un mensaje de error y un código de estado 500
        return jsonify({'message': f'Error getting pokemon names: {str(e)}'}), 500
    



# Función de controlador para obtener la data completa de un Pokémon por id
@app.route('/pokemons/<int:id>', methods=['GET'])
def get_pokemon(id):
    try:
        # Realizamos una petición GET a la API pública de Pokemon para obtener la información del Pokémon por id
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{id}')
        # Convertimos la respuesta JSON en un diccionario de Python
        data = response.json()
        # Retornamos la información del Pokémon como una respuesta JSON con un código de estado 200
        return jsonify(data), 200
    except requests.exceptions.RequestException as e:
        # En caso de un error al hacer la petición GET, retornamos una respuesta JSON con un mensaje de error y un código de estado 500
        return jsonify({'message': f'Error getting pokemon data: {str(e)}'}), 500
    



# Función de controlador para crear un nuevo Pokémon con toda su información
@app.route('/pokemons', methods=['POST'])
def create_pokemon():
    try:
        # Obtenemos los datos del nuevo Pokémon a través del cuerpo de la petición
        pokemon_data = request.get_json()
        # Insertamos el nuevo Pokémon en la colección de la base de datos
        result = collection.db.insert_one(pokemon_data)
        # Retornamos una respuesta JSON con un mensaje de éxito y el id del nuevo Pokémon creado con un código de estado 201
        return jsonify({'message': 'Pokemon created successfully', 'id': str(result.inserted_id)}), 201
    except errors.PyMongoError as e:
        # En caso de un error al insertar los datos en la base de datos, retornamos una respuesta JSON con un mensaje de error y un código de estado 500
        return jsonify({'message': f'Error creating pokemon: {str(e)}'}), 500

    


# Función de controlador para modificar los atributos de un Pokémon guardado
@app.route('/pokemons/<id>', methods=['PUT'])
def update_pokemon(id):
    try:
        # Obtenemos los datos actualizados del Pokémon a través del cuerpo de la petición
        updated_pokemon_data = request.get_json()
        # Actualizamos el Pokémon en la base de datos
        result = collection.db.update_one({'_id': ObjectId(id)}, {'$set': updated_pokemon_data})
        if result.modified_count == 1:
            # Si la operación de actualización ha modificado un registro, retornamos una respuesta JSON con un mensaje de éxito y un código de estado 200
            return jsonify({'message': 'Pokemon updated successfully'}), 200
        else:
            # Si no se ha encontrado el Pokémon en la base de datos, retornamos una respuesta JSON con un mensaje de error y un código de estado 404
            return jsonify({'message': 'Pokemon not found'}), 404
    except errors.PyMongoError as e:
        # En caso de un error al actualizar los datos en la base de datos,una respuesta JSON con un mensaje de error y un código de estado 500
        return jsonify({'message': f'Error updating pokemon: {str(e)}'}), 500
    
 


# Función de controlador para eliminar un Pokémon de la base de datos
@app.route('/pokemons/<id>', methods=['DELETE'])
def delete_pokemon(id):
    try:
        # Eliminamos el Pokémon de la base de datos
        result = collection.db.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 1:
            # Si la operación de eliminación ha eliminado un registro, retornamos una respuesta JSON con un mensaje de éxito y un código de estado 200
            return jsonify({'message': 'Pokemon deleted successfully'}), 200
        else:
            # Si no se ha encontrado el Pokémon en la base de datos, retornamos una respuesta JSON con un mensaje de error y un código de estado 404
            return jsonify({'message': 'Pokemon not found'}), 404
    except errors.PyMongoError as e:
        # En caso de un error al eliminar los datos en la base de datos, retornamos una respuesta JSON con un mensaje de error y un código de estado 500
        return jsonify({'message': f'Error deleting pokemon: {str(e)}'}), 500




# Función de controlador para obtener todos los Pokémons en la base de datos
@app.route('/pokemons/list', methods=['GET'])
def get_all_pokemons():
    try:
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=1000')
        # Convertimos la respuesta JSON en un diccionario de Python
        data = response.json()
        # Obtenemos la lista de resultados de la respuesta
        results = data['results']
        pokemon_list = [{'name': result['name'], 'id': int(result['url'].split('/')[-2])} for result in results]
        collection.db.insert_many(pokemon_list)
        # Retornamos la lista de Pokémons en formato JSON con un código de estado 200
        return jsonify({'result':'Pokemon saved in database'}), 200
    except errors.PyMongoError as e:
        # En caso de un error al obtener los datos de la base de datos, retornamos una respuesta JSON con un mensaje de error y un código de estado 500
        return jsonify({'message': f'Error getting pokemons: {str(e)}'}), 500 
    





# Función principal para iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True) 
