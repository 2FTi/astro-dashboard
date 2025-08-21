import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🌌 Astronomia Interativa | por Felix e Jimmy")

# Fase da Lua
st.subheader("🌒 Fase Atual da Lua")
moon_phase_api = "https://api.farmsense.net/v1/moonphases/?d=now"
try:
    moon_data = requests.get(moon_phase_api).json()[0]
    st.markdown(f"**Fase atual:** {moon_data['Phase']}")
    st.markdown(f"**Iluminação:** {moon_data['Illumination']}%")
except:
    st.warning("Erro ao obter dados da Lua.")

# Atividade Solar
st.subheader("☀️ Atividade Solar - Flares Recentes")
solar_api = "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"
try:
    solar_data = requests.get(solar_api).json()
    solar_df = pd.DataFrame(solar_data)
    solar_df['time_tag'] = pd.to_datetime(solar_df['time_tag'])
    fig_solar = px.scatter(solar_df, x='time_tag', y='flux', color='class_type',
                           title='Flares solares (X-ray)', labels={'flux': 'Intensidade', 'time_tag': 'Data/Hora'})
    st.plotly_chart(fig_solar, use_container_width=True)
except:
    st.warning("Erro ao obter dados solares.")

# Terremotos
st.subheader("🌍 Terremotos em Tempo Real")
earthquake_api = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson"
try:
    quake_data = requests.get(earthquake_api).json()['features']
    quake_df = pd.DataFrame([{
        'place': q['properties']['place'],
        'magnitude': q['properties']['mag'],
        'time': datetime.utcfromtimestamp(q['properties']['time'] / 1000.0),
        'lat': q['geometry']['coordinates'][1],
        'lon': q['geometry']['coordinates'][0],
        'depth': q['geometry']['coordinates'][2]
    } for q in quake_data])

    fig_quake = px.scatter_mapbox(quake_df, lat='lat', lon='lon',
                                  color='magnitude', size='magnitude',
                                  hover_name='place', zoom=1,
                                  mapbox_style="carto-darkmatter")
    st.plotly_chart(fig_quake, use_container_width=True)
    st.dataframe(quake_df)
except:
    st.warning("Erro ao obter dados de terremotos.")

# Correlação
st.subheader("🔄 Correlação Visual: Flares x Terremotos")
try:
    if not solar_df.empty and not quake_df.empty:
        fig_corr = px.timeline(pd.concat([
            solar_df[['time_tag']].rename(columns={'time_tag': 'event'}).assign(type='Solar Flare'),
            quake_df[['time']].rename(columns={'time': 'event'}).assign(type='Terremoto')
        ]), x_start='event', x_end='event', y='type', color='type')
        fig_corr.update_yaxes(categoryorder='array', categoryarray=['Terremoto', 'Solar Flare'])
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Dados insuficientes para correlação.")
except:
    st.warning("Erro ao gerar gráfico de correlação.")
