import googlemaps
import requests
import streamlit as st
import folium
import polyline
import pandas as pd
import time

# Read API key
api_key = open("key.txt", "r").read()
# API base url
url = "https://maps.googleapis.com/maps/api/directions/json"


# Get coordinates of a location
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


def display_coordinates_on_map(api_key, origin, destination, waypoints):
    # Get coordinates
    origin_coordinates = get_coordinates(api_key, origin)
    destination_coordinates = get_coordinates(api_key, destination)

    if origin_coordinates and destination_coordinates:
        # Create map
        m = folium.Map(location=[(origin_coordinates[0] + destination_coordinates[0]) / 2, (origin_coordinates[1] + destination_coordinates[1]) / 2], zoom_start=6)

        # Güzergahı haritaya ekleyin
        folium.PolyLine(
        locations=decoded_path,
        color='green'
        ).add_to(m)

        # Add marker on starting point
        folium.Marker(
            location=origin_coordinates,
            icon= folium.Icon(color="green", icon="home",icon_color="white"),
            popup=origin
        ).add_to(m)

        # Add marker on destination point
        folium.Marker(
            location=destination_coordinates,
            icon= folium.Icon(color="red", icon="stop", icon_color="white"),
            popup=destination
        ).add_to(m)

        # Add markers on waypoints
        if waypoints:
            waypoints_list = waypoints.split("|")
            for waypoint in waypoints_list:
                waypoint_coordinates = get_coordinates(api_key, waypoint.strip())
                if waypoint_coordinates:
                    folium.Marker(
                        location=waypoint_coordinates,
                        icon= folium.Icon(color="blue", icon="play", icon_color="white"),
                        popup=waypoint
                    ).add_to(m)

        # Add color to map
        folium.TileLayer('Stamen Watercolor').add_to(m)
        #folium.TileLayer('OpenStreetMap').add_to(m)

        # Remove success text
        succes_text.empty()
        # Add the processed map to the placeholder
        with placeholder_map.container():
            # Display map
            st.components.v1.html(m._repr_html_(), width=750, height=450)
        with container_mapandinfo:
            with containerInfo:
                st.caption(distanceInfo)
                st.caption(durationInfo)

# Display title
st.set_page_config(page_title="Yol Bul", page_icon= "random", layout="centered")

# Display inputs
cols = st.columns([2,1])
with cols[0]:
    # Display inputs for origin, destination and waypoints
    origin = st.text_input("Başlangıç Noktası").title()
    destination = st.text_input("Varış Noktası").title()
    waypoints = st.text_input("Ara Noktalar", help="Ara noktaları virgül(,) veya tire(-) ile ayırın").title()

with cols[1]:
    # Display input for navigation mode
    navigation_mode = st.radio("Navigasyon Modu Seçin:", ("Araba", "Toplu Taşıma", "Yaya"))
    
# Display button
button_yol_tarifi = st.button("Yol Tarifi Al")

# Created container for map and info to show them side by side
container_mapandinfo = st.container()

# Create placeholder for map for changing it after button is clicked and process is done
placeholder_map = st.empty()

with container_mapandinfo:
    # Display clean map
    with placeholder_map.container():
        m = folium.Map(location=[38.9637, 35.2433], zoom_start=6)
        folium.TileLayer('Stamen Watercolor').add_to(m)
        st.components.v1.html(m._repr_html_(), width=750, height=450)
    
# If button is clicked then process
if button_yol_tarifi:
    # Clear the placeholder
    placeholder_map.empty()

    # Replace , and - with | for waypoints
    waypoints = waypoints.replace(",", "|").replace("-", "|")
    # Optimize waypoints
    waypoints = f"optimize:true|{waypoints}"
    # Get travel mode
    if navigation_mode == "Araba":
        navigation_mode = "driving"
    elif navigation_mode == "Toplu Taşıma":
        navigation_mode = "transit"
    else:
        navigation_mode = "walking"

    # Make request
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": waypoints,
        "key": api_key,
        "mode": navigation_mode,
    }

    # Get response
    response = requests.get(url, params=params)
    # Get data
    data = response.json()

    # Check status
    if data["status"] != "OK":
        # Display error message
        error_text = ("Hata: " + data["status"] + ", Yol tarifi alınamadı!")
        st.error(error_text, icon="🚨")
    else:   
        # Display success message
        with container_mapandinfo:
            succes_text = st.success("Yol tarifi alınıyor!",icon="🚗")
            
        # Display on the map
        path_data = data["routes"][0]["overview_polyline"]["points"]
        decoded_path = polyline.decode(path_data)
        containerInfo = st.container()

        # Get distance and duration
        distance = data["routes"][0]["legs"][0]["distance"]["text"]
        duration = data["routes"][0]["legs"][0]["duration"]["text"].replace("hours", "saat").replace("mins", "dakika").replace("days","gün")

        # Because of we cant caption more than one variable, we need to combine them
        distanceInfo = ("Toplam mesafe: " + distance)
        durationInfo = ("Tahmini varış süresi: " + duration)
        # Haritayı göster
        display_coordinates_on_map(api_key, origin, destination, waypoints)