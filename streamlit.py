import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Global değişkenler
start_coordinates = None
end_coordinates = None



def get_coordinates(api_key, location_name):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        "address": location_name,
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data["status"] == "OK":
        results = data["results"]
        if results:
            location = results[0]["geometry"]["location"]
            return location["lat"], location["lng"]
    else:
        st.error("Konum bilgisi alınamadı. Lütfen geçerli bir konum girin.")
    
    return None


def main():
    st.title("Yol Tarifi Uygulaması")
    api_key = "AIzaSyAvUEMGznowOozaDggLP1ySoYkq2901jng"

    global start_coordinates
    global end_coordinates

    # Kullanıcıdan alınan bilgileri alın
    start_point = st.text_input("Başlangıç Noktası", 
                                help="Başlangıç noktasını girin",
                                placeholder="Başlangıç noktasını girin",
                                )

    end_point = st.text_input("Varış Noktası",
                              help="Varış noktasını girin",
                              placeholder="Varış noktasını girin",
                              )

    way_point = st.text_input("Ara Noktalar", 
                              help="Ara noktaları tek tek girin",
                              placeholder="Ara noktaları girin. Birden çok eklemek için aralarına virgül koyarak yazın. Örn: Ankara, İstanbul, İzmir",
                              )

    if st.button("Uygun Rotayı Bul"):
        start_coordinates = get_coordinates(api_key, start_point)
        end_coordinates = get_coordinates(api_key, end_point)
        print({start_point: start_coordinates, end_point: end_coordinates})
        
        
if __name__ == "__main__":
    main()
    map = folium.Map(location=start_coordinates, zoom_start=12)
    st_folium(map, width=800, height=600)



