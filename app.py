from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import qrcode, io, base64

# Import des modèles
from models import db, User, Lot, Bid

# Initialisation Flask
app = Flask(__name__)
app.secret_key = "super_secret_key"

# Config base SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///onp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB avec l’app
db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def generate_qr_code(lot_id):
    # Lien direct vers la page du lot
    lot_url = url_for("detail_lot", lot_id=lot_id, _external=True)
    img = qrcode.make(lot_url)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return base64.b64encode(buf.getvalue()).decode("utf-8")


# =====================
# ROUTES
# =====================

@app.route("/", methods=["GET", "POST"])
def home():
    qr_img = None
    if request.method == "POST":
        data = request.form["text"]
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        qr_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    return render_template("index.html", qr_img=qr_img)

@app.route("/encheres")
def encheres():
    lots = Lot.query.all()
    # Générer le QR code pour chaque lot (en l’ajoutant comme attribut temporaire)
    for lot in lots:
        lot.qr_code = generate_qr_code(lot.id)
    return render_template("encheres.html", lots=lots)

@app.route("/creer-lot", methods=["GET", "POST"])
@login_required
def creer_lot():
    if current_user.role != "vendeur":
        flash("❌ Accès réservé aux vendeurs", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        espece = request.form["espece"]
        poids = float(request.form["poids"])
        origine = request.form["origine"]
        prix = float(request.form["prix_base"])
        duree = int(request.form.get("duree", 5))  # valeur par défaut = 5 min
        date_fin = datetime.utcnow() + timedelta(minutes=duree)
        nouveau_lot = Lot(
            espece=espece,
            poids=poids,
            origine=origine,
            prix_base=prix,
            prix_actuel=prix,
            vendeur_id=current_user.id,
            date_fin=date_fin
        )
        db.session.add(nouveau_lot)
        db.session.commit()
        flash("✅ Lot ajouté avec succès !")
        return redirect(url_for("encheres"))

    return render_template("creer_lot.html")

@app.route("/profil")
@login_required
def profil():
    return render_template("profil.html", user=current_user)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Déconnexion réussie.", "success")
    return redirect(url_for("login"))

@app.route("/users")
def show_users():
    users = User.query.all()
    return "<br>".join([f"{u.nom} - {u.email} - {u.role}" for u in users])

@app.route("/lots")
def show_lots():
    lots = Lot.query.all()
    if not lots:
        return "Aucun lot trouvé."
    return "<br>".join([f"{l.espece} - {l.poids}kg - {l.origine} - Prix base: {l.prix_base}" for l in lots])

@app.route("/bids")
def show_bids():
    bids = Bid.query.all()
    if not bids:
        return "Aucune enchère trouvée."
    return "<br>".join([f"Montant: {b.montant} - Lot ID: {b.lot_id} - Acheteur ID: {b.acheteur_id}" for b in bids])

from datetime import datetime

@app.route("/encherir/<int:lot_id>", methods=["POST"])
@login_required
def encherir(lot_id):
    lot = Lot.query.get_or_404(lot_id)
     # 🚫 Interdire qu'un vendeur enchérisse sur son propre lot
    if lot.vendeur_id == current_user.id:
        flash("⛔ Vous ne pouvez pas enchérir sur vos propres lots.", "danger")
        return redirect(url_for("detail_lot", lot_id=lot.id))

    # Vérifier si l'enchère est terminée
    if datetime.utcnow() > lot.date_fin:
        flash("⛔ Cette enchère est déjà terminée.", "danger")
        return redirect(url_for("detail_lot", lot_id=lot.id))

    montant = float(request.form["montant"])

    if montant > lot.prix_actuel:
        lot.prix_actuel = montant
        nouvelle_enchere = Bid(
            montant=montant,
            lot_id=lot.id,
            acheteur_id=current_user.id
        )
        db.session.add(nouvelle_enchere)
        db.session.commit()
        flash("✅ Enchère placée avec succès !", "success")
    else:
        flash("⚠️ Votre offre doit être supérieure au prix actuel.", "warning")

    # Redirection propre vers la page du lot
    return redirect(url_for("detail_lot", lot_id=lot.id))


@app.route("/lot/<int:lot_id>")
def detail_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)

    # Récupérer les enchères du lot (du plus récent au plus ancien)
    encheres = Bid.query.filter_by(lot_id=lot.id).order_by(Bid.date.desc()).all()

    # Statut (en cours ou terminé)
    statut = "Terminé" if lot.est_termine() else "En cours"

    # Gagnant : uniquement si l’enchère est terminée et qu’il y a eu au moins 1 enchère
    gagnant = None
    if lot.est_termine() and encheres:
        gagnant = encheres[0].acheteur.nom   # le dernier enchérisseur

    vendeur = User.query.get(lot.vendeur_id)

    return render_template(
        "detail_lot.html",
        lot=lot,
        encheres=encheres,
        vendeur=vendeur,
        statut=statut,
        gagnant=gagnant
    )

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

# Formulaire d'inscription
class RegisterForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    role = SelectField("Rôle", choices=[("vendeur", "Vendeur"), ("acheteur", "Acheteur")])
    submit = SubmitField("S'inscrire")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("❌ Email déjà utilisé", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(form.mot_de_passe.data)
        new_user = User(
            nom=form.nom.data,
            email=form.email.data,
            mot_de_passe=hashed_password,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("✅ Inscription réussie, connectez-vous.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)
# Formulaire de connexion
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.mot_de_passe, form.mot_de_passe.data):
            login_user(user)
            flash("✅ Connexion réussie !", "success")
            return redirect(url_for("profil"))
        else:
            flash("❌ Identifiants incorrects", "error")

    return render_template("login.html", form=form)

