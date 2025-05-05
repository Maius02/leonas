import streamlit as st
import json
import os
import random

# ---------- CONFIGURACION ----------
st.set_page_config(page_title="🌸 Angelito Secreto", layout="centered")

# ---------- FUNCIONES DE DATOS ----------
def cargar_json(ruta, defecto):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return defecto

def guardar_json(ruta, datos):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def obtener_destinatario(nombre, historial):
    for entrada in historial:
        if entrada['angelito'] == nombre:
            return entrada['destinatario']
    return None

def participantes_disponibles(historial, yo, todos):
    ya_fui_angelito_de = [a['destinatario'] for a in historial if a['angelito'] == yo]
    return [p for p in todos if p != yo and p not in ya_fui_angelito_de]

def asignar_angelito(nombre, participantes, historial):
    disponibles = participantes_disponibles(historial, nombre, participantes)
    if not disponibles:
        return None
    elegido = random.choice(disponibles)
    historial.append({"angelito": nombre, "destinatario": elegido})
    guardar_json("historial.json", historial)
    return elegido

# ---------- CARGA DE DATOS ----------
config = cargar_json("config.json", {})
participantes = config.get("participantes", {})
admin_password = config.get("admin_password", "")
ronda_habilitada = config.get("ronda_habilitada", True)
historial = cargar_json("historial.json", [])

# ---------- INTERFAZ ----------
st.markdown("""
    <style>
    .title { text-align: center; font-size: 2.8em; font-weight: bold; color: #d48ecb; margin-bottom: 0.5em; }
    .subtle { font-style: italic; color: #888; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌸 Angelito Secreto 🌸</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Ingresá tu nombre y clave para descubrir o girar la ruleta</div>', unsafe_allow_html=True)

nombre = st.selectbox("Tu nombre", [""] + list(participantes.keys()))
clave = st.text_input("Tu clave secreta", type="password")

usuario_valido = nombre and participantes.get(nombre) == clave

if nombre and not usuario_valido:
    st.error("⚠️ Clave incorrecta para ese nombre.")

if usuario_valido:
    if not ronda_habilitada:
        st.warning("⚠️ La ronda está deshabilitada por el admin. Volvé más tarde.")
    else:
        ya_asignado = obtener_destinatario(nombre, historial)
        if ya_asignado:
            st.success(f"🎁 ¡Ya tenés a tu angelito secreto!: {ya_asignado}")
        else:
            st.markdown("### 🎡 Girá la ruleta para descubrir a quién mimar")

            if st.button("🎠 Girar ruleta"):
                elegido = asignar_angelito(nombre, list(participantes.keys()), historial)
                if elegido:
                    st.success(f"💖 ¡Te tocó: {elegido}! Guardalo en secreto... 🤫")
                else:
                    st.error("🚫 No quedan personas disponibles para vos.")

            # Mostrar ruleta HTML
            disponibles = participantes_disponibles(historial, nombre, list(participantes.keys()))
            colores = ['#ffd6e8', '#ffe0b2', '#e0f7fa', '#c8e6c9', '#f8bbd0', '#d1c4e9', '#b3e5fc', '#f0f4c3']
            segmentos = "".join([
                f"{{label: \"{p}\", color: \"{colores[i % len(colores)]}\"}},"
                for i, p in enumerate(disponibles)
            ])

            st.components.v1.html(f"""
            <div style='text-align:center; margin-top: 30px;'>
              <canvas id='wheel' width='300' height='300'></canvas>
              <script>
                const segmentos = [{segmentos}];
                const canvas = document.getElementById("wheel");
                const ctx = canvas.getContext("2d");
                const total = segmentos.length;
                const radius = canvas.width / 2;
                let angleStart = 0;
                let currentAngle = 0;
                
                function drawWheel() {{
                  ctx.clearRect(0, 0, canvas.width, canvas.height);
                  for (let i = 0; i < total; i++) {{
                    const angle = (2 * Math.PI) / total;
                    const start = angleStart + i * angle;
                    const end = start + angle;
                    ctx.beginPath();
                    ctx.moveTo(radius, radius);
                    ctx.arc(radius, radius, radius, start, end);
                    ctx.fillStyle = segmentos[i].color;
                    ctx.fill();
                    ctx.save();
                    ctx.translate(radius, radius);
                    ctx.rotate(start + angle / 2);
                    ctx.textAlign = "right";
                    ctx.fillStyle = "#333";
                    ctx.font = "bold 14px sans-serif";
                    ctx.fillText(segmentos[i].label, radius - 10, 5);
                    ctx.restore();
                  }}
                }}
                drawWheel();
              </script>
            </div>
            """, height=360)

# ---------- PANEL ADMIN ----------
with st.expander("🔒 Panel administrador"):
    pw = st.text_input("Clave admin", type="password")
    if pw == admin_password:
        st.success("Acceso concedido.")
        if st.button("🔁 Reiniciar juego"):
            guardar_json("historial.json", [])
            config["ronda_habilitada"] = True
            guardar_json("config.json", config)
            st.info("Juego reiniciado.")
        activar = st.checkbox("✅ Habilitar ronda", value=config.get("ronda_habilitada", True))
        config["ronda_habilitada"] = activar
        guardar_json("config.json", config)
