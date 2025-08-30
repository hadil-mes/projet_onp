from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from flask_login import UserMixin

# Définir db ici sans lier à app
db = SQLAlchemy()

# =====================
# Table des utilisateurs
# =====================
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    lots = db.relationship("Lot", backref="vendeur", lazy=True)
    bids = db.relationship("Bid", backref="acheteur", lazy=True)

    def __repr__(self):
        return f"<User {self.nom}>"

# =====================
# Table des lots
# =====================

class Lot(db.Model):
    __tablename__ = "lots"

    id = db.Column(db.Integer, primary_key=True)
    espece = db.Column(db.String(100), nullable=False)
    poids = db.Column(db.Float, nullable=False)
    origine = db.Column(db.String(100), nullable=False)
    prix_base = db.Column(db.Float, nullable=False)
    prix_actuel = db.Column(db.Float, nullable=False)
    vendeur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relation avec Bid (enchères)
    encheres = db.relationship("Bid", backref="lot", lazy=True)

    # Date de fin (par défaut 5 minutes après création)
    date_fin = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=5)
    )

    def est_termine(self):
        """Vérifie si l'enchère est finie"""
        return datetime.utcnow() > self.date_fin

    def __repr__(self):
        return f"<Lot {self.espece} ({self.poids}kg)>"
# =====================
# Table des enchères
# =====================


class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    lot_id = db.Column(db.Integer, db.ForeignKey("lots.id"), nullable=False)
    acheteur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Bid {self.montant} sur lot {self.lot_id}>"
