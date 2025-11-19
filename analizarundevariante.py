import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from numba import jit
from collections import Counter

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
if 'variante_filtrate_finale' not in st.session_state:
    st.session_state.variante_filtrate_finale = []

# Funcții Numba pentru viteză maximă
@jit(nopython=True)
def verifica_varianta_numba(varianta, runda):
    """Verifică câte numere se potrivesc între variantă și rundă"""
    count = 0
    for v in varianta:
        for r in runda:
            if v == r:
                count += 1
                break
    return count

@jit(nopython=True)
def calculeaza_punctaj_numba(potriviri):
    """Calculează punctaj bazat pe potriviri"""
    if potriviri == 2:
        return 5
    elif potriviri == 3:
        return 8
    elif potriviri == 4:
        return 10
    return 0

@jit(nopython=True)
def calculeaza_statistici_chenar(variante_arr, runde_arr, numar_minim):
    """Calculează statistici pentru un chenar"""
    castiguri = 0
    count_2_4 = 0
    count_3_4 = 0
    count_4_4 = 0
    punctaje_lista = []
    
    for runda in runde_arr:
        for varianta in variante_arr:
            potriviri = verifica_varianta_numba(varianta, runda)
            
            if potriviri >= numar_minim:
                castiguri += 1
            
            punctaj = calculeaza_punctaj_numba(potriviri)
            if punctaj > 0:
                punctaje_lista.append(punctaj)
                
                if potriviri == 4:
                    count_4_4 += 1
                elif potriviri == 3:
                    count_3_4 += 1
                elif potriviri == 2:
                    count_2_4 += 1
    
    return castiguri, count_2_4, count_3_4, count_4_4, np.array(punctaje_lista)

def aplica_restrictie_diversitate(variante_sortate, max_aparitii):
    """Aplică restricția de diversitate - fiecare număr apare maxim X ori"""
    counter_numere = Counter()
    variante_filtrate = []
    
    for var in variante_sortate:
        poate_adauga = True
        
        for num in var['numere']:
            if counter_numere[num] + 1 > max_aparitii:
                poate_adauga = False
                break
        
        if poate_adauga:
            variante_filtrate.append(var)
            for num in var['numere']:
                counter_numere[num] += 1
        
        if len(variante_filtrate) >= 100:
            break
    
    return variante_filtrate, counter_numere

def filtrare_variante_finale_hibrid(toate_variantele, runde_chenare, usar_runde, max_aparitii_finale, target_count):
    """Filtrează variante HIBRID - cu sau fără runde pentru sortare"""
    
    # PAS 1: Sortare (dacă se folosesc runde)
    if usar_runde and any(len(runde) > 0 for runde in runde_chenare):
        # Calculează punctaj pentru fiecare variantă
        variante_cu_punctaj = []
        
        for var_obj in toate_variantele:
            varianta = np.array(var_obj['numere'], dtype=np.int64)
            punctaj_total = 0
            chenare_active = 0
            
            for i in range(7):
                if not runde_chenare[i]:
                    continue
                    
                runde_arr = np.array(runde_chenare[i], dtype=np.int64)
                punctaj_chenar = 0
                are_potriviri = False
                
                for runda in runde_arr:
                    potriviri = verifica_varianta_numba(varianta, runda)
                    punctaj = calculeaza_punctaj_numba(potriviri)
                    punctaj_chenar += punctaj
                    
                    if potriviri >= 2:
                        are_potriviri = True
                
                punctaj_total += punctaj_chenar
                
                if are_potriviri:
                    chenare_active += 1
            
            variante_cu_punctaj.append({
                'id': var_obj['id'],
                'numere': var_obj['numere'],
                'punctaj_total': punctaj_total,
                'chenare_active': chenare_active
            })
        
        # Sortare după punctaj
        variante_sortate = sorted(variante_cu_punctaj, key=lambda x: (-x['chenare_active'], -x['punctaj_total']))
    else:
        # Fără sortare - ordinea originală
        variante_sortate = toate_variantele
    
    # PAS 2: Filtrare diversitate (max apariții)
    counter_numere = Counter()
    variante_filtrate = []
    
    for var in variante_sortate:
        poate_adauga = True
        
        for num in var['numere']:
            if counter_numere[num] + 1 > max_aparitii_finale:
                poate_adauga = False
                break
        
        if poate_adauga:
            variante_filtrate.append(var)
            for num in var['numere']:
                counter_numere[num] += 1
        
        if len(variante_filtrate) >= target_count:
            break
    
    return variante_filtrate, counter_numere

# MENIU LATERAL - NAVIGARE
st.sidebar.title("🎯 Navigare")
pagina = st.sidebar.radio(
    "Selectează modul:",
    ["📊 Analiză Runde + Variante", "🔬 Filtrare Hibrid Variante"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("**Analiză**: Verifică variante pe runde\n\n**Filtrare Hibrid**: Filtrează cu/fără runde")

# =====================================================
# PAGINA 1: ANALIZĂ RUNDE + VARIANTE
# =====================================================

if pagina == "📊 Analiză Runde + Variante":
    
    # SECȚIUNEA RUNDE - 7 CHENARE
    st.header("📋 Runde")
    
    # Primul rând - 4 chenare
    cols_rand1 = st.columns(4)
    for i in range(4):
        with cols_rand1[i]:
            st.subheader(f"Chenar {i+1}")
            
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
        
        variante_arr = np.array([var['numere'] for var in st.session_state.variante], dtype=np.int64)
        
        for i in range(7):
            with cols_stats[i]:
                if st.session_state.runde_chenare[i]:
                    runde_arr = np.array(st.session_state.runde_chenare[i], dtype=np.int64)
                    
                    castiguri_chenar, count_2_4, count_3_4, count_4_4, punctaje_chenar = calculeaza_statistici_chenar(
                        variante_arr, runde_arr, numar_minim
                    )
                    
                    medie_punctaj = np.mean(punctaje_chenar) if len(punctaje_chenar) > 0 else 0
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
                    runde_arr = np.array(st.session_state.runde_chenare[i], dtype=np.int64)
                    castiguri_total, _, _, _, _ = calculeaza_statistici_chenar(variante_arr, runde_arr, numar_minim)
                    st.text(f"Chenarul {i+1} - {castiguri_total} variante câștigătoare")
        
        st.divider()
        
        # SECȚIUNEA 2 - TOP 100 STABILITATE
        st.header("💎 Secțiunea 2 - TOP 100 Stabilitate")
        
        max_aparitii = st.slider(
            "🎯 Maxim apariții per număr în TOP 100:",
            min_value=1,
            max_value=20,
            value=10,
            help="Fiecare număr poate apărea maxim de atâtea ori în cele 100 variante."
        )
        
        st.divider()
        
        with st.spinner('Calculare TOP 100...'):
            rezultate = []
            
            for var_obj in st.session_state.variante:
                var_id = var_obj['id']
                varianta = np.array(var_obj['numere'], dtype=np.int64)
                
                punctaje_per_chenar = []
                chenare_active = 0
                punctaj_total = 0
                
                for i in range(7):
                    if not st.session_state.runde_chenare[i]:
                        punctaje_per_chenar.append(0)
                        continue
                        
                    runde_arr = np.array(st.session_state.runde_chenare[i], dtype=np.int64)
                    punctaj_chenar = 0
                    are_potriviri = False
                    
                    for runda in runde_arr:
                        potriviri = verifica_varianta_numba(varianta, runda)
                        punctaj = calculeaza_punctaj_numba(potriviri)
                        punctaj_chenar += punctaj
                        
                        if potriviri >= 2:
                            are_potriviri = True
                    
                    punctaje_per_chenar.append(punctaj_chenar)
                    punctaj_total += punctaj_chenar
                    
                    if are_potriviri:
                        chenare_active += 1
                
                sd = np.std(punctaje_per_chenar)
                
                rezultate.append({
                    'id': var_id,
                    'numere': var_obj['numere'],
                    'punctaj_total': punctaj_total,
                    'chenare_active': chenare_active,
                    'sd': sd,
                    'punctaje_per_chenar': punctaje_per_chenar
                })
            
            rezultate_sortate = sorted(rezultate, key=lambda x: (-x['chenare_active'], -x['punctaj_total'], x['sd']))
            top_100, counter_numere = aplica_restrictie_diversitate(rezultate_sortate, max_aparitii)
        
        st.success(f"✅ TOP {len(top_100)} Variante - Cu diversitate maximă!")
        
        numere_peste_limita = [num for num, count in counter_numere.items() if count > max_aparitii]
        st.info(f"📊 Numere unice folosite: {len(counter_numere)} din 66 | Maxim apariții găsite: {max(counter_numere.values()) if counter_numere else 0} | Peste limită: {len(numere_peste_limita)} numere")
        
        st.divider()
        
        # HEATMAP
        st.subheader("🔥 Heatmap Distribuție Punctaj")
        
        heatmap_data = []
        labels_y = []
        
        display_count = min(20, len(top_100))
        
        for idx, item in enumerate(top_100[:display_count], 1):
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
        
        col_h1, col_h2, col_h3, col_h4, col_h5, col_h6, col_h7 = st.columns([1, 2, 4, 2, 2, 2, 2])
        with col_h1:
            st.markdown("**#**")
        with col_h2:
            st.markdown("**ID**")
        with col_h3:
            st.markdown("**Numere**")
        with col_h4:
            st.markdown("**Punctaj**")
        with col_h5:
            st.markdown("**Chenare**")
        with col_h6:
            st.markdown("**SD**")
        with col_h7:
            st.markdown("**Detalii**")
        
        st.divider()
        
        tabel_container = st.container(height=400)
        with tabel_container:
            for idx, item in enumerate(top_100, 1):
                badge = ""
                if item['sd'] < 50.0:
                    badge += "⭐ "
                if item['chenare_active'] >= 5:
                    badge += "🎯 "
                if idx == 1:
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
                    with st.expander("👁️"):
                        for i, punctaj in enumerate(item['punctaje_per_chenar'], 1):
                            st.text(f"Chenar {i}: {punctaj} puncte")
                
                if badge:
                    st.caption(badge)
        
        st.divider()
        
        # FORMAT 2 - COPY-PASTE
        st.subheader("📝 Format 2 - Copy-Paste")
        
        copy_text = ""
        for item in top_100:
            copy_text += f"{item['id']}, {' '.join(map(str, item['numere']))}\n"
        
        st.text_area(
            "Copy-paste:",
            value=copy_text,
            height=300,
            key="copy_paste_area"
        )
    
    else:
        st.info("Adaugă runde și variante pentru verificare")

# =====================================================
# PAGINA 2: FILTRARE HIBRID VARIANTE
# =====================================================

elif pagina == "🔬 Filtrare Hibrid Variante":
    
    st.header("🔬 Filtrare Hibrid Variante")
    
    st.markdown("""
    **Mod Hibrid:** Filtrează variante cu sau fără validare pe runde.
    
    - **Cu runde (ON):** Sortează variante după performanță pe runde → apoi filtrează cu restricție apariții
    - **Fără runde (OFF):** Filtrare pură bazată doar pe restricția de apariții (ordine originală)
    """)
    
    st.divider()
    
    # TOGGLE - Folosește runde sau nu
    usar_runde = st.toggle(
        "🎯 Folosește rundele din Pagina 1 pentru sortare",
        value=True,
        help="ON = sortează după punctaj pe runde | OFF = filtrare pură fără runde"
    )
    
    if usar_runde:
        are_runde_disponibile = any(len(runde) > 0 for runde in st.session_state.runde_chenare)
        if are_runde_disponibile:
            total_runde = sum(len(runde) for runde in st.session_state.runde_chenare)
            st.success(f"✅ Runde detectate: {total_runde} runde în {sum(1 for r in st.session_state.runde_chenare if len(r) > 0)} chenare")
        else:
            st.warning("⚠️ Toggle activat DAR nu există runde în Pagina 1! Mergi la 'Analiză Runde + Variante' și adaugă runde.")
    else:
        st.info("ℹ️ Filtrare fără runde - ordinea variantelor rămâne ca în input")
    
    st.divider()
    
    text_variante_finale = st.text_area(
        "Paste variante pentru filtrare (format: ID, numere separate prin spațiu):",
        height=300,
        placeholder="1, 5 12 34 56\n2, 3 15 42 89\n3, 7 21 48 63\n...",
        key="input_variante_finale"
    )
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        max_aparitii_finale = st.number_input(
            "Maxim apariții per număr:",
            min_value=1,
            max_value=50,
            value=10,
            help="Fiecare număr poate apărea maxim de atâtea ori în setul final."
        )
    
    with col_f2:
        target_variante = st.number_input(
            "Câte variante să păstrezi:",
            min_value=1,
            max_value=10000,
            value=1000,
            help="Numărul de variante finale după filtrare."
        )
    
    with col_f3:
        st.write("")
        st.write("")
        if st.button("🎯 Filtrează Variante", type="primary", use_container_width=True):
            if text_variante_finale.strip():
                with st.spinner('Filtrare hibrid în curs...'):
                    linii = text_variante_finale.strip().split('\n')
                    variante_input = []
                    
                    for linie in linii:
                        try:
                            parti = linie.split(',', 1)
                            if len(parti) == 2:
                                id_var = parti[0].strip()
                                numere_str = parti[1].strip()
                                numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                                if numere:
                                    variante_input.append({
                                        'id': id_var,
                                        'numere': numere
                                    })
                        except:
                            pass
                    
                    if variante_input:
                        variante_filtrate, counter_finale = filtrare_variante_finale_hibrid(
                            variante_input,
                            st.session_state.runde_chenare,
                            usar_runde,
                            max_aparitii_finale,
                            target_variante
                        )
                        
                        st.session_state.variante_filtrate_finale = variante_filtrate
                        
                        mod_text = "cu sortare pe runde" if usar_runde else "fără runde (ordine originală)"
                        st.success(f"✅ Filtrat ({mod_text}): {len(variante_input)} → {len(variante_filtrate)} variante!")
                        st.info(f"📊 Numere unice: {len(counter_finale)} | Max apariții: {max(counter_finale.values()) if counter_finale else 0}")
                    else:
                        st.error("Nu s-au putut procesa variante. Verifică formatul.")
            else:
                st.warning("Adaugă variante pentru filtrare.")
    
    if st.session_state.variante_filtrate_finale:
        st.divider()
        
        st.subheader("📋 Rezultat Filtrare")
        
        # Analiză distribuție
        counter_distributie = Counter()
        for var in st.session_state.variante_filtrate_finale:
            for num in var['numere']:
                counter_distributie[num] += 1
        
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            st.metric("Variante finale", len(st.session_state.variante_filtrate_finale))
        with col_a2:
            st.metric("Numere unice", len(counter_distributie))
        with col_a3:
            st.metric("Acoperire", f"{len(counter_distributie)/66*100:.1f}%")
        
        st.divider()
        
        # Copy-paste format
        st.subheader("📝 Variante Filtrate - Copy-Paste")
        
        copy_text_filtrat = ""
        for item in st.session_state.variante_filtrate_finale:
            copy_text_filtrat += f"{item['id']}, {' '.join(map(str, item['numere']))}\n"
        
        st.text_area(
            "Variante finale:",
            value=copy_text_filtrat,
            height=400,
            key="copy_paste_filtrate"
        )
        
        # Analiză distribuție detaliată
        with st.expander("📊 Analiză Distribuție Numere"):
            df_distributie = pd.DataFrame([
                {"Număr": num, "Apariții": count}
                for num, count in sorted(counter_distributie.items())
            ])
            
            st.dataframe(df_distributie, use_container_width=True, height=400)