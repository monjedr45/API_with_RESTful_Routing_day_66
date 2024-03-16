from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import json
from flask import session as flask_session
import random


app = Flask(__name__)
engine = create_engine('sqlite:///cafes.db')
session = Session(engine)
Base = declarative_base()

class Cafe(Base):
    __tablename__ = 'cafe'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    map_url = Column(String(500), nullable=False)
    img_url = Column(String(500), nullable=False)
    location = Column(String(250), nullable=False)
    seats = Column(String(250), nullable=False)
    has_toilet = Column(Boolean, nullable=False)
    has_wifi = Column(Boolean, nullable=False)
    has_sockets = Column(Boolean, nullable=False)
    can_take_calls = Column(Boolean , nullable=False)
    coffee_price = Column(String(250), nullable=False)

Base.metadata.create_all(engine)




@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random", methods=['GET', 'POST'])
def random_cofee():
    cafe_table = session.query(Cafe).all()
    all_data_list = []
    for cell in cafe_table:
        all_data = {
            "id": cell.id,
            "name": cell.name,
            "map_url":cell.map_url,
            "img_url":cell.img_url,
            "location":cell.location,
            "seats":cell.seats,
            "has_toilet":cell.has_toilet,
            "has_wifi":cell.has_wifi,
            "has_sockets":cell.has_sockets,
            "can_take_calls":cell.can_take_calls,
            "coffee_price":cell.coffee_price,
        }
        all_data_list.append(all_data)
    rand = random.choice(all_data_list)
    return jsonify(rand) # serialization

@app.route("/all", methods=['GET', 'POST'])
def all_cofee():
    cafe_table = session.query(Cafe).all()
    all_data_list = []
    for cell in cafe_table:
        all_data = {
            "id": cell.id,
            "name": cell.name,
            "map_url":cell.map_url,
            "img_url":cell.img_url,
            "location":cell.location,
            "seats":cell.seats,
            "has_toilet":cell.has_toilet,
            "has_wifi":cell.has_wifi,
            "has_sockets":cell.has_sockets,
            "can_take_calls":cell.can_take_calls,
            "coffee_price":cell.coffee_price,
        }
        all_data_list.append(all_data)
    return jsonify(all_data_list) # serialization


@app.route("/search", methods=['GET', 'POST'])
def search():
    location = request.args.get('location')
    cafe_table = session.query(Cafe).all()
    all_data_list = []
    search_by_location = []

    for cell in cafe_table:
        all_data = {
            "id": cell.id,
            "name": cell.name,
            "map_url":cell.map_url,
            "img_url":cell.img_url,
            "location":cell.location,
            "seats":cell.seats,
            "has_toilet":cell.has_toilet,
            "has_wifi":cell.has_wifi,
            "has_sockets":cell.has_sockets,
            "can_take_calls":cell.can_take_calls,
            "coffee_price":cell.coffee_price,
        }
        all_data_list.append(all_data)

    for item in all_data_list:
        if item['location'] == location:
            search_by_location.append(item)
    if search_by_location==[]:
        error = {
            "error": {
                "Not Found": "No coffees at that location"
            }
        }
        return jsonify(error)
    else:
        return jsonify(search_by_location) # serialization
    

@app.route('/add', methods=["POST"])
def add():
    # Convert boolean values from strings to actual booleans
    has_toilet = request.args.get('has_toilet') == 'true'
    has_wifi = request.args.get('has_wifi') == 'true'
    has_sockets = request.args.get('has_sockets') == 'true'
    can_take_calls = request.args.get('can_take_calls') == 'true'

    add_record = Cafe(
        name=request.args.get('name'),
        map_url=request.args.get('map_url'),
        img_url=request.args.get('img_url'),
        location=request.args.get('location'),
        seats=request.args.get('seats'),
        has_toilet=has_toilet,  
        has_wifi=has_wifi,  
        has_sockets=has_sockets,  
        can_take_calls=can_take_calls,  
        coffee_price=request.args.get('coffee_price'),
    )
    try:
        session.add(add_record)
        session.commit()
    except Exception as e:
        print(f"An error occurred while trying to add coffee {add_record}: {e}")
        session.rollback()

    success = {
        "response": {
            "success": "Successfully added the new cafe"
        }
    }
    return success
    # Use this in postman to post the record to the database: http://127.0.0.1:5000/add?name=monjed&map_url=https://maps.app.goo.gl/R2jCQYdkFZGB7rYb6&img_url=https://media-cdn.tripadvisor.com/media/photo-s/1c/89/6c/51/shelter-coffee-drive.jpg&location=irbid&seats=20-30&has_toilet=true&has_wifi=false&has_sockets=true&can_take_calls=true&coffee_price=£2.30


@app.route('/update-price/<cafe_id>', methods=["PATCH"])
def patch(cafe_id):
    try:
        cafe_by_id = session.query(Cafe).filter_by(id=cafe_id).first()
        new_price=request.args.get('new_price')
        if cafe_by_id:
            cafe_by_id.coffee_price = new_price
            session.commit()
            return {"message": "Successfully Updated"}
        else:
            return {"message": "Cafe not found"}
    except Exception as e:
        return {"error": str(e)}
    

@app.route('/report-closed/<cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    secret = "*G&WS^&D@UI@"
    cafe_by_id = session.query(Cafe).filter_by(id=cafe_id).first()
    api_key=request.args.get('api_key')

    if api_key == secret:
        try:
            if cafe_by_id:
                session.delete(cafe_by_id)
                session.commit()
                return {"message": "Successfully Deleted"}
            else:
                return {"message": "Cafe not found"}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"message": "Authentication Error"}
    # use the following in postman: DELETE http://127.0.0.1:5000/report-closed/22?api_key=*G%26WS^%26D@UI@



if __name__ == "__main__":
    app.run(debug=True)