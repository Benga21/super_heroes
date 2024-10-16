from sqlite3 import Connection
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _):
    if not isinstance(dbapi_connection, Connection):
        return
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    #  this Serialization rules are to prevent circular references
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    @validates('strength')
    def validate_strength(self, key, value):
        """Ensure strength is one of 'Strong', 'Weak', or 'Average'."""
        valid_values = ['Strong', 'Weak', 'Average']
        if value not in valid_values:
            raise ValueError(f'Strength must be one of {valid_values}.')
        return value


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String, unique=True)

    #  here are relationships
    hero_powers = db.relationship('HeroPower', backref='hero', cascade='all, delete-orphan')
    powers = association_proxy('hero_powers', 'power')


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)

    #  another Relationships
    hero_powers = db.relationship('HeroPower', backref='power', cascade='all, delete-orphan')

    @validates('description')
    def validate_description(self, key, value):
        """Ensure description is at least 20 characters long."""
        if not (value and len(value) >= 20):
            raise ValueError(f'Description must be at least 20 characters long.')
        return value
