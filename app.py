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
                st.sidebar.info(f"📁 Datos cargados desde: {ruta_archivo}")
                return registros
        else:
            st.sidebar.info("📝 No se encontraron datos previos. Se creará nuevo archivo.")
    except Exception as e:
        st.error(f"❌ Error al cargar datos guardados: {str(e)}")
    return []  # Si no existe, lista vacía

# Cargar datos al iniciar la aplicación
if 'records' not in st.session_state:
    st.session_state.records = cargar_registros()
    if st.session_state.records:
        st.sidebar.success(f"💾 {len(st.session_state.records)} registros cargados correctamente")
    else:
        st.sidebar.info("📝 Iniciando con 0 registros")

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

# Función para obtener estadísticas por tienda (MEJORADA VISUALMENTE)
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

# Función para obtener estadísticas generales (PARA EXPORTACIÓN)
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
            'avg_soles_per_day': 0
        }
    
    # Usar valores por defecto para registros antiguos
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
    
    return {
        'total_clients': total_clients,
        'total_records': total_records,
        'total_tickets': total_tickets,
        'total_soles': total_soles,
        'top_seller': {'name': top_seller, 'count': top_seller_count},
        'top_tienda': {'name': top_tienda_name, 'count': top_tienda_count},
        'avg_per_day': round(avg_per_day, 1),
        'avg_tickets_per_day': round(avg_tickets_per_day, 1),
        'avg_soles_per_day': round(avg_soles_per_day, 1)
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
    
    st.info("""
    **Para agregar nuevas tiendas/vendedores:**
    1. Edita tu archivo Excel
    2. Haz clic en **🔄 Recargar Datos**
    3. ¡Los cambios aparecerán!
    """)

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"📋 HISTORIAL DE REGISTROS - {tienda_seleccionada}")
    
    if not st.session_state.records:
        st.info("📝 No hay registros aún. Agrega el primero en el panel izquierdo.")
    else:
        # Filtrar registros por la tienda seleccionada en el sidebar
        registros_filtrados = [r for r in st.session_state.records if r.get('tienda') == tienda_seleccionada]
        
        if not registros_filtrados:
            st.info(f"📝 No hay registros para la tienda {tienda_seleccionada}.")
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
                
                # MEJORA VISUAL: Estilo mejorado para los cuadros
                with st.expander(f"👤 {vendedor} - {len(registros_vendedor)} registros", expanded=True):
                    # Mostrar mini-estadísticas del vendedor en la parte superior
                    total_clientes_vendedor = sum([obtener_valor_seguro(r, 'count', 0) for r in registros_vendedor])
                    total_tickets_vendedor = sum([obtener_valor_seguro(r, 'tickets', 0) for r in registros_vendedor])
                    total_soles_vendedor = sum([obtener_valor_seguro(r, 'soles', 0) for r in registros_vendedor])
                    porcentaje_promedio = calcular_porcentaje(total_tickets_vendedor, total_clientes_vendedor)
                    
                    # Mini métricas en columnas
                    col_mini1, col_mini2, col_mini3, col_mini4 = st.columns(4)
                    with col_mini1:
                        st.metric("👥 Total Clientes", total_clientes_vendedor, 
                                 delta=f"{len(registros_vendedor)} días", delta_color="off")
                    with col_mini2:
                        st.metric("🎫 Total Tickets", total_tickets_vendedor)
                    with col_mini3:
                        st.metric("💰 Total Soles", f"S/. {total_soles_vendedor:,.0f}")
                    with col_mini4:
                        st.metric("📈 Efectividad", f"{porcentaje_promedio}%")
                    
                    # Dataframe con estilo mejorado
                    st.dataframe(
                        df_vendedor,
                        width='stretch',
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Clientes": st.column_config.NumberColumn(format="%d"),
                            "Tickets": st.column_config.NumberColumn(format="%d"),
                            "Soles (S/.)": st.column_config.NumberColumn(format="S/. %.2f"),
                            "Porcentaje": st.column_config.TextColumn()
                        }
                    )
            
            # MEJORA VISUAL: Sección de eliminación más organizada
            st.markdown("---")
            st.subheader("🗑️ Gestión de Registros")
            # Filtrar índices para mostrar solo los de la tienda seleccionada
            indices_tienda = [i for i, r in enumerate(st.session_state.records) if r.get('tienda') == tienda_seleccionada]
            
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
    # MEJORA VISUAL: Estadísticas con mejor presentación
    st.header(f"📊 ESTADÍSTICAS - {tienda_seleccionada}")
    
    # Usar estadísticas filtradas por tienda
    stats_tienda = get_stats_por_tienda(tienda_seleccionada)
    
    # Dividir las métricas en grupos lógicos
    st.subheader("📈 Métricas Principales")
    
    # Métricas principales en 2 columnas
    col_met1, col_met2 = st.columns(2)
    with col_met1:
        st.metric(
            "👥 Total Clientes", 
            f"{stats_tienda['total_clients']:,}",
            help="Número total de clientes atendidos"
        )
        st.metric(
            "🎫 Total Tickets", 
            f"{stats_tienda['total_tickets']:,}",
            delta=f"{stats_tienda['porcentaje_general']}% efectividad",
            delta_color="normal"
        )
        st.metric(
            "💰 Total Recaudado", 
            f"S/. {stats_tienda['total_soles']:,.0f}",
            help="Total en soles generado"
        )
    
    with col_met2:
        st.metric(
            "📋 Total Registros", 
            stats_tienda['total_records'],
            help="Número total de registros"
        )
        st.metric(
            "📅 Promedio Clientes/día", 
            stats_tienda['avg_per_day'],
            help="Promedio de clientes por día"
        )
        st.metric(
            "💵 Promedio Soles/día", 
            f"S/. {stats_tienda['avg_soles_per_day']:,.1f}",
            help="Promedio de soles por día"
        )
    
    st.markdown("---")
    st.subheader("🏆 Desempeño")
    
    # Métricas de desempeño
    col_perf1, col_perf2 = st.columns(2)
    with col_perf1:
        st.metric(
            "⭐ Vendedor Top", 
            stats_tienda['top_seller']['name'],
            delta=f"{stats_tienda['top_seller']['count']} clientes",
            delta_color="off"
        )
        st.metric(
            "📊 Promedio Tickets/día", 
            stats_tienda['avg_tickets_per_day'],
            help="Promedio de tickets por día"
        )
    
    with col_perf2:
        st.metric(
            "📈 Efectividad General", 
            f"{stats_tienda['porcentaje_general']}%",
            help="Porcentaje de conversión clientes a tickets"
        )
        # Calcular ticket promedio
        ticket_promedio = stats_tienda['total_soles'] / stats_tienda['total_tickets'] if stats_tienda['total_tickets'] > 0 else 0
        st.metric(
            "🎟️ Ticket Promedio", 
            f"S/. {ticket_promedio:,.1f}",
            help="Valor promedio por ticket"
        )
    
    # Gráficos solo si hay datos
    if st.session_state.records:
        st.markdown("---")
        st.subheader("📊 Análisis Visual")
        
        # Crear datos seguros para gráficos - SOLO DE LA TIENDA SELECCIONADA
        datos_grafico = []
        for record in st.session_state.records:
            if record.get('tienda') == tienda_seleccionada:
                datos_grafico.append({
                    'seller': record.get('seller', 'Desconocido'),
                    'count': obtener_valor_seguro(record, 'count', 0),
                    'tickets': obtener_valor_seguro(record, 'tickets', 0),
                    'soles': obtener_valor_seguro(record, 'soles', 0),
                    'tienda': record.get('tienda', 'Desconocido')
                })
        
        df_grafico = pd.DataFrame(datos_grafico)
        
        if not df_grafico.empty:
            # Gráfico de desempeño por vendedor
            st.write("**👥 Desempeño por Vendedor (Clientes Atendidos)**")
            seller_totals = df_grafico.groupby('seller')['count'].sum()
            st.bar_chart(seller_totals, use_container_width=True)
            
            # Gráfico de tickets por vendedor
            st.write("**🎫 Tickets por Vendedor**")
            seller_tickets = df_grafico.groupby('seller')['tickets'].sum()
            st.bar_chart(seller_tickets, use_container_width=True)

# Sección de datos de tiendas (MEJORADA VISUALMENTE)
with st.expander("🏪 INFORMACIÓN DE TIENDAS Y VENDEDORES", expanded=False):
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.subheader("📊 Resumen General")
        st.write(f"**Total de tiendas únicas:** {len(df_tiendas['Tienda'].unique())}")
        st.write(f"**Total de vendedores únicos:** {len(df_tiendas['Vendedor'].unique())}")
        st.write(f"**Total de registros en base:** {len(df_tiendas)}")
        
        st.subheader("🏪 Distribución por Tienda")
        for tienda in df_tiendas['Tienda'].unique():
            vendedores_tienda = df_tiendas[df_tiendas['Tienda'] == tienda]['Vendedor'].unique()
            st.write(f"**{tienda}:** {len(vendedores_tienda)} vendedores")
    
    with col_info2:
        st.subheader("📋 Datos Completos")
        st.dataframe(
            df_tiendas, 
            width='stretch', 
            hide_index=True,
            use_container_width=True
        )

# Sección para limpiar registros antiguos (MEJORADA)
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
            # GUARDAR CAMBIOS
            if guardar_registros():
                st.success(f"✅ Se eliminaron {eliminados} registros antiguos")
            st.rerun()
    
    with col_mant2:
        st.write("**Información del Sistema**")
        st.info(f"**Registros actuales:** {len(st.session_state.records)}")
        st.info(f"**Tiendas activas:** {len(obtener_tiendas())}")
        st.info(f"**Archivo de datos:** {obtener_ruta_archivo()}")

# Sección de exportación (MEJORADA VISUALMENTE)
st.markdown("---")
st.header("📤 EXPORTACIÓN DE DATOS")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if st.session_state.records:
        # Crear DataFrame seguro para exportación - TODOS LOS REGISTROS
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
                'Porcentaje General': f"{calcular_porcentaje(stats_general['total_tickets'], stats_general['total_clients'])}%"
            }])
            stats_df.to_excel(writer, index=False, sheet_name='Estadisticas_Generales')
            
            # Hoja 3: Datos de tiendas y vendedores
            df_tiendas.to_excel(writer, index=False, sheet_name='Tiendas_Vendedores')
        
        output.seek(0)
        
        # Botón de descarga con mejor presentación
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
        
        # Resumen de exportación
        st.info(f"**El reporte incluirá:**")
        st.write(f"• {len(st.session_state.records)} registros de todas las tiendas")
        st.write(f"• Estadísticas generales y por tienda")
        st.write(f"• Datos de {len(df_tiendas)} tiendas y vendedores")
        
    else:
        st.warning("No hay datos para exportar")

with col_exp2:
    if st.session_state.records:
        # Botón de reinicio con mejor presentación
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
                        st.session_state.records = []
                        # GUARDAR LISTA VACÍA
                        if guardar_registros():
                            st.success("✅ Todos los datos han sido eliminados permanentemente")
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

# Información sobre el guardado permanente (MEJORADA)
st.sidebar.markdown("---")
st.sidebar.success("""
**💾 SISTEMA DE GUARDADO**
- Guardado automático permanente
- Datos seguros en archivo local
- Sobrevive a cierres del navegador
""")

# Footer mejorado
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <strong>📱 App Web de Registro de Clientes</strong> - <em>Sistema con guardado permanente</em><br>
    <small>Última actualización: {}</small>
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)