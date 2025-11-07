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

# ARCHIVO PERSISTENTE - CORRECCIÓN PRINCIPAL
def obtener_ruta_archivo():
    """Obtener ruta de archivo persistente"""
    directorio_datos = "./datos_app"
    if not os.path.exists(directorio_datos):
        os.makedirs(directorio_datos)
    return os.path.join(directorio_datos, 'registros_clientes_viale.json')

# Funciones para guardar y cargar datos PERMANENTEMENTE - CORREGIDAS
def guardar_registros():
    """Guardar registros permanentemente"""
    try:
        ruta_archivo = obtener_ruta_archivo()
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.records, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar datos: {str(e)}")
        return False

def cargar_registros():
    """Cargar registros guardados"""
    try:
        ruta_archivo = obtener_ruta_archivo()
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                registros = json.load(f)
                if isinstance(registros, list):
                    st.sidebar.success(f"💾 {len(registros)} registros cargados desde archivo")
                    return registros
                else:
                    st.sidebar.warning("⚠️ Archivo corrupto, iniciando con lista vacía")
                    return []
        else:
            st.sidebar.info("📝 No se encontraron datos previos")
    except Exception as e:
        st.sidebar.error(f"❌ Error al cargar: {str(e)}")
    return []

# INICIALIZACIÓN CRÍTICA - CORREGIDA
if 'records' not in st.session_state:
    st.session_state.records = cargar_registros()

# DEPURACIÓN: Mostrar información de diagnóstico
st.sidebar.markdown("---")
st.sidebar.header("🔍 DIAGNÓSTICO")

# Mostrar información de los registros cargados
if st.session_state.records:
    # Obtener todas las tiendas únicas en los registros
    tiendas_en_registros = list(set([r.get('tienda', 'SIN_TIENDA') for r in st.session_state.records]))
    st.sidebar.info(f"**Tiendas en registros:** {len(tiendas_en_registros)}")
    st.sidebar.info(f"**Total registros:** {len(st.session_state.records)}")
    
    # Mostrar las primeras 5 tiendas para diagnóstico
    st.sidebar.write("**Primeras tiendas encontradas:**")
    for tienda in tiendas_en_registros[:5]:
        count = len([r for r in st.session_state.records if r.get('tienda') == tienda])
        st.sidebar.write(f"- {tienda}: {count} registros")
    
    if len(tiendas_en_registros) > 5:
        st.sidebar.write(f"- ... y {len(tiendas_en_registros) - 5} más")
else:
    st.sidebar.warning("⚠️ No hay registros cargados")

# Inicializar estados de sesión
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
        st.success("📁 Archivo cargado: Asesores.xlsx")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar Excel: {str(e)}")
        # Datos de ejemplo
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor A', 'Vendedor B', 'KAELIN DÍAZ', 'JAVIER VLAVERDE']
        }
        return pd.DataFrame(datos_ejemplo)

# Cargar datos
df_tiendas = cargar_datos_tiendas()

# Mostrar información del archivo cargado
if 'Tienda' in df_tiendas.columns and 'Vendedor' in df_tiendas.columns:
    st.success(f"✅ {len(df_tiendas)} registros de tiendas y vendedores")
    
    with st.expander("📊 RESUMEN DE DATOS CARGADOS"):
        st.write(f"**Tiendas únicas en Excel:** {len(df_tiendas['Tienda'].unique())}")
        st.write(f"**Vendedores únicos:** {len(df_tiendas['Vendedor'].unique())}")
        
        # DEPURACIÓN: Mostrar todas las tiendas del Excel
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

def add_record(tienda, vendedor, rango_horario, date_str, count, tickets, soles):
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
    st.session_state.records.append(record)
    if guardar_registros():
        st.success(f"✅ Guardado: {tienda} - {vendedor}")

def delete_record(index):
    if 0 <= index < len(st.session_state.records):
        deleted = st.session_state.records.pop(index)
        if guardar_registros():
            st.success(f"🗑️ Eliminado: {deleted.get('seller', 'N/A')}")
        return True
    return False

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
                add_record(tienda_seleccionada, vendedor_seleccionado, rango_horario, fecha.isoformat(), count, tickets, soles)
                st.rerun()
            else:
                st.error("❌ Selecciona un vendedor válido")

# BOTÓN PARA RECARGAR DATOS
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 Recargar Datos de Tiendas", use_container_width=True):
        limpiar_cache_tiendas()
        st.rerun()

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    # USAR LA TIENDA SELECCIONADA EN EL SIDEBAR
    tienda_actual = st.session_state.tienda_selector if 'tienda_selector' in st.session_state else (tiendas[0] if tiendas else "NO_HAY_TIENDAS")
    
    st.header(f"📋 HISTORIAL DE REGISTROS - {tienda_actual}")
    
    # DEPURACIÓN EXTENDIDA
    st.info(f"**Estado del sistema:** {len(st.session_state.records)} registros totales")
    
    if st.session_state.records:
        # Obtener registros de la tienda actual - CON DEPURACIÓN
        registros_tienda_actual = [r for r in st.session_state.records if r.get('tienda') == tienda_actual]
        
        # INFORMACIÓN DE DEPURACIÓN
        st.write(f"**Registros encontrados para {tienda_actual}:** {len(registros_tienda_actual)}")
        
        # Mostrar algunos registros de ejemplo para diagnóstico
        if registros_tienda_actual:
            st.write("**Ejemplo de registros (primeros 3):**")
            for i, registro in enumerate(registros_tienda_actual[:3]):
                st.write(f"{i+1}. {registro.get('seller', 'N/A')} - {registro.get('date', 'N/A')} - {registro.get('count', 'N/A')} clientes")
        else:
            st.warning(f"⚠️ No se encontraron registros para la tienda '{tienda_actual}'")
            
            # MOSTRAR REGISTROS DE OTRA TIENDA COMO EJEMPLO
            otras_tiendas = list(set([r.get('tienda', 'SIN_TIENDA') for r in st.session_state.records if r.get('tienda') != tienda_actual]))
            if otras_tiendas:
                st.write("**Registros encontrados en otras tiendas:**")
                for otra_tienda in otras_tiendas[:3]:  # Mostrar solo 3 para no saturar
                    count = len([r for r in st.session_state.records if r.get('tienda') == otra_tienda])
                    st.write(f"- **{otra_tienda}**: {count} registros")
        
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
                    st.dataframe(df_vendedor, hide_index=True, use_container_width=True)
            
            # Sección de eliminación
            st.subheader("🗑️ Eliminar Registros")
            indices_tienda = [i for i, r in enumerate(st.session_state.records) if r.get('tienda') == tienda_actual]
            
            if indices_tienda:
                def formatear_registro(index):
                    r = st.session_state.records[index]
                    return f"{r.get('seller', 'N/A')} - {r.get('date', 'N/A')} - {r.get('count', 0)} clientes"
                
                record_index = st.selectbox("Selecciona registro:", options=indices_tienda, format_func=formatear_registro)
                if st.button("Eliminar Registro Seleccionado", type="secondary"):
                    delete_record(record_index)
                    st.rerun()
    else:
        st.info("📝 No hay registros en el sistema. Agrega el primero en el sidebar.")

with col2:
    tienda_actual = st.session_state.tienda_selector if 'tienda_selector' in st.session_state else (tiendas[0] if tiendas else "NO_HAY_TIENDAS")
    
    st.header(f"📊 ESTADÍSTICAS - {tienda_actual}")
    
    # Estadísticas simples
    registros_tienda = [r for r in st.session_state.records if r.get('tienda') == tienda_actual]
    
    if registros_tienda:
        total_clientes = sum(r.get('count', 0) for r in registros_tienda)
        total_tickets = sum(r.get('tickets', 0) for r in registros_tienda)
        total_soles = sum(r.get('soles', 0) for r in registros_tienda)
        total_registros = len(registros_tienda)
        
        st.metric("👥 Total Clientes", f"{total_clientes:,}")
        st.metric("🎫 Total Tickets", total_tickets)
        st.metric("💰 Total Soles", f"S/. {total_soles:,.0f}")
        st.metric("📋 Total Registros", total_registros)
        
        if total_clientes > 0:
            porcentaje = (total_tickets / total_clientes) * 100
            st.metric("📈 Efectividad", f"{int(porcentaje)}%")
        
        # Vendedor top
        vendedor_stats = {}
        for r in registros_tienda:
            vendedor = r.get('seller', 'Desconocido')
            if vendedor in vendedor_stats:
                vendedor_stats[vendedor] += r.get('count', 0)
            else:
                vendedor_stats[vendedor] = r.get('count', 0)
        
        if vendedor_stats:
            top_vendedor = max(vendedor_stats, key=vendedor_stats.get)
            st.metric("⭐ Vendedor Top", top_vendedor)
    else:
        st.info("No hay estadísticas para esta tienda")

# Funciones auxiliares
def calcular_porcentaje(tickets, clientes):
    try:
        if clientes == 0:
            return 0
        return int((tickets / clientes) * 100)
    except:
        return 0

# HERRAMIENTAS DE DEPURACIÓN
with st.expander("🔧 HERRAMIENTAS DE DIAGNÓSTICO", expanded=False):
    st.subheader("Depuración de Datos")
    
    col_dep1, col_dep2 = st.columns(2)
    
    with col_dep1:
        if st.button("📋 Mostrar Todos los Registros (RAW)"):
            st.write("**Todos los registros en crudo:**")
            for i, record in enumerate(st.session_state.records[:10]):  # Mostrar solo primeros 10
                st.write(f"{i}. {record}")
            
            if len(st.session_state.records) > 10:
                st.write(f"... y {len(st.session_state.records) - 10} más")
    
    with col_dep2:
        if st.button("🔄 Verificar Archivo de Guardado"):
            ruta = obtener_ruta_archivo()
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    st.success(f"✅ Archivo OK: {len(datos)} registros")
                    st.write(f"**Ruta:** {ruta}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Archivo no existe")

# Footer
st.markdown("---")
st.markdown("**📱 App Web de Registro de Clientes** - *Sistema con diagnóstico*")