import streamlit as st

st.write("""
# My first app
Hello *world!*
""")

import streamlit as st
import geopandas as gpd
import pandas as pd
import streamlit.components.v1 as stc
import matplotlib.pyplot as plt
import numpy as np
import Calculations_streamlit as calc
#import Calculations_streamlit_avg_last as calc_last

st.markdown(
    """
    <link rel='stylesheet' href='static/css/styles.css'>
    <script src='static/js/labels.js'></script>
    """,
    unsafe_allow_html=True
)

path_to_html = 'index.html'

with open(path_to_html, 'r', encoding="utf-8") as f:
    html_data = f.read()

#https://docs.streamlit.io/1.30.0/library/components/components-api#stiframe
st.header("En recirkuleringskarta")
map = st.components.v1.iframe('http://127.0.0.1:5500/index.html#14/',height=500, width= 700)  # För att se hela hemsidan. Funkar sålänge man går live i samma map.
#st.components.v1.html(html_data, height=800, width=1200, scrolling=True)
#map = st.components.v1.iframe('https://api.lantmateriet.se/open/topowebb-ccby/v1/wmts',height=500, width= 700)

#
# Input
#

# arean = st.number_input("Ange önskad takarea [m²]", value=0.0, step=0.5)
# magazinsize = st.number_input("Ange storlek på magazintank [m³]", value=0.0, step=0.5)
# water_use = st.number_input("Ange vattenanvändning [l/dag]", value=0.0, step=0.5)

st.subheader("Sliders")
arean = st.slider("Ange önskad takarea [m²]", 
    min_value=0.0, max_value=1000.0,step=1.0)
st.write("Taakarea", arean)
magazinsize = st.slider("Ange storlek på magazintank [m³]", 
    min_value=0.0, max_value=100.0,step=1.0)
st.write("Tankstorlek:", magazinsize)
water_use = st.slider("Ange vattenbehov [l/d]", 
    min_value=0.0, max_value=1000.0,step=1.0)
st.write("Vattenbehov [l/d]:", water_use)

#
# Beräkningar
#
# Avrunda det angivna numret till en viss precision (t.ex. 2 decimaler)
# Allt i m, m2 och m3
rounded_arean = round(arean, 2) # m2
water_use_rev = water_use * 0.001 # l/dag --> (dm3 to m3) --> m3/dag
vatten_spar = rounded_arean * 365 * 0.001

# Read the CSV file into a DataFrame
df = pd.read_csv('SMHI_modified3.csv')
day = df['Dagar']
prec = df['Precip Medel']
temp = df['Temperature Medel']

#tanksize = 10                                     # m3 
#wateruseday = 150 * 0.001                         # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)
#roofarea = 50                                     # m2 
# def model_streamlit(tanksize, tankVol, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp):
svar = calc.TaInGeUt(magazinsize, water_use, arean)
#svar1 = calc_last.GetData(magazinsize, water_use, arean)
#print(resultat)

#
# Output
#
st.write("# Resultat")
st.write("Vattenmängd som samlas in på takyta", round(sum(svar[10]),1), "m³ per år.")
st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
st.write("Vattenmängd använt från vattentanken:", round(svar[0],3), "m³ per år.")
st.write("Vattenmägd som hamnar utanför tanken (pga fylld tank):", round(svar[1],2), "m³ per år.")
st.write("Vattemmängd kvar i tanken:", round(svar[2],2), "m³ per år.")
st.write("Vattenmängd kvar på taket:", svar[3], "m³ per år.")
st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
total = svar[0]+svar[1]+svar[2]+svar[3]
regn_proc = round(svar[0] / (water_use * 0.001 *365),3)
st.write("Vattenmängd som kommer ut i systemet total:", round(total,1), " m³.")
st.write("Mängd dricksvatten som tvingas användas från kran:", round((water_use * 0.001 *365) - svar[0], 2), " m³.")
st.write("Vattenbehovet för ett år är:", round((water_use * 0.001 *365),2), " m³.")
st.write("Procent anvädning av regnvatten mot behov dricksvatten:", round(regn_proc*100,3), " %.")

# plots
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
plt.figure(figsize=(8, 6))
plt.bar(months, svar[5], color='skyblue')
plt.title('Använt regnvatten i byggnad [m³]')
plt.xlabel('Month')
plt.ylabel('m³')
plt.xticks(rotation=45)
st.pyplot(plt.gcf())
#plt.show()


# Plot boxplot för nederbörd av avg. månad
month = svar[11]
prec_m3 = svar[10]
zippad = []
# Iterate over both lists simultaneously
for month, prec_m3 in zip(month, prec_m3):
    # Create a tuple with values from both lists
    pair = (month, prec_m3)
    # Append the tuple to the result list
    zippad.append(pair)
# New list containing 12 sublists
month_data = [[] for _ in range(12)]
# Iterate over the original data and append values to corresponding sublists
for item in zippad:
    month1 = item[0]  # Extract the month value
    month_data[month1 - 1].append(item[1])
# Create a figure and axis object
fig, ax = plt.subplots()
# Create boxplots for each month
ax.boxplot(month_data)
ax.set_xticklabels(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
ax.set_xlabel('Month')
ax.set_ylabel('m³')
plt.xticks(rotation=45)
plt.title('Nederbördsfödelning på takyta för varje månad av nederbördsdata')
st.pyplot(plt.gcf())
#plt.show()






































#st.write("Ni har angivet följande area:", rounded_arean, "m²")

#def nutestarvi(rounded_arean):
#    result = rounded_arean*5
#    return round(result,2)

#st.write("Beräknad regnvatteninsamlingspotential:", nutestarvi(rounded_arean))
# Call the function and display the result with customized styling
#st.write("Beräknad regnvatteninsamlingspotential: <span style='color: blue; font-size: 18px;'>{}</span>".format(nutestarvi(rounded_arean)), unsafe_allow_html=True)

#def vattenitank(rounded_arean):
#    vattenmangd = rounded_arean * 0.85 * 0.9 
#    return round(vattenmangd,2)

#st.write("Beräknad regnvatteninsamlingspotential:", vattenitank(rounded_arean))

