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
        try:
            gezilecek_yerler = createDict(placeDetails)
            gezilecek_yerler_list = gezilecek_yerler[placeDetails]
        except:
            gezilecek_yerler_list = ["Lütfen yalnızca şehir ismi giriniz. Bilgi bulunamadı."]
        
        
        #* Show the details
        with tab1Name:
            st.write(name)
        with tab2PlacesToVisit:
            for yer in gezilecek_yerler_list:
                st.write(f"- {yer}")
        with tab3Address:
            st.write(address)
        with tab4Phone:
            st.write(phone)
        with tab5Website:
            st.write(website)
        #* Show the photos
        with tab6Photos:
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

st.cache_data(ttl=20, show_spinner=False)
def createDict(key):
    gezilecek_yerler = {
    "Adana": ["Adana Merkez Parkı", "Seyhan Baraj Gölü", "Sabancı Merkez Camii"],
    "Adıyaman": ["Nemrut Dağı", "Adıyaman Müzesi", "Perre Antik Kenti"],
    "Afyonkarahisar": ["Afyon Kalesi", "Termal Kaplıcalar", "Afyonkarahisar Zafer Anıtı"],
    "Ağrı": ["Ağrı Dağı", "İshak Paşa Sarayı", "Noah's Ark National Park"],
    "Aksaray": ["Ihlara Vadisi", "Sultan Marshes", "Aksaray Ulu Camii"],
    "Amasya": ["Amasya Kalesi", "Yeşilırmak Nehri", "Amasya Safranbolu Evleri"],
    "Ankara": ["Anıtkabir", "Atatürk Orman Çiftliği", "Ankara Kalesi"],
    "Antalya": ["Antalya Kaleiçi", "Düden Şelalesi", "Antalya Müzesi"],
    "Ardahan": ["Çıldır Gölü", "Ardahan Kalesi", "Tarihi Kale Camii"],
    "Artvin": ["Şavşat Karagöl", "Artvin Şehir Merkezi", "Hopa Sahili"]
    }
    gezilecek_yerler["Aydın"] = ["Didim Antik Kenti", "Kuşadası Plajları", "Akbük Koyu"]
    gezilecek_yerler["Balıkesir"] = ["Ayvalık Cunda Adası", "Troya Antik Kenti", "Kazdağı Milli Parkı"]
    gezilecek_yerler["Bilecik"] = ["Söğüt Köyü", "Bilecik Şeyh Edebali Türbesi", "Bozüyük Atatürk Evi"]
    gezilecek_yerler["Bingöl"] = ["Yeraltı Şehri", "Karlıova Kayak Merkezi", "Kral Kızı Kalesi"]
    gezilecek_yerler["Bitlis"] = ["Nemrut Krater Gölü", "Bitlis Kalesi", "Ahlat Selçuklu Mezarlıkları"]
    gezilecek_yerler["Bolu"] = ["Yedigöller Milli Parkı", "Abant Gölü", "Gölcük Tabiat Parkı"]
    gezilecek_yerler["Burdur"] = ["Burdur Müzesi", "Salda Gölü", "Burdur Göleti"]
    gezilecek_yerler["Bursa"] = ["Uludağ Kayak Merkezi", "Bursa Ulu Camii", "Bursa Kalesi"]
    gezilecek_yerler["Çanakkale"] = ["Çanakkale Şehitler Abidesi", "Troya Antik Kenti", "Bozcaada"]
    gezilecek_yerler["Çankırı"] = ["Çankırı Kalesi", "Atatürk Evi", "Çankırı Müzesi"]
    gezilecek_yerler["Çorum"] = ["Hattuşaş Antik Kenti", "Alacahöyük Höyüğü", "Çorum Müzesi"]
    gezilecek_yerler["Denizli"] = ["Pamukkale Travertenleri", "Hierapolis Antik Kenti", "Laodikeia Antik Kenti"]
    gezilecek_yerler["Diyarbakır"] = ["Diyarbakır Surları", "Hevsel Bahçeleri", "Mardinkapı"]
    gezilecek_yerler["Edirne"] = ["Selimiye Camii", "Edirne Kalesi", "Tarihi Edirne Evleri"]
    gezilecek_yerler["Elazığ"] = ["Harput Kalesi", "Buzluk Mağarası", "XV. Yüzyıl Kümbeti"]
    gezilecek_yerler["Erzincan"] = ["Kemaliye (Eğin)", "Erzincan Müzesi", "Terzibaba Türbesi"]
    gezilecek_yerler["Erzurum"] = ["Palandöken Kayak Merkezi", "Tortum Gölü", "Atatürk Üniversitesi Botanik Bahçesi"]
    gezilecek_yerler["Eskişehir"] = ["Porsuk Çayı", "Odunpazarı Evleri", "Eskişehir Bilim, Sanat ve Kültür Parkı"]
    gezilecek_yerler["Gaziantep"] = ["Zeugma Mozaik Müzesi", "Gaziantep Kalesi", "Bakırcılar Çarşısı"]
    gezilecek_yerler["Giresun"] = ["Giresun Adası", "Giresun Kalesi", "Giresun Müzesi"]
    gezilecek_yerler["Gümüşhane"] = ["Gümüşhane Kalesi", "Karaca Mağarası", "Haho Kilisesi"]
    gezilecek_yerler["Hakkari"] = ["Cennet Vadisi", "Şemdinli Kayak Merkezi", "Sümbül Vadisi"]
    gezilecek_yerler["Hatay"] = ["Antakya Mozaik Müzesi", "St. Pierre Kilisesi", "Harbiye Şelalesi"]
    gezilecek_yerler["Isparta"] = ["Eğirdir Gölü", "Sagalassos Antik Kenti", "Isparta Müzesi"]
    gezilecek_yerler["Mersin"] = ["Silifke Kalesi", "Kızkalesi", "Tarsus Ulu Camii"]
    gezilecek_yerler["İstanbul"] = ["Ayasofya", "Topkapı Sarayı", "Kapalıçarşı"]
    gezilecek_yerler["İzmir"] = ["Efes Antik Kenti", "Kemeraltı Çarşısı", "Asansör"]
    gezilecek_yerler["Kahramanmaraş"] = ["Kahramanmaraş Kalesi", "Cendere Köprüsü", "Bakırcılar Çarşısı"]
    gezilecek_yerler["Karabük"] = ["Safranbolu Evleri", "Safranbolu Çarşısı", "Kent Ormanı"]
    gezilecek_yerler["Karaman"] = ["Ermenek Baraj Gölü", "Alahan Manastırı", "Binbir Kilise"]
    gezilecek_yerler["Kars"] = ["Ani Harabeleri", "Kars Kalesi", "Sarıkamış Şehitliği"]
    gezilecek_yerler["Kastamonu"] = ["İnebolu Eski Evleri", "Kastamonu Kalesi", "Valla Canyon"]
    gezilecek_yerler["Kayseri"] = ["Erciyes Kayak Merkezi", "Gevasa Hanı", "Kayseri Kalesi"]
    gezilecek_yerler["Kırıkkale"] = ["Karakeçili Göleti", "Çamlıca Göleti", "Kalecik Göleti"]
    gezilecek_yerler["Kırklareli"] = ["Dupnisa Mağarası", "Kıyıköy Sahili", "Beylik Dere Tabiat Parkı"]
    gezilecek_yerler["Kırşehir"] = ["Tarihi Kırşehir Evleri", "Cacabey Medresesi", "Kırşehir Kalesi"]
    gezilecek_yerler["Kilis"] = ["Zeugma Mozaik Müzesi", "Kilis Kalesi", "Kilis Orman Çadır Kampı"]
    gezilecek_yerler["Kocaeli"] = ["Seka Parkı", "İzmit Saat Kulesi", "Kartepe Kayak Merkezi"]
    gezilecek_yerler["Konya"] = ["Mevlana Müzesi", "Karatay Medresesi", "Türk Hava Kurumu Müzesi"]
    gezilecek_yerler["Kütahya"] = ["Kütahya Kalesi", "Aizanoi Antik Kenti", "Kossuth Evi"]
    gezilecek_yerler["Malatya"] = ["Aslantepe Höyüğü", "Malatya Kalesi", "Battalgazi Grand Mosque"]
    gezilecek_yerler["Manisa"] = ["Sardes Antik Kenti", "Manisa Kalesi", "Niobe Heykeli"]
    gezilecek_yerler["Mardin"] = ["Mardin Evleri", "Deyrulzafaran Manastırı", "Kasımiye Medresesi"]
    gezilecek_yerler["Mersin"] = ["Silifke Kalesi", "Cennet ve Cehennem Mağaraları", "Mersin Aqualand Su Parkı"]
    gezilecek_yerler["Muğla"] = ["Bodrum Antik Tiyatrosu", "Marmaris Kalesi", "Oludeniz Sahili"]
    gezilecek_yerler["Muş"] = ["Muş Kalesi", "Muş Atatürk Anı Evi", "Havutlu Kervansarayı"]
    gezilecek_yerler["Nevşehir"] = ["Kapadokya Vadileri", "Göreme Açık Hava Müzesi", "Kaymaklı Yeraltı Şehri"]
    gezilecek_yerler["Niğde"] = ["Aladağlar Milli Parkı", "Niğde Kalesi", "Borçka Karagöl"]
    gezilecek_yerler["Ordu"] = ["Boztepe Tepesi", "Perşembe Yaylası", "Ordu Kalesi"]
    gezilecek_yerler["Osmaniye"] = ["Kastabala Antik Kenti", "Osmaniye Kent Müzesi", "Karatepe-Aslantaş Açık Hava Müzesi"]
    gezilecek_yerler["Rize"] = ["Ayder Yaylası", "Rize Kalesi", "Fırtına Vadisi"]
    gezilecek_yerler["Sakarya"] = ["Sapanca Gölü", "Sakarya Müzesi", "Taraklı Tarihi Evleri"]
    gezilecek_yerler["Samsun"] = ["Atatürk Caddesi", "Amisos Tepesi", "Bandırma Vapuru Müzesi"]
    gezilecek_yerler["Siirt"] = ["Cizre Gümrük Kapısı", "Siirt Kalesi", "Botan Vadisi"]
    gezilecek_yerler["Sinop"] = ["Sinop Cezaevi Müzesi", "Sinop Kalesi", "Akliman Plajı"]
    gezilecek_yerler["Sivas"] = ["Divriği Ulu Camii ve Darüşşifası", "Atatürk Caddesi", "Gökpınar Gölü"]
    gezilecek_yerler["Şanlıurfa"] = ["Göbeklitepe", "Şanlıurfa Balıklı Göl", "Rızvaniye Camii"]
    gezilecek_yerler["Şırnak"] = ["Cudi Dağı Milli Parkı", "Şırnak Kalesi", "Beytüşşebap Şelalesi"]
    gezilecek_yerler["Tekirdağ"] = ["Namık Kemal Evi", "Rakoczi Müzesi", "Tekirdağ Kalesi"]
    gezilecek_yerler["Tokat"] = ["Tokat Kalesi", "Atatürk Caddesi", "Ballıca Mağarası"]

    return gezilecek_yerler

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
        tab1Name, tab2PlacesToVisit ,tab3Address, tab4Phone, tab5Website, tab6Photos= st.tabs(["Yer Adı", "Ziyaret Edilecek Yerler", "Adres", "Telefon", "Web Sitesi", "Fotoğraflar"])
        showTheDatils(api_key_place, IDofPlace)
        
        









