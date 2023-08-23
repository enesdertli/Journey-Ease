import streamlit as st
from streamlit_folium import st_folium
import folium

def main():
    st.title("Google Maps Rota Oluşturucu")

    m = folium.Map(location=[38.58, 27.43], zoom_start=8)
    folium.Marker([38.58, 27.43], popup="Manisa").add_to(m)
    st_data = st_folium(m, width=725)
    
   

if __name__ == "__main__":
    main()
