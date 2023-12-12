from flask import Flask, jsonify, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("POSTGRES_DB_URI")
db = SQLAlchemy(app)


class Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    

@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/all")
def get_all_cafes():
    all_ingredients = db.session.query(Ingredients).all()
    all_data = []
    for ingredient in all_ingredients:
        ingredients = dict(name=ingredient.name,
                     description=ingredient.description,
                     rating=ingredient.rating,
                    )
        all_data.append(ingredients)

    return jsonify(ingredients=all_data)


# ## HTTP GET - Read Record
@app.route("/ingredients", methods=["GET"])
def search_ingredients():
    loc_data = request.args.get('name')
    ingredients = Ingredients.query.filter_by(name=loc_data.title()).all()
    if ingredients: # if the data requested exist
        all_data = ingredients
        data_list = []
        for data in all_data:
            data_dict = dict(name=data.name,
                       description=data.description,
                       rating=data.rating,
                        )
            data_list.append(data_dict)

        return jsonify(ingredient=data_list)
    else:
        not_found = {"Not Found": "Sorry, we don't have this ingredient information."}
        return jsonify(error=not_found)
    
    
API_KEY = "secret_api_key"


## HTTP POST - Post Record
@app.route("/add", methods=['GET', 'POST'])
def post_ingredient():
    # Check if the correct API key was provided
    api_key_provided = request.headers.get('api-key')
    if api_key_provided != API_KEY:
        # If the key is wrong or not provided, return an error
        abort(401, description="Unauthorized: API key is missing or invalid.")
    
    if request.method == "POST":
        data = request.json

        
        if isinstance(data, list): # Check if data is a list of items
            for item in data:
                process_ingredient(item)
        elif isinstance(data, dict): # It's a single item
            process_ingredient(data)
        else:
            abort(400, description="Bad Request: Invalid data format.")

        return jsonify(response={"success": "Successfully added new ingredient(s)."})
    else:
        return jsonify(response={"error": "Could't add new ingredient to database."})


def process_ingredient(item):
    name = item.get('name')
    description = item.get('description')
    rating = item.get('rating')

    if not name or not description or not rating:
        abort(400, description="Bad Request: 'name', 'description', and 'rating' fields are required.")

    existing_ingredient = Ingredients.query.filter_by(name=name).first()
    if existing_ingredient:
        abort(400, description="An ingredient with this name already exists.")

    new_ingredient = Ingredients(name=name, description=description, rating=rating)
    db.session.add(new_ingredient)
    db.session.commit()


## HTTP DELETE - Delete Record
@app.route("/delete/<int:id>", methods=['GET', 'DELETE'])
def delete_cafe(id):
    apikey = request.headers.get('api-key')

    if apikey != API_KEY:
        abort(401, description="Unauthorized: API key is missing or invalid.")
    
    if request.method == "DELETE":
            try:
                ingredient_to_delete = Ingredients.query.get(id)
                db.session.delete(ingredient_to_delete)
                db.session.commit()
                return jsonify(response={"Success": "Successfully deleted the cafe from the database."})
            except:
                return jsonify(response={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=False)