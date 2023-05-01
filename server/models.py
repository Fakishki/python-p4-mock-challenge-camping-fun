from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'
    
    serialize_rules = ("-created_at", "-updated_at", "-campers.activities", "-signups.activity" )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    signups = db.relationship("Signup", back_populates="activity")
    campers = association_proxy("signups", "camper",
        creator=lambda cmp: Signup(camper=cmp))

    def __repr__(self):
        return f"Activity: {self.name}"
    

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'
    
    serialize_rules = ("-activity.signups", "-camper.signups")
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))

    activity = db.relationship("Activity", back_populates="signups")
    camper = db.relationship("Camper", back_populates="signups")

    @validates("time")
    def validates_time(self, key, time):
        if 0 <= time <= 23:
            return time
        else:
            raise ValueError("Time must be an hour between 0 and 23")

    def __repr__(self):
        return f"Signup: {self.id}, Time: {self.time}, Activity: {self.activity.name}, Camper: {self.camper.name}"
    

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    serialize_rules = ("-created_at", "-updated_at", "-activities.campers", "-signups.camper")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    signups = db.relationship("Signup", back_populates="camper")
    activities = association_proxy("signups", "activity",
        creator=lambda act: Signup(activity=act))
    
    @validates("name")
    def validate_name(self, key, name):
        if name:
            return name
        raise ValueError("Camper must have name.")
    
    @validates("age")
    def validates_age(self, key, age):
        if 8 <= age <= 18:
            return age
        raise ValueError("Camper must be between 8 and 18 years old.")
    
    def __repr__(self):
        return f"Camper: {self.name}, Age: {self.age}"

# add any models you may need. 