from instance.app.app import app
from instance.app.models import db

with app.app_context():
    inspector = db.inspect(db.engine)
    colonnes = inspector.get_columns("lots")
    print("📌 Colonnes dans la table 'lots' :")
    for col in colonnes:
        print(" -", col["name"], col["type"])
