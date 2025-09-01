import sqlite3
from datetime import datetime
import pytz

# Connexion à la base SQLite
conn = sqlite3.connect("onp.db")
cursor = conn.cursor()

# Récupérer toutes les dates
cursor.execute("SELECT id, date_fin FROM lot")
rows = cursor.fetchall()

for row in rows:
    lot_id, date_fin_str = row
    if date_fin_str is None:
        continue

    try:
        # Essayer de parser la date (naive)
        date_naive = datetime.fromisoformat(date_fin_str)

        # Si elle n'a pas de timezone -> on force en UTC
        if date_naive.tzinfo is None:
            date_utc = pytz.UTC.localize(date_naive)
            # Sauvegarde en ISO format avec timezone
            cursor.execute(
                "UPDATE lot SET date_fin = ? WHERE id = ?",
                (date_utc.isoformat(), lot_id)
            )
            print(f"✅ Lot {lot_id} corrigé -> {date_utc}")
    except Exception as e:
        print(f"⚠️ Erreur pour lot {lot_id}: {e}")

conn.commit()
conn.close()
print("✅ Correction terminée.")
