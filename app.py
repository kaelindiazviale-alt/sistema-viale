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

# ARCHIVO PERSISTENTE - SOLUCIÓN DEFINITIVA
def obtener_ruta_archivo():
    """Obtener ruta de archivo persistente"""
    directorio_datos = "./datos_app"
    if not os.path.exists(directorio_datos):
        os.makedirs(directorio_datos)
    return os.path.join(directorio_datos, 'registros_clientes_viale.json')

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
    """Cargar registros guardados - SIEMPRE desde archivo"""
    try:
        ruta_archivo = obtener_ruta_archivo()
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                registros = json.load(f)
                if isinstance(registros, list):
                    return registros
                else:
                    return []
        return []
    except Exception as e:
        st.error(f"❌ Error al cargar: {str(e)}")
        return []

# FUNCIÓN CRÍTICA: Obtener registros SIEMPRE actualizados
def obtener_registros_actualizados():
    """Obtener registros siempre frescos desde el archivo"""
    return cargar_registros()

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

# INICIALIZACIÓN - SOLUCIÓN PARA MÚLTIPLES PESTAÑAS
if 'records' not in st.session_state:
    # SIEMPRE cargar desde archivo al iniciar
    st.session_state.records = cargar_registros()
    st.sidebar.success(f"💾 {len(st.session_state.records)} registros cargados")

# Función para ACTUALIZAR session_state desde archivo
def actualizar_desde_archivo():
    """Forzar actualización desde archivo"""
    registros_actuales = cargar_registros()
    st.session_state.records = registros_actuales
    return registros_actuales

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
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor A', 'Vendedor B', 'KAELIN DÍAZ', 'JAVIER VLAVERDE']
        }
        return pd.DataFrame(datos_ejemplo)

# Cargar datos de tiendas
df_tiendas = cargar_datos_tiendas()

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

# FUNCIÓN MODIFICADA: Guardar y actualizar inmediatamente
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
    
    # CARGAR REGISTROS ACTUALES desde archivo (no confiar en session_state)
    registros_actuales = cargar_registros()
    registros_actuales.append(record)
    
    # Guardar en archivo
    try:
        ruta_archivo = obtener_ruta_archivo()
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(registros_actuales, f, ensure_ascii=False, indent=2)
        
        # ACTUALIZAR session_state
        st.session_state.records = registros_actuales
        st.success(f"✅ Guardado: {tienda} - {vendedor}")
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {str(e)}")
        return False

# FUNCIÓN MODIFICADA: Eliminar y actualizar inmediatamente
def delete_record(index):
    # CARGAR REGISTROS ACTUALES desde archivo
    registros_actuales = cargar_registros()
    
    if 0 <= index < len(registros_actuales):
        deleted = registros_actuales.pop(index)
        
        # Guardar en archivo
        try:
            ruta_archivo = obtener_ruta_archivo()
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(registros_actuales, f, ensure_ascii=False, indent=2)
            
            # ACTUALIZAR session_state
            st.session_state.records = registros_actuales
            st.success(f"🗑️ Eliminado: {deleted.get('seller', 'N/A')}")
            return True
        except Exception as e:
            st.error(f"❌ Error al guardar: {str(e)}")
            return False
    return False

def formatear_registro_para_mostrar(index):
    record = st.session_state.records[index]
    return f"{record.get('seller', 'N/A')} - {record.get('date', 'N/A')} - {record.get('count', 0)} clientes"

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

    # BOTÓN CRÍTICO: Actualizar desde archivo
    st.markdown("---")
    st.header("🔄 SINCRONIZACIÓN")
    
    if st.button("🔄 Actualizar desde Archivo", use_container_width=True):
        registros_actualizados = actualizar_desde_archivo()
        st.success(f"✅ Sincronizado: {len(registros_actualizados)} registros")
        st.rerun()
    
    # Información de estado
    st.info(f"**Registros en memoria:** {len(st.session_state.records)}")
    
    # Verificar archivo
    ruta_archivo = obtener_ruta_archivo()
    if os.path.exists(ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_archivo = json.load(f)
            st.info(f"**Registros en archivo:** {len(datos_archivo)}")
            
            # Mostrar diferencia si existe
            if len(datos_archivo) != len(st.session_state.records):
                st.warning(f"⚠️ Diferencia: {len(datos_archivo)} en archivo")
        except:
            st.error("❌ Error leyendo archivo")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    # USAR LA TIENDA SELECCIONADA EN EL SIDEBAR
    tienda_actual = st.session_state.tienda_selector if 'tienda_selector' in st.session_state else (tiendas[0] if tiendas else "NO_HAY_TIENDAS")
    
    st.header(f"📋 HISTORIAL DE REGISTROS - {tienda_actual}")
    
    # MOSTRAR INFORMACIÓN DE SINCRONIZACIÓN
    st.info(f"**Registros cargados:** {len(st.session_state.records)}")
    
    # BOTÓN PARA FORZAR ACTUALIZACIÓN
    if st.button("🔄 Actualizar Vista", key="actualizar_vista"):
        actualizar_desde_archivo()
        st.success("✅ Vista actualizada")
        st.rerun()
    
    if st.session_state.records:
        # Obtener registros de la tienda actual
        registros_tienda_actual = [r for r in st.session_state.records if r.get('tienda') == tienda_actual]
        
        st.write(f"**Registros para {tienda_actual}:** {len(registros_tienda_actual)}")
        
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
                record_index = st.selectbox("Selecciona registro:", options=indices_tienda, format_func=formatear_registro_para_mostrar)
                if st.button("Eliminar Registro Seleccionado", type="secondary"):
                    delete_record(record_index)
                    st.rerun()
        else:
            st.warning(f"⚠️ No hay registros para la tienda '{tienda_actual}'")
            
            # Mostrar otras tiendas disponibles
            otras_tiendas = list(set([r.get('tienda', 'SIN_TIENDA') for r in st.session_state.records]))
            if otras_tiendas:
                st.write("**Registros en otras tiendas:**")
                for otra_tienda in otras_tiendas[:5]:
                    count = len([r for r in st.session_state.records if r.get('tienda') == otra_tienda])
                    st.write(f"- **{otra_tienda}**: {count} registros")
    else:
        st.info("📝 No hay registros en el sistema. Agrega el primero en el sidebar.")

with col2:
    tienda_actual = st.session_state.tienda_selector if 'tienda_selector' in st.session_state else (tiendas[0] if tiendas else "NO_HAY_TIENDAS")
    
    st.header(f"📊 ESTADÍSTICAS - {tienda_actual}")
    
    # Estadísticas
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

# Footer
st.markdown("---")
st.markdown("**📱 App Web de Registro de Clientes** - *Sistema multi-pestaña*")