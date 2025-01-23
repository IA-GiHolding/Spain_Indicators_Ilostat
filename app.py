import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Ajustar el ancho de la página a un 1/3
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 33%;
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# URLs de la API para obtener los datos de fuerza laboral, desocupación y población
url_indicadoresilostat = "https://rplumber.ilo.org/data/indicator/?id=EAP_TEAP_SEX_AGE_NB_Q&time=2020,2021,2022,2023,2024"
url_desocupacion = "https://rplumber.ilo.org/data/indicator/?id=UNE_TUNE_SEX_AGE_NB_Q&time=2020,2021,2022,2023,2024"
url_poblacion = "https://rplumber.ilo.org/data/indicator/?id=POP_XWAP_SEX_AGE_NB_Q&time=2020,2021,2022,2023,2024"

# Función para cargar y procesar los datos
def cargar_datos(url, ref_area='ESP', classif='AGE_AGGREGATE_TOTAL'):
    try:
        # Leer los datos CSV desde la URL
        data = pd.read_csv(url)

        # Filtrar por España (ref_area) y 'AGE_AGGREGATE_TOTAL' en classif1
        data_filtrada = data[
            (data['ref_area'] == ref_area) & 
            (data['classif1'].str.contains(classif, case=False, na=False)) & 
            (data['sex'] != 'SEX_T')  # Excluir SEX_T
        ]

        return data_filtrada

    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# Cargar los datos de Fuerza Laboral, Desocupación y Población
fuerza_laboral = cargar_datos(url_indicadoresilostat)
desocupacion = cargar_datos(url_desocupacion)
poblacion = cargar_datos(url_poblacion)

# Segmentador de años - Obtener los últimos datos de cada año
years = sorted(fuerza_laboral['time'].unique(), reverse=True)

# Mostrar el título principal
st.title("Indicadores Ilostat")

# Mostrar segmentador de años
selected_year = st.selectbox("Selecciona el Año", options=years, index=0)

# Filtrar los datos por el año seleccionado
fuerza_laboral_year = fuerza_laboral[fuerza_laboral['time'] == selected_year]
desocupacion_year = desocupacion[desocupacion['time'] == selected_year]
poblacion_year = poblacion[poblacion['time'] == selected_year]

# Obtener los valores para cada categoría
fuerza_laboral_hombres = fuerza_laboral_year[fuerza_laboral_year['sex'] == 'SEX_M']['obs_value'].sum()
fuerza_laboral_mujeres = fuerza_laboral_year[fuerza_laboral_year['sex'] == 'SEX_F']['obs_value'].sum()

desocupacion_hombres = desocupacion_year[desocupacion_year['sex'] == 'SEX_M']['obs_value'].sum()
desocupacion_mujeres = desocupacion_year[desocupacion_year['sex'] == 'SEX_F']['obs_value'].sum()

poblacion_hombres = poblacion_year[poblacion_year['sex'] == 'SEX_M']['obs_value'].sum()
poblacion_mujeres = poblacion_year[poblacion_year['sex'] == 'SEX_F']['obs_value'].sum()

# Crear gráfico de tarta (pie chart) de distribución por hombres y mujeres
def pie_chart(hombres, mujeres, title):
    labels = ['Hombres', 'Mujeres']
    values = [hombres, mujeres]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(
        title=title,
        width=400,
        height=400,
        showlegend=False
    )
    return fig

# Crear gráfico de barras para los tres conceptos
def bar_chart(hombres, mujeres, labels):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=hombres,
        name='Hombres',
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        x=labels,
        y=mujeres,
        name='Mujeres',
        marker_color='mediumpurple'
    ))
    fig.update_layout(
        barmode='group',
        title="Distribución por Sexo en los Tres Conceptos",
        xaxis_title="Conceptos",
        yaxis_title="Cantidad",
        width=800,
        height=400
    )
    return fig

# Mostrar la gráfica de barras al inicio
st.subheader("Comparativa de los Tres Conceptos por Sexo")
labels = ["Fuerza Laboral", "Desocupación", "Población"]
hombres_values = [fuerza_laboral_hombres, desocupacion_hombres, poblacion_hombres]
mujeres_values = [fuerza_laboral_mujeres, desocupacion_mujeres, poblacion_mujeres]
bar_fig = bar_chart(hombres_values, mujeres_values, labels)
st.plotly_chart(bar_fig)

# Mostrar los cuadros de indicadores para el año seleccionado
if fuerza_laboral_year is not None:
    st.subheader("Indicadores de Fuerza Laboral por Sexo")
    col1, col2 = st.columns([3, 2])  # Una columna para indicadores y otra para la gráfica

    with col1:
        st.metric("Total Fuerza Laboral", f"{fuerza_laboral_year['obs_value'].sum():,.0f}")
        st.metric("Hombres", f"{fuerza_laboral_hombres:,.0f}")
        st.metric("Mujeres", f"{fuerza_laboral_mujeres:,.0f}")
    
    with col2:
        fig = pie_chart(fuerza_laboral_hombres, fuerza_laboral_mujeres, "Fuerza Laboral")
        st.plotly_chart(fig)

if desocupacion_year is not None:
    st.subheader("Indicadores de Desocupación por Sexo")
    col1, col2 = st.columns([3, 2])  # Una columna para indicadores y otra para la gráfica

    with col1:
        st.metric("Total Desocupación", f"{desocupacion_year['obs_value'].sum():,.0f}")
        st.metric("Hombres", f"{desocupacion_hombres:,.0f}")
        st.metric("Mujeres", f"{desocupacion_mujeres:,.0f}")

    with col2:
        fig = pie_chart(desocupacion_hombres, desocupacion_mujeres, "Desocupación")
        st.plotly_chart(fig)

if poblacion_year is not None:
    st.subheader("Indicadores de Población por Sexo")
    col1, col2 = st.columns([3, 2])  # Una columna para indicadores y otra para la gráfica

    with col1:
        st.metric("Total Población", f"{poblacion_year['obs_value'].sum():,.0f}")
        st.metric("Hombres", f"{poblacion_hombres:,.0f}")
        st.metric("Mujeres", f"{poblacion_mujeres:,.0f}")

    with col2:
        fig = pie_chart(poblacion_hombres, poblacion_mujeres, "Población")
        st.plotly_chart(fig)
