import googlemaps
import requests
import streamlit as st
import folium
import polyline

# Read API key
api_key = open("key.txt", "r").read()
# API base url
url = "https://maps.googleapis.com/maps/api/directions/json"

# Display title
st.title("Yol Bul")

# Display inputs
origin = st.text_input("Başlangıç Noktası")
destination = st.text_input("Varış Noktası")
waypoints = st.text_input("Ara Noktalar", help="Ara noktaları virgül ile ayırın")

# Display button
if st.button("Yol Tarifi Al"):

    # Replace , with | for waypoints
    waypoints = waypoints.replace(",", "|")
    # Optimize waypoints
    waypoints = f"optimize:true|{waypoints}"

    # Make request
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": waypoints,
        "key": api_key
    }

    # Get response
    response = requests.get(url, params=params)
    # Get data
    data = response.json()

    # Check status
    if data["status"] != "OK":
        st.write("Error:", data["status"])

    # Display on the map
    path_data = data["routes"][0]["overview_polyline"]["points"]
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=13)
    decoded_path = polyline.decode(path_data)

    # Güzergahı haritaya ekleyin
    folium.PolyLine(
    locations=decoded_path,
    color='blue'
    ).add_to(m)

    # Haritayı göster
    st.components.v1.html(m._repr_html_(), width=800, height=600)







