# requisitos: pip install streamlit easyocr pandas opencv-python pillow
import streamlit as st
import easyocr
import re
import pandas as pd
from datetime import datetime
from PIL import Image
import os

st.title("Registro de Placas - Oficina")

# Lista de mecânicos por quadrante
mecanicos_por_quadrante = {
    "Quadrante 1": ["Aleksander Lucard Sousa Vidal", "Bruno da Silva Carvalho", "Denílson Cardoso Silva","Ederson Sousa da Costa","Francisco Chagas de Sousa", "Gabriel Lucas de Sousa Verçosa", "JACKSON ADRIANO DE PAULO AMARANTE", "Matheus Pereira Coutinho", "Max Oliveira da Silva", "Raysson Pereira Albuquerque","Wilkemberg Soares Santos"],
    "Quadrante 2": ["Adriel Menezes da Fonseca", "Antônio Tailan Alves Correia", "ARTUR BRUNO BERNARDO DE LIMA","Francisco Rone Silva Costa", "João kayllan da Silva Castro", "JOÃO VICTOR DE ABREU DA SILVA", "JULIO DE SOUSA COELHO", "Marcos Sousa dos Santos"],
    "Quadrante 3": ["Cássio Cardoso de Paiva", "Edio Bruno Rodrigues de Freitas", "kristian de abreu silva","Paulo Roberto de Sousa da Silva","Paulo Vitor de Castro Matos", "Pedro Henrique Nascimento de Oliveira", "PEDRO LEONARDO DOS SANTOS FERREIRA", "RAFAEL ARAUJO DA SILVA", "Romildo de Melo Benevides Filho"],
    "Quadrante 4": ["Ana", "Roberto", "Cláudia"]
}

quadrante = st.selectbox("Selecione o Quadrante", list(mecanicos_por_quadrante.keys()))
mecanico = st.selectbox("Nome do Mecânico", mecanicos_por_quadrante[quadrante])
rampa_num = st.selectbox("Rampa", [f"Rampa {i}" for i in range(1, 11)])
rampa = f"{quadrante} - {rampa_num}"
tipo_servico = st.selectbox("Tipo de Serviço", ["Motor Completo", "Motor Parcial", "Outros Serviços"])
foto = st.file_uploader("Envie a foto da placa", type=["jpg", "png", "jpeg"])

reader = easyocr.Reader(['pt'])

def extrair_placa(textos):
    ignorar = {"BRASIL", "BR", "MERCOSUL"}
    partes = [txt[1].upper().replace(" ", "") for txt in textos if re.match(r"^[A-Z0-9]+$", txt[1].upper()) and txt[1].upper() not in ignorar]
    st.write("Textos reconhecidos pelo OCR:", partes)

    for parte in partes:
        # Placa Mercosul de moto (ABC1A23)
        if re.match(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$", parte):
            return f"{parte[:3]}-{parte[3:]}"
        # Placa antiga (ABC1234)
        elif re.match(r"^[A-Z]{3}[0-9]{4}$", parte):
            return f"{parte[:3]}-{parte[3:]}"
    
    for i in range(len(partes) - 1):
        parte1 = partes[i]
        parte2 = partes[i + 1]
        if re.match(r"^[A-Z]{3}$", parte1):
            if re.match(r"^[0-9][A-Z][0-9]{2}$", parte2):  # Mercosul
                return f"{parte1}-{parte2}"
            elif re.match(r"^[0-9]{4}$", parte2):  # Antiga
                return f"{parte1}-{parte2}"
    
    return None

if st.button("Enviar"):
    if not foto:
        st.warning("Por favor, envie a imagem da placa.")
    else:
        img = Image.open(foto)
        img_path = os.path.join("temp.jpg")
        img.convert("RGB").save(img_path, format="JPEG")

        resultados = reader.readtext(img_path)
        placa = extrair_placa(resultados)

        if placa:
            st.success(f"Placa reconhecida: **{placa}**")

            dados = {
                "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "quadrante": quadrante,
                "mecanico": mecanico,
                "rampa": rampa,
                "tipo_servico": tipo_servico,
                "placa": placa
            }

            df = pd.DataFrame([dados])

            if os.path.exists("registros.csv"):
                df_antigo = pd.read_csv("registros.csv")
                df_total = pd.concat([df_antigo, df], ignore_index=True)
            else:
                df_total = df

            df_total.to_csv("registros.csv", index=False)
            st.success("Registro salvo com sucesso!")
        else:
            st.error("Não foi possível identificar uma placa válida na imagem.")
