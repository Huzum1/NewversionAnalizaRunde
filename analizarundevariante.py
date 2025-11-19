import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configurare pagină
st.set_page_config(
    page_title="Verificare Loterie",
    page_icon="🎰",
    layout="wide"
)

# Titlu principal
st.title("🎰 Verificare Variante Loterie")
st.divider()

# Inițializare session state
if 'runde_chenare' not in st.session_state:
    st.session_state.runde_chenare = [[] for _ in range(7)]
if 'variante' not in st.session_state:
    st.session_state.variante = []

# Funcție pentru comparare numere
@st.cache_data
def verifica_varianta(varianta, runda):
    """Verifică câte numere se potrivesc între variantă și rundă"""
    set_varianta = set(varianta)
    set_runda = set(runda)
    return len(set_varianta.intersection(set_runda))

@st.cache_data
def calculeaza_punctaj(potriviri):
    """Calculează punctaj bazat pe potriviri"""
    if potriviri == 2:
        return 5
    elif potriviri == 3:
        return 8
    elif potriviri == 4:
        return 10
    return 0

# SECȚIUNEA RUNDE - 7 CHENARE
st.header("📋 Runde")

# Primul rând - 4 chenare
cols_rand1 = st.columns(4)
for i in range(4):
    with cols_rand1[i]:
        st.subheader(f"Chenar {i+1}")
        
        # Upload file
        uploaded_file = st.file_uploader(f"Import .txt", type=['txt'], key=f"upload_{i}")
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            linii = content.strip().split('\n')
            runde_noi = []
            
            for linie in linii:
                try:
                    numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                    if numere:
                        runde_noi.append(numere)
                except:
                    pass
            
            if runde_noi:
                st.session_state.runde_chenare[i] = runde_noi
                st.success(f"✅ {len(runde_noi)} runde")
                st.rerun()
        
        text_runde = st.text_area(
            "Format: 1,6,7,9,44,77",
            height=100,
            placeholder="1,6,7,9,44,77",
            key=f"input_runde_{i}"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Adaugă", type="primary", use_container_width=True, key=f"add_runde_{i}"):
                if text_runde.strip():
                    linii = text_runde.strip().split('\n')
                    runde_noi = []
                    
                    for linie in linii:
                        try:
                            numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                            if numere:
                                runde_noi.append(numere)
                        except:
                            pass
                    
                    if runde_noi:
                        st.session_state.runde_chenare[i].extend(runde_noi)
                        st.success(f"✅ {len(runde_noi)} runde")
                        st.rerun()
        
        with col_btn2:
            if st.button("Șterge", use_container_width=True, key=f"del_runde_{i}"):
                st.session_state.runde_chenare[i] = []
                st.rerun()
        
        if st.session_state.runde_chenare[i]:
            st.caption(f"Total: {len(st.session_state.runde_chenare[i])} runde")
            
            container_runde = st.container(height=150)
            with container_runde:
                for j, runda in enumerate(st.session_state.runde_chenare[i], 1):
                    st.text(f"{j}. {','.join(map(str, runda))}")

# Al doilea rând - 3 chenare
cols_rand2 = st.columns(3)
for i in range(3):
    idx = i + 4
    with cols_rand2[i]:
        st.subheader(f"Chenar {idx+1}")
        
        # Upload file
        uploaded_file = st.file_uploader(f"Import .txt", type=['txt'], key=f"upload_{idx}")
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            linii = content.strip().split('\n')
            runde_noi = []
            
            for linie in linii:
                try:
                    numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                    if numere:
                        runde_noi.append(numere)
                except:
                    pass
            
            if runde_noi:
                st.session_state.runde_chenare[idx] = runde_noi
                st.success(f"✅ {len(runde_noi)} runde")
                st.rerun()
        
        text_runde = st.text_area(
            "Format: 1,6,7,9,44,77",
            height=100,
            placeholder="1,6,7,9,44,77",
            key=f"input_runde_{idx}"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Adaugă", type="primary", use_container_width=True, key=f"add_runde_{idx}"):
                if text_runde.strip():
                    linii = text_runde.strip().split('\n')
                    runde_noi = []
                    
                    for linie in linii:
                        try:
                            numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                            if numere:
                                runde_noi.append(numere)
                        except:
                            pass
                    
                    if runde_noi:
                        st.session_state.runde_chenare[idx].extend(runde_noi)
                        st.success(f"✅ {len(runde_noi)} runde")
                        st.rerun()
        
        with col_btn2:
            if st.button("Șterge", use_container_width=True, key=f"del_runde_{idx}"):
                st.session_state.runde_chenare[idx] = []
                st.rerun()
        
        if st.session_state.runde_chenare[idx]:
            st.caption(f"Total: {len(st.session_state.runde_chenare[idx])} runde")
            
            container_runde = st.container(height=150)
            with container_runde:
                for j, runda in enumerate(st.session_state.runde_chenare[idx], 1):
                    st.text(f"{j}. {','.join(map(str, runda))}")

st.divider()

# SECȚIUNEA VARIANTE
st.header("🎲 Variante")

text_variante = st.text_area(
    "Format: 1, 6 7 5 77",
    height=150,
    placeholder="1, 6 7 5 77\n2, 4 65 45 23",
    key="input_variante_bulk"
)

col_btn3, col_btn4 = st.columns(2)
with col_btn3:
    if st.button("Adaugă", type="primary", use_container_width=True, key="add_var"):
        if text_variante.strip():
            linii = text_variante.strip().split('\n')
            variante_noi = []
            
            for linie in linii:
                try:
                    parti = linie.split(',', 1)
                    if len(parti) == 2:
                        id_var = parti[0].strip()
                        numere_str = parti[1].strip()
                        numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                        if numere:
                            variante_noi.append({
                                'id': id_var,
                                'numere': numere
                            })
                except:
                    pass
            
            if variante_noi:
                st.session_state.variante.extend(variante_noi)
                st.success(f"✅ {len(variante_noi)} variante")
                st.rerun()

with col_btn4:
    if st.button("Șterge", use_container_width=True, key="del_var"):
        st.session_state.variante = []
        st.rerun()

if st.session_state.variante:
    st.caption(f"Total: {len(st.session_state.variante)} variante")
    
    container_variante = st.container(height=250)
    with container_variante:
        for var in st.session_state.variante:
            st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

st.divider()

# VERIFICARE EXISTENȚĂ DATE
are_runde = any(len(runde) > 0 for runde in st.session_state.runde_chenare)
are_variante = len(st.session_state.variante) > 0

if are_runde and are_variante:
    
    # SECȚIUNEA 1 - ANALIZĂ CLASICĂ
    st.header("🏆 Secțiunea 1 - Analiză Clasică")
    
    numar_minim = st.slider(
        "Numere minime potrivite:",
        min_value=2,
        max_value=10,
        value=4,
        key="slider_clasic"
    )
    
    st.divider()
    
    # Statistici avansate per chenar
    st.subheader("📊 Statistici Avansate per Chenar")
    
    cols_stats = st.columns(7)
    
    for i in range(7):
        with cols_stats[i]:
            if st.session_state.runde_chenare[i]:
                castiguri_chenar = 0
                punctaje_chenar = []
                count_4_4 = 0
                count_3_4 = 0
                count_2_4 = 0
                
                for runda in st.session_state.runde_chenare[i]:
                    for var_obj in st.session_state.variante:
                        varianta = var_obj['numere']
                        potriviri = verifica_varianta(varianta, runda)
                        
                        if potriviri >= numar_minim:
                            castiguri_chenar += 1
                        
                        punctaj = calculeaza_punctaj(potriviri)
                        if punctaj > 0:
                            punctaje_chenar.append(punctaj)
                            
                            if potriviri == 4:
                                count_4_4 += 1
                            elif potriviri == 3:
                                count_3_4 += 1
                            elif potriviri == 2:
                                count_2_4 += 1
                
                medie_punctaj = np.mean(punctaje_chenar) if punctaje_chenar else 0
                coverage = (castiguri_chenar / (len(st.session_state.runde_chenare[i]) * len(st.session_state.variante)) * 100) if castiguri_chenar > 0 else 0
                
                st.metric(f"Chenar {i+1}", f"{castiguri_chenar}")
                st.caption(f"Medie: {medie_punctaj:.1f}")
                st.caption(f"4/4: {count_4_4}")
                st.caption(f"3/4: {count_3_4}")
                st.caption(f"2/4: {count_2_4}")
                st.caption(f"Coverage: {coverage:.1f}%")
    
    st.divider()
    
    # Rezultate per chenar
    rezultate_container = st.container(height=200)
    with rezultate_container:
        for i in range(7):
            if st.session_state.runde_chenare[i]:
                castiguri_total = 0
                
                for runda in st.session_state.runde_chenare[i]:
                    for var_obj in st.session_state.variante:
                        varianta = var_obj['numere']
                        potriviri = verifica_varianta(varianta, runda)
                        
                        if potriviri >= numar_minim:
                            castiguri_total += 1
                
                st.text(f"Chenarul {i+1} - {castiguri_total} variante câștigătoare")
    
    st.divider()
    
    # SECȚIUNEA 2 - TOP 100 STABILITATE
    st.header("💎 Secțiunea 2 - TOP 100 Stabilitate")
    
    # Calculare punctaje pentru toate variantele
    @st.cache_data
    def calculeaza_top_100(_variante, _runde_chenare):
        rezultate = []
        
        for var_obj in _variante:
            var_id = var_obj['id']
            varianta = var_obj['numere']
            
            punctaje_per_chenar = []
            chenare_active = 0
            punctaj_total = 0
            
            for i in range(7):
                punctaj_chenar = 0
                are_potriviri = False
                
                for runda in _runde_chenare[i]:
                    potriviri = verifica_varianta(varianta, runda)
                    punctaj = calculeaza_punctaj(potriviri)
                    punctaj_chenar += punctaj
                    
                    if potriviri >= 2:
                        are_potriviri = True
                
                punctaje_per_chenar.append(punctaj_chenar)
                punctaj_total += punctaj_chenar
                
                if are_potriviri:
                    chenare_active += 1
            
            if chenare_active >= 5:
                sd = np.std(punctaje_per_chenar)
                
                rezultate.append({
                    'id': var_id,
                    'numere': varianta,
                    'punctaj_total': punctaj_total,
                    'chenare_active': chenare_active,
                    'sd': sd,
                    'punctaje_per_chenar': punctaje_per_chenar
                })
        
        # Sortare: prioritate chenare_active, apoi punctaj_total DESC, apoi sd ASC
        rezultate_sortate = sorted(rezultate, key=lambda x: (-x['chenare_active'], -x['punctaj_total'], x['sd']))
        
        return rezultate_sortate[:100]
    
    top_100 = calculeaza_top_100(st.session_state.variante, st.session_state.runde_chenare)
    
    if top_100:
        # FILTRARE DINAMICĂ
        st.subheader("🎛️ Filtrare Dinamică")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            min_chenare = st.slider("Minim chenare active:", 5, 7, 5, key="filter_chenare")
        
        with col_f2:
            min_punctaj = st.slider("Punctaj minim total:", 0, int(max([x['punctaj_total'] for x in top_100])), 0, key="filter_punctaj")
        
        with col_f3:
            max_sd = st.slider("SD maxim acceptat:", 0.0, 10.0, 10.0, 0.1, key="filter_sd")
        
        # Aplicare filtre
        top_100_filtrat = [
            x for x in top_100 
            if x['chenare_active'] >= min_chenare 
            and x['punctaj_total'] >= min_punctaj 
            and x['sd'] <= max_sd
        ]
        
        st.caption(f"Variante filtrate: {len(top_100_filtrat)}")
        
        st.divider()
        
        # HEATMAP
        st.subheader("🔥 Heatmap Distribuție Punctaj")
        
        if len(top_100_filtrat) > 0:
            # Pregătire date pentru heatmap
            heatmap_data = []
            labels_y = []
            
            for idx, item in enumerate(top_100_filtrat[:20], 1):  # Primele 20 pentru vizibilitate
                heatmap_data.append(item['punctaje_per_chenar'])
                labels_y.append(f"#{idx} ID:{item['id']}")
            
            heatmap_array = np.array(heatmap_data)
            
            fig = px.imshow(
                heatmap_array,
                labels=dict(x="Chenar", y="Variantă", color="Punctaj"),
                x=[f"C{i+1}" for i in range(7)],
                y=labels_y,
                color_continuous_scale="RdYlGn",
                aspect="auto"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # FORMAT 1 - TABEL DETALIAT
        st.subheader("📋 Format 1 - Tabel Detaliat")
        
        tabel_container = st.container(height=400)
        with tabel_container:
            for idx, item in enumerate(top_100_filtrat, 1):
                # Highlighting
                badge = ""
                if item['sd'] < 2.0:
                    badge += "⭐ "
                if item['chenare_active'] == 7:
                    badge += "🎯 "
                if item['punctaj_total'] == max([x['punctaj_total'] for x in top_100_filtrat]):
                    badge += "🏆 "
                
                col_t1, col_t2, col_t3, col_t4, col_t5, col_t6, col_t7 = st.columns([1, 2, 4, 2, 2, 2, 2])
                
                with col_t1:
                    st.text(f"#{idx}")
                with col_t2:
                    st.text(f"ID {item['id']}")
                with col_t3:
                    st.text(' '.join(map(str, item['numere'])))
                with col_t4:
                    st.text(f"{item['punctaj_total']}")
                with col_t5:
                    st.text(f"{item['chenare_active']}/7")
                with col_t6:
                    st.text(f"{item['sd']:.2f}")
                with col_t7:
                    if st.button("👁️", key=f"detalii_{idx}"):
                        with st.expander(f"Detalii ID {item['id']}", expanded=True):
                            for i, punctaj in enumerate(item['punctaje_per_chenar'], 1):
                                st.text(f"Chenar {i}: {punctaj} puncte")
                
                if badge:
                    st.caption(badge)
                
                st.divider()
        
        st.divider()
        
        # FORMAT 2 - COPY-PASTE
        st.subheader("📝 Format 2 - Copy-Paste")
        
        copy_text = ""
        for item in top_100_filtrat:
            copy_text += f"{item['id']}, {' '.join(map(str, item['numere']))}\n"
        
        st.text_area(
            "Copy-paste:",
            value=copy_text,
            height=300,
            key="copy_paste_area"
        )
    
    else:
        st.info("Nu există variante care îndeplinesc criteriile pentru TOP 100")

else:
    st.info("Adaugă runde și variante pentru verificare")