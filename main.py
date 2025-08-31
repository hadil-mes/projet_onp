from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import qrcode, io, base64, pytz
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

# Import des modèles (depuis app/models.py)
from app.models import db, User, Lot, Bid

# ===================== CONFIGURATION APP =====================
app = Flask(__name__,
            template_folder="app/templates",   # chemin des templates
            static_folder="app/static")        # chemin des fichiers statiques
app.secret_key = "super_secret_key"

# Config base SQLite (locale)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///onp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ===================== FORMS =====================
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")


class RegisterForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    role = SelectField("Rôle", choices=[("acheteur", "Acheteur"), ("vendeur", "Vendeur")], validators=[DataRequired()])
    submit = SubmitField("S'inscrire")


# ===================== QR CODE =====================
def generate_qr_code(lot_id):
    lot_url = url_for("detail_lot", lot_id=lot_id, _external=True)
    img = qrcode.make(lot_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ===================== ROUTES =====================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encheres")
def encheres():
    lots = Lot.query.all()
    for lot in lots:
        lot.qr_code = generate_qr_code(lot.id)
    return render_template("encheres.html", lots=lots)


@app.route("/creer-lot", methods=["GET", "POST"])
@login_required
def creer_lot():
    if current_user.role != "vendeur":
        flash("⛔ Seuls les vendeurs peuvent créer un lot.", "danger")
        return redirect(url_for("encheres"))

    if request.method == "POST":
        espece = request.form["espece"]
        poids = float(request.form["poids"])
        origine = request.form["origine"]
        prix_base = float(request.form["prix_base"])
        prix_actuel = prix_base

        date_fin_str = request.form["date_fin"]  # ex: "2025-08-31T20:30"
        date_fin_local = datetime.strptime(date_fin_str, "%Y-%m-%dT%H:%M")

        # Ajout fuseau horaire Casablanca
        local_tz = pytz.timezone("Africa/Casablanca")
        date_fin_localized = local_tz.localize(date_fin_local)

        # Conversion en UTC
        date_fin_utc = date_fin_localized.astimezone(pytz.UTC)

        lot = Lot(
            espece=espece,
            poids=poids,
            origine=origine,
            prix_base=prix_base,
            prix_actuel=prix_actuel,
            vendeur_id=current_user.id,
            date_fin=date_fin_utc
        )
        db.session.add(lot)
        db.session.commit()
        flash("✅ Lot créé avec succès !", "success")
        return redirect(url_for("encheres"))

    return render_template("creer_lot.html")


@app.route("/encherir/<int:lot_id>", methods=["POST"])
@login_required
def encherir(lot_id):
    lot = Lot.query.get_or_404(lot_id)

    if lot.vendeur_id == current_user.id:
        flash("⛔ Vous ne pouvez pas enchérir sur vos propres lots.", "danger")
        return redirect(url_for("detail_lot", lot_id=lot.id))

    now = datetime.now(pytz.UTC)
    date_fin = lot.date_fin
    if date_fin.tzinfo is None:
        date_fin = pytz.UTC.localize(date_fin)

    if now > date_fin:
        flash("⛔ Cette enchère est déjà terminée.", "danger")
        return redirect(url_for("detail_lot", lot_id=lot.id))

    montant = float(request.form["montant"])
    if montant > lot.prix_actuel:
        lot.prix_actuel = montant
        enchere = Bid(montant=montant, lot_id=lot.id, acheteur_id=current_user.id)
        db.session.add(enchere)
        db.session.commit()
        flash("✅ Enchère placée avec succès !", "success")
    else:
        flash("⚠️ Votre offre doit être supérieure au prix actuel.", "warning")

    return redirect(url_for("detail_lot", lot_id=lot.id))


@app.route("/lot/<int:lot_id>")
def detail_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)
    encheres = Bid.query.filter_by(lot_id=lot.id).order_by(Bid.date.desc()).all()
    statut = "Terminé" if lot.est_termine() else "En cours"

    gagnant = None
    if lot.est_termine() and encheres:
        gagnant = User.query.get(encheres[0].acheteur_id)

    vendeur = User.query.get(lot.vendeur_id)

    # enrichir les enchères
    encheres_data = []
    for e in encheres:
        acheteur = User.query.get(e.acheteur_id)
        encheres_data.append({
            "montant": e.montant,
            "date": e.date,
            "acheteur": acheteur.nom if acheteur else "Anonyme",
            "acheteur_id": e.acheteur_id
        })

    return render_template("detail_lot.html",
                           lot=lot,
                           encheres=encheres_data,
                           vendeur=vendeur,
                           statut=statut,
                           gagnant=gagnant)


@app.route("/profil")
@login_required
def profil():
    return render_template("profil.html", user=current_user)


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
            flash("❌ Identifiants incorrects", "danger")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("⚠️ Cet email est déjà utilisé.", "warning")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(form.mot_de_passe.data)
        user = User(
            nom=form.nom.data,
            email=form.email.data,
            mot_de_passe=hashed_pw,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()

        flash("✅ Compte créé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Déconnexion réussie.", "success")
    return redirect(url_for("login"))


# ===================== INITIALISATION DB =====================
with app.app_context():
    db.create_all()
