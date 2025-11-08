import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import os
import json
import tempfile

# Configurar la página
st.set_page_config(
    page_title="Registro de Clientes",
    page_icon="🏪",
    layout="wide"
)

# Título principal
st.title("🏪 REGISTRO DE CLIENTES ATENDIDOS")
st.markdown("---")

# Lista de rangos de horario
RANGOS_HORARIO = [
    "10 a.m - 11 a.m",
    "11 a.m - 12 p.m", 
    "12 p.m - 1 p.m",
    "1 p.m - 2 p.m",
    "2 p.m - 3 p.m",
    "3 p.m - 4 p.m",
    "4 p.m - 5 p.m",
    "5 p.m - 6 p.m",
    "6 p.m - 7 p.m",
    "7 p.m - 8 p.m",
    "8 p.m - 9 p.m",
    "9 p.m - 10 p.m"
]

# RUTA PERSISTENTE MEJORADA
def obtener_ruta_archivo():
    """Obtener ruta de archivo persistente - MEJORADA"""
    # Usar directorio de trabajo actual
    directorio_datos = "./datos_persistentes"
    if not os.path.exists(directorio_datos):
        os.makedirs(directorio_datos, exist_ok=True)
    return os.path.join(directorio_datos, 'registros_clientes_viale.json')

def guardar_registros(registros):
    """Guardar registros permanentemente - MEJORADA"""
    try:
        ruta_archivo = obtener_ruta_archivo()
        # Guardar con formato seguro
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(registros, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"❌ Error crítico al guardar datos: {str(e)}")
        return False

def cargar_registros():
    """Cargar registros guardados - MEJORADA con manejo robusto"""
    try:
        ruta_archivo = obtener_ruta_archivo()
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                registros = json.load(f)
                if isinstance(registros, list):
                    st.sidebar.success(f"💾 {len(registros)} registros cargados desde archivo")
                    return registros
                else:
                    st.warning("⚠️ Formato de archivo inválido, iniciando con lista vacía")
                    return []
        else:
            st.sidebar.info("📝 No se encontró archivo previo, iniciando nuevo registro")
            return []
    except Exception as e:
        st.error(f"❌ Error al cargar archivo: {str(e)}")
        return []

# FUNCIONES AUXILIARES
def calcular_porcentaje(tickets, clientes):
    try:
        if clientes == 0:
            return 0
        return int((tickets / clientes) * 100)
    except:
        return 0

def obtener_valor_seguro(record, campo, default=0):
    return record.get(campo, default)

# INICIALIZACIÓN ROBUSTA - SIEMPRE CARGAR DESDE ARCHIVO
def inicializar_datos():
    """Inicializar datos siempre desde archivo - SOLUCIÓN DEFINITIVA"""
    registros = cargar_registros()
    
    # Verificar si session_state necesita actualización
    if 'records' not in st.session_state or st.session_state.records != registros:
        st.session_state.records = registros
    
    return registros

# Inicializar la aplicación
registros_iniciales = inicializar_datos()

# Función para ACTUALIZAR desde archivo
def actualizar_desde_archivo():
    """Forzar actualización desde archivo - MEJORADA"""
    registros_actuales = cargar_registros()
    st.session_state.records = registros_actuales
    st.success(f"✅ Sincronizado: {len(registros_actuales)} registros")
    return registros_actuales

# Inicializar estados de sesión para los modales
if 'mostrar_modal_descarga' not in st.session_state:
    st.session_state.mostrar_modal_descarga = False
if 'mostrar_modal_reinicio' not in st.session_state:
    st.session_state.mostrar_modal_reinicio = False

# Función para limpiar cache
def limpiar_cache_tiendas():
    if 'cargar_datos_tiendas' in st.session_state:
        del st.session_state['cargar_datos_tiendas']
    st.cache_data.clear()
    st.success("✅ Cache limpiado")

# Cargar datos de tiendas y vendedores
@st.cache_data(ttl=300)
def cargar_datos_tiendas():
    """Cargar datos de tiendas y vendedores"""
    try:
        df = pd.read_excel("Asesores.xlsx")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar Excel: {str(e)}")
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor A', 'Vendedor B', 'KAELIN DÍAZ', 'JAVIER VLAVERDE']
        }
        return pd.DataFrame(datos_ejemplo)

# Cargar datos de tiendas
df_tiendas = cargar_datos_tiendas()

# Mostrar información del archivo cargado
if 'Tienda' in df_tiendas.columns and 'Vendedor' in df_tiendas.columns:
    st.sidebar.success(f"✅ {len(df_tiendas)} registros de tiendas cargados")
    
    with st.expander("📊 RESUMEN DE DATOS CARGADOS", expanded=False):
        st.write(f"**Tiendas únicas en Excel:** {len(df_tiendas['Tienda'].unique())}")
        st.write(f"**Vendedores únicos:** {len(df_tiendas['Vendedor'].unique())}")
        
        st.write("**Todas las tiendas en Excel:**")
        for tienda in sorted(df_tiendas['Tienda'].unique()):
            vendedores = df_tiendas[df_tiendas['Tienda'] == tienda]['Vendedor'].unique()
            st.write(f"- **{tienda}**: {len(vendedores)} vendedores")

# Funciones básicas
def obtener_tiendas():
    if 'Tienda' in df_tiendas.columns:
        return sorted(df_tiendas['Tienda'].unique().tolist())
    return []

def obtener_vendedores_por_tienda(tienda_seleccionada):
    if 'Tienda' in df_tiendas.columns and 'Vendedor' in df_tiendas.columns:
        if tienda_seleccionada:
            vendedores = df_tiendas[df_tiendas['Tienda'] == tienda_seleccionada]['Vendedor'].unique().tolist()
            return vendedores if vendedores else ["No hay vendedores"]
        return ["Selecciona tienda"]
    return ["Error"]

# FUNCIÓN CRÍTICA MEJORADA: Guardar permanentemente
def add_record(tienda, vendedor, rango_horario, date_str, count, tickets, soles):
    """Guardar registro - SOLUCIÓN PERSISTENTE MEJORADA"""
    record = {
        'tienda': tienda,
        'seller': vendedor,
        'rango_horario': rango_horario,
        'date': date_str,
        'count': count,
        'tickets': tickets,
        'soles': soles,
        'timestamp': datetime.now().isoformat()
    }
    
    # SIEMPRE cargar desde archivo primero para evitar conflictos
    registros_actuales = cargar_registros()
    registros_actuales.append(record)
    
    # Guardar en archivo inmediatamente
    if guardar_registros(registros_actuales):
        # Actualizar session_state solo después de guardar exitosamente
        st.session_state.records = registros_actuales
        st.success(f"✅ Guardado permanentemente: {tienda} - {vendedor} - {rango_horario}")
        return True
    else:
        st.error("❌ Error crítico: No se pudo guardar el registro")
        return False

# FUNCIÓN CRÍTICA MEJORADA: Eliminar permanentemente
def delete_record(index):
    """Eliminar registro - SOLUCIÓN PERSISTENTE MEJORADA"""
    # SIEMPRE cargar desde archivo primero
    registros_actuales = cargar_registros()
    
    if 0 <= index < len(registros_actuales):
        deleted = registros_actuales.pop(index)
        
        # Guardar en archivo inmediatamente
        if guardar_registros(registros_actuales):
            # Actualizar session_state solo después de guardar exitosamente
            st.session_state.records = registros_actuales
            st.success(f"🗑️ Eliminado permanentemente: {deleted.get('seller', 'N/A')}")
            return True
        else:
            st.error("❌ Error crítico: No se pudo eliminar el registro")
            return False
    return False

def formatear_registro_para_mostrar(index):
    record = st.session_state.records[index]
    if 'tienda' in record:
        tickets = record.get('tickets', 'N/A')
        soles = record.get('soles', 'N/A')
        rango_horario = record.get('rango_horario', 'N/A')
        return f"{record['tienda']} - {record['seller']} - {rango_horario} - {record['date']} - {record['count']} clientes - {tickets} tickets - S/. {soles}"
    else:
        return f"{record['seller']} - {record['date']} - {record['count']} clientes (registro antiguo)"

# FUNCIONES DE ESTADÍSTICAS MEJORADAS
def get_stats_por_tienda(tienda_seleccionada):
    """Obtener estadísticas solo para la tienda seleccionada"""
    if not st.session_state.records:
        return {
            'total_clients': 0,
            'total_records': 0,
            'total_tickets': 0,
            'total_soles': 0,
            'top_seller': {'name': 'N/A', 'count': 0},
            'avg_per_day': 0,
            'avg_tickets_per_day': 0,
            'avg_soles_per_day': 0,
            'porcentaje_general': 0,
            'ticket_promedio': 0,
            'mejor_dia': {'fecha': 'N/A', 'clientes': 0},
            'horario_pico': {'horario': 'N/A', 'clientes': 0}
        }
    
    # Filtrar registros por tienda
    registros_tienda = [r for r in st.session_state.records if r.get('tienda') == tienda_seleccionada]
    
    if not registros_tienda:
        return {
            'total_clients': 0,
            'total_records': 0,
            'total_tickets': 0,
            'total_soles': 0,
            'top_seller': {'name': 'N/A', 'count': 0},
            'avg_per_day': 0,
            'avg_tickets_per_day': 0,
            'avg_soles_per_day': 0,
            'porcentaje_general': 0,
            'ticket_promedio': 0,
            'mejor_dia': {'fecha': 'N/A', 'clientes': 0},
            'horario_pico': {'horario': 'N/A', 'clientes': 0}
        }
    
    total_clients = 0
    total_tickets = 0
    total_soles = 0
    
    # Estadísticas por día y horario
    dias_stats = {}
    horarios_stats = {}
    
    for record in registros_tienda:
        total_clients += obtener_valor_seguro(record, 'count', 0)
        total_tickets += obtener_valor_seguro(record, 'tickets', 0)
        total_soles += obtener_valor_seguro(record, 'soles', 0)
        
        # Estadísticas por fecha
        fecha = record.get('date', '')
        if fecha in dias_stats:
            dias_stats[fecha] += obtener_valor_seguro(record, 'count', 0)
        else:
            dias_stats[fecha] = obtener_valor_seguro(record, 'count', 0)
        
        # Estadísticas por horario
        horario = record.get('rango_horario', '')
        if horario in horarios_stats:
            horarios_stats[horario] += obtener_valor_seguro(record, 'count', 0)
        else:
            horarios_stats[horario] = obtener_valor_seguro(record, 'count', 0)
    
    total_records = len(registros_tienda)
    
    # Calcular top seller
    seller_stats = {}
    for record in registros_tienda:
        seller = record.get('seller', 'Desconocido')
        count = obtener_valor_seguro(record, 'count', 0)
        if seller in seller_stats:
            seller_stats[seller] += count
        else:
            seller_stats[seller] = count
    
    top_seller = 'N/A'
    top_seller_count = 0
    if seller_stats:
        top_seller = max(seller_stats, key=seller_stats.get)
        top_seller_count = seller_stats[top_seller]
    
    # Calcular promedios
    avg_per_day = total_clients / total_records if total_records > 0 else 0
    avg_tickets_per_day = total_tickets / total_records if total_records > 0 else 0
    avg_soles_per_day = total_soles / total_records if total_records > 0 else 0
    
    # Calcular porcentaje general
    porcentaje_general = calcular_porcentaje(total_tickets, total_clients)
    
    # Calcular ticket promedio
    ticket_promedio = total_soles / total_tickets if total_tickets > 0 else 0
    
    # Mejor día
    mejor_dia = 'N/A'
    mejor_dia_count = 0
    if dias_stats:
        mejor_dia = max(dias_stats, key=dias_stats.get)
        mejor_dia_count = dias_stats[mejor_dia]
    
    # Horario pico
    horario_pico = 'N/A'
    horario_pico_count = 0
    if horarios_stats:
        horario_pico = max(horarios_stats, key=horarios_stats.get)
        horario_pico_count = horarios_stats[horario_pico]
    
    return {
        'total_clients': total_clients,
        'total_records': total_records,
        'total_tickets': total_tickets,
        'total_soles': total_soles,
        'top_seller': {'name': top_seller, 'count': top_seller_count},
        'avg_per_day': round(avg_per_day, 1),
        'avg_tickets_per_day': round(avg_tickets_per_day, 1),
        'avg_soles_per_day': round(avg_soles_per_day, 1),
        'porcentaje_general': porcentaje_general,
        'ticket_promedio': round(ticket_promedio, 1),
        'mejor_dia': {'fecha': mejor_dia, 'clientes': mejor_dia_count},
        'horario_pico': {'horario': horario_pico, 'clientes': horario_pico_count}
    }

def get_stats_general():
    """Obtener estadísticas de todas las tiendas"""
    if not st.session_state.records:
        return {
            'total_clients': 0,
            'total_records': 0,
            'total_tickets': 0,
            'total_soles': 0,
            'top_seller': {'name': 'N/A', 'count': 0},
            'top_tienda': {'name': 'N/A', 'count': 0},
            'avg_per_day': 0,
            'avg_tickets_per_day': 0,
            'avg_soles_per_day': 0,
            'porcentaje_general': 0,
            'ticket_promedio': 0
        }
    
    total_clients = 0
    total_tickets = 0
    total_soles = 0
    
    for record in st.session_state.records:
        total_clients += obtener_valor_seguro(record, 'count', 0)
        total_tickets += obtener_valor_seguro(record, 'tickets', 0)
        total_soles += obtener_valor_seguro(record, 'soles', 0)
    
    total_records = len(st.session_state.records)
    
    # Calcular top seller
    seller_stats = {}
    for record in st.session_state.records:
        seller = record.get('seller', 'Desconocido')
        count = obtener_valor_seguro(record, 'count', 0)
        if seller in seller_stats:
            seller_stats[seller] += count
        else:
            seller_stats[seller] = count
    
    top_seller = 'N/A'
    top_seller_count = 0
    if seller_stats:
        top_seller = max(seller_stats, key=seller_stats.get)
        top_seller_count = seller_stats[top_seller]
    
    # Calcular top tienda
    tienda_stats = {}
    for record in st.session_state.records:
        tienda = record.get('tienda', 'Desconocido')
        count = obtener_valor_seguro(record, 'count', 0)
        if tienda in tienda_stats:
            tienda_stats[tienda] += count
        else:
            tienda_stats[tienda] = count
    
    top_tienda_name = 'N/A'
    top_tienda_count = 0
    if tienda_stats:
        top_tienda_name = max(tienda_stats, key=tienda_stats.get)
        top_tienda_count = tienda_stats[top_tienda_name]
    
    # Calcular promedios
    avg_per_day = total_clients / total_records if total_records > 0 else 0
    avg_tickets_per_day = total_tickets / total_records if total_records > 0 else 0
    avg_soles_per_day = total_soles / total_records if total_records > 0 else 0
    
    # Calcular porcentaje general
    porcentaje_general = calcular_porcentaje(total_tickets, total_clients)
    
    # Calcular ticket promedio
    ticket_promedio = total_soles / total_tickets if total_tickets > 0 else 0
    
    return {
        'total_clients': total_clients,
        'total_records': total_records,
        'total_tickets': total_tickets,
        'total_soles': total_soles,
        'top_seller': {'name': top_seller, 'count': top_seller_count},
        'top_tienda': {'name': top_tienda_name, 'count': top_tienda_count},
        'avg_per_day': round(avg_per_day, 1),
        'avg_tickets_per_day': round(avg_tickets_per_day, 1),
        'avg_soles_per_day': round(avg_soles_per_day, 1),
        'porcentaje_general': porcentaje_general,
        'ticket_promedio': round(ticket_promedio, 1)
    }

# Sidebar para nuevo registro
with st.sidebar:
    st.header("➕ NUEVO REGISTRO")
    
    tiendas = obtener_tiendas()
    if tiendas:
        tienda_seleccionada = st.selectbox(
            "🏪 Selecciona la Tienda:",
            options=tiendas,
            index=0,
            key="tienda_selector"
        )
        
        vendedores = obtener_vendedores_por_tienda(tienda_seleccionada)
        
        if vendedores and vendedores[0] not in ["No hay vendedores", "Selecciona tienda", "Error"]:
            st.info(f"👤 Vendedores de {tienda_seleccionada}: {len(vendedores)} disponibles")
        
        vendedor_seleccionado = st.selectbox(
            "👤 Selecciona el Vendedor:",
            options=vendedores,
            key="vendedor_selector"
        )
        
        rango_horario = st.selectbox(
            "⏰ Rango horario:",
            options=RANGOS_HORARIO,
            key="rango_selector"
        )
        
        fecha = st.date_input("📅 Fecha:", value=date.today())
        count = st.number_input("✅ Clientes:", min_value=1, value=1)
        tickets = st.number_input("🎫 Tickets:", min_value=0, value=0)
        soles = st.number_input("💰 Soles (S/.):", min_value=0.0, value=0.0, step=0.1, format="%.2f")
        
        if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
            if vendedor_seleccionado not in ["No hay vendedores", "Selecciona tienda", "Error"]:
                if add_record(tienda_seleccionada, vendedor_seleccionado, rango_horario, fecha.isoformat(), count, tickets, soles):
                    st.rerun()
            else:
                st.error("❌ Selecciona un vendedor válido")

    # BOTÓN CRÍTICO: Actualizar desde archivo
    st.markdown("---")
    st.header("🔄 SINCRONIZACIÓN")
    
    if st.button("🔄 Actualizar desde Archivo", use_container_width=True):
        actualizar_desde_archivo()
        st.rerun()
    
    # BOTÓN PARA RECARGAR DATOS
    if st.button("🔄 Recargar Datos de Tiendas", use_container_width=True):
        limpiar_cache_tiendas()
        st.rerun()
    
    # Información de estado
    st.info(f"**Registros en memoria:** {len(st.session_state.records)}")
    
    # Información del archivo
    ruta_archivo = obtener_ruta_archivo()
    if os.path.exists(ruta_archivo):
        st.success("💾 Archivo de datos: PRESENTE")
    else:
        st.warning("📝 Archivo de datos: Por crear")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    # USAR LA TIENDA SELECCIONADA EN EL SIDEBAR
    tienda_actual = st.session_state.tienda_selector if 'tienda_selector' in st.session_state else (tiendas[0] if tiendas else "NO_HAY_TIENDAS")
    
    st.header(f"📋 HISTORIAL DE REGISTROS - {tienda_actual}")
    
    # BOTÓN PARA FORZAR ACTUALIZACIÓN
    if st.button("🔄 Actualizar Vista", key="actualizar_vista"):
        actualizar_desde_archivo()
        st.rerun()
    
    if st.session_state.records:
        # Obtener registros de la tienda actual
        registros_tienda_actual = [r for r in st.session_state.records if r.get('tienda') == tienda_actual]
        
        st.info(f"**Registros para {tienda_actual}:** {len(registros_tienda_actual)}")
        
        if registros_tienda_actual:
            # Agrupar por vendedor
            vendedores_tienda = list(set([r['seller'] for r in registros_tienda_actual]))
            
            for vendedor in vendedores_tienda:
                registros_vendedor = [r for r in registros_tienda_actual if r['seller'] == vendedor]
                
                datos_vendedor = []
                for registro in registros_vendedor:
                    datos_vendedor.append({
                        'Fecha': pd.to_datetime(registro['date']).strftime('%d/%m/%Y'),
                        'Vendedor': registro.get('seller', 'N/A'),
                        'Rango Horario': registro.get('rango_horario', 'N/A'),
                        'Clientes': registro.get('count', 0),
                        'Tickets': registro.get('tickets', 0),
                        'Soles (S/.)': registro.get('soles', 0),
                        'Porcentaje': f"{calcular_porcentaje(registro.get('tickets', 0), registro.get('count', 0))}%"
                    })
                
                df_vendedor = pd.DataFrame(datos_vendedor)
                df_vendedor = df_vendedor.sort_values('Fecha', ascending=False)
                
                with st.expander(f"👤 {vendedor} - {len(registros_vendedor)} registros", expanded=True):
                    # Estadísticas del vendedor
                    total_clientes_vendedor = sum([r.get('count', 0) for r in registros_vendedor])
                    total_tickets_vendedor = sum([r.get('tickets', 0) for r in registros_vendedor])
                    total_soles_vendedor = sum([r.get('soles', 0) for r in registros_vendedor])
                    porcentaje_promedio = calcular_porcentaje(total_tickets_vendedor, total_clientes_vendedor)
                    
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("Total Clientes", total_clientes_vendedor)
                    with col_stat2:
                        st.metric("Total Tickets", total_tickets_vendedor)
                    with col_stat3:
                        st.metric("Porcentaje", f"{porcentaje_promedio}%")
                    
                    st.dataframe(df_vendedor, hide_index=True, use_container_width=True)
            
            # Sección de eliminación
            st.subheader("🗑️ Eliminar Registros")
            indices_tienda = [i for i, r in enumerate(st.session_state.records) if r.get('tienda') == tienda_actual]
            
            if indices_tienda:
                record_index = st.selectbox("Selecciona registro:", options=indices_tienda, format_func=formatear_registro_para_mostrar)
                if st.button("Eliminar Registro Seleccionado", type="secondary"):
                    if delete_record(record_index):
                        st.rerun()
        else:
            st.warning(f"⚠️ No hay registros para la tienda '{tienda_actual}'")
    else:
        st.info("📝 No hay registros en el sistema. Agrega el primero en el sidebar.")

with col2:
    tienda_actual = st.session_state.tienda_selector if 'tienda_selector' in st.session_state else (tiendas[0] if tiendas else "NO_HAY_TIENDAS")
    
    st.header(f"📊 ESTADÍSTICAS - {tienda_actual}")
    
    # Estadísticas MEJORADAS
    stats_tienda = get_stats_por_tienda(tienda_actual)
    
    if stats_tienda['total_records'] > 0:
        # Métricas principales
        st.subheader("📈 Métricas Principales")
        
        col_met1, col_met2 = st.columns(2)
        with col_met1:
            st.metric("👥 Total Clientes", f"{stats_tienda['total_clients']:,}")
            st.metric("🎫 Total Tickets", stats_tienda['total_tickets'])
            st.metric("💰 Total Recaudado", f"S/. {stats_tienda['total_soles']:,.0f}")
        
        with col_met2:
            st.metric("📋 Total Registros", stats_tienda['total_records'])
            st.metric("📅 Promedio Clientes/día", stats_tienda['avg_per_day'])
            st.metric("💵 Promedio Soles/día", f"S/. {stats_tienda['avg_soles_per_day']:,.1f}")
        
        st.markdown("---")
        st.subheader("🏆 Desempeño")
        
        col_perf1, col_perf2 = st.columns(2)
        with col_perf1:
            st.metric("⭐ Vendedor Top", stats_tienda['top_seller']['name'])
            st.metric("📊 Promedio Tickets/día", stats_tienda['avg_tickets_per_day'])
        
        with col_perf2:
            st.metric("📈 Efectividad General", f"{stats_tienda['porcentaje_general']}%")
            st.metric("🎟️ Ticket Promedio", f"S/. {stats_tienda['ticket_promedio']:,.1f}")
        
        st.markdown("---")
        st.subheader("📅 Análisis Temporal")
        
        col_temp1, col_temp2 = st.columns(2)
        with col_temp1:
            if stats_tienda['mejor_dia']['fecha'] != 'N/A':
                fecha_formateada = pd.to_datetime(stats_tienda['mejor_dia']['fecha']).strftime('%d/%m/%Y')
                st.metric("📅 Mejor Día", fecha_formateada, delta=f"{stats_tienda['mejor_dia']['clientes']} clientes")
        
        with col_temp2:
            if stats_tienda['horario_pico']['horario'] != 'N/A':
                st.metric("⏰ Horario Pico", stats_tienda['horario_pico']['horario'], delta=f"{stats_tienda['horario_pico']['clientes']} clientes")
        
        # Gráficos
        if st.session_state.records:
            st.markdown("---")
            st.subheader("📊 Análisis Visual")
            
            datos_grafico = []
            for record in st.session_state.records:
                if record.get('tienda') == tienda_actual:
                    datos_grafico.append({
                        'seller': record.get('seller', 'Desconocido'),
                        'count': obtener_valor_seguro(record, 'count', 0),
                        'tickets': obtener_valor_seguro(record, 'tickets', 0),
                        'soles': obtener_valor_seguro(record, 'soles', 0)
                    })
            
            df_grafico = pd.DataFrame(datos_grafico)
            
            if not df_grafico.empty:
                st.write("**👥 Desempeño por Vendedor (Clientes Atendidos)**")
                seller_totals = df_grafico.groupby('seller')['count'].sum()
                st.bar_chart(seller_totals, use_container_width=True)
    else:
        st.info("No hay estadísticas para esta tienda")

# SECCIÓN DE EXPORTACIÓN CON CONTRASEÑA
st.markdown("---")
st.header("📤 EXPORTACIÓN DE DATOS")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if st.session_state.records:
        # Crear DataFrame para exportación
        datos_exportacion = []
        for record in st.session_state.records:
            clientes = obtener_valor_seguro(record, 'count', 0)
            tickets = obtener_valor_seguro(record, 'tickets', 0)
            soles = obtener_valor_seguro(record, 'soles', 0)
            rango_horario = record.get('rango_horario', 'N/A')
            porcentaje = calcular_porcentaje(tickets, clientes)
            
            datos_exportacion.append({
                'Tienda': record.get('tienda', 'N/A'),
                'Vendedor': record.get('seller', 'N/A'),
                'Rango Horario': rango_horario,
                'Fecha': record['date'],
                'Clientes': clientes,
                'Tickets': tickets,
                'Soles (S/.)': soles,
                'Porcentaje': f"{porcentaje}%",
                'Timestamp': record.get('timestamp', 'N/A')
            })
        
        df_export = pd.DataFrame(datos_exportacion)
        df_export['Fecha'] = pd.to_datetime(df_export['Fecha'])
        df_export = df_export.sort_values('Fecha', ascending=False)
        
        # Obtener estadísticas generales para el reporte
        stats_general = get_stats_general()
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja 1: Todos los registros
            df_export.to_excel(writer, index=False, sheet_name='Todos_Los_Registros')
            
            # Hoja 2: Estadísticas generales
            stats_df = pd.DataFrame([{
                'Total Clientes': stats_general['total_clients'],
                'Total Tickets': stats_general['total_tickets'],
                'Total Soles': stats_general['total_soles'],
                'Total Registros': stats_general['total_records'],
                'Vendedor Top': f"{stats_general['top_seller']['name']} ({stats_general['top_seller']['count']})",
                'Tienda Top': f"{stats_general['top_tienda']['name']} ({stats_general['top_tienda']['count']})",
                'Promedio Clientes/Día': stats_general['avg_per_day'],
                'Promedio Tickets/Día': stats_general['avg_tickets_per_day'],
                'Promedio Soles/Día': stats_general['avg_soles_per_day'],
                'Porcentaje General': f"{stats_general['porcentaje_general']}%",
                'Ticket Promedio': f"S/. {stats_general['ticket_promedio']:,.1f}"
            }])
            stats_df.to_excel(writer, index=False, sheet_name='Estadisticas_Generales')
            
            # Hoja 3: Datos de tiendas y vendedores
            df_tiendas.to_excel(writer, index=False, sheet_name='Tiendas_Vendedores')
        
        output.seek(0)
        
        # Botón de descarga con protección por contraseña
        st.subheader("💾 Exportar Reporte Completo")
        st.info("Descarga un archivo Excel con todos los registros, estadísticas y datos de tiendas.")
        
        if st.button("📊 Generar Reporte Excel", key="download_excel", use_container_width=True):
            st.session_state.mostrar_modal_descarga = True
            st.rerun()
        
        # Modal para descarga
        if st.session_state.mostrar_modal_descarga:
            st.markdown("---")
            st.subheader("🔒 Confirmación de Descarga")
            st.warning("El reporte contiene información sensible. Confirme con la contraseña.")
            
            contraseña = st.text_input("Ingrese la contraseña:", type="password", key="contraseña_descarga")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Confirmar Descarga", key="confirmar_descarga", use_container_width=True):
                    if contraseña == "demanda2025":
                        st.session_state.mostrar_modal_descarga = False
                        st.success("✅ Contraseña correcta - Descargando archivo...")
                        # Descargar el archivo inmediatamente
                        st.download_button(
                            label="⬇️ Haga clic aquí para descargar",
                            data=output,
                            file_name=f"registro_clientes_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_final",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Contraseña incorrecta")
            with col_btn2:
                if st.button("❌ Cancelar", key="cancelar_descarga", use_container_width=True):
                    st.session_state.mostrar_modal_descarga = False
                    st.rerun()
        
        st.info(f"**El reporte incluirá:** {len(st.session_state.records)} registros de todas las tiendas")
        
    else:
        st.warning("No hay datos para exportar")

with col_exp2:
    if st.session_state.records:
        # Botón de reinicio con protección por contraseña
        st.subheader("🔄 Reinicio de Datos")
        st.error("**ACCIÓN IRREVERSIBLE:** Esta acción elimina PERMANENTEMENTE todos los registros.")
        
        if st.button("🗑️ Iniciar Proceso de Reinicio", type="primary", key="reset_all", use_container_width=True):
            st.session_state.mostrar_modal_reinicio = True
            st.rerun()
        
        # Modal para reinicio
        if st.session_state.mostrar_modal_reinicio:
            st.markdown("---")
            st.subheader("🔒 Confirmar Reinicio Total")
            st.error("""
            ⚠️ **ADVERTENCIA CRÍTICA:** 
            - Se eliminarán TODOS los registros permanentemente
            - Esta acción NO se puede deshacer
            - Se perderá toda la información histórica
            """)
            
            contraseña = st.text_input("Ingrese la contraseña para confirmar:", type="password", key="contraseña_reinicio")
            
            col_rein1, col_rein2 = st.columns(2)
            with col_rein1:
                if st.button("✅ CONFIRMAR REINICIO", type="primary", key="confirmar_reinicio", use_container_width=True):
                    if contraseña == "demanda2025":
                        # Limpiar tanto session_state como archivo
                        st.session_state.records = []
                        try:
                            ruta_archivo = obtener_ruta_archivo()
                            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                                json.dump([], f)
                            st.success("✅ Todos los datos han sido eliminados permanentemente")
                        except:
                            st.error("❌ Error al limpiar archivo")
                        st.session_state.mostrar_modal_reinicio = False
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
            with col_rein2:
                if st.button("❌ Cancelar", key="cancelar_reinicio", use_container_width=True):
                    st.session_state.mostrar_modal_reinicio = False
                    st.rerun()
    else:
        st.info("No hay datos para reiniciar")

# HERRAMIENTAS ADICIONALES
with st.expander("🔄 HERRAMIENTAS DE GESTIÓN", expanded=False):
    st.subheader("🧹 Mantenimiento de Datos")
    
    col_mant1, col_mant2 = st.columns(2)
    
    with col_mant1:
        st.write("**Limpiar Registros Antiguos**")
        st.warning("Elimina registros que no tienen información de tienda (formato antiguo).")
        if st.button("🧹 Ejecutar Limpieza", key="clean_old", use_container_width=True):
            registros_originales = len(st.session_state.records)
            st.session_state.records = [r for r in st.session_state.records if 'tienda' in r]
            registros_nuevos = len(st.session_state.records)
            eliminados = registros_originales - registros_nuevos
            
            # Guardar cambios
            if guardar_registros(st.session_state.records):
                st.success(f"✅ Se eliminaron {eliminados} registros antiguos")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("**📱 App Web de Registro de Clientes** - *Sistema persistente multi-pestaña*")