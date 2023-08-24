import streamlit as st
from streamlit_folium import st_folium
import folium


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
    way_point = st.text_input("Ara Noktalar", 
                              help = "Ara noktaları tek tek girin",
                              placeholder="Ara noktaları girin. Birden çok eklemek için enter tuşuna basın",
                              )

    #When the button is clicked or the enter key is pressed while the text input is in focus, ara_nokta is added to the list and the text input is cleared. Then the list is displayed.
    # if st.button("Ara Nokta Ekle"):
    #     if way_point:
    #         way_points.append(way_point)
    #         st.session_state.enter_pressed = False  # Enter tuşuna tepkiyi sıfırla
    #         way_point = ""
    #         print(way_points)

    # # Ara Noktaları göster
    # st.header("Ara Noktalar")
    # for i, nokta in enumerate(way_points, 1):
    #     st.write(f"{i}. {nokta}")
        


        



    

if __name__ == "__main__":
    main()
