import streamlit as st
from streamlit_folium import st_folium
import requests


def main():

    st.title("Google Maps Rota Oluşturucu")
    st.markdown("<h3 style='text-align: left;'>Harita</h3>", unsafe_allow_html=True)
    
    # Google Haritalar iframe URL
    iframe_url = """
        <iframe
          width="700"
          height="450"
          src="https://www.google.com/maps/embed/v1/place?q=Amasya&key=AIzaSyAvUEMGznowOozaDggLP1ySoYkq2901jng"
          frameborder="0"
          style="border:0"
          allowfullscreen
        ></iframe>
    """
    st.write(iframe_url, unsafe_allow_html=True)

    
    #* Başlangıç Noktası
    #st.markdown("<h3 style='text-align: left;'>Başlangıç Noktası</h3>", unsafe_allow_html=True)
    start_point = st.text_input("Başlangıç Noktası", 
                                help="Başlangıç noktasını girin",
                                placeholder="Başlangıç noktasını girin",
                                )

    
    #* Varış Noktası
    end_point = st.text_input("Varış Noktası",
                              help="Varış noktasını girin",
                              placeholder="Varış noktasını girin",
                              )
    

    #* Ara Noktalar
    way_points = st.text_input("Ara Noktalar", 
                              help = "Ara noktaları tek tek girin",
                              placeholder="Ara noktaları girin. Birden çok eklemek için aralarına virgül koyarak yazın. Örn: Ankara, İstanbul, İzmir",
                              )
    if st.button("Yol Tarifi Bul"):
        get_directions(api_key, start_point, end_point, way_points)

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
        print("Error:", data["status"])
    
    return None


def get_directions(api_key, origin, destination, waypoints):
    origin_coordinates = get_coordinates(api_key, origin)
    destination_coordinates = get_coordinates(api_key, destination)
    
    if origin_coordinates and destination_coordinates:
        base_url = "https://maps.googleapis.com/maps/api/directions/json"
        
        params = {
            "origin": f"{origin_coordinates[0]},{origin_coordinates[1]}",
            "destination": f"{destination_coordinates[0]},{destination_coordinates[1]}",
            "key": api_key
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
    
      
    
        if data["status"] == "OK":
            routes = data["routes"]
            for route in routes:
                print("Route Summary:", route["summary"])
                print("Total Distance:", route["legs"][0]["distance"]["text"])
                print("Total Duration:", route["legs"][0]["duration"]["text"])
                print("Steps:")
                for step in route["legs"][0]["steps"]:
                    print(step["html_instructions"])
                    print("Distance:", step["distance"]["text"])
                    print("Duration:", step["duration"]["text"])
                    print("="*50)
        else:
            print("Error:", data["status"])

    else:
        print("Could not retrieve coordinates for origin or destination.")



api_key = "AIzaSyAvUEMGznowOozaDggLP1ySoYkq2901jng"

if __name__ == "__main__":
    main()
