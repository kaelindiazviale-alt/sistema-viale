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
    # Usar el directorio actual o crear uno específico para la app
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
                # VERIFICAR que los datos cargados sean válidos
                if isinstance(registros, list):
                    st.sidebar.success(f"💾 {len(registros)} registros cargados desde archivo permanente")
                    return registros
                else:
                    st.sidebar.warning("⚠️ Archivo corrupto, iniciando con lista vacía")
                    return []
        else:
            st.sidebar.info("📝 No se encontraron datos previos. Se creará nuevo archivo.")
    except Exception as e:
        st.sidebar.error(f"❌ Error al cargar datos: {str(e)}")
    return []  # Si no existe o hay error, lista vacía

# INICIALIZACIÓN CRÍTICA - CORREGIDA
# Primero cargar los registros antes de cualquier otra operación
if 'records' not in st.session_state:
    st.session_state.records = cargar_registros()
    st.sidebar.info(f"📊 Estado inicial: {len(st.session_state.records)} registros en memoria")

# Inicializar estados de sesión para los modales
if 'mostrar_modal_descarga' not in st.session_state:
    st.session_state.mostrar_modal_descarga = False

if 'mostrar_modal_reinicio' not in st.session_state:
    st.session_state.mostrar_modal_reinicio = False

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

# Cargar datos de tiendas (esto es independiente de los registros)
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

# Función para agregar registro (MODIFICADA PARA INCLUIR NUEVOS CAMPOS)
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
    
    # GUARDAR EN ARCHIVO JSON INMEDIATAMENTE - CORREGIDO
    if guardar_registros():
        st.success(f"✅ Registro guardado permanentemente: {tienda} - {vendedor} - {rango_horario} - {count} clientes - {tickets} tickets - S/. {soles}")
    else:
        st.error("⚠️ Error al guardar permanentemente")

# Función para eliminar registro (MODIFICADA PARA GUARDAR PERMANENTEMENTE)
def delete_record(index):
    if 0 <= index < len(st.session_state.records):
        registro_eliminado = st.session_state.records.pop(index)
        # GUARDAR CAMBIOS EN ARCHIVO JSON
        if guardar_registros():
            st.success(f"🗑️ Registro eliminado permanentemente: {registro_eliminado['seller']} - {registro_eliminado['date']}")
        else:
            st.error("⚠️ Error al guardar cambios después de eliminar")
        return True
    return False

# Función para formatear registro para mostrar
def formatear_registro_para_mostrar(index):
    record = st.session_state.records[index]
    if 'tienda' in record:
        tickets = record.get('tickets', 'N/A')
        soles = record.get('soles', 'N/A')
        rango_horario = record.get('rango_horario', 'N/A')
        return f"{record['tienda']} - {record['seller']} - {rango_horario} - {record['date']} - {record['count']} clientes - {tickets} tickets - S/. {soles}"
    else:
        return f"{record['seller']} - {record['date']} - {record['count']} clientes (registro antiguo)"

# Función para calcular porcentaje (sin decimales) con manejo de errores
def calcular_porcentaje(tickets, clientes):
    try:
        if clientes == 0:
            return 0
        porcentaje = (tickets / clientes) * 100
        return int(round(porcentaje))  # Sin decimales
    except (TypeError, ZeroDivisionError):
        return 0

# Función para obtener valores seguros de los registros
def obtener_valor_seguro(record, campo, default=0):
    """Obtener valor de un campo de manera segura"""
    return record.get(campo, default)

# Función para obtener estadísticas por tienda
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
            'porcentaje_general': 0
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
            'porcentaje_general': 0
        }
    
    # Usar valores por defecto para registros antiguos
    total_clients = 0
    total_tickets = 0
    total_soles = 0
    
    for record in registros_tienda:
        total_clients += obtener_valor_seguro(record, 'count', 0)
        total_tickets += obtener_valor_seguro(record, 'tickets', 0)
        total_soles += obtener_valor_seguro(record, 'soles', 0)
    
    total_records = len(registros_tienda)
    
    # Calcular top seller de la tienda
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
    
    return {
        'total_clients': total_clients,
        'total_records': total_records,
        'total_tickets': total_tickets,
        'total_soles': total_soles,
        'top_seller': {'name': top_seller, 'count': top_seller_count},
        'avg_per_day': round(avg_per_day, 1),
        'avg_tickets_per_day': round(avg_tickets_per_day, 1),
        'avg_soles_per_day': round(avg_soles_per_day, 1),
        'porcentaje_general': porcentaje_general
    }

# Sidebar para nuevo registro
with st.sidebar:
    st.header("➕ NUEVO REGISTRO")
    
    # Selectores FUERA del formulario para permitir callbacks
    tiendas = obtener_tiendas()
    
    if tiendas:
        # Selector de tienda con callback - CORREGIDO: valor por defecto seguro
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
        
        # Selector de rango horario
        rango_horario_seleccionado = st.selectbox(
            "⏰ Selecciona rango de horario:",
            options=RANGOS_HORARIO,
            key="rango_horario_selector"
        )
        
        # Resto de campos
        fecha = st.date_input("📅 Fecha:", value=date.today(), key="fecha_input")
        count = st.number_input("✅ Cantidad de clientes:", min_value=1, value=1, key="count_input")
        tickets = st.number_input("🎫 Cantidad de Tickets:", min_value=0, value=0, key="tickets_input")
        soles = st.number_input("💰 Cantidad Soles (S/.):", min_value=0.0, value=0.0, step=0.1, format="%.2f", key="soles_input")
        
        # Botón de guardar separado
        if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
            if tienda_seleccionada and vendedor_seleccionado and vendedor_seleccionado not in ["No hay vendedores para esta tienda", "Primero selecciona una tienda"]:
                add_record(tienda_seleccionada, vendedor_seleccionado, rango_horario_seleccionado, fecha.isoformat(), count, tickets, soles)
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
    
    # INFORMACIÓN CRÍTICA SOBRE EL ESTADO DE LOS DATOS
    st.markdown("---")
    st.header("💾 ESTADO DE DATOS")
    st.info(f"**Registros en memoria:** {len(st.session_state.records)}")
    st.info(f"**Archivo de guardado:** {obtener_ruta_archivo()}")
    
    # Botón para verificar el guardado
    if st.button("🔍 Verificar Estado de Guardado", use_container_width=True):
        ruta_archivo = obtener_ruta_archivo()
        if os.path.exists(ruta_archivo):
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    datos_guardados = json.load(f)
                st.success(f"✅ Archivo verificado: {len(datos_guardados)} registros guardados")
            except Exception as e:
                st.error(f"❌ Error al verificar archivo: {e}")
        else:
            st.warning("⚠️ Archivo de guardado no existe aún")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    # VERIFICACIÓN CRÍTICA: Asegurar que tienda_seleccionada existe
    if 'tienda_selector' in st.session_state:
        tienda_actual = st.session_state.tienda_selector
    else:
        tiendas = obtener_tiendas()
        tienda_actual = tiendas[0] if tiendas else "No hay tiendas"
    
    st.header(f"📋 HISTORIAL DE REGISTROS - {tienda_actual}")
    
    # MOSTRAR INFORMACIÓN DE ESTADO DE DATOS
    st.info(f"**Estado actual:** {len(st.session_state.records)} registros cargados en el sistema")
    
    if not st.session_state.records:
        st.info("📝 No hay registros aún. Agrega el primero en el panel izquierdo.")
    else:
        # Filtrar registros por la tienda seleccionada en el sidebar
        registros_filtrados = [r for r in st.session_state.records if r.get('tienda') == tienda_actual]
        
        if not registros_filtrados:
            st.info(f"📝 No hay registros para la tienda {tienda_actual}.")
            st.info("💡 **Sugerencia:** Los registros pueden estar guardados para otras tiendas. Revisa el selector de tienda en el sidebar.")
        else:
            # Obtener vendedores únicos de la tienda seleccionada
            vendedores_tienda = list(set([r['seller'] for r in registros_filtrados]))
            
            # Mostrar cuadros separados para cada vendedor
            for vendedor in vendedores_tienda:
                # Filtrar registros del vendedor actual
                registros_vendedor = [r for r in registros_filtrados if r['seller'] == vendedor]
                
                # Crear DataFrame para este vendedor con manejo seguro de campos
                datos_vendedor = []
                for registro in registros_vendedor:
                    fecha_str = pd.to_datetime(registro['date']).strftime('%d/%m/%Y')
                    clientes = obtener_valor_seguro(registro, 'count', 0)
                    tickets = obtener_valor_seguro(registro, 'tickets', 0)
                    soles = obtener_valor_seguro(registro, 'soles', 0)
                    rango_horario = registro.get('rango_horario', 'N/A')
                    porcentaje = calcular_porcentaje(tickets, clientes)
                    
                    datos_vendedor.append({
                        'Fecha': fecha_str,
                        'Tienda': registro.get('tienda', 'N/A'),
                        'Vendedor': registro.get('seller', 'N/A'),
                        'Rango Horario': rango_horario,
                        'Clientes': clientes,
                        'Tickets': tickets,
                        'Soles (S/.)': soles,
                        'Porcentaje': f"{porcentaje}%"
                    })
                
                df_vendedor = pd.DataFrame(datos_vendedor)
                df_vendedor = df_vendedor.sort_values('Fecha', ascending=False)
                
                # Mostrar cuadro para este vendedor
                with st.expander(f"👤 {vendedor} - {len(registros_vendedor)} registros", expanded=True):
                    # Mostrar mini-estadísticas del vendedor en la parte superior
                    total_clientes_vendedor = sum([obtener_valor_seguro(r, 'count', 0) for r in registros_vendedor])
                    total_tickets_vendedor = sum([obtener_valor_seguro(r, 'tickets', 0) for r in registros_vendedor])
                    total_soles_vendedor = sum([obtener_valor_seguro(r, 'soles', 0) for r in registros_vendedor])
                    porcentaje_promedio = calcular_porcentaje(total_tickets_vendedor, total_clientes_vendedor)
                    
                    # Mini métricas en columnas
                    col_mini1, col_mini2, col_mini3, col_mini4 = st.columns(4)
                    with col_mini1:
                        st.metric("👥 Total Clientes", total_clientes_vendedor)
                    with col_mini2:
                        st.metric("🎫 Total Tickets", total_tickets_vendedor)
                    with col_mini3:
                        st.metric("💰 Total Soles", f"S/. {total_soles_vendedor:,.0f}")
                    with col_mini4:
                        st.metric("📈 Efectividad", f"{porcentaje_promedio}%")
                    
                    # Dataframe
                    st.dataframe(
                        df_vendedor,
                        width='stretch',
                        hide_index=True,
                        use_container_width=True
                    )
            
            # Sección de eliminación
            st.markdown("---")
            st.subheader("🗑️ Gestión de Registros")
            # Filtrar índices para mostrar solo los de la tienda seleccionada
            indices_tienda = [i for i, r in enumerate(st.session_state.records) if r.get('tienda') == tienda_actual]
            
            if indices_tienda:
                col_elim1, col_elim2 = st.columns([3, 1])
                with col_elim1:
                    record_index_tienda = st.selectbox(
                        "Selecciona registro a eliminar:",
                        options=indices_tienda,
                        format_func=formatear_registro_para_mostrar,
                        key="delete_selector_tienda"
                    )
                with col_elim2:
                    st.write("")  # Espacio vertical
                    st.write("")
                    if st.button("🚫 Eliminar Registro", type="secondary", use_container_width=True):
                        if delete_record(record_index_tienda):
                            st.rerun()
            else:
                st.info("No hay registros para eliminar en esta tienda")

with col2:
    # VERIFICACIÓN CRÍTICA: Usar la misma tienda que en col1
    if 'tienda_selector' in st.session_state:
        tienda_actual = st.session_state.tienda_selector
    else:
        tiendas = obtener_tiendas()
        tienda_actual = tiendas[0] if tiendas else "No hay tiendas"
    
    st.header(f"📊 ESTADÍSTICAS - {tienda_actual}")
    
    # Usar estadísticas filtradas por tienda
    stats_tienda = get_stats_por_tienda(tienda_actual)
    
    # Métricas principales
    st.subheader("📈 Métricas Principales")
    
    col_met1, col_met2 = st.columns(2)
    with col_met1:
        st.metric("👥 Total Clientes", f"{stats_tienda['total_clients']:,}")
        st.metric("🎫 Total Tickets", f"{stats_tienda['total_tickets']:,}")
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
        # Calcular ticket promedio
        ticket_promedio = stats_tienda['total_soles'] / stats_tienda['total_tickets'] if stats_tienda['total_tickets'] > 0 else 0
        st.metric("🎟️ Ticket Promedio", f"S/. {ticket_promedio:,.1f}")

# Información sobre el guardado permanente (MEJORADA)
st.sidebar.markdown("---")
st.sidebar.success("""
**💾 SISTEMA DE GUARDADO**
- Guardado automático permanente
- Datos seguros en archivo local
- Sobrevive a cierres del navegador
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <strong>📱 App Web de Registro de Clientes</strong> - <em>Sistema con guardado permanente</em><br>
    <small>Última actualización: {}</small>
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)