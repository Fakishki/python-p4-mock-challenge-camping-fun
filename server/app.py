#!/usr/bin/env python3

from flask import Flask, request
from flask_migrate import Migrate

from models import db, Activity, Signup, Camper

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route("/campers", methods=["GET", "POST"])
def campers():
    if request.method == "GET":
        return [camper.to_dict(rules=("-activities", "-signups")) for camper in Camper.query.all()]
    elif request.method == "POST":
        fields = request.get_json()
        try:
            camper = Camper(
                name=fields.get("name"),
                age=fields.get("age")
            )
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict()
        except ValueError:
            return {'error': '400: Validation error'}, 400

@app.route("/campers/<int:id>", methods=["GET"])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).one_or_none()
    if camper:
        return camper.to_dict()
    else:
        return {"error": "404: Camper not found"}, 404
    
@app.route("/activities", methods=["GET"])
def activities():
    return [activity.to_dict() for activity in Activity.query.all()]

@app.route("/activities/<int:id>", methods=["DELETE"])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).one_or_none()
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return {}, 204
    return {"error": "404: Activity not found"}, 404

@app.route("/signups", methods=["POST"])
def signups():
    fields = request.get_json()
    try:
        signup = Signup(
            time=fields.get("time"),
            camper_id=fields.get("camper_id"),
            activity_id=fields.get("activity_id")
        )
        db.session.add(signup)
        db.session.commit()
        return signup.to_dict()
    except ValueError:
        return {"error": "400: Validation error"}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
