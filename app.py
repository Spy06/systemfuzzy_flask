import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

delta_elo = ctrl.Antecedent(np.arange(0, 401, 1), 'delta_elo')
waktu_tunggu = ctrl.Antecedent(np.arange(0, 121, 1), 'waktu_tunggu')
kualitas_match = ctrl.Consequent(np.arange(0, 101, 1), 'kualitas_match')

delta_elo['dekat'] = fuzz.trapmf(delta_elo.universe, [0, 0, 50, 150])
delta_elo['sedang'] = fuzz.trimf(delta_elo.universe, [50, 150, 250])
delta_elo['jauh'] = fuzz.trapmf(delta_elo.universe, [150, 250, 400, 400])

waktu_tunggu['sebentar'] = fuzz.trapmf(waktu_tunggu.universe, [0, 0, 30, 60])
waktu_tunggu['sedang'] = fuzz.trimf(waktu_tunggu.universe, [30, 60, 90])
waktu_tunggu['lama'] = fuzz.trapmf(waktu_tunggu.universe, [60, 90, 120, 120])

kualitas_match['buruk'] = fuzz.trimf(kualitas_match.universe, [0, 0, 50])
kualitas_match['cukup'] = fuzz.trimf(kualitas_match.universe, [25, 50, 75])
kualitas_match['bagus'] = fuzz.trimf(kualitas_match.universe, [50, 100, 100])

rule1 = ctrl.Rule(delta_elo['dekat'], kualitas_match['bagus'])
rule2 = ctrl.Rule(delta_elo['sedang'] & waktu_tunggu['sebentar'], kualitas_match['cukup'])
rule3 = ctrl.Rule(delta_elo['sedang'] & (waktu_tunggu['sedang'] | waktu_tunggu['lama']), kualitas_match['bagus'])
rule4 = ctrl.Rule(delta_elo['jauh'] & waktu_tunggu['sebentar'], kualitas_match['buruk'])
rule5 = ctrl.Rule(delta_elo['jauh'] & (waktu_tunggu['sedang'] | waktu_tunggu['lama']), kualitas_match['cukup'])

match_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
match_simulator = ctrl.ControlSystemSimulation(match_ctrl)

st.title("Sistem Evaluasi Matchmaking Fuzzy")
st.write("Masukkan data pemain untuk menghitung kualitas kecocokan.")

col1, col2 = st.columns(2)
with col1:
    elo_p1 = st.number_input("ELO Player 1", value=1200)
with col2:
    elo_p2 = st.number_input("ELO Player 2", value=1250)

tunggu = st.slider("Waktu Tunggu (detik)", 0, 120, 10)

if st.button("Hitung Kecocokan"):
    selisih = min(abs(elo_p1 - elo_p2), 400)
    
    match_simulator.input['delta_elo'] = selisih
    match_simulator.input['waktu_tunggu'] = tunggu
    match_simulator.compute()
    
    skor = match_simulator.output['kualitas_match']
    
    if skor >= 60:
        status = "Match Diterima (Bagus)"
        st.success(f"Skor: {round(skor, 2)} - {status}")
    elif skor >= 40:
        status = "Bisa Diterima (Cukup)"
        st.warning(f"Skor: {round(skor, 2)} - {status}")
    else:
        status = "Match Ditolak (Buruk)"
        st.error(f"Skor: {round(skor, 2)} - {status}")

    st.info(f"Selisih ELO: {selisih}")