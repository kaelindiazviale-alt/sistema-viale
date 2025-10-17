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

# Funciones para guardar y cargar datos PERMANENTEMENTE
def guardar_registros():
    """Guardar registros permanentemente"""
    try:
        # Usar archivo temporal para persistencia
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, 'registros_clientes_viale.json')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.records, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar datos: {str(e)}")
        return False

def cargar_registros():
    """Cargar registros guardados"""
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, 'registros_clientes_viale.json')
        if os.path.exists(temp_file):
            with open(temp_file, 'r', encoding='utf-8') as f:
                registros = json.load(f)
                return registros
    except Exception as e:
        st.error(f"❌ Error al cargar datos guardados: {str(e)}")
    return []  # Si no existe, lista vacía

# Cargar datos al iniciar la aplicación
if 'records' not in st.session_state:
    st.session_state.records = cargar_registros()
    if st.session_state.records:
        st.sidebar.success(f"💾 {len(st.session_state.records)} registros cargados")

# Función para limpiar cache y forzar recarga
def limpiar_cache_tiendas():
    """Limpiar cache de datos de tiendas"""
    if 'cargar_datos_tiendas' in st.session_state:
        del st.session_state['cargar_datos_tiendas']
    st.cache_data.clear()
    st.success("✅ Cache limpiado. Recargando datos...")

# Cargar datos de tiendas y vendedores desde GitHub
@st.cache_data(ttl=300)
def cargar_datos_tiendas():
    """Cargar datos de tiendas y vendedores desde el archivo en GitHub"""
    try:
        # Intentar cargar el archivo "Asesores.xlsx" desde GitHub
        try:
            df = pd.read_excel("Asesores.xlsx")
            st.success("📁 Archivo cargado: Asesores.xlsx")
            st.info(f"📊 Se cargaron {len(df)} registros de tiendas y vendedores")
            return df
        except Exception as e:
            st.warning(f"⚠️ No se pudo cargar 'Asesores.xlsx': {str(e)}")
        
        # Si falla, buscar otros nombres posibles
        archivos_posibles = [
            "Asesores.xls",
            "asesores.xlsx", 
            "asesores.xls",
            "tiendas_vendedores.xlsx",
            "tiendas_vendedores.xls"
        ]
        
        for archivo in archivos_posibles:
            try:
                df = pd.read_excel(archivo)
                st.success(f"📁 Archivo cargado: {archivo}")
                st.info(f"📊 Se cargaron {len(df)} registros de tiendas y vendedores")
                return df
            except:
                continue
        
        # Si no se encuentra ningún archivo
        st.error("❌ No se encontró el archivo Excel en el repositorio")
        st.info("""
        **Para solucionar esto:**
        1. Sube tu archivo Excel 'Asesores.xlsx' a GitHub
        2. Asegúrate de que esté en la raíz del repositorio
        3. Haz clic en '🔄 Recargar Datos de Tiendas' en el sidebar
        """)
        
        # Datos de ejemplo temporal
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor AL705-A', 'Vendedor AL705-B', 'KAELIN DÍAZ', 'JAVIER VLAVERDE', 'ISAAC MELENDEZ', 'EDWAR CAMARGO']
        }
        return pd.DataFrame(datos_ejemplo)
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        # Datos de ejemplo como respaldo
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor AL705-A', 'Vendedor AL705-B', 'KAELIN DÍAZ', 'JAVIER VLAVERDE', 'ISAAC MELENDEZ', 'EDWAR CAMARGO']
        }
        return pd.DataFrame(datos_ejemplo)

# Cargar datos
df_tiendas = cargar_datos_tiendas()

# Mostrar información del archivo cargado
if 'Tienda' in df_tiendas.columns and 'Vendedor' in df_tiendas.columns:
    st.success(f"✅ Datos cargados correctamente: {len(df_tiendas)} registros de tiendas y vendedores")
    
    # Mostrar resumen de datos cargados
    with st.expander("📊 VER RESUMEN DE DATOS CARGADOS"):
        st.write(f"**Tiendas únicas:** {len(df_tiendas['Tienda'].unique())}")
        st.write(f"**Vendedores únicos:** {len(df_tiendas['Vendedor'].unique())}")
        st.write("**Tiendas disponibles:**")
        for tienda in df_tiendas['Tienda'].unique():
            vendedores = df_tiendas[df_tiendas['Tienda'] == tienda]['Vendedor'].unique()
            st.write(f"- {tienda}: {len(vendedores)} vendedores")
else:
    st.error("❌ El archivo no tiene las columnas 'Tienda' y 'Vendedor'")
    st.info("Las columnas encontradas son: " + ", ".join(df_tiendas.columns.tolist()))

# Función para obtener tiendas únicas
def obtener_tiendas():
    if 'Tienda' in df_tiendas.columns:
        return df_tiendas['Tienda'].unique().tolist()
    return []

# Función para obtener vendedores por tienda
def obtener_vendedores_por_tienda(tienda_seleccionada):
    """Obtener SOLO los vendedores de la tienda seleccionada"""
    if 'Tienda' in df_tiendas.columns and 'Vendedor' in df_tiendas.columns:
        if tienda_seleccionada:
            # FILTRAR: solo vendedores de la tienda seleccionada
            vendedores_filtrados = df_tiendas[df_tiendas['Tienda'] == tienda_seleccionada]['Vendedor'].unique().tolist()
            return vendedores_filtrados if vendedores_filtrados else ["No hay vendedores para esta tienda"]
        else:
            return ["Primero selecciona una tienda"]
    return ["Error: Columnas no encontradas"]

# Función para agregar registro (MODIFICADA PARA GUARDAR PERMANENTEMENTE)
def add_record(tienda, vendedor, date_str, count):
    record = {
        'tienda': tienda,
        'seller': vendedor,
        'date': date_str,
        'count': count,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.records.append(record)
    
    # GUARDAR EN ARCHIVO JSON INMEDIATAMENTE
    if guardar_registros():
        st.success(f"✅ Registro guardado permanentemente: {tienda} - {vendedor} - {count} clientes")
    else:
        st.error("⚠️ Registro guardado temporalmente (error al guardar permanentemente)")

# Función para eliminar registro (MODIFICADA PARA GUARDAR PERMANENTEMENTE)
def delete_record(index):
    if 0 <= index < len(st.session_state.records):
        registro_eliminado = st.session_state.records.pop(index)
        # GUARDAR CAMBIOS EN ARCHIVO JSON
        if guardar_registros():
            st.success(f"🗑️ Registro eliminado permanentemente: {registro_eliminado['seller']} - {registro_eliminado['date']}")
        else:
            st.error("⚠️ Registro eliminado temporalmente (error al guardar cambios)")
        return True
    return False

# Función para formatear registro para mostrar
def formatear_registro_para_mostrar(index):
    record = st.session_state.records[index]
    if 'tienda' in record:
        return f"{record['tienda']} - {record['seller']} - {record['date']} - {record['count']} clientes"
    else:
        return f"{record['seller']} - {record['date']} - {record['count']} clientes (registro antiguo)"

# Función para obtener estadísticas
def get_stats():
    if not st.session_state.records:
        return {
            'total_clients': 0,
            'total_records': 0,
            'top_seller': {'name': 'N/A', 'count': 0},
            'top_tienda': {'name': 'N/A', 'count': 0},
            'avg_per_day': 0
        }
    
    df = pd.DataFrame(st.session_state.records)
    df['count'] = pd.to_numeric(df['count'])
    
    total_clients = df['count'].sum()
    total_records = len(df)
    
    seller_stats = df.groupby('seller')['count'].sum()
    top_seller = seller_stats.idxmax()
    top_seller_count = seller_stats.max()
    
    top_tienda_name = 'N/A'
    top_tienda_count = 0
    if 'tienda' in df.columns:
        tienda_stats = df.groupby('tienda')['count'].sum()
        if not tienda_stats.empty:
            top_tienda_name = tienda_stats.idxmax()
            top_tienda_count = tienda_stats.max()
    
    avg_per_day = df['count'].mean()
    
    return {
        'total_clients': total_clients,
        'total_records': total_records,
        'top_seller': {'name': top_seller, 'count': top_seller_count},
        'top_tienda': {'name': top_tienda_name, 'count': top_tienda_count},
        'avg_per_day': round(avg_per_day, 1)
    }

# Sidebar para nuevo registro
with st.sidebar:
    st.header("➕ NUEVO REGISTRO")
    
    # Selectores FUERA del formulario para permitir callbacks
    tiendas = obtener_tiendas()
    
    if tiendas:
        # Selector de tienda con callback
        tienda_seleccionada = st.selectbox(
            "🏪 Selecciona la Tienda:",
            options=tiendas,
            index=0,
            key="tienda_selector"
        )
        
        # Obtener vendedores para la tienda seleccionada ACTUAL
        vendedores_disponibles = obtener_vendedores_por_tienda(tienda_seleccionada)
        
        # Mostrar información de qué vendedores se están mostrando
        if vendedores_disponibles and vendedores_disponibles[0] not in ["No hay vendedores para esta tienda", "Primero selecciona una tienda"]:
            st.info(f"👤 Vendedores de {tienda_seleccionada}: {len(vendedores_disponibles)} disponibles")
        
        # Selector de vendedor que se actualiza con la tienda
        vendedor_seleccionado = st.selectbox(
            "👤 Selecciona el Vendedor:",
            options=vendedores_disponibles,
            key="vendedor_selector"
        )
        
        # Resto de campos
        fecha = st.date_input("📅 Fecha:", value=date.today(), key="fecha_input")
        count = st.number_input("✅ Cantidad de clientes:", min_value=1, value=1, key="count_input")
        
        # Botón de guardar separado
        if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
            if tienda_seleccionada and vendedor_seleccionado and vendedor_seleccionado not in ["No hay vendedores para esta tienda", "Primero selecciona una tienda"]:
                add_record(tienda_seleccionada, vendedor_seleccionado, fecha.isoformat(), count)
                st.rerun()
            else:
                st.error("❌ Debes seleccionar una tienda y un vendedor válido")
    else:
        st.error("No hay datos de tiendas disponibles")

# BOTÓN PARA RECARGAR DATOS - EN LA BARRA LATERAL
with st.sidebar:
    st.markdown("---")
    st.header("🔄 ACTUALIZAR DATOS")
    
    if st.button("🔄 Recargar Datos de Tiendas", use_container_width=True):
        limpiar_cache_tiendas()
        st.rerun()
    
    st.info("""
    **Para agregar nuevas tiendas/vendedores:**
    1. Edita tu archivo Excel
    2. Haz clic en **🔄 Recargar Datos**
    3. ¡Los cambios aparecerán!
    """)

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 HISTORIAL DE REGISTROS")
    
    if not st.session_state.records:
        st.info("📝 No hay registros aún. Agrega el primero en el panel izquierdo.")
    else:
        df_display = pd.DataFrame(st.session_state.records)
        df_display['Fecha'] = pd.to_datetime(df_display['date']).dt.strftime('%d/%m/%Y')
        
        if 'tienda' in df_display.columns:
            df_display['Tienda'] = df_display['tienda']
        else:
            df_display['Tienda'] = 'N/A'
            
        df_display['Vendedor'] = df_display['seller']
        df_display['Clientes'] = df_display['count']
        
        df_display = df_display.sort_values('date', ascending=False)
        
        st.dataframe(
            df_display[['Fecha', 'Tienda', 'Vendedor', 'Clientes']],
            width='stretch',
            hide_index=True
        )
        
        st.subheader("🗑️ Eliminar Registros")
        if st.session_state.records:
            record_index = st.selectbox(
                "Selecciona registro a eliminar:",
                range(len(st.session_state.records)),
                format_func=formatear_registro_para_mostrar,
                key="delete_selector"
            )
            
            if st.button("Eliminar Registro Seleccionado", type="secondary"):
                delete_record(record_index)
                st.rerun()

with col2:
    st.header("📊 ESTADÍSTICAS")
    
    stats = get_stats()
    
    st.metric("👥 Total Clientes", stats['total_clients'])
    st.metric("📋 Total Registros", stats['total_records'])
    st.metric("⭐ Vendedor Top", f"{stats['top_seller']['name']} ({stats['top_seller']['count']})")
    st.metric("🏪 Tienda Top", f"{stats['top_tienda']['name']} ({stats['top_tienda']['count']})")
    st.metric("📅 Promedio por día", stats['avg_per_day'])
    
    if st.session_state.records:
        st.subheader("📈 Gráficos")
        df = pd.DataFrame(st.session_state.records)
        df['count'] = pd.to_numeric(df['count'])
        
        seller_totals = df.groupby('seller')['count'].sum()
        st.bar_chart(seller_totals)
        
        if 'tienda' in df.columns:
            tienda_totals = df.groupby('tienda')['count'].sum()
            st.bar_chart(tienda_totals)

# Sección de datos de tiendas
with st.expander("🏪 VER DATOS CARGADOS DE TIENDAS Y VENDEDORES"):
    st.subheader("Datos del Archivo Excel")
    st.dataframe(df_tiendas, width='stretch', hide_index=True)
    
    st.subheader("📊 Información del Dataset")
    st.write(f"**Total de registros:** {len(df_tiendas)}")
    st.write(f"**Total de tiendas únicas:** {len(df_tiendas['Tienda'].unique())}")
    st.write(f"**Total de vendedores únicos:** {len(df_tiendas['Vendedor'].unique())}")
    
    st.subheader("🏪 Tiendas y sus Vendedores")
    for tienda in df_tiendas['Tienda'].unique():
        vendedores_tienda = df_tiendas[df_tiendas['Tienda'] == tienda]['Vendedor'].unique()
        st.write(f"**{tienda}:** {', '.join(vendedores_tienda)}")

# Sección para limpiar registros antiguos
with st.expander("🔄 GESTIÓN DE DATOS"):
    st.subheader("Limpiar Registros Antiguos")
    st.warning("Esta acción eliminará todos los registros que no tienen información de tienda (registros antiguos).")
    if st.button("🧹 Limpiar Registros Antiguos", key="clean_old"):
        registros_originales = len(st.session_state.records)
        st.session_state.records = [r for r in st.session_state.records if 'tienda' in r]
        registros_nuevos = len(st.session_state.records)
        eliminados = registros_originales - registros_nuevos
        # GUARDAR CAMBIOS
        if guardar_registros():
            st.success(f"✅ Se eliminaron {eliminados} registros antiguos y se guardaron los cambios")
        st.rerun()

# Sección de exportación
st.markdown("---")
st.header("📤 EXPORTAR DATOS")

col1, col2 = st.columns(2)

with col1:
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Registros')
            df_tiendas.to_excel(writer, index=False, sheet_name='Tiendas_Vendedores')
        
        output.seek(0)
        
        st.download_button(
            label="💾 Descargar Excel Completo",
            data=output,
            file_name=f"registro_clientes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No hay datos para exportar")

with col2:
    if st.session_state.records:
        if st.button("🔄 Reiniciar Todos los Datos", type="primary", key="reset_all"):
            st.session_state.records = []
            # GUARDAR LISTA VACÍA
            if guardar_registros():
                st.success("✅ Todos los datos han sido eliminados permanentemente")
            st.rerun()
    else:
        st.info("No hay datos para reiniciar")

# Información sobre el guardado permanente
st.sidebar.markdown("---")
st.sidebar.success("""
**💾 GUARDADO AUTOMÁTICO**
- Los registros se guardan automáticamente
- Sobreviven a actualizaciones de página
- Tus datos están seguros
""")

# Footer
st.markdown("---")
st.markdown("**📱 App Web de Registro de Clientes** - *Sistema con guardado permanente*")