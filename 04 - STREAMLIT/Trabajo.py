import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import seaborn as sns



data_comple=pd.read_csv("Union.csv")
data_comple=data_comple[["Estado","latitude","longitude","category","name"]]
Population=pd.read_csv("Population_limpio.csv")
Population=Population[["State","Total population","Categoría de densidad"]]
Rewiews=pd.read_csv("yast.csv")
Rewiews=Rewiews[["name","text","date"]]
puntuacion=pd.read_csv("Puntuacion.csv")
puntuacion=puntuacion[["name","Promedio"]]

data_comple.dropna(subset=["category"], inplace=True)

st.markdown("***")

st.markdown("# 	:zap: Densidad poblacional :zap:")
st.markdown("***")

lista=Population["Categoría de densidad"].unique()
select=st.selectbox("Seleccione Estado: ",lista)



Popu =Population[Population["Categoría de densidad"]== select]



st.dataframe(Popu)


st.markdown("***")

st.markdown("# 	:zap: Restaurant Sectorizado  :zap:")
st.markdown("***")


lista=Popu["State"].unique()
select=st.selectbox("Seleccione Estado: ",lista)



df = data_comple[data_comple['Estado'] == select]
conteo = pd.DataFrame(df['category'].value_counts().head(5).reset_index())

st.dataframe(conteo)
st.set_option('deprecation.showPyplotGlobalUse', False)
sns.barplot(y='category', x='count', data=conteo)
st.pyplot()



latitudes = df["latitude"]
longitudes = df["longitude"]

# Crear el mapa centrado en las coordenadas promedio
mapa = folium.Map(location=[sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)], zoom_start=5)

# Agregar marcadores al mapa
for lat, lon in zip(latitudes, longitudes):
    folium.Marker([lat, lon]).add_to(mapa)
        

# Mostrar el mapa
st_data = st_folium(mapa,returned_objects=[])

st.markdown("***")

st.markdown("# 	:zap:  Categorizacion de Restaurant  :zap:")
st.markdown("***")



category=conteo
select2=st.selectbox("Seleccione Categoria: ",category)


categori=df[df["category"] ==select2]
Cate=pd.DataFrame(categori['name'].value_counts().head(5).reset_index())

#sns.barplot(y='category', x='count', data=conteo)
st.dataframe(Cate)
sns.barplot(y='name', x='count', data=Cate)
st.pyplot()

latitudes = categori["latitude"]
longitudes = categori["longitude"]

# Crear el mapa centrado en las coordenadas promedio
mapa = folium.Map(location=[sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)], zoom_start=5)

# Agregar marcadores al mapa
for lat, lon in zip(latitudes, longitudes):
    folium.Marker([lat, lon]).add_to(mapa)


# Mostrar el mapa
st_data = st_folium(mapa,returned_objects=[])

st.markdown("***")

st.markdown("# 	:zap: Franquicias del sector   :zap:")
st.markdown("***")


Franquicias=pd.DataFrame(df['name'].value_counts().head(5).reset_index())



#sns.barplot(y='category', x='count', data=conteo)
st.dataframe(Franquicias)
sns.barplot(y='name', x='count', data=Franquicias)
st.pyplot()


    
st.markdown("***")

st.markdown("# 	:zap: Rewiews de la Franquicia   :zap:")
st.markdown("***")

lista=Franquicias["name"].unique()
select=st.selectbox("Seleccione una Franquicia: ",lista)

Puntu=puntuacion[puntuacion['name'] == select]

rewiew=Rewiews[Rewiews['name'] == select]

rewiew.sort_values('date', ascending=False, inplace=True)
rewiew.reset_index(drop=True, inplace=True)


result=rewiew[["text","date"]]
result=result.head(5)

st.dataframe(Puntu)
st.dataframe(result)
