import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import folium
from folium.plugins import MarkerCluster
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from geopy.distance import great_circle



# Cargar los tres DataFrames
df_reviews_completo = pd.read_csv('/Users/benjaminzelaya/Desktop/PGF/PG/PF_DS_REVIEWS_AND_RECOMMENDATIONS/sprint_2/datasets_limpios/Reviews_Completo.csv')
df_franquicias_inversion = pd.read_csv('/Users/benjaminzelaya/Desktop/PGF/PG/PF_DS_REVIEWS_AND_RECOMMENDATIONS/sprint_2/datasets_limpios/Franquicias_Inversion.csv')
df_estados = pd.read_csv('/Users/benjaminzelaya/Desktop/PGF/PG/PF_DS_REVIEWS_AND_RECOMMENDATIONS/sprint_2/datasets_limpios/Estados.csv')
df_ML = pd.read_csv('/Users/benjaminzelaya/Desktop/PGF/PG/PF_DS_REVIEWS_AND_RECOMMENDATIONS/Sprint_3/Modelo/df_ML.csv')


    # Unir los DataFrames
merged_df = df_reviews_completo.merge(df_franquicias_inversion, on='Id_Franquicia', how='inner')
final_df = merged_df.merge(df_estados, on='Id_Estado', how='inner')




# Personalización del tema
st.set_page_config(
    page_title="Recomendación de Franquicias para Inversión 🚀📊",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo de la aplicación
st.markdown(
    """<style>
    body {
        background-color: #F8F8F8;
        font-family: Arial, sans-serif;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stAlert {
        background-color: #D6EAF8;
        color: #333333;
    }
    .stButton {
        background-color: #3498DB;
        color: #FFFFFF;
    }
    .stButton:hover {
        background-color: #2980B9;
    }
    h1 {
        font-size: 32px;
    }
    h2 {
        font-size: 24px;
    }
    </style>""",
    unsafe_allow_html=True

)


# Imagen o logo más pequeño
st.image("/Users/benjaminzelaya/Desktop/PGF/PG/PF_DS_REVIEWS_AND_RECOMMENDATIONS/Images/ICOn COnsulting.png", 
        width=200,
        use_column_width=False, 
        output_format='auto')  


st.header("Categoria segun niveles de densidad demografica y Estado seleccionado")

# Barra lateral personalizada
st.sidebar.title('Selecciona una Categoría de Densidad y un Estado:')
categoria_deseada = st.sidebar.selectbox("Selecciona una Categoría de Densidad:", df_ML['Categoria_Densidad'].unique())

# Filtrar el DataFrame para incluir solo las ubicaciones de la Categoría de Densidad seleccionada
estados_categoria_densidad = df_ML[df_ML['Categoria_Densidad'] == categoria_deseada]

# Obtener la lista de opciones de estados dentro de la categoría de densidad seleccionada
opciones_estados = estados_categoria_densidad['Nombre_Estado'].unique()

# Usar un segundo selectbox en la barra lateral para seleccionar un estado dentro de la Categoría de Densidad
estado_deseado_seccion2 = st.sidebar.selectbox("Selecciona un estado:", opciones_estados)

# Estilo de texto con formato
st.markdown(f"Las categorías con más sucursales en **{estado_deseado_seccion2}** son:")

# Filtrar franquicias por estado y categoría de densidad
franquicias_en_estado_seccion1 = df_ML[(df_ML['Nombre_Estado'] == estado_deseado_seccion2) & (df_ML['Categoria_Densidad'] == categoria_deseada)]

# Calcular las categorías con más sucursales 
categorias_mas_sucursales = franquicias_en_estado_seccion1.groupby('Categoria').size().sort_values(ascending=False).head(5)


# Crear el gráfico de barras
fig = px.bar(
    categorias_mas_sucursales.reset_index(),
    x='Categoria',
    y=0,
    text=0,
    title='Cantidad de Sucursales por Categoría',
    labels={'0': 'Cantidad de Sucursales'}
)

# Ajustar la apariencia del gráfico
fig.update_traces(
    texttemplate='%{text}',  # Etiquetas con el valor de las barras
    textposition='outside',  # Ubicación de las etiquetas
    marker_color='royalblue',  # Color de las barras
    hoverinfo='x+y',  # Información que se muestra al pasar el ratón
    hovertemplate='Categoría: %{x}<br>Cantidad de Sucursales: %{y}',  # Formato de información al pasar el ratón
)

# Personalizar el diseño
fig.update_layout(
    xaxis_title='',  # Título del eje X
    yaxis_title='Cantidad de Sucursales',  # Título del eje Y
    xaxis_tickangle=-45,  # Ángulo de las etiquetas del eje X
    margin_b=100,  # Ajuste del margen inferior
    showlegend=False  # Ocultar la leyenda
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)

# Gráfico de pastel interactivo
st.subheader("Distribución de Categorías")
fig, ax = plt.subplots()
ax.pie(categorias_mas_sucursales, labels=categorias_mas_sucursales.index.tolist(), autopct='%1.1f%%', startangle=90)
ax.axis('equal')  #

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

# Agregar separador visual
st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)


#######################
# Sección 2: Recomendación de Inversión en Franquicias
st.header("Franquicias según categoría y rango de Promedio de Rating")

# Barra lateral personalizada
st.sidebar.title('Selecciona una Categoria y rango de Rating')

# Campos de entrada de usuario en la barra lateral
categoria_seleccionada = st.sidebar.selectbox("Seleccione una categoría de franquicia:", df_ML['Categoria'].unique())
promedio_rating_min = st.sidebar.number_input("Promedio mínimo de rating:", value=1.0, step=0.1)
promedio_rating_max = st.sidebar.number_input("Promedio máximo de rating:", value=5.0, step=0.1)

# Botón para obtener las recomendaciones
if st.sidebar.button('Obtener Recomendaciones', key='obtener_recomendaciones_button'):
    # Filtrar franquicias por categoría y rango de promedio de rating
    franquicias_filtradas = df_ML[
        (df_ML['Promedio_Rating'] >= promedio_rating_min) &
        (df_ML['Promedio_Rating'] <= promedio_rating_max) &
        (df_ML['Categoria'] == categoria_seleccionada)
    ]

    # Ordenar franquicias por promedio de rating descendente y eliminar duplicados en "Nombre_Franquicia"
    franquicias_recomendadas = franquicias_filtradas.drop_duplicates(subset=['Nombre_Franquicia']).nlargest(10, 'Promedio_Rating')

    # Mostrar franquicias recomendadas con información adicional
    st.dataframe(franquicias_recomendadas[['Nombre_Franquicia', 'Promedio_Rating']])



# Agregar separador visual
st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)

##################################

# Seccion 3
# Título de la aplicación con formato
st.header("Franquicias por Rango de Inversión seleccionado")

# Barra lateral personalizada
st.sidebar.title('Franquicias Recomendadas por Rango de Inversión:')
# Crear una función para realizar recomendaciones
def main():
    # Entrada para el presupuesto mínimo y máximo
    budget_min = st.sidebar.number_input('Presupuesto Mínimo', min_value=0, max_value=99000000000, value=0)
    budget_max = st.sidebar.number_input('Presupuesto Máximo', min_value=0, max_value=99000000000, value=99000000000)

    # Botón para realizar recomendaciones
    if st.sidebar.button('Obtener Recomendaciones'):
        # Convierte los valores de 'Año_Fundado' a cadenas de texto, luego elimina comas y convierte a tipo int
        df_franquicias_inversion['Año_Fundado'] = pd.to_numeric(df_franquicias_inversion['Año_Fundado'].astype(str).str.replace(',', '', regex=True), errors='coerce')

        # Filtrar franquicias por rango de inversión
        franquicias_filtradas = df_franquicias_inversion[
            (df_franquicias_inversion['Min_Inversion'] >= budget_min) &
            (df_franquicias_inversion['Max_Inversion'] <= budget_max)
        ]

        # Calcular el porcentaje de inversión para cada franquicia, redondear a 2 decimales y agregar el símbolo '%'
        franquicias_filtradas['Ratio_Inversion'] = (franquicias_filtradas['Min_Inversion'] / franquicias_filtradas['Max_Inversion']) * 100
        franquicias_filtradas['Ratio_Inversion'] = franquicias_filtradas['Ratio_Inversion'].round(2).astype(str) + '%'

        # Ordenar franquicias filtradas primero por 'Unidades' (de mayor a menor) y luego por 'Min_Inversion' (de menor a mayor)
        franquicias_filtradas = franquicias_filtradas.sort_values(by=['Unidades', 'Min_Inversion'], ascending=[False, True])

        # Limitar la salida a las 10 primeras franquicias y eliminar la columna 'Id_Franquicia'
        franquicias_top_10 = franquicias_filtradas.head(10).drop(columns=['Id_Franquicia'])

        # Mostrar recomendaciones en el cuerpo principal
        st.write(franquicias_top_10)

        # Agregar la descripción del ratio de inversión en un tamaño más pequeño
        st.markdown("<sub><sup> *El ratio de inversión proporciona información clave sobre cómo se distribuyen los recursos financieros en relación con un rango de inversión disponible. Su uso puede ayudar en la toma de decisiones, la planificación financiera y la optimización de recursos, lo que es fundamental para lograr objetivos financieros y maximizar el rendimiento de las inversiones.</sup></sub>", unsafe_allow_html=True)
        st.markdown("<sub><sup> *Si el ratio de inversión indica que la inversión mínima representa una pequeña fracción de la inversión máxima, esto podría sugerir la oportunidad de diversificar aún más la cartera de inversiones.</sup></sub>", unsafe_allow_html=True)
if __name__ == '__main__':
    main()


# Agregar separador visual
st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)


############################################
# seccion 4
st.header('Sucursales con mejor rating de la Franquicia Seleccionada')

# Construir una matriz de características TF-IDF a partir de la columna 'Caracteristicas'
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df_ML['Caracteristicas'].fillna(''))

# Calcular la similitud coseno entre los vectores TF-IDF
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def get_recommendations(nombre_franquicia, cosine_sim=cosine_sim):
    # Filtrar el DataFrame para incluir solo las ubicaciones de la franquicia especificada por el usuario
    df_combined_final_franquicia = df_ML[df_ML['Nombre_Franquicia'] == nombre_franquicia]

    if not df_combined_final_franquicia.empty:
        # Obtener las 10 franquicias más similares
        sim_scores = cosine_sim[df_combined_final_franquicia.index[0]]

        # Obtener los índices de las franquicias recomendadas
        franquicias_indices = sim_scores.argsort()[::-1][1:11]

        # Filtrar las recomendaciones para que solo sean de la misma franquicia
        recomendaciones = df_ML.iloc[franquicias_indices]
        recomendaciones = recomendaciones[recomendaciones['Nombre_Franquicia'] == nombre_franquicia]

        # Ordenar las recomendaciones por 'Promedio_Rating' de mayor a menor
        recomendaciones = recomendaciones.sort_values(by='Promedio_Rating', ascending=False)

        # Seleccionar las columnas deseadas
        recomendaciones = recomendaciones[['Nombre_Franquicia', 'Latitud', 'Longitud', 'Nombre_Estado', 'Promedio_Rating']]
        return recomendaciones
    else:
        return "La franquicia especificada no se encontró en los datos."

def main():
    st.sidebar.title('Selecciona una Franquicia para conocer las sucursales con mejor rating')

    # Obtener la lista de opciones de franquicias desde la columna 'Nombre_Franquicia' de tu DataFrame
    opciones_franquicias = df_ML['Nombre_Franquicia'].unique()

    # Usar un selectbox en la barra lateral para seleccionar una franquicia
    nombre_franquicia_ejemplo = st.sidebar.selectbox('Seleccione una franquicia:', opciones_franquicias)

    # Inicializar recomendaciones
    recomendaciones = None

    # Botón principal para obtener recomendaciones
    if st.sidebar.button('Obtener Recomendaciones', key='obtener_recomendaciones_button_sidebar'):
        recomendaciones = get_recommendations(nombre_franquicia_ejemplo)

    if recomendaciones is not None:
        if isinstance(recomendaciones, pd.DataFrame):
            st.write('Sucursales:')
        
        # Resaltar la mejor opción
        if not recomendaciones.empty:
            best_option = recomendaciones.iloc[0]
            st.write(f"La Sucursal con mejor promedio de rating de {best_option['Nombre_Franquicia']}, esta ubicada en el Estado de {best_option['Nombre_Estado']}.")
            
        st.dataframe(recomendaciones)
    else:
        st.write(recomendaciones)

if __name__ == '__main__':
    main()

# Agregar separador visual
st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)

#### seccion 5

st.header('Franquicias y Sucursales dentro de un Radio especifico de 10Km')


# Esta es tu función para filtrar franquicias cercanas
def get_franquicias_cercanas(longitud, latitud, radio_km=10):
    franquicias_cercanas = []

    user_location = (latitud, longitud)

    for index, row in df_ML.iterrows():
        franquicia_location = (row['Latitud'], row['Longitud'])
        distance = great_circle(user_location, franquicia_location).kilometers
        if distance <= radio_km:
            franquicias_cercanas.append({
                'nombre_franquicia': row['Nombre_Franquicia'],
                'Latitud': row['Latitud'],
                'Longitud': row['Longitud'],
                'Nombre_Estado': row['Nombre_Estado'],
                'Promedio_Rating': row['Promedio_Rating'],
                'Categoria': row['Categoria']
            })

    if franquicias_cercanas:
        # Convertir a DataFrame y eliminar duplicados por latitud y longitud
        franquicias_df = pd.DataFrame(franquicias_cercanas)
        franquicias_df = franquicias_df.drop_duplicates(subset=['Latitud', 'Longitud'])
        return franquicias_df
    else:
        return "No se encontraron franquicias cercanas."


# Tu función principal de Streamlit
def main():
    st.sidebar.title('Buscar Franquicias y Sucursales Cercanas')

    longitud = st.sidebar.number_input('Longitud:', value=0.0, min_value=-180.0, max_value=180.0, step=0.0001)
    latitud = st.sidebar.number_input('Latitud:', value=0.0, min_value=-90.0, max_value=90.0, step=0.0001)

    if st.sidebar.button('Buscar'):
        franquicias_cercanas = get_franquicias_cercanas(longitud, latitud)
        if isinstance(franquicias_cercanas, pd.DataFrame):
            st.write('Franquicias y Sucursales Cercanas:')
            st.dataframe(franquicias_cercanas)
        else:
            st.write(franquicias_cercanas)

if __name__ == '__main__':
    main()



# Agregar separador visual
st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)


    # Imagen o logo más pequeño
st.image("/Users/benjaminzelaya/Desktop/PGF/PG/PF_DS_REVIEWS_AND_RECOMMENDATIONS/Images/ICOn COnsulting.png", 
            caption="©Icon Data Science Consulting",
            width=200,
            use_column_width=False,  # Evita que ocupe todo el ancho de la columna
            output_format='auto')  # Ajusta el formato de la imagen automáticamente

 
    # Pie de página personalizado
st.markdown(
        """<div style="background-color:#F8F8F8;padding:10px;border-radius:5px;">
        <p style="text-align:center;">©Icon Data Science Consulting</p></div>""",
        unsafe_allow_html=True
    )


