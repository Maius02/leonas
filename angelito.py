import streamlit as st
import json
import random
import os
from PIL import Image

st.set_page_config(page_title="Angelito Secreto", layout="centered")

# ---------- FUNCIONES ----------
def cargar_json(ruta, valor_defecto):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return valor_defecto

def guardar_json(ruta, contenido):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(contenido, f, indent=4, ensure_ascii=False)

def participantes_disponibles(historial, yo, todos):
    ya_fui_angelito_de = [asignacion['destinatario'] for asignacion in historial if asignacion['angelito'] == yo]
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
participantes = config.get("participantes", [])
admin_password = config.get("admin_password", "")
ronda_habilitada = config.get("ronda_habilitada", True)
historial = cargar_json("historial.json", [])

# ---------- ESTILOS PERSONALIZADOS ----------
st.markdown("""
    <style>
    .title { text-align: center; font-size: 2.5em; font-weight: bold; color: #da70d6; margin-bottom: 0.5em; }
    .ruleta { display: flex; justify-content: center; align-items: center; margin: 1em 0; }
    .petalo { background: #fcdff2; padding: 10px 20px; margin: 8px; border-radius: 999px; display: inline-block; font-weight: bold; }
    .mensaje { font-style: italic; text-align: center; color: #888; margin-bottom: 1em; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌸 Angelito Secreto 🌸</div>', unsafe_allow_html=True)
st.markdown('<div class="mensaje">Cada 15 días se revelará una nueva persona para mimar con gestos secretos... ¡Sé un angelito ejemplar!</div>', unsafe_allow_html=True)

# ---------- SELECCIÓN DE USUARIO ----------
nombre = st.selectbox("Seleccioná tu nombre", [""] + participantes)

if nombre:
    if not ronda_habilitada:
        st.warning("⚠️ La ronda está deshabilitada por el admin. Volvé más tarde.")
    else:
        ya_participo = any(a['angelito'] == nombre for a in historial)
        if ya_participo:
            destinatario = next(a['destinatario'] for a in historial if a['angelito'] == nombre)
            st.success(f"🎉 Ya te tocó: **{destinatario}**. ¡Prepará tus sorpresas angelicales!")
        else:
            st.markdown("### 🌺 Ruleta de Angelitos")
            if st.button("🎡 Girar ruleta"):
                elegido = asignar_angelito(nombre, participantes, historial)
                if elegido:
                    st.balloons()
                    st.success(f"🎉 ¡Tu angelito secreto es **{elegido}**! Guardalo en secreto 😉")
                else:
                    st.error("🚫 Ya fuiste angelito de todas. Esperá la próxima ronda.")

            # RUEDA ESTÉTICA (simulada con pétalos + imagen central)
            st.markdown('<div class="ruleta">', unsafe_allow_html=True)
            for p in participantes:
                if p != nombre:
                    st.markdown(f'<span class="petalo">{p}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if os.path.exists("assets/santuario.jpg"):
                st.image("assets/santuario.jpg", width=180, caption="Santuario en el centro 🌸")

# ---------- PANEL ADMIN ----------
with st.expander("🔒 Acceso administrador"):
    pw = st.text_input("Clave secreta", type="password")
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
