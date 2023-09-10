import requests
import streamlit as st
import folium
import polyline
import time

#* Display title
st.set_page_config(page_title="Yol Bul", layout="centered")

#* Read API keys
@st.cache_data
def read_api_key():
    api_key = open("key.txt", "r").read()
    api_key_place = open("placeapi.txt", "r").read()
    return api_key, api_key_place
api_key, api_key_place = read_api_key()


#* API base url
url = "https://maps.googleapis.com/maps/api/directions/json"


#* Get coordinates of a location
@st.cache_data(ttl=1800, show_spinner=False)
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

#* Get place ID
@st.cache_data(ttl=1800, show_spinner=False)
def get_place_id(api_key_place, place):
    url_place = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place}&inputtype=textquery&fields=place_id&key={api_key_place}'
    response_place = requests.get(url_place)
    data_place = response_place.json()
    if 'candidates' in data_place and data_place['candidates']:
        place_id = data_place['candidates'][0]['place_id']
        return place_id
    else:
        st.error('Yer bulunamadı veya hata oluştu.')
    #return place_id


def display_coordinates_on_map(api_key, origin, destination, waypoints):
    #* Get coordinates
    origin_coordinates = get_coordinates(api_key, origin)
    destination_coordinates = get_coordinates(api_key, destination)

    if origin_coordinates and destination_coordinates:
        #* Create map
        m = folium.Map(location=[(origin_coordinates[0] + destination_coordinates[0]) / 2, (origin_coordinates[1] + destination_coordinates[1]) / 2], zoom_start=6)

        #* Add color to map > Decided to not use it
        #folium.TileLayer('Stamen Watercolor').add_to(m)
        #folium.TileLayer('OpenStreetMap').add_to(m)

        #* Add path to map
        folium.PolyLine(
        locations=decoded_path,
        color='green'
        ).add_to(m)

        #* Add marker on starting point
        folium.Marker(
            location=origin_coordinates,
            icon= folium.Icon(color="green", icon="home",icon_color="white"),
            popup=origin
        ).add_to(m)

        #* Add marker on destination point
        folium.Marker(
            location=destination_coordinates,
            icon= folium.Icon(color="red", icon="stop", icon_color="white"),
            popup=destination
        ).add_to(m)

        #* Add markers on waypoints
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
        
        #* Add delay
        with container_mapandinfo:
            with st.spinner("Harita yükleniyor..."):
                # Remove success text
                time.sleep(1.5)
                succes_text.empty()

        #* Add the processed map to the placeholder
        with placeholder_map.container():
            #* Display map
            st.components.v1.html(m._repr_html_(), width=750, height=450)
        with container_mapandinfo:
            with containerInfo:
                st.caption(distanceInfo + ", " + durationInfo)
                

#* Show the details of the place
def showTheDatils(api_key_place, place_id):
    url_place_details = f'https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={api_key_place}'
    response_place_details = requests.get(url_place_details)
    data_place_details = response_place_details.json()  

    #* Check status
    if 'result' in data_place_details:
        place_details = data_place_details['result']
        name = place_details.get('name', 'Bilgi yok')
        address = place_details.get('formatted_address', 'Bilgi yok')
        phone = place_details.get('formatted_phone_number', 'Bilgi yok')
        website = place_details.get('website', 'Bilgi yok')
        photos = place_details.get('photos', [])
        tab_count = (len(photos) +2) // 3
        tab_titles = [f'Sayfa {i+1}' for i in range(tab_count)]
        
        
        #* Show the details
        with tab1Name:
            st.subheader(name)
        with tab2Address:
            st.subheader(address)
        with tab3Phone:
            st.subheader(phone)
        with tab4Website:
            st.subheader(website)
        #* Show the photos
        with tab5Photos:
            tabsOfPhotos = st.tabs(tab_titles)
            for i in range(tab_count):
                with tabsOfPhotos[i]:
                    start_index = i * 3
                    end_index = min(start_index + 3, len(photos))
                    cols = st.columns(3)
                    
                    for j in range(start_index, end_index):
                        photo_reference = photos[j].get('photo_reference', '')
                        photo_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key_place}'
                        with cols[j % 3]:
                            st.image(photo_url, caption="Şehir Fotoğrafı", use_column_width=True)   
    else:
        st.error('Yer detayları bulunamadı veya hata oluştu.')

#? Input section ----------------------------
# Display inputs
cols = st.columns(spec = [2,0.5],gap= "small")
with cols[0]:
    # Display inputs for origin, destination and waypoints
    origin = st.text_input("Başlangıç Noktası").title()
    destination = st.text_input("Varış Noktası").title()
    waypoints = st.text_input("Ara Noktalar", help="Ara noktaları virgül(,) veya tire(-) ile ayırın").title()
with cols[1]:
    #* Display input for navigation mode
    if 'navigation_mode' not in st.session_state:
        st.session_state['navigation_mode'] = "Araba"
    navigation_mode = st.radio("Navigasyon Modu Seçin:", ("Araba", "Toplu Taşıma", "Yaya"),key=st.session_state["navigation_mode"]) 
#? Input section end ------------------------

#* Display button
buttonDirections = st.button(label = "Yol Tarifi Al", key = "buttonDirections", type = "primary", disabled = False, use_container_width = False)

#* Created container for map and info to show them side by side
container_mapandinfo = st.container()

#* Create placeholder for map for changing it after button is clicked and process is done
placeholder_map = st.empty()

#! Decided to not show the map before button is clicked -----------------
# with container_mapandinfo:
#     # Display clean map
#     with placeholder_map.container():
#         m = folium.Map(location=[38.9637, 35.2433], zoom_start=6)
#         #folium.TileLayer('Stamen Watercolor').add_to(m)
#         st.components.v1.html(m._repr_html_(), width=750, height=450)
#! ----------------------------------------------------------------------
    
#* If button is clicked then process
if buttonDirections:

    #* Clear the placeholder > Dont need it anymore
    #placeholder_map.empty()
    #* Replace , and - with | for waypoints
    waypoints = waypoints.replace(",", "|").replace("-", "|")
    #* Optimize waypoints
    waypoints = f"optimize:true|{waypoints}"
    #* Get travel mode
    if navigation_mode == "Araba":
        navigation_mode = "driving"
    elif navigation_mode == "Toplu Taşıma":
        navigation_mode = "transit"
    else:
        navigation_mode = "walking"

    #* Make request
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": waypoints,
        "key": api_key,
        "mode": navigation_mode,
    }

    #* Get response
    response = requests.get(url, params=params)
    #* Get data
    data = response.json()

    #* Check status
    if data["status"] != "OK":
        #* Display error message
        error_text = ("Hata: " + data["status"] + ", Yol tarifi alınamadı!")
        st.error(error_text, icon="🚨")
    else:   
        #* Display success message
        with container_mapandinfo:
            succes_text = st.success("Yol tarifi alınıyor!",icon="🚗")
            
        #* Display on the map
        path_data = data["routes"][0]["overview_polyline"]["points"]
        decoded_path = polyline.decode(path_data)
        containerInfo = st.container()

        #* Get distance and duration
        distance = data["routes"][0]["legs"][0]["distance"]["text"]
        duration = data["routes"][0]["legs"][0]["duration"]["text"].replace("hours", "saat").replace("mins", "dakika").replace("days","gün")

        #* Because of we cant caption more than one variable, we need to combine them
        distanceInfo = ("Toplam mesafe: " + distance)
        durationInfo = ("Tahmini varış süresi: " + duration)
        #* Haritayı göster
        display_coordinates_on_map(api_key, origin, destination, waypoints)
        #* Streamlit experimental set query params
        st.experimental_set_query_params(
            start_point = origin,
            end_point = destination,
            waypoints = waypoints,
            travel_mode = navigation_mode,
                            )


#* Divider 
st.divider()
#* Get the place name from the user and create and button right next to it
col1, col2 = st.columns([2,1])
with col1:
    placeDetails = st.text_input("Yer Adı", label_visibility = "collapsed", placeholder="Detaylarını merak ettiğiniz yerin adını girin").title()
button_yer_bul = col2.button("Detayları Göster",type = "primary", disabled = False, use_container_width = True)

#* If button is clicked then process finding details of the place
#* First find the ID of the place
if button_yer_bul:
    IDofPlace = get_place_id(api_key_place, placeDetails)
    #* If ID is found then get details of the place
    if IDofPlace:
        tab1Name, tab2Address, tab3Phone, tab4Website, tab5Photos = st.tabs(["Yer Adı", "Adres", "Telefon", "Web Sitesi", "Fotoğraflar"])
        showTheDatils(api_key_place, IDofPlace)
        
        




