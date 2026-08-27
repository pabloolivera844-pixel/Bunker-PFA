from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
import os, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dif_secret_2026'
DB_FILE = "dfi_agentes.json"
LOG_FILE = "dfi_secops.log"
UPL = "uploads"
if not os.path.exists(UPL): os.makedirs(UPL)

def db_load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            for k in ["civiles", "vehiculos", "notas_campo", "archivos_desclasificados"]:
                if k not in d: d[k] = []
            return d
        return {
        "oficiales_pfa": [
            {
                "id": "PFA-001", 
                "nombre": "Alexis", 
                "rango": "Comisario General", 
                "llave": os.environ.get("ALEXIS_LLAVE", "key_alexis_cg2026")
            },
            {
                "id": "PFA-002", 
                "nombre": "Joel", 
                "rango": "Comisario", 
                "llave": os.environ.get("JOEL_LLAVE", "key_joel_com2026")
            }
        ],
        "dfi_director": [
            {
                "id": "DIF-001", 
                "nombre": "Pablo", 
                "rango": "Director DFI", 
                "llave": os.environ.get("DIRECTOR_LLAVE", "llave_maestra_dfi")
            }
        ],
        "civiles": [{"id_civil": "CIV-1001", "nombre": "Base Central", "nacionalidad": "Argentina", "estado": "Verificado"}],
        "vehiculos": [{"patente": "AB123CD", "modelo": "Patrulla Federal", "estado": "Activo"}],
        "notas_campo": [{"autor": "Director Pablo", "texto": "Sistema operativo inicializado y blindado.", "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}],
        "archivos_desclasificados": []
    }


def db_save(d):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(d, f, indent=4, ensure_ascii=False)

def log(m):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {m}\n")

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><title>D.I.F. Táctica</title>
<style>
body { background: #0d1117; color: #c9d1d9; font-family: Arial; padding: 15px; margin: 0; }
.box { max-width: 900px; margin: auto; background: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
h2, h3 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 5px; }
.nav { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 15px; }
.nbtn { background: #21262d; color: #58a6ff; padding: 6px 10px; border: 1px solid #30363d; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: bold; }
.nbtn.active, .nbtn:hover { background: #30363d; color: #fff; }
.btn { background: #238636; color: #fff; padding: 8px 12px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
.btn-danger { background: #da3633; }
input, select, textarea { background: #0d1117; border: 1px solid #30363d; color: #fff; padding: 8px; border-radius: 4px; width: 100%; margin: 5px 0; box-sizing: border-box; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 15px; }
th, td { border: 1px solid #30363d; padding: 8px; font-size: 13px; text-align: left; }
th { background: #21262d; color: #58a6ff; }
.card { background: #1f242c; padding: 12px; border-radius: 6px; border: 1px solid #30363d; margin-top: 10px; }
</style>
</head>
<body>
<div class="box">
    <h2>🛡️ D.I.F. Terminal Central</h2>
    <div style="font-size:13px; color:#8b949e; margin-bottom:10px;">Agente: <b>{{user.nombre}}</b> | Rango: <b>{{user.rango}}</b></div>
    
    <div class="nav">
        <a href="/dashboard?tab=expedientes" class="nbtn {% if tab=='expedientes' %}active{% endif %}">📁 Expedientes</a>
        <a href="/dashboard?tab=personal" class="nbtn {% if tab=='personal' %}active{% endif %}">👥 Personal</a>
        <a href="/dashboard?tab=civiles" class="nbtn {% if tab=='civiles' %}active{% endif %}">🪪 Civiles</a>
        <a href="/dashboard?tab=vehiculos" class="nbtn {% if tab=='vehiculos' %}active{% endif %}">🚗 Vehículos</a>
        <a href="/dashboard?tab=notas" class="nbtn {% if tab=='notas' %}active{% endif %}">📝 Notas</a>
    </div>

        {% if tab == 'expedientes' %}
        <h3>Repositorio de Expedientes</h3>
        <table>
            <tr><th>ID</th><th>Título</th><th>Acción</th></tr>
            {% for d in res %}
            <tr><td>{{d.doc_id}}</td><td>{{d.titulo}}</td><td><a href="/descargar/{{d.titulo}}" class="btn" style="padding:4px 8px; font-size:11px;">Descargar</a></td></tr>
            {% endfor %}
        </table>

        {% if user.acceso == 'Master_Total' %}
        <div class="card">
            <h3>Subir Expediente PDF</h3>
            <form action="/subir" method="POST" enctype="multipart/form-data">
                <input type="file" name="archivo" accept=".pdf" required><br>
                <button type="submit" class="btn" style="margin-top:5px;">Subir</button>
            </form>
        </div>
        {% endif %}   
{% elif tab == 'personal' %}
    <h3>Personal PFA / DFI</h3>
    <input type="text" id="buscadorPersonal" onkeyup="filtrarTabla('buscadorPersonal', 'tablaPersonal')" placeholder="Filtrar personal..." style="width: 100%; padding: 8px; margin-bottom: 10px; background: #111; color: #fff; border: 1px solid #333;">
    <table id="tablaPersonal">
        <tr>
            <th>Nombre</th>
            <th>Rango</th>
            <th>Acceso</th>
            <th>Acción</th>
        </tr>
        {% for p in db.get('oficiales', []) %}
        <tr>
    <td>{{p.nombre}}</td>
    <td>{{p.rango}}</td>
    <td>{{p.acceso}}</td>
<td><a href="/eliminar/oficial/{{p.nombre}}" style="color: #ff4444; text-decoration: none; font-weight: bold;">[ X ]</a></td>

</tr>

        {% endfor %}
    </table>
    
    {% if user.acceso == 'Master_Total' %}
    <div class="card" style="margin-top: 15px;">
        <h3>Incorporar Nuevo Oficial</h3>
        <form action="/agregar_oficial" method="POST">
            <input type="text" name="nombre" placeholder="Nombre del oficial" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <input type="text" name="rango" placeholder="Rango" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <input type="password" name="llave" placeholder="Llave de acceso" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <select name="acceso" style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
                <option value="Oficial">Oficial</option>
                <option value="Master_Total">Master_Total</option>
            </select>
            <button type="submit" class="btn" style="width: 100%;">Incorporar a la Base</button>
        </form>
    </div>
    {% endif %}


{% elif tab == 'civiles' %}
    <h3>Registro de Civiles</h3>
    <input type="text" id="buscadorCiviles" onkeyup="filtrarTabla('buscadorCiviles', 'tablaCiviles')" placeholder="Filtrar registros..." style="width: 100%; padding: 8px; margin-bottom: 10px; background: #111; color: #fff; border: 1px solid #333;">
    <table id="tablaCiviles">
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Nacionalidad</th>
            <th>Estado</th>
            <th>Acción</th>
        </tr>
{% for c in res %}
<tr>
    <td>{{c.id_civil}}</td>
    <td>{{c.nombre}}</td>
    <td>{{c.nacionalidad}}</td>
    <td>{{c.estado}}</td>
    <td><a href="/eliminar/civil/{{c.id_civil}}" style="color: #ff4444; text-decoration: none; font-weight: bold;">[ X ]</a></td>
</tr>
{% endfor %}


    </table>
    
    <div class="card" style="margin-top: 15px;">
        <h3>Registrar Nuevo Civil</h3>
        <form action="/agregar_civil" method="POST">
            <input type="text" name="nombre" placeholder="Nombre completo" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <input type="text" name="nacionalidad" placeholder="Nacionalidad" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <select name="estado" style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
                <option value="Verificado">Verificado</option>
                <option value="Investigación">En Investigación</option>
                <option value="Busqueda">Pedido de Captura</option>
            </select>
            <button type="submit" class="btn" style="width: 100%;">Registrar en Base de Datos</button>
        </form>
    </div>

{% elif tab == 'vehiculos' %}
    <h3>Parque Automotor</h3>
    <input type="text" id="buscadorVehiculos" onkeyup="filtrarTabla('buscadorVehiculos', 'tablaVehiculos')" placeholder="Filtrar vehículos..." style="width: 100%; padding: 8px; margin-bottom: 10px; background: #111; color: #fff; border: 1px solid #333;">
    <table id="tablaVehiculos">
        <tr>
            <th>Patente</th>
            <th>Modelo</th>
            <th>Estado</th>
            <th>Acción</th>
        </tr>
        {% for v in res %}
        <tr>
    <td>{{v.patente}}</td>
    <td>{{v.modelo}}</td>
    <td>{{v.estado}}</td>
    <td><a href="/eliminar/vehiculo/{{v.patente}}" style="color: #ff4444; text-decoration: none; font-weight: bold;">[ X ]</a></td>
</tr>

        {% endfor %}
    </table>
    
    <div class="card" style="margin-top: 15px;">
        <h3>Registrar Vehículo</h3>
        <form action="/agregar_vehiculo" method="POST">
            <input type="text" name="patente" placeholder="Patente / Dominio" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <input type="text" name="modelo" placeholder="Modelo del vehículo" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
            <select name="estado" style="width: 100%; padding: 8px; margin-bottom: 8px; background: #111; color: #fff; border: 1px solid #333;">
                <option value="Activo">Activo</option>
                <option value="Secuestrado">Secuestrado</option>
                <option value="Busqueda">Con Pedido</option>
            </select>
            <button type="submit" class="btn" style="width: 100%;">Registrar Vehículo</button>
        </form>
    </div>

{% elif tab == 'notas' %}
    <h3>Bitácora y Notas de Campo</h3>
    
    <div class="card" style="margin-bottom: 15px;">
        <h3>Registrar Nueva Nota</h3>
        <form action="/agregar_nota" method="POST">
            <textarea name="texto" placeholder="Escriba el reporte o nota de campo..." rows="3" required style="width: 100%; padding: 8px; margin-bottom: 8px; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; box-sizing: border-box;"></textarea>
            <button type="submit" class="btn" style="width: 100%;">Guardar Nota</button>
        </form>
    </div>

    <h3>Historial de Notas</h3>
    <table>
        <tr>
            <th>Fecha / Hora</th>
            <th>Autor</th>
            <th>Contenido</th>
        </tr>
        {% for n in db.get('notas_campo', []) %}
        <tr>
            <td>{{n.timestamp}}</td>
            <td>{{n.autor}}</td>
            <td>{{n.texto}}</td>
        </tr>
        {% endfor %}
    </table>


    {% endif %}
    <br><a href="/logout" class="btn btn-danger">Cerrar Sesión</a>
</div>
</body>
</html>
<script>
function filtrarTabla(inputId, tablaId) {
    let input = document.getElementById(inputId).value.toLowerCase();
    let filas = document.querySelectorAll("#" + tablaId + " tbody tr");
    filas.forEach(fila => {
        let texto = fila.textContent.toLowerCase();
        fila.style.display = texto.includes(input) ? "" : "none";
    });
}
</script>
"""

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Login D.I.F.</title>
<style>
body { background: #0d1117; color: #c9d1d9; font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
.c { width: 100%%; max-width: 350px; padding: 20px; background: #161b22; border-radius: 8px; border: 1px solid #30363d; }
input { background: #0d1117; border: 1px solid #30363d; color: #fff; padding: 8px; width: 100%%; margin: 5px 0 15px 0; box-sizing: border-box; }
.btn { background: #238636; color: #fff; padding: 10px; border: none; border-radius: 4px; width: 100%%; font-weight: bold; cursor: pointer; }
.err { background: #382a04; color: #e3b341; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-size: 12px; text-align: center; }
</style></head>
<body>
<div class="c">
    <h2 style="color:#58a6ff; margin-top:0; text-align:center;">🔒 D.I.F. Login</h2>
    {% if error %}<div class="err">{{error}}</div>{% endif %}
    <form method="POST">
        <label>Usuario:</label><input type="text" name="usr" required>
        <label>Llave:</label><input type="password" name="llv" required>
        <button type="submit" class="btn">Entrar</button>
    </form>
</div></body></html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    err = None
    db = db_load()
    if request.method == "POST":
        u, l = request.form.get("usr"), request.form.get("llv")
        for p in db["dfi_director"] + db["oficiales_pfa"] + db.get("oficiales", []):

            if p["nombre"].lower() == u.lower():
                if p["llave"] == l:
                    session["usr"] = p["nombre"]
                    log(f"Login OK: {p['nombre']}")
                    return redirect(url_for("dashboard"))
                else:
                    err = "Credenciales incorrectas"
        if not err: err = "Usuario no encontrado"
    return render_template_string(HTML_LOGIN, error=err)

@app.route("/dashboard")
def dashboard():
    if "usr" not in session: return redirect("/")
    db = db_load()
    user = next((p for p in db["dfi_director"] + db["oficiales_pfa"] if p["nombre"] == session["usr"]), None)
    tab = request.args.get("tab", "expedientes")
    
    res = db["archivos_desclasificados"] if tab == "expedientes" else db.get(tab, [])
    return render_template_string(HTML, user=user, db=db, tab=tab, res=res)

@app.route("/subir", methods=["POST"])
def subir():
    if "usr" not in session: return redirect("/")
    db = db_load()
    f = request.files.get("archivo")
    if f and f.filename.endswith(".pdf"):
        f.save(os.path.join(UPL, f.filename))
        db["archivos_desclasificados"].append({"doc_id": f"EXP-{len(db['archivos_desclasificados'])+1:02d}", "titulo": f.filename})
        db_save(db)
    return redirect(url_for("dashboard", tab="expedientes"))

@app.route("/eliminar/<tipo>/<id_item>")
def eliminar_item(tipo, id_item):
    if "usr" not in session: return redirect(url_for("login"))
    db = db_load()
    
    # Dependiendo de la sección, filtramos el elemento para borrarlo
    if tipo == "civil" and "civiles" in db:
        db["civiles"] = [c for c in db["civiles"] if str(c.get("id")) != str(id_item)]
    elif tipo == "vehiculo" and "vehiculos" in db:
        db["vehiculos"] = [v for v in db["vehiculos"] if str(v.get("patente")) != str(id_item)]
    elif tipo == "oficial" and "oficiales" in db:
        db["oficiales"] = [o for o in db["oficiales"] if str(o.get("nombre")) != str(id_item)]
        
    db_save(db)
    return redirect(url_for("dashboard", tab=tipo))


@app.route("/agregar_civil", methods=["POST"])
def agregar_civil():
    if "usr" not in session: return redirect(url_for("/"))
    db = db_load()
    db["civiles"].append({"id_civil": f"CIV-{len(db['civiles'])+1000}", "nombre": request.form.get("nombre"), "nacionalidad": request.form.get("nacionalidad"), "estado": request.form.get("estado")})
    db_save(db)
    return redirect(url_for("dashboard", tab="civiles"))

@app.route("/agregar_oficial", methods=["POST"])
def agregar_oficial():
    if "usr" not in session: return redirect(url_for("login"))
    db = db_load()
    
    # Asegurarnos de que la lista 'oficiales' exista en el diccionario
    if "oficiales" not in db:
        db["oficiales"] = []
        
    db["oficiales"].append({
        "nombre": request.form.get("nombre"),
        "rango": request.form.get("rango"),
        "llave": request.form.get("llave"),
        "acceso": request.form.get("acceso")
    })
    db_save(db)
    return redirect(url_for("dashboard", tab="personal"))


@app.route("/agregar_vehiculo", methods=["POST"])
def agregar_vehiculo():
    if "usr" not in session: return redirect(url_for("/"))
    db = db_load()
    db["vehiculos"].append({"patente": request.form.get("patente").upper(), "modelo": request.form.get("modelo"), "estado": request.form.get("estado")})
    db_save(db)
    return redirect(url_for("dashboard", tab="vehiculos"))

@app.route("/agregar_nota", methods=["POST"])
def agregar_nota():
    if "usr" not in session: return redirect(url_for("/"))
    db = db_load()
    db["notas_campo"].append({"autor": session["usr"], "texto": request.form.get("texto"), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    db_save(db)
    return redirect(url_for("dashboard", tab="notas"))

@app.route("/descargar/<f>")
def descargar(f):
    if "usr" not in session: return redirect(url_for("/"))
    return send_from_directory(UPL, f)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


