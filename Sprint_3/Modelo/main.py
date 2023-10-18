import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from geopy.distance import great_circle
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder


import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from geopy.distance import great_circle

def custom_tabs():
    tabs = st.radio("Selecciona una pestaña:", ("Categoría según niveles de densidad demográfica y Estado seleccionado", "Franquicias según categoría y rango de Promedio de Rating", "Franquicias por Rango de Inversión seleccionado", "Sucursales con mejor rating de la Franquicia Seleccionada", "Predicción de Promedio de Rating de Franquicia"))
    return tabs


# Cargar los tres DataFrames
df_ML = pd.read_csv('/Users/benjaminzelaya/Desktop/nuevo_directorio/Sprint_3/Modelo/df_ML.csv')

# Personalización del tema
st.set_page_config(
    page_title="Recomendación de Franquicias para Inversión 🚀📊",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Imagen o logo más pequeño
st.image("/Users/benjaminzelaya/Desktop/nuevo_directorio/Images/ICOn COnsulting.png", 
        width=200,
        use_column_width=False, 
        output_format='auto')  

# Crear pestañas personalizadas
selected_tab = custom_tabs()

# Pestaña 1: Categoría según niveles de densidad demográfica y Estado seleccionado
if selected_tab == "Categoría según niveles de densidad demográfica y Estado seleccionado":
    st.title("Categoría según niveles de densidad demográfica y Estado seleccionado")


    # Campos de entrada específicos para esta pestaña
    categoria_deseada = st.selectbox("Selecciona una Categoría de Densidad:", df_ML['Categoria_Densidad'].unique())
    
    # Filtrar el DataFrame para incluir solo las ubicaciones de la Categoría de Densidad seleccionada
    estados_categoria_densidad = df_ML[df_ML['Categoria_Densidad'] == categoria_deseada]

    # Obtener la lista de opciones de estados dentro de la categoría de densidad seleccionada
    opciones_estados = estados_categoria_densidad['Nombre_Estado'].unique()

    estado_deseado_seccion2 = st.selectbox("Selecciona un estado:", opciones_estados)

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

# Agregar un botón para obtener los resultados
    if st.button('Obtener Resultados'):
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig)


# Agregar separador visual
    st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)


#######################
# Pestaña 2: Franquicias según categoría y rango de Promedio de Rating
elif selected_tab == "Franquicias según categoría y rango de Promedio de Rating":
    st.title("Franquicias según categoría y rango de Promedio de Rating")
    
    # Campos de entrada de usuario directamente en la pestaña, sin barra lateral
    categoria_seleccionada = st.selectbox("Seleccione una categoría de franquicia:", df_ML['Categoria'].unique())
    promedio_rating_min = st.number_input("Promedio mínimo de rating:", value=1.0, step=0.1)
    promedio_rating_max = st.number_input("Promedio máximo de rating:", value=5.0, step=0.1)

    # Botón para obtener las recomendaciones
    if st.button('Obtener Recomendaciones', key='obtener_recomendaciones_button'):
        # Filtrar franquicias por categoría y rango de promedio de rating
        franquicias_filtradas = df_ML[
            (df_ML['Promedio_Rating'] >= promedio_rating_min) &
            (df_ML['Promedio_Rating'] <= promedio_rating_max) &
            (df_ML['Categoria'] == categoria_seleccionada)
        ]

        # Ordenar franquicias por promedio de rating descendente y eliminar duplicados en "Nombre_Franquicia"
        franquicias_recomendadas = franquicias_filtradas.drop_duplicates(subset=['Nombre_Franquicia']).nlargest(10, 'Promedio_Rating')

        # Crear un gráfico de barras interactivas con Plotly
        fig = px.bar(franquicias_recomendadas, x='Promedio_Rating', y='Nombre_Franquicia', orientation='h',
                    labels={'Nombre_Franquicia': 'Nombre de Franquicia'},
                    title='Franquicias Recomendadas')

        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig)

# Agregar separador visual
    st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)

##################################

# # Seccion 3
# Pestaña 3: Franquicias por Rango de Inversión seleccionado
elif selected_tab == "Franquicias por Rango de Inversión seleccionado":
    st.title("Franquicias por Rango de Inversión seleccionado")

    # Entrada para el presupuesto mínimo y máximo
    budget_min = st.number_input('Presupuesto Mínimo', min_value=0, max_value=99000000000, value=0)
    budget_max = st.number_input('Presupuesto Máximo', min_value=0, max_value=99000000000, value=99000000000)

    # Configurable: Número de franquicias a mostrar
    num_franquicias_mostrar = st.number_input('Número de Franquicias a Mostrar', min_value=1, value=5)

    # Botón para realizar recomendaciones
    if st.button('Obtener Recomendaciones'):
        try:
            # Realiza una copia explícita del DataFrame para evitar el SettingWithCopyWarning
            df_ML = df_ML.copy()

            # Convierte los valores de 'Año_Fundado' a cadenas de texto, luego elimina comas y convierte a tipo int
            df_ML['Año_Fundado'] = pd.to_numeric(df_ML['Año_Fundado'].astype(str).str.replace(',', '', regex=True), errors='coerce')

            # Filtrar franquicias por rango de inversión
            franquicias_filtradas = df_ML[
                (df_ML['Min_Inversion'] >= budget_min) &
                (df_ML['Max_Inversion'] <= budget_max)
            ]

            if franquicias_filtradas.empty:
                st.warning('No hay franquicias disponibles en el rango de inversión seleccionado.')
            else:
                # Calcular el porcentaje de inversión para cada franquicia
                franquicias_filtradas['Ratio_Inversion'] = (franquicias_filtradas['Min_Inversion'] / franquicias_filtradas['Max_Inversion']) * 100
                franquicias_filtradas['Ratio_Inversion'] = franquicias_filtradas['Ratio_Inversion'].round(2)

                # Ordenar franquicias filtradas primero por 'Unidades' (de mayor a menor) y luego por 'Min_Inversion' (de menor a mayor)
                franquicias_filtradas = franquicias_filtradas.sort_values(by=['Unidades', 'Min_Inversion'], ascending=[False, True])

                # Eliminar duplicados y mostrar solo las filas únicas
                franquicias_unicas = franquicias_filtradas.drop_duplicates(subset=['Nombre_Franquicia'])

                # Crear un gráfico de burbujas para visualizar el rango de inversión y el ratio de inversión de cada franquicia
                fig = px.scatter(franquicias_unicas.head(num_franquicias_mostrar), x='Min_Inversion', y='Max_Inversion', size='Ratio_Inversion', text='Nombre_Franquicia',
                                labels={'Min_Inversion': 'Inversión Mínima', 'Max_Inversion': 'Inversión Máxima', 'Ratio_Inversion': 'Ratio de Inversión'})

                # Mostrar el gráfico de burbujas en el dashboard
                st.write("A continuación, se muestra un gráfico de burbujas que representa el rango de inversión y el ratio de inversión de las franquicias:")
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Ocurrió un error: {str(e)}")

         # Agregar la descripción del ratio de inversión en un tamaño más pequeño
        st.markdown("<sub><sup> *El ratio de inversión proporciona información clave sobre cómo se distribuyen los recursos financieros en relación con un rango de inversión disponible. Su uso puede ayudar en la toma de decisiones, la planificación financiera y la optimización de recursos, lo que es fundamental para lograr objetivos financieros y maximizar el rendimiento de las inversiones.</sup></sub>", unsafe_allow_html=True)
        st.markdown("<sub><sup> *Si el ratio de inversión indica que la inversión mínima representa una pequeña fracción de la inversión máxima, esto podría sugerir la oportunidad de diversificar aún más la cartera de inversiones.</sup></sub>", unsafe_allow_html=True)

# Agregar separador visual
    st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)


# ############################################
# Pestaña 4: Sucursales con mejor rating de la Franquicia Seleccionada
elif selected_tab == "Sucursales con mejor rating de la Franquicia Seleccionada":
    st.title("Sucursales con mejor rating de la Franquicia Seleccionada")

    df_ML['Caracteristicas'] = df_ML['Nombre_Estado'] + ' ' + df_ML['Categoria']

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

                # Cambia el número de recomendaciones deseadas (por ejemplo, 20 en lugar de 10)
                franquicias_indices = sim_scores.argsort()[::-1][1:21]

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
    
    # Mover esta parte del código a la pestaña principal
    st.markdown("### Selecciona una Franquicia para conocer las sucursales con mejor rating")

    # Filtra las franquicias que tienen al menos un número mínimo de sucursales
    min_sucursales = 1  # Define el número mínimo de sucursales requerido
    franquicias_con_suficientes_sucursales = df_ML['Nombre_Franquicia'].value_counts()[df_ML['Nombre_Franquicia'].value_counts() >= min_sucursales].index.tolist()

    if franquicias_con_suficientes_sucursales:
        # Crea un selectbox directamente en la pestaña
        nombre_franquicia_ejemplo = st.selectbox('Seleccione una franquicia:', franquicias_con_suficientes_sucursales)

        # Obtener la lista de opciones de franquicias desde la columna 'Nombre_Franquicia' de tu DataFrame
        opciones_franquicias = df_ML['Nombre_Franquicia'].unique()

        # Inicializar recomendaciones
        recomendaciones = None

        # Botón principal para obtener recomendaciones
        if st.button('Obtener Recomendaciones', key='obtener_recomendaciones_button'):
            recomendaciones = get_recommendations(nombre_franquicia_ejemplo)

        if recomendaciones is not None and not isinstance(recomendaciones, str):  # Verifica que las recomendaciones no sean un mensaje de error
            map = folium.Map(location=[recomendaciones.iloc[0]['Latitud'], recomendaciones.iloc[0]['Longitud']], zoom_start=10)

            for _, row in recomendaciones.iterrows():
                popup_content = f"Nombre Franquicia: {row['Nombre_Franquicia']}<br>Nombre Estado: {row['Nombre_Estado']}<br>Promedio Rating: {row['Promedio_Rating']}<br>Latitud: {row['Latitud']}<br>Longitud: {row['Longitud']}"
                if row['Promedio_Rating'] == recomendaciones['Promedio_Rating'].max():
                    # Usar un color rojo para resaltar la mejor sucursal
                    icon = folium.Icon(color='red')
                     # Agregar el texto aquí
                    st.write(f"*La Sucursal indicada con color Rojo con el mejor promedio de rating de {row['Nombre_Franquicia']}, está ubicada en el Estado de {row['Nombre_Estado']}.")
                else:
                    icon = None

                folium.Marker(
                    location=[row['Latitud'], row['Longitud']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=icon
                ).add_to(map)

            st.write('Mapa de Sucursales:')     
            folium_static(map)
        else:
            st.write('No se encontraron recomendaciones para la franquicia seleccionada.')


# Agregar separador visual
    st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)

# Pestaña 5: Predicción de Promedio de Rating de Franquicia
elif selected_tab == "Predicción de Promedio de Rating de Franquicia":
        # Entrenamiento del modelo Random Forest Regressor

        # Crear un LabelEncoder y ajustarlo a tus datos
    label_encoder = LabelEncoder()
    label_encoder.fit(df_ML['Nombre_Estado'])  # Asegúrate de que df sea tu DataFrame con los datos

    # Función para obtener la representación numérica de un estado
    def obtener_numero_estado(estado):
        try:
            numero_estado = label_encoder.transform([estado])[0]
            return numero_estado
        except ValueError:
            return None  # Devuelve None si el estado no se encuentra en el LabelEncoder

    # Título de la aplicación
    st.title("Codificación Numérica de Estados")

    # Campo de entrada para el usuario
    estado_ingresado = st.text_input("Ingresa un nombre de estado:")

    # Botón para realizar la conversión
    if st.button("Obtener Representación Numérica"):
        numero_estado = obtener_numero_estado(estado_ingresado)
        if numero_estado is not None:
            st.write(f"El estado '{estado_ingresado}' tiene la representación numérica: {numero_estado}")
        else:
            st.write(f"El estado '{estado_ingresado}' no se encuentra en los datos originales.")
    
 

    # Crear un LabelEncoder y ajustarlo a tus datos
    label_encoder = LabelEncoder()
    label_encoder.fit(df_ML['Id_Franquicia'])  # Asegúrate de que df_ML sea tu DataFrame con los datos

    # Función para obtener el nombre de la franquicia a partir de su número
    def obtener_nombre_franquicia(numero):
        try:
            nombre_franquicia = label_encoder.inverse_transform([numero])[0]
            return nombre_franquicia
        except ValueError:
            return None  # Devuelve None si el número de franquicia no se encuentra en el LabelEncoder

    # Función para obtener la representación numérica de una franquicia
    def obtener_numero_franquicia(franquicia):
        try:
            numero_franquicia = label_encoder.transform([franquicia])[0]
            return numero_franquicia
        except ValueError:
            return None  # Devuelve None si la franquicia no se encuentra en el LabelEncoder

    # Crear un LabelEncoder y ajustarlo a tus datos
    label_encoder_nombre = LabelEncoder()
    label_encoder_id = LabelEncoder()
    label_encoder_nombre.fit(df_ML['Nombre_Franquicia'])  # Asegúrate de que df_ML sea tu DataFrame con los datos
    label_encoder_id.fit(df_ML['Id_Franquicia'])  # Asegúrate de que df_ML sea tu DataFrame con los datos

    # Función para obtener el nombre de la franquicia a partir de su número
    def obtener_nombre_franquicia(numero):
        try:
            nombre_franquicia = label_encoder_nombre.inverse_transform([numero])[0]
            return nombre_franquicia
        except ValueError:
            return None  # Devuelve None si el número de franquicia no se encuentra en el LabelEncoder

    # Función para obtener la representación numérica de una franquicia por nombre
    def obtener_numero_franquicia_por_nombre(franquicia):
        try:
            numero_franquicia = label_encoder_nombre.transform([franquicia])[0]
            return numero_franquicia
        except ValueError:
            return None  # Devuelve None si la franquicia no se encuentra en el LabelEncoder

    # Función para obtener la representación numérica de una franquicia por número
    def obtener_numero_franquicia_por_numero(numero):
        try:
            numero_franquicia = label_encoder_id.transform([numero])[0]
            return numero_franquicia
        except ValueError:
            return None  # Devuelve None si el número de franquicia no se encuentra en el LabelEncoder

    # Título de la aplicación
    st.title("Codificación Numérica de Franquicias")

    # Campo de entrada para el usuario
    franquicia_ingresada = st.text_input("Ingresa un nombre de franquicia o número:")

    # Botón para realizar la conversión
    if st.button("Buscar Franquicia"):
        # Verificar si la entrada es un número o un nombre de franquicia
        if franquicia_ingresada.isdigit():
            numero_franquicia = int(franquicia_ingresada)
            nombre_franquicia = obtener_nombre_franquicia(numero_franquicia)
            if nombre_franquicia is not None:
                st.write(f"El número de franquicia '{numero_franquicia}' corresponde a la franquicia: {nombre_franquicia}")
            else:
                st.write(f"No se encontró una franquicia con el número '{numero_franquicia}'.")
        else:
            numero_por_nombre = obtener_numero_franquicia_por_nombre(franquicia_ingresada)
            numero_por_numero = obtener_numero_franquicia_por_numero(franquicia_ingresada)
            if numero_por_nombre is not None:
                st.write(f"La franquicia '{franquicia_ingresada}' tiene la representación numérica por nombre: {numero_por_nombre}")
            elif numero_por_numero is not None:
                st.write(f"La franquicia '{franquicia_ingresada}' tiene la representación numérica por número: {numero_por_numero}")
            else:
                st.write(f"La franquicia '{franquicia_ingresada}' no se encuentra en los datos originales.")

            
    st.title("Predicción de Promedio de Rating de Franquicia")

    # Elimina la columna 'Categoria_Densidad'
    df_ML = df_ML.drop('Categoria_Densidad', axis=1)

    # Define las columnas del dataset
    columnas = ['Min_Inversion', 'Max_Inversion', 'Total_Poblacion', 
                'Cantidad_Reviews', 'Id_Estado', 'Id_Franquicia', 'Unidades']

    # Divide el dataset en características (X) y el valor a predecir (y)
    X = df_ML[columnas]
    y = df_ML['Promedio_Rating']

    # Divide los datos en un conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrena el modelo Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Realizar predicciones en el conjunto de prueba
    y_pred = model.predict(X_test)

    # Calcular métricas de evaluación
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    # Función para realizar una predicción personalizada
    @st.cache_data()
    def custom_franchise_prediction(min_inversion, max_inversion, poblacion,  cantidad_reviews, id_estado, id_franquicia, unidades):
        # Realiza una predicción personalizada utilizando las características proporcionadas
        features = [ min_inversion, max_inversion, poblacion, cantidad_reviews, id_estado, id_franquicia, unidades]
        prediction = model.predict([features])[0]
        return prediction

    # Ingrese las características para la predicción directamente en la pestaña
    st.markdown("### Ingrese las Características para la Predicción")
    min_inversion = st.number_input('Inversión Mínima:', min_value=0)
    max_inversion = st.number_input('Inversión Máxima:', min_value=0)
    poblacion = st.number_input('Población:', min_value=0)
    cantidad_reviews = st.number_input('Cantidad_Reviews:', min_value=0)
    id_estado = st.number_input('Id_Estado:', min_value=0)
    id_franquicia = st.number_input('Id_Franquicia:', min_value=0)
    unidades = st.number_input('Unidades:', min_value=0)

    # Botón para realizar la predicción personalizada
    if st.button('Obtener Predicción Personalizada'):
        prediction = custom_franchise_prediction(min_inversion, max_inversion, poblacion, cantidad_reviews, id_estado, id_franquicia, unidades)
        st.write(f'Predicción del Promedio de Rating por Machine Learning: {prediction:.2f}')

    # Muestra las métricas de evaluación del modelo
    st.markdown("### Métricas de Evaluación del Modelo")
    st.write(f'R2 Score: {r2:.2f}')
    st.write(f'RMSE: {rmse:.2f}')
    st.write(f'MAE: {mae:.2f}')
    st.write(f'MSE: {mse:.2f}')

# Agregar separador visual
    st.markdown('<hr style="border: 2px solid #e74c3c;">', unsafe_allow_html=True)


    st.image("/Users/benjaminzelaya/Desktop/nuevo_directorio/Images/ICOn COnsulting.png", 
        caption="©Icon Data Science Consulting",
        width=200,
        use_column_width=False,
        output_format='auto')


    st.markdown(
        """<div style="background-color:#F8F8F8;padding:10px;border-radius:5px;">
        <p style="text-align:center;">©Icon Data Science Consulting</p></div>""",
        unsafe_allow_html=True
    )