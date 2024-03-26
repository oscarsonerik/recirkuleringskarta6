import streamlit as st
import numpy as np
import streamlit as st
import geopandas as gpd
import pandas as pd
import streamlit.components.v1 as stc
import matplotlib.pyplot as plt
import numpy as np
import Calc_streamlit_6 as calc_last
import time
st.set_page_config(page_title="Examensarbete", page_icon=":world_map:", layout="centered") # ":potable_water:"

# '''""""""'''
# Import the map to streamlit
# '''""""""'''

# This doesn't work..but it would be better
#path_to_html = 'index.html'
#with open(path_to_html, 'r', encoding="utf-8") as f:
#    html_data = f.read()
#st.components.v1.html(html_data, height=800, width=1200, scrolling=True)    
#https://docs.streamlit.io/1.30.0/library/components/components-api#stiframe

# To mirror the map on the streamlit window. The map needs to be online (website) by it self.
st.header("Recirkuleringskarta")
map = st.components.v1.iframe('https://oscarsonerik.github.io/endastindex/',height=400)
#https://oscarsonerik.github.io/endastindex/
#http://127.0.0.1:5500/index.html#14/
#"""""""""
# Input
#"""""""""
st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
# arean = st.number_input("Ange önskad takarea [m²]", value=0.0, step=0.5)
# magazinsize = st.number_input("Ange storlek på magazintank [m³]", value=0.0, step=0.5)
# water_use = st.number_input("Ange vattenanvändning [l/dag]", value=0.0, step=0.5)
st.subheader("Scenario för regnvattenanvändning")

# st.markdown("""
#     <style>
#     .stSlider [data-baseweb=slider]{
#         width: 150%;
#         margin: 0 auto;
#     }c
#     </style>
#     """,unsafe_allow_html=True)

#arean = st.slider("Ange takarea för regnvatteninsamling [m²]", 
#    min_value=0.0, max_value=1000.0,step=1.0, format="%.1f")
arean = st.slider("Ange takarea för regnvatteninsamling [m²]", 
    min_value=0, max_value=1000,step=1)
#st.write("Taakarea", arean)
magazinsize = st.slider("Ange storlek på regnvattenmagasinet [m³]", 
    min_value=0, max_value=100,step=1)
#st.write("Tankstorlek:", magazinsize)
water_use = st.slider("Ange vattenbehov [l/d]", 
    min_value=0, max_value=1000,step=1)
#st.write("Vattenbehov [l/d]:", water_use)
wateruseday = water_use * 0.001

st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)


#"""""""""
# Calculations
#"""""""""

# Read the CSV file into a DataFrame
df = pd.read_csv('SMHI/SMHI_modified3.csv')
day = df['Dagar']
prec = df['Precip Medel']
temp = df['Temperature Medel']

# Call on GetData in Calculation.py file
svar = calc_last.GetData(magazinsize, water_use, arean)

print("__Data mellan 2014-2022__")
print(f'Vattenmängd som kommer in i systemet {round(sum(svar[7]),2)}')
print(f'Rad 1. Vattenmängd använt från tanken: {round(svar[0],5)}')
print(f'Rad 2. Vattenmägd utanför tanken: {round(svar[1],5)}')
print(f'Rad 3. Vattemmängd kvar i tanken: {round(svar[2],5)}')
print(f'Rad 4. Vattenmängd kvar på taket: {round(svar[3],5)}')
total = svar[0]+svar[1]+svar[2]+svar[3]
print(f'Vattenmängd som kommer ut i systemet {round(total,2)}\n')
print("\t >> Tester för modellen 2014-2022<<")
if round(total,2) == round(sum(svar[7]),2):
    print("\t >> Modellen stämmer <<")
if svar[0] == sum(svar[5]):
    print("\t >> Appendar rätt upptagen vattenmängd <<")
if svar[1] == sum(svar[6]):
    print("\t >> Appendar rätt vattenförlust <<\n")
# plt.plot(svar[5]); plt.figure(2); plt.plot(svar[6]); plt.show()
#plt.plot(svar[4]); plt.show()
    
# Create a new data-set --> an average year based on the model run. New data-set created by Make365. 
print("__Skapar ett nytt dataset - avg_2014-2022 år__\n")
upptag = svar[5]
losten = svar[6]
prec_M3 = svar[7]
avg_year_365 = calc_last.Make365(upptag, losten, prec_M3)

wateruseday = water_use * 0.001
print(f"Vattenmängd som samlas in på takyta", round(sum(avg_year_365[2]),3), "m³/år.")
print(f'Önskad mängd regnvatten utnyttjad: {round((wateruseday*365),3)} m³/år. ')
print(f"Mängd regnvatten som inte får plats i vattentanken:", round(sum(avg_year_365[1]),3), " m³.\n")
print(f'Din input ger {round(sum(avg_year_365[0]),3)} m³ utnyttjad regnvatten per år.') # Blir inte exakt rätt då vi inte hämtar något vatten första dagen om det inte är någon nederbörd. First data dilemma.
#print("Mängd regnvatten kvar i tanken efter körning:", round((svar[2]/9),4), " m³.")
#procent_upptag = sum(avg_year_365[0]) / (wateruseday*365)
#print(f'Regnvatten står för {round(procent_upptag,4)*100} % av önskat behov under året.')
print(f'Mängd dricksvatten taget från kran {round((wateruseday*365) - sum(avg_year_365[0]),3)} m³/år.')

print('')

# Call on MonthDisp to get data over how water is distributed over each month for avg year
month_avg = calc_last.MonthDisp(avg_year_365)
#print(month_avg)


#"""""""""
#Output
#"""""""""


st.write("# Resultat")
st.write("Vattenmängd som samlas in på takyta", round(sum(avg_year_365[2]),1), "m³/år.")
st.write("Önskat återvunnet regnvatten till hushåll", round((wateruseday*365),1), "m³/år.")
st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)

# st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
st.write("Vattenmängd använt från vattentanken:", round(sum(avg_year_365[0]),1), "m³/år.")
#st.write("Mängd regnvatten som inte får plats i vattentanken:", round(sum(avg_year_365[1]),4), " m³.")
#st.write("Mängd regnvatten kvar i tanken efter körning:", round((svar[2]/9),4), " m³.")
procent_upptag = sum(avg_year_365[0]) / (wateruseday*365)
st.write("Andel av behovet som kommer täckas av regnvatten:", round((procent_upptag*100),1), " %.")
st.write("Mängd dricksvatten som behövs från annan källa:", round((wateruseday*365) - sum(avg_year_365[0]),1), " m³.")

col1, col2 = st.columns(2)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
# Plot the results
with col1:
    plt.figure(figsize=(8, 6))
    plt.bar(months, month_avg[0])
    plt.xlabel('Månad')#, fontsize=7)
    plt.ylabel('m³')#, fontsize=7)
    plt.title('Genomsnittlig nederbörd som faller på taket')#, fontsize = 8)
    plt.tick_params(axis='both', which='major')#, labelsize=5)  # Adjust tick label font size
    plt.ylim(0, max(month_avg[0])+ max(month_avg[0]) * 0.1)
    st.pyplot(plt.gcf())

with col2:
    plt.figure(figsize=(8, 6))
    plt.bar(months, month_avg[1], color='darkorange')
    plt.xlabel('Månad')
    plt.ylabel('m³')
    plt.title('Genomsnittlig uttagsvolym från regnvattentanken')
    plt.ylim(0, max(month_avg[1])+ max(month_avg[1]) * 0.1)
    st.pyplot(plt.gcf())

# PLot Medelvärde av volym förlorad regnvatten
# plt.figure(figsize=(8, 6))
# plt.bar(months, month_avg[2], color='#FF5733')
# plt.xlabel('Månad')
# plt.ylabel('Volym förlorad regnvatten m³')
# plt.title('Medelvärde av volym förlorad regnvatten')
# st.pyplot(plt.gcf())

# Vill plotta en plotta för varje månad, dels mängd från regnvatten, regnvatten från drickskran och sedan totalt behov för månad
# Ta fram mängd dricksvatten som används för varje månad istället för regnvatten
antal_dagar_månad = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
wateruse_month = [i * wateruseday for i in antal_dagar_månad]
# print(antal_dagar_månad); print(wateruseday); print(wateruse_month)
dricksvatten_mån = np.array(wateruse_month) - np.array(month_avg[1])
x = months
x = np.arange(len(months))
y1 = wateruse_month
y2 = month_avg[1]
y3 = dricksvatten_mån
bar_width = 0.1

data = {'Totalt vattenbehov': wateruse_month,
        'Regnvattenanvändning': month_avg[1],
        'Dricksvattenanvändning': dricksvatten_mån}
#dfen = pd.DataFrame(data, index=months)
#dfen.plot.bar(figsize=(10, 6))
dfen = pd.DataFrame(data, index=months)
ax = dfen.plot.bar(figsize=(10, 6))
plt.title('Fördelning av vattenanvändning')
plt.xlabel('Månad')
plt.ylabel('m³')
plt.xticks(x+bar_width, months)
plt.grid(False)
#plt.legend()
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.ylim(0, max(y1)+ max(y1) * 0.1)
plt.tight_layout()
st.pyplot(plt.gcf())

# Uppehållstid vid total omblandning: Volym/Flöde, ex. m3/m3/dag

df_med_last_14 = pd.read_csv('SMHI/SMHI_2014_2020.csv',  delimiter=";", decimal=",")
years = df_med_last_14['År siffra']
days_per_year = 365

plt.figure(figsize=(10, 4))
plt.plot(svar[4])
# Calculate the position of the ticks to be in the middle of the year intervals (around June)
tick_positions = [days_per_year * (i + 0.5) for i in range(len(years) // days_per_year)]
plt.xticks(
    tick_positions, #range(0, len(svar[4]), days_per_year),
    years[::days_per_year],  # Selecting only the first day of each year for labeling
    rotation=45  # Rotate labels for better readability
)
plt.xlabel('År')
plt.ylabel('m³')
plt.title('Volym vatten i tanken per dag mellan 2014-2022')
#plt.plot(months, svar[4])
for i in range(0, len(svar[4]), days_per_year):
    plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.5)  # Vertical line at the start of the year
    plt.axvline(x=i+days_per_year-1, color='gray', linestyle='--', linewidth=0.5)  # Vertical line at the end of the year
st.pyplot(plt.gcf())


