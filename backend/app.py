import re
from typing import Optional, Dict
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================
#   Validaciones básicas
# =========================
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email or ""))

def is_valid_password(pwd: str) -> bool:
    return isinstance(pwd, str) and len(pwd) >= 4


# =========================
#   Modelo y "BD" en memoria
# =========================
class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def to_public_json(self) -> Dict[str, str]:
        # No exponemos la contraseña
        return {"email": self.email}

# Clave = email
users_db: Dict[str, User] = {}


# =========================
#   Helpers CRUD
# =========================
def create_user(email: str, password: str) -> bool:
    """Crea un usuario si no existe. True si lo crea, False si ya existe."""
    if email in users_db:
        return False
    users_db[email] = User(email, password)
    return True

def get_user(email: str) -> Optional[User]:
    return users_db.get(email)

def update_user(email: str, new_password: str) -> bool:
    u = users_db.get(email)
    if not u:
        return False
    u.password = new_password
    return True

def delete_user(email: str) -> bool:
    return users_db.pop(email, None) is not None

def check_credentials(email: str, password: str) -> bool:
    u = users_db.get(email)
    return bool(u and u.password == password)


# =========================
#   Endpoints requeridos
# =========================

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "Datos incompletos"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    if not is_valid_email(email):
        return jsonify({"msg": "Email inválido"}), 400
    if not is_valid_password(password):
        return jsonify({"msg": "La contraseña debe tener al menos 4 caracteres"}), 400
    if not create_user(email, password):
        return jsonify({"msg": "El email ya está registrado"}), 409

    return jsonify({"msg": "Usuario registrado exitosamente"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "Datos incompletos"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    # Usuario fijo de prueba (según el enunciado)
    if email == "user@test.com" and password == "Test123":
        return jsonify({"msg": "Login exitoso (usuario de prueba)"}), 200

    # Validación contra la "BD" en memoria
    if check_credentials(email, password):
        return jsonify({"msg": "Login exitoso"}), 200

    return jsonify({"msg": "Credenciales inválidas"}), 401


# ========== CRUD extra para demostrar uso de "modelo + helpers" ==========

# READ: listar usuarios (solo email, sin contraseñas)
@app.route("/users", methods=["GET"])
def list_users():
    payload = [u.to_public_json() for u in users_db.values()]
    return jsonify({"count": len(payload), "items": payload}), 200

# READ: obtener un usuario
@app.route("/users/<email>", methods=["GET"])
def get_one(email: str):
    u = get_user(email.strip().lower())
    if not u:
        return jsonify({"msg": "No existe"}), 404
    return jsonify(u.to_public_json()), 200

# UPDATE: cambiar contraseña
@app.route("/users/<email>", methods=["PUT"])
def update_one(email: str):
    data = request.get_json() or {}
    new_pwd = data.get("password", "")
    if not is_valid_password(new_pwd):
        return jsonify({"msg": "La contraseña debe tener al menos 4 caracteres"}), 400
    ok = update_user(email.strip().lower(), new_pwd)
    if not ok:
        return jsonify({"msg": "No existe"}), 404
    return jsonify({"msg": "Actualizado"}), 200

# DELETE: eliminar usuario
@app.route("/users/<email>", methods=["DELETE"])
def delete_one(email: str):
    ok = delete_user(email.strip().lower())
    if not ok:
        return jsonify({"msg": "No existe"}), 404
    return jsonify({"msg": "Eliminado"}), 200


# (Opcional) Healthcheck simple
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    print("Iniciando servidor Flask en http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
