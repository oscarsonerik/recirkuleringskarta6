import streamlit as st

st.write("""
# My first app
Hello *world!*
""")
import numpy as np
import streamlit as st
import geopandas as gpd
import pandas as pd
import streamlit.components.v1 as stc
import matplotlib.pyplot as plt
import numpy as np
#import Calculations_streamlit as calc
import pythoncompare.Calculations_streamlit_avg_last as calc_last


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
#https://oscarsonerik.github.io/endastindex/
#
# Input
#

st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
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

st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
#
# Beräkningar
#
# Avrunda det angivna numret till en viss precision (t.ex. 2 decimaler)
# Allt i m, m2 och m3
# rounded_arean = round(arean, 2) # m2
# water_use_rev = water_use * 0.001 # l/dag --> (dm3 to m3) --> m3/dag
# vatten_spar = rounded_arean * 365 * 0.001

# Read the CSV file into a DataFrame
df = pd.read_csv('SMHI\SMHI_modified3.csv')
day = df['Dagar']
prec = df['Precip Medel']
temp = df['Temperature Medel']

#tanksize = 10                                     # m3 
#wateruseday = 150 * 0.001                         # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)
#roofarea = 50                                     # m2 
# def model_streamlit(tanksize, tankVol, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp):
#svar = calc.TaInGeUt(magazinsize, water_use, arean)
svar = calc_last.GetData(magazinsize, water_use, arean)

print(f'Rad 1. Vattenmängd använt från tanken: {round(svar[0],5)}')
print(f'Rad 2. Vattenmägd utanför tanken: {round(svar[1],5)}')
print(f'Rad 3. Vattemmängd kvar i tanken: {round(svar[2],5)}')
print(f'Rad 4. Vattenmängd kvar på taket: {round(svar[3],5)}')
total = svar[0]+svar[1]+svar[2]+svar[3]
print(f'Vattenmängd som kommer ut i systemet {round(total,2)}\n')
print("\t >> Tester för modellen 2014-2022<<")
if round(total,2) == round(sum(svar[12]),2):
    print("\t >> Modellen stämmer <<")
if svar[0] == sum(svar[10]):
    print("\t >> Appendar rätt upptagen vattenmängd <<")
if svar[1] == sum(svar[11]):
    print("\t >> Appendar rätt vattenförlust <<\n")
# plt.plot(svar[10])
# plt.figure(2)
# plt.plot(svar[11])
# plt.show()
print("__Skapar ett nytt dataset - avg_2014-2022 år__\n")

upptag = svar[10]
losten = svar[11]
prec_M3 = svar[12]

avg_year_365 = calc_last.Make365(upptag, losten, prec_M3)

wateruseday = water_use * 0.001
print(f'Önskad mängd regnvatten utnyttjad: {round((wateruseday*365),4)} m³/år. ')
print(f'Din input ger {round(sum(avg_year_365[0]),4)} m³ utnyttjad regnvatten per år.') # Blir inte exakt rätt då vi inte hämtar något vatten första dagen om det inte är någon nederbörd. First data dilemma.
print(f'Mängd dricksvatten taget från kran {round((wateruseday*365)-sum(avg_year_365[0]),4)} m³/år.')
procent_upptag = sum(avg_year_365[0]) / (wateruseday*365)
print(f'Regnvatten står för {round(procent_upptag,4)*100} % av önskat behov under året.')

df_365 = pd.read_csv('SMHI\SMHI_modified3.csv')
mån = df_365['Månad']
antal_dagar_månad = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
my_365 = [i for i in range(1, 366)]
mån_avg_prec = []
mån_avg_upptag = []
mån_avg_lost = []
mån_check = 1
tempo_prec = 0
tempo_up = 0
tempo = 0
for i in my_365:
    if mån[i-1] == mån_check:
        tempo_prec += avg_year_365[2][i-1]
        tempo_up += avg_year_365[0][i-1]
        tempo += avg_year_365[1][i-1]
        if i == 365:
            mån_avg_prec.append(tempo_prec)
            mån_avg_upptag.append(tempo_up)
            mån_avg_lost.append(tempo)
    else:
        mån_avg_prec.append(tempo_prec)
        mån_avg_upptag.append(tempo_up)
        mån_avg_lost.append(tempo)
        tempo_prec = 0
        tempo_up = 0
        tempo = 0
        mån_check += 1
        tempo_prec += avg_year_365[2][i-1]
        tempo_up += avg_year_365[0][i-1]
        tempo += avg_year_365[1][i-1]
# Just nu summeras samtliga värden för varje enskild månad. 
# Vill man ha genomsnittligt sparande per dag för specifik månad får man dela med antal dagar också.
# for i in range(0,12):
#print(i)
# mån_avg_upptag[i] = mån_avg_upptag[i]/ antal_dagar_månad[i]
# mån_avg_lost[i] = mån_avg_lost[i]/ antal_dagar_månad[i]

# Ta fram mängd dricksvatten som används för varje månad istället för regnvatten
wateruse_month = [i * wateruseday for i in antal_dagar_månad]
# print(antal_dagar_månad)
# print(wateruseday)
# print(wateruse_month)
array1 = np.array(wateruse_month)
array2 = np.array(mån_avg_upptag)
resultatet = array1 - array2


# #
# # Output
# #
st.write("# Resultat")
st.write("Vattenmängd som samlas in på takyta", round(sum(avg_year_365[2]),3), "m³/år.")
st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
st.write("Önskat återvunnet regnvatten till hushåll", round((wateruseday*365),3), "m³/år.")
# st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
st.write("Vattenmängd använt från vattentanken:", round(sum(avg_year_365[0]),3), "m³/år.")
#st.write("Vattenmägd som hamnar utanför tanken (pga fylld tank):", , "m³/år.")
# st.write("Vattemmängd kvar i tanken:", round(svar[2],2), "m³ per år.")
# st.write("Vattenmängd kvar på taket:", svar[3], "m³ per år.")
# st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
# total = svar[0]+svar[1]+svar[2]+svar[3]
# regn_proc = round(svar[0] / (water_use * 0.001 *365),3)
# st.write("Vattenmängd som kommer ut i systemet total:", round(total,1), " m³.")
st.write("Mängd dricksvatten som tvingas användas från kran:", round((wateruseday*365)-sum(avg_year_365[0]),4), " m³.")
# st.write("Vattenbehovet för ett år är:", round((water_use * 0.001 *365),2), " m³.")
procent_upptag = sum(avg_year_365[0]) / (wateruseday*365)
st.write("Procent anvädning av regnvatten mot behov dricksvatten:", round(procent_upptag,4)*100, " %.")

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#print(mån_avg_prec)

plt.figure(figsize=(8, 6))
plt.bar(months, mån_avg_prec)
plt.xlabel('Månad')
plt.ylabel('m³')
plt.title('Genomsnittligt nederbörd tak m³')
plt.ylim(0, max(mån_avg_prec)+ max(mån_avg_prec) * 0.1)
st.pyplot(plt.gcf())

# plt.show()
# plt.figure(4)
plt.figure(figsize=(8, 6))
plt.bar(months, mån_avg_upptag, color='green')
plt.xlabel('Månad')
plt.ylabel('Volym utnytjad regnvatten m³')
plt.title('Genomsnitt av volym utnyttjad regnvatten')
plt.ylim(0, max(mån_avg_upptag)+ max(mån_avg_upptag) * 0.1)
st.pyplot(plt.gcf())

plt.figure(figsize=(8, 6))
plt.bar(months, mån_avg_lost, color='#FF5733')
plt.xlabel('Månad')
plt.ylabel('Volym förlorad regnvatten m³')
plt.title('Medelvärde av volym förlorad regnvatten')
st.pyplot(plt.gcf())

# Vill plotta en plotta för varje månad, dels mängd från regnvatten, regnvatten från drickskran och sedan totalt behov för månad
x = months
x = np.arange(len(months))
y1 = wateruse_month
y2 = mån_avg_upptag
y3 = resultatet
bar_width = 0.1

data = {'Vattenbehov månad': wateruse_month,
        'Regnvattenanvändning månad': mån_avg_upptag,
        'Dricksvattenupptag': resultatet}
dfen = pd.DataFrame(data, index=months)
dfen.plot.bar(figsize=(10, 6))
# plt.figure(figsize=(10,6))
# plt.bar(x, y1, label='Vattenbehov månad')
# plt.bar(x + bar_width, y2, label='Regnvattenanväning månad')
# plt.bar(x + 0.1*bar_width, y3, label='Dricksvattenupptag')
plt.title('Tre grafer i samma figur')
plt.xlabel('Månad')
plt.ylabel('m³')
plt.xticks(x+bar_width, months)
plt.grid(False)
plt.legend()
plt.ylim(0, max(y1)+ max(y1) * 0.1)
st.pyplot(plt.gcf())











# # plots
# months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# plt.figure(figsize=(8, 6))
# plt.bar(months, svar[5], color='skyblue')
# plt.title('Använt regnvatten i byggnad [m³]')
# plt.xlabel('Month')
# plt.ylabel('m³')
# plt.xticks(rotation=45)
# st.pyplot(plt.gcf())
# #plt.show()

# # Plot boxplot för nederbörd av avg. månad
# month = svar[11]
# prec_m3 = svar[10]
# zippad = []
# # Iterate over both lists simultaneously
# for month, prec_m3 in zip(month, prec_m3):
#     # Create a tuple with values from both lists
#     pair = (month, prec_m3)
#     # Append the tuple to the result list
#     zippad.append(pair)
# # New list containing 12 sublists
# month_data = [[] for _ in range(12)]
# # Iterate over the original data and append values to corresponding sublists
# for item in zippad:
#     month1 = item[0]  # Extract the month value
#     month_data[month1 - 1].append(item[1])
# # Create a figure and axis object
# fig, ax = plt.subplots()
# # Create boxplots for each month
# ax.boxplot(month_data)
# ax.set_xticklabels(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
# ax.set_xlabel('Month')
# ax.set_ylabel('m³')
# plt.xticks(rotation=45)
# plt.title('Nederbördsfödelning på takyta för varje månad av nederbördsdata')
# st.pyplot(plt.gcf())
# #plt.show()

my_list1 = [i for i in range(1, 101)]
#print(my_list1)

st.write("# Wizard 1-100")
st.markdown('<hr style="border: 1px solid green;">', unsafe_allow_html=True)
bestämd_arean = st.number_input("Ange önskad takarea [m²]", value=0.0, step=0.5)
bestämd_water_use = st.number_input("Ange vattenanvändning [l/dag]", value=0.0, step=0.5)
import time
# Add a button
if st.button('Run wizards 1-100'):
    # Add your code here to run when the button is clicke
    opt_tanksize = 0
    previus_proc = 0 
    procent_upptag = 0
    for i in range(1,len(my_list1)+1):
        print(i)
        svar = calc_last.GetData(i, bestämd_water_use, bestämd_arean)
        upptag = svar[10]
        losten = svar[11]
        prec_M3 = svar[12]
        avg_year_365 = calc_last.Make365(upptag, losten, prec_M3)
        #print(avg_year_365[0])
        #magres = calc_last.Make365(avg_year_365[10], avg_year_365[11], avg_year_365[12])
        procent_upptag = (sum(avg_year_365[0]) / (wateruseday*365))
        if procent_upptag > previus_proc:
            best = procent_upptag
            previus_proc = procent_upptag
            opt_tanksize = i
        print(f'_____{opt_tanksize}____________')
st.write("Wizard: Du får som mest effektiv regnvattenåtervinning om du använder en tankstrolek på:",opt_tanksize,"m3")
st.write("Wizard: Den optimala tankstorleken ger dig en effektivitet på:",round(best,4)*100,"%")



































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

