from flask import Flask, jsonify, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("POSTGRES_DB_URI")
db = SQLAlchemy(app)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"{self.name}"


@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record
@app.route("/all")
def get_all_cafes():
    all_ingredients = db.session.query(Ingredient).all()
    all_data = []
    for ingredient in all_ingredients:
        ingredients = dict(name=ingredient.name,
                     description=ingredient.description
                    )

        all_data.append(ingredients)

    return jsonify(ingredients=all_data)


## HTTP GET - Read Record
@app.route("/ingredients", methods=["GET"])
def search_ingredients():
    loc_data = request.args.get('name')
    ingredients = Ingredient.query.filter_by(name=loc_data.title()).all()
    if ingredients: # if the data requested exist
        all_data = ingredients
        data_list = []
        for data in all_data:
            data_dict = dict(name=data.name,
                       description=data.description
                        )
            
            data_list.append(data_dict)

        return jsonify(ingredient=data_list)
    else:
        not_found = {"Not Found": "Sorry, we don't have this ingredient information."}
        return jsonify(error=not_found)
    
    
API_KEY = "secret_api_key"

## HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def post_ingredient():
    # Check if the correct API key was provided
    api_key_provided = request.headers.get('api-key')
    if api_key_provided != API_KEY:
        # If the key is wrong or not provided, return an error
        abort(401, description="Unauthorized: API key is missing or invalid.")
    
    if request.method == "POST":
        name = request.json.get('name')
        description = request.json.get('description')

        if not name or not description:
            abort(400, description="Bad Request: 'name' and 'description' fields are required.")

        existing_ingredient = Ingredient.query.filter_by(name=name).first()
        if existing_ingredient:
            abort(400, description="An ingredient with this name already exists.")

        new_ingredient = Ingredient(name=name, description=description)
        db.session.add(new_ingredient)
        db.session.commit()
        return jsonify(response={"success": "Successfully added new ingredient."})
    else:
        return jsonify(response={"error": "Could't add new ingredient to database."})



if __name__ == '__main__':
    app.run(debug=False)