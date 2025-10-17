import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import os

# Configurar la página
st.set_page_config(
    page_title="Registro de Clientes",
    page_icon="🏪",
    layout="wide"
)

# Título principal
st.title("🏪 REGISTRO DE CLIENTES ATENDIDOS")
st.markdown("---")

# Ruta específica del archivo Excel
RUTA_ARCHIVO = r"D:\Users\usuario\Desktop\VIALE\APP\Asesores"

# Función para limpiar cache y forzar recarga
def limpiar_cache_tiendas():
    """Limpiar cache de datos de tiendas"""
    if 'cargar_datos_tiendas' in st.session_state:
        del st.session_state['cargar_datos_tiendas']
    st.cache_data.clear()

# Cargar datos de tiendas y vendedores
@st.cache_data(ttl=300)  # Cache por 5 minutos en lugar de permanente
def cargar_datos_tiendas():
    """Cargar datos de tiendas y vendedores desde la ruta específica"""
    try:
        # Buscar archivos Excel en la ruta especificada
        if os.path.exists(RUTA_ARCHIVO):
            # Si es un directorio, buscar archivos Excel dentro
            if os.path.isdir(RUTA_ARCHIVO):
                archivos = os.listdir(RUTA_ARCHIVO)
                archivos_excel = [f for f in archivos if f.endswith(('.xlsx', '.xls'))]
                
                if archivos_excel:
                    # Tomar el primer archivo Excel encontrado
                    archivo_path = os.path.join(RUTA_ARCHIVO, archivos_excel[0])
                    st.success(f"📁 Archivo cargado: {archivos_excel[0]}")
                    df = pd.read_excel(archivo_path)
                    st.info(f"📊 Se cargaron {len(df)} registros de tiendas y vendedores")
                    return df
                else:
                    st.error("❌ No se encontraron archivos Excel en la ruta especificada")
            else:
                # Si es un archivo directo
                return pd.read_excel(RUTA_ARCHIVO)
        
        # Si no se encuentra, buscar en ubicaciones alternativas
        st.warning("⚠️ No se encontró el archivo en la ruta especificada. Buscando alternativas...")
        
        # Buscar en otras ubicaciones posibles
        ubicaciones_alternativas = [
            r"D:\Users\usuario\Desktop\VIALE\APP\Asesores\*.xlsx",
            r"D:\Users\usuario\Desktop\VIALE\APP\Asesores\*.xls",
            "tiendas_vendedores.xlsx",
            "tiendas_vendedores.csv"
        ]
        
        for ubicacion in ubicaciones_alternativas:
            if "*" in ubicacion:
                # Buscar archivos con patrón
                import glob
                archivos = glob.glob(ubicacion)
                if archivos:
                    archivo_path = archivos[0]
                    st.success(f"📁 Archivo encontrado: {os.path.basename(archivo_path)}")
                    return pd.read_excel(archivo_path)
            elif os.path.exists(ubicacion):
                st.success(f"📁 Archivo encontrado: {os.path.basename(ubicacion)}")
                if ubicacion.endswith('.csv'):
                    return pd.read_csv(ubicacion)
                else:
                    return pd.read_excel(ubicacion)
        
        # Si no hay archivo, crear datos de ejemplo
        st.info("📋 No se encontró archivo de tiendas. Usando datos de ejemplo.")
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor AL705-A', 'Vendedor AL705-B', 'JAVIER VLAVERDE', 'Vendedor AL418-B', 'Vendedor AL418-C', 'Vendedor AL418-D']
        }
        return pd.DataFrame(datos_ejemplo)
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        # Datos de ejemplo como respaldo
        datos_ejemplo = {
            'Tienda': ['AL705', 'AL705', 'AL418', 'AL418'],
            'Vendedor': ['Vendedor AL705-A', 'Vendedor AL705-B', 'JAVIER VLAVERDE', 'Vendedor AL418-B']
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

# Inicializar datos en session state
if 'records' not in st.session_state:
    st.session_state.records = []

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

# Función para agregar registro
def add_record(tienda, vendedor, date_str, count):
    record = {
        'tienda': tienda,
        'seller': vendedor,
        'date': date_str,
        'count': count,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.records.append(record)
    st.success(f"✅ Registro guardado: {tienda} - {vendedor} - {count} clientes")

# Función para eliminar registro
def delete_record(index):
    if 0 <= index < len(st.session_state.records):
        st.session_state.records.pop(index)
        st.success("🗑️ Registro eliminado")
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
        st.success("✅ Cache limpiado. Recargando aplicación...")
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
        st.success(f"✅ Se eliminaron {eliminados} registros antiguos")
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
            st.success("Todos los datos han sido eliminados")
            st.rerun()
    else:
        st.info("No hay datos para reiniciar")

# Footer
st.markdown("---")
st.markdown("**📱 App Web de Registro de Clientes** - *Sistema multi-tienda con vendedores*")