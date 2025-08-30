from app import app, db, User, Lot
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    # ✅ Créer les tables si elles n'existent pas
    db.create_all()

    # ✅ Ajouter vendeur si pas déjà présent
    vendeur = User.query.filter_by(email="ali@onp.com").first()
    if not vendeur:
        vendeur = User(
            nom="Ali Vendeur",
            email="ali@onp.com",
            mot_de_passe=generate_password_hash("123"),
            role="vendeur"
        )
        db.session.add(vendeur)
        db.session.commit()
        print("✅ Vendeur ajouté")
    else:
        print("ℹ️ Vendeur déjà existant")

    # ✅ Ajouter acheteur si pas déjà présent
    acheteur = User.query.filter_by(email="said@onp.com").first()
    if not acheteur:
        acheteur = User(
            nom="Said Acheteur",
            email="said@onp.com",
            mot_de_passe=generate_password_hash("123"),
            role="acheteur"
        )
        db.session.add(acheteur)
        db.session.commit()
        print("✅ Acheteur ajouté")
    else:
        print("ℹ️ Acheteur déjà existant")

    # ✅ Ajouter lot si aucun lot pour ce vendeur
    lot = Lot.query.filter_by(vendeur_id=vendeur.id).first()
    if not lot:
        lot1 = Lot(
            espece="Sardine",
            poids=50,
            origine="Agadir",
            prix_base=2000,
            prix_actuel=2000,
            vendeur_id=vendeur.id,
            date_fin=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(lot1)
        db.session.commit()
        print("✅ Lot ajouté")
    else:
        print("ℹ️ Lot déjà existant")

print("🎉 Base initialisée sans doublons")
