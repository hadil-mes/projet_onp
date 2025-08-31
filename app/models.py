from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import pytz

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # acheteur ou vendeur


class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    espece = db.Column(db.String(100), nullable=False)
    poids = db.Column(db.Float, nullable=False)
    origine = db.Column(db.String(100), nullable=False)
    prix_base = db.Column(db.Float, nullable=False)
    prix_actuel = db.Column(db.Float, nullable=False)
    vendeur_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)

    def est_termine(self):
        now = datetime.now(pytz.UTC)
        date_fin = self.date_fin
        if date_fin.tzinfo is None:
            date_fin = pytz.UTC.localize(date_fin)
        return now > date_fin


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("lot.id"), nullable=False)
    acheteur_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))
