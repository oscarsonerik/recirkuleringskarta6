import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
print('')
""" Read CSV 
# Read the CSV file into a DataFrame - Se till så att det är rätt format. Kommatecken eller inte.
"""
df_365 = pd.read_csv('SMHI\SMHI_modified3.csv')
df_med = pd.read_csv('SMHI\SMHI_modified_medel.csv')
#df_med_last_14 = pd.read_csv('SMHI\SMHI_2014_2020.csv',  delimiter=";", decimal=",")
df_med_last_14 = pd.read_csv('SMHI\SMHI_2014_2020_test.csv',  delimiter=";", decimal=",")
df_med_last_14.insert(0, 'ID', range(len(df_med_last_14)))
"""
# Load data into variable
"""
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
roofarea = 100                                   # m2
tanksize = 10                                    # m3 
wateruseday = 100 * 0.001                        # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)
ind = df_med_last_14["ID"]                       # Lägger till ID i första kolumnen
day = df_med_last_14['Dag siffra']               # Dag
month = df_med_last_14['Månad siffra']           # Månad
year = df_med_last_14['År siffra']
prec_mm = df_med_last_14['Nederbördsmängd']      # mm
avrin_coef = 1          # !!! Kom ihåg att kolla upp avrin_coeff !!!
prec_m = [i * avrin_coef * 0.001 for i in prec_mm]   # Gör om millimeter till meter
prec_m3 = [i * roofarea for i in prec_m]             # Gör ny lista med area X nederbörd --> m3
temp = df_med_last_14['Temperatur']                  # Celcius
temp = [i for i in temp]
vol_tank = 0
tot_h2o_use = 0
water_out = 0

'''
Snowmelt funciton
'''
def Snowmelt(temp_dag, roofarea):
  Cm = 3.5                    # Koefficient
  Tt = 0                      # Tröskelvärde
  Ms = Cm * (temp_dag - Tt)   # mm
  Ms = roofarea * Ms * 0.001  # m2 * mm * 0,001 = m3
  return Ms # Returns in m3
"""
Vattenbalansmodell
"""
print("__Data mellan 2014-2022__")
print(f'Vattenmängd som kommer in i systemet {round(sum(prec_m3),2)}')
#plt.bar(ind,prec_m3); plt.show(); plt.plot(ind,temp); plt.show()
# Modellen tar in data för år 2014-2022 och kör den för att sedan returnera hur/var vattnet befinner sig under de 9 åren.
# Modellen tar in regnvatten först i tanken (början av dagen), sedan tar den upp vatten till huset(slutet av dagen)
# Antar att: vattentank fryser inte, snö på taket smälter efter HBV-model
def model_streamlit(ind, tanksize, vol_tank, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp):
  tak_lager = drink_water_use = mm = nn = cc = 0
  water_out_temp = 0
  apnd_upptag = []
  apnd_water_out = []
  vattentanknivå = []
  for i in ind:
    # Minusgrader
    if temp[i] < 0: # Kollar om det är snö eller regn
      nn += 1
      tak_lager += prec_m3[i]         # Det är snö, bygger upp lager
    # Tömma tank
      if wateruseday < vol_tank:      # Ska ändå kunna ta från tanken vid slutet av dagen vid minusgrader
        vol_tank -= wateruseday       # Tar bort vatten från tanken
        tot_h2o_use += wateruseday    # Fyller på countern i total användning av regnvatten
        apnd_upptag.append(wateruseday)
      else:
        apnd_upptag.append(vol_tank)
        tot_h2o_use += vol_tank
        vol_tank -= vol_tank           # Tömmer tanken på det vatten som finns kvar i tanken
      apnd_water_out.append(0)
    # Plusgrader
    else: 
      # Fyller på tanken
      day_melt = 0
      #print(temp[i])
      snowmelt_m3 = Snowmelt(temp[i], roofarea) # Hur mycket snö som smält den dagen [m3]
      #print(f'amount snowmelt {snowmelt_m3}')
      cc += 1
      if tak_lager > snowmelt_m3: # Om det finns mer snö på lagret än vad som smältet är dagens snowmelt = snowmelt_m3
        day_melt = snowmelt_m3
        tak_lager -= snowmelt_m3  # Tar bort den mängd som smälter från taklagret
      else:  # Om taklagret är mindre än det som snöar
        day_melt = tak_lager      
        tak_lager = 0 
      avrinn_amount = day_melt + prec_m3[i]

      if tanksize > vol_tank + avrinn_amount:  # Checkar om tanken får plats med allt vatten 
        vol_tank += avrinn_amount              # Beräknar vol_tankym, Antar att all snö smälter på en dag vid plusgrader
        #tak_lager = 0                                   # Nollställer tak_lager
        apnd_water_out.append(0)
      else: # Om inte allt vatten får plats i tanken
        utrymme = tanksize - vol_tank
        water_out += avrinn_amount - utrymme 
        water_out_temp += avrinn_amount - utrymme
        apnd_water_out.append(water_out_temp)
        water_out_temp = 0
        vol_tank += utrymme                # Beräknar vol_tank, # Antar att all snö på taket smälter på en dag vid plusgrader
        #tak_lager = 0                     # Nollställer tak_lager
      
      # Tömma tank
      if wateruseday < vol_tank:           # Ta vatten från tanken vid slutet av dagen vid plusgrader
        apnd_upptag.append(wateruseday)
        vol_tank -= wateruseday            # Tar bort vatten från tanken
        tot_h2o_use += wateruseday        # Fyller på countern i total användning av regnvatten
      else:
        # Skulle nog kunna skriva de två kommande rader som: vol_tank -= vol_tank # tot_h2o_use += vol_tank
        apnd_upptag.append(vol_tank)
        tot_h2o_use += min(wateruseday, vol_tank)  # Fyller på countern i total anvädning av regnvatten (det som finns kvar i tanken)
        vol_tank -= min(wateruseday, vol_tank)      # Tömmer tanken på det vatten som finns kvar i tanken
    vattentanknivå.append(vol_tank)
  return (tot_h2o_use, water_out, vol_tank, tak_lager, cc, mm, nn, cc, vattentanknivå, drink_water_use, apnd_upptag, apnd_water_out)
# return (tot_h2o_use, water_out, vol_tank, tak_lager, counter, monthly_collected_water, monthly_lost_water, cum_water_use, vattentanknivå, drink_water_use, apnd_upptag, apnd_water_out)

"""
Kollar på värdena som kommer ut från funtionen
"""

svar = model_streamlit(ind, tanksize, vol_tank, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp)
print(f'Rad 1. Vattenmängd använt från tanken: {round(svar[0],5)}')
print(f'Rad 2. Vattenmägd utanför tanken: {round(svar[1],5)}')
print(f'Rad 3. Vattemmängd kvar i tanken: {round(svar[2],5)}')
print(f'Rad 4. Vattenmängd kvar på taket: {round(svar[3],5)}')
total = svar[0]+svar[1]+svar[2]+svar[3]
print(f'Vattenmängd som kommer ut i systemet {round(total,2)}\n')
print("\t >> Tester för modellen 2014-2022 <<")
if round(total,2) == round(sum(prec_m3),2):
  print("\t >> Modellen stämmer <<")
if svar[0] == sum(svar[10]):
  print("\t >> Appendar rätt upptagen vattenmängd <<")
if svar[1] == sum(svar[11]):
  print("\t >> Appendar rätt vattenförlust <<\n")
# plt.plot(svar[10]); plt.figure(2); plt.plot(svar[11]); plt.show()
#plt.plot(svar[8]); plt.show()

print(f'countern är {svar[4]}')
print(f'countern är {svar[6]}')
print(f'längdt av stäng {len(prec_m3)}')

"""
Med den genomkördadatan gå i vattenmodellen tas nu årsmedelvärden ut
Ta fram 365 lång lista med medelvärden (delar långa listan med 9år).
"""
print("__Skapar ett nytt dataset - avg_2014-2022 år__\n")
def Make365(upptag, losten, prec_m3):
  yearss = 9  # Number of years
  values_per_year = 365
  avg_year_prec_m3 = []
  avg_year_upptag = []
  avg_year_lost = []
  for i in range(0,365):
      sum_prec_m3 = 0
      sum_upptag = 0
      sum_lost = 0
      for j in range(0,9):
          index = (j * values_per_year) + (i)
          sum_prec_m3 += prec_m3[index]
          sum_upptag += upptag[index]
          sum_lost += losten[index]
      average_prec_m3 = sum_prec_m3 / yearss
      average_upptag = sum_upptag / yearss
      average_lost = sum_lost / yearss
      avg_year_prec_m3.append(average_prec_m3)
      avg_year_upptag.append(average_upptag)
      avg_year_lost.append(average_lost)
  # Får fram average_year_upptag och average_year_vattenförlust
  return avg_year_upptag, avg_year_lost, avg_year_prec_m3

upptag = svar[10]
losten = svar[11]
avg_year_365 = Make365(upptag, losten, prec_m3)

print(f"Vattenmängd som samlas in på takyta", round(sum(avg_year_365[2]),3), "m³/år.")
print(f'Önskad mängd regnvatten utnyttjad: {round((wateruseday*365),4)} m³/år. ')
print(f'Din input ger {round(sum(avg_year_365[0]),4)} m³ utnyttjad regnvatten per år.') # Blir inte exakt rätt då vi inte hämtar något vatten första dagen om det inte är någon nederbörd. First data dilemma.
procent_upptag = sum(avg_year_365[0]) / (wateruseday*365)
print(f'Mängd dricksvatten taget från kran {round((wateruseday*365) - sum(avg_year_365[0]),4)} m³/år.')
print(f'Regnvatten står för {round(procent_upptag,4)*100} % av önskat behov under året.')

"""
Plotta upp månadsvärden för average år 
"""
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
    
wateruse_month = [i * wateruseday for i in antal_dagar_månad]
print(wateruseday)
print(wateruse_month)
array1 = np.array(wateruse_month)
array2 = np.array(mån_avg_upptag)
print(array2)
resultatet = array1 - array2
print(resultatet)

plt.bar(months, mån_avg_prec)
plt.xlabel('Månad')
plt.ylabel('m³')
plt.title('Genomsnittligt nederbörd tak m³')
plt.ylim(0, max(mån_avg_prec)+ max(mån_avg_prec) * 0.1)
plt.show()
plt.figure(4)
plt.bar(months, mån_avg_upptag)
plt.xlabel('Månad')
plt.ylabel('Volym utnytjad regnvatten m³')
plt.title('Medelvärde av volym utnyttjad regnvatten')
plt.ylim(0, max(mån_avg_upptag)+ max(mån_avg_upptag) * 0.1)
plt.show()
plt.figure(5)
plt.bar(months, mån_avg_lost)
plt.xlabel('Månad')
plt.ylabel('Volym förlorad regnvatten m³')
plt.title('Medelvärde av volym förlorad regnvatten')
plt.show()


mån_365 = df_365['Månad']
print(len(mån_365))
prec_year_avg = avg_year_365[2]

plt.figure()
plt.scatter(mån_365,prec_year_avg)
plt.show()
zippad = []
# Iterate over both lists simultaneously
for mån_365, prec_year_avg in zip(mån_365, prec_year_avg):
    # Create a tuple with values from both lists
    pair = (mån_365, prec_year_avg)
    # Append the tuple to the result list
    zippad.append(pair)
# New list containing 12 sublists
month_data = [[] for _ in range(12)]
# Iterate over the original data and append values to corresponding sublists
for item in zippad:
    month1 = item[0]  # Extract the month value
    month_data[month1 - 1].append(item[1])
fig, ax = plt.subplots()
ax.boxplot(month_data)
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'])
ax.set_xlabel('Month')
ax.set_ylabel('Data')
plt.xticks(rotation=45)
plt.title('Boxplot för varje månad av nederbördsdata')
plt.show()


# Tester med variabler för robusethet och vid fel i koden
# 1. Superstor tank --> Funkar
# 2. Superliten tank --> Funkar
# 3. Superhög användning per dag --> Funkar
# 4. Superliten anvädning per dag --> Funkar
# 5. Superlitet tak --> Funkar
# 6. Superstort tak --> Funkar


print('')