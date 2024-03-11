import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean
print('')

# Read the CSV file into a DataFrame - Se till så att det är rätt format. Kommatecken eller inte.
df = pd.read_csv('SMHI_modified3.csv')
df_med = pd.read_csv('SMHI_modified_medel.csv')
#print(df)
#print(df['Temperature Medel'])
# Load data into variable
# Notera att wateruseday aldrig får vara högre än tanksize

def TaInGeUt(tanksize, wateruseday, roofarea):
  df = pd.read_csv('SMHI_modified3.csv')
  df_med = pd.read_csv('SMHI_modified_medel.csv')
  tanksize = tanksize
  wateruseday = wateruseday * 0.001
  roofarea = roofarea
#tanksize = 10                                     # m3 
#wateruseday = 150 * 0.001                         # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)
#roofarea = 50                                     # m2 
  day = df['Dagar']                                 # Dag
  month = df['Månad']                               # Månad
  prec_mm = df['Precip Medel']                      # mm
  avrin_coef = 0.85              
  prec_m = [i * avrin_coef * 0.001 for i in prec_mm]             # Gör om millimeter till meter
  prec_m3 = [i * roofarea for i in prec_m]          # Gör ny lista med area X nederbörd --> m3 
  temp = df['Temperature Medel']                    # Celcius
  temp = [i for i in temp]
  tankVol = 0
  tot_h2o_use = 0
  water_out = 0
  svar = model_streamlit(tanksize, tankVol, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp)
  return svar

# Tester med variabler för robusethet och vid fel i koden
# 1. Superstor tank --> Funkar
# 2. Superliten tank --> Funkar
# 3. Superhög användning per dag --> Funkar
# 4. Superliten anvädning per dag --> Funkar
# 5. Superlitet tak --> Funkar
# 6. Superstort tak --> Funkar

  #print(f'Vattenmängd som kommer in i systemet {round(sum(prec_m3),1)}')
# Modellen tar in regnvatten först i tanken (början av dagen), sedan tar den upp vatten till huset(slutet av dagen)
# Antar att tanken inte fryser
# Antar att all snö på taket smälter på en dag vid plusgrader
# Än så länge utan avrinningskoffecient
def model_streamlit(tanksize, tankVol, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp):
  #print(f'Vattenmängd som kommer in i systemet {round(sum(prec_m3),1)}')
  # Create a lists to hold datainfo
  prec_m3 = prec_m3
  month = month
  monthly_collected_water = []
  monthly_lost_water = []
  cumulative_total = 0
  cum_water_use = []
  vattentanknivå = []
  drink_water_use = 0
  tak_lager = counter = previous_h2o = previous_water_out = 0
  current_month = 1
  for i in day:
    # Minusgrader
    if temp[i-1] < 0: # Kollar om det är snö eller regn
      # Påfyllnad
      tak_lager += prec_m3[i-1]      # Det är snö, bygger upp lager
      # Tömma tank
      if wateruseday < tankVol:      # Ska ändå kunna ta från tanken vid slutet av dagen vid minusgrader
        tankVol -= wateruseday       # Tar bort vatten från tanken
        tot_h2o_use += wateruseday   # Fyller på countern i total användning av regnvatten
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
      else:
        ##drink_water_use += tankVol   # Mängd vatten som tas från kranvatten istället
        tankVol -= tankVol           # Tömmer tanken på det vatten som finns kvar i tanken
        tot_h2o_use += tankVol       # Fyller på countern i total anvädning av regnvatten (det som finns kvar i tanken)
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
    # Plusgrader
    else: 
      # Påfyllnad
      if tanksize > tankVol + prec_m3[i-1] + tak_lager:  # Checkar om tanken får plats med allt vatten 
        tankVol += prec_m3[i-1] + tak_lager              # Beräknar tankvolym, Antar att all snö smälter på en dag vid plusgrader
        tak_lager = 0                                    # Nollställer tak_lager
      else: # Om inte allt vatten får plats i tanken
        utrymme = tanksize - tankVol
        water_out += prec_m3[i-1] + tak_lager - utrymme 
        tankVol += utrymme                # Beräknar tankvolym, # Antar att all snö på taket smälter på en dag vid plusgrader
        tak_lager = 0                     # Nollställer tak_lager
      # Tömma tank
      if wateruseday < tankVol:           # Ta vatten från tanken vid slutet av dagen vid plusgrader
        tankVol -= wateruseday            # Tar bort vatten från tanken
        tot_h2o_use += wateruseday        # Fyller på countern i total användning av regnvatten
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
      else:
        # Skulle nog kunna skriva de två kommande rader som: tankVol -= tankVol # tot_h2o_use += tankVol
        tot_h2o_use += min(wateruseday, tankVol)  # Fyller på countern i total anvädning av regnvatten (det som finns kvar i tanken)
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
        ##drink_water_use += tankVol   # Mängd vatten som tas från kranvatten istället
        tankVol -= min(wateruseday, tankVol)      # Tömmer tanken på det vatten som finns kvar i tanken
    vattentanknivå.append(tankVol)

    # Kolla om det är ny månad för att lägga över månadsbesparning samt förlorad mängd
    if month[i-1] == current_month:
      current_tot_h2o_use = tot_h2o_use - previous_h2o
      current_water_out = water_out - previous_water_out
      if day[i-1] == 365:
        monthly_collected_water.append(current_tot_h2o_use)
        monthly_lost_water.append(current_water_out)
      else:
        continue
    else:
      monthly_collected_water.append(current_tot_h2o_use)
      monthly_lost_water.append(current_water_out)
      previous_h2o += current_tot_h2o_use
      previous_water_out += current_water_out 
      current_tot_h2o_use = current_water_out = 0
      current_month += 1 
    counter += 1
  return tot_h2o_use, water_out, tankVol, tak_lager, counter, monthly_collected_water, monthly_lost_water, cum_water_use, vattentanknivå, drink_water_use, prec_m3, month

'''
svar = model_streamlit(tanksize, tankVol, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp)
print(f'Rad 1. Vattenmängd använt från tanken: {round(svar[0],3)}')
print(f'Rad 2. Vattenmägd utanför tanken: {svar[1]}')
print(f'Rad 3. Vattemmängd kvar i tanken: {svar[2]}')
print(f'Rad 4. Vattenmängd kvar på taket: {svar[3]}')
total = svar[0]+svar[1]+svar[2]+svar[3]
regn_proc = round(svar[0] / (wateruseday*365),3)
print(f'Rad 5. Procent anvädning av regnvatten mot behov dricksvatten: {round(regn_proc*100,3)} %')
print(f'Vattenmängd som kommer ut i systemet total {round(total,1)}')
print('')
#print(svar[5])
#print(sum(svar[5]))
#print(svar[6])
#print(sum(svar[6]))

# plt.plot(range(len(svar[7])), svar[7])
# plt.xlabel('Dag på året')  # Label for x-axis
# plt.ylabel('Cumulativt sparat dricksvatten')  # Label for y-axis
# plt.title('Plot of svar[7]')  # Title of the plot
#plt.show()
#print(svar[8])
plt.plot(range(len(svar[8])), svar[8])
# plt.xlabel('Dag på året')  # Label for x-axis
# plt.ylabel('Cumulativt sparat dricksvatten')  # Label for y-axis
plt.title('Vattennivå i tank under året, börjar med 0')  # Title of the plot
#plt.show()
print(f'Vattenbehovet för ett år är {wateruseday*365} m3')
print(f'Mängd dricksvatten som tvingas användas från kran {round(wateruseday*365 - svar[0], 3)} m3')
print('(Drickvatten (kran) + upptaget regnvatten (tank) vara samma.)')

plt.figure()
# Plot månadsvis använt regnvatten i hus
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
plt.bar(months, svar[5], color='skyblue')
plt.title('Använt regnvatten i byggnad m3')
plt.xlabel('Month')
plt.ylabel('m3')
plt.xticks(rotation=45)
#plt.show()

# Plot månadsvis förlorat regnvatten ut
plt.figure()
plt.bar(months, svar[6], color='skyblue')
plt.title('Regnvatten som går förlorat')
plt.xlabel('Month')
plt.ylabel('m3')
plt.xticks(rotation=45)
#plt.show()

#def CallOnModel(tanksize, wateruseday, roof_area):
  # Behöver lägg till ett steg där takarean omvandlas
#  return model_streamlit(tanksize, tankVol, tot_h2o_use, water_out, wateruseday, day, prec_m3, temp)
'''
'''
'''
'''
Presentera nederbörd och temperatur för medelåret 2000-2022
'''
'''
'''
'''
# Read the CSV file into a DataFrame - Se till så att det är rätt format. Kommatecken eller inte.
df = pd.read_csv('SMHI_modified3.csv')
df_med = pd.read_csv('SMHI_modified_medel.csv')

prec_medel = df_med['Medel precip']
temp_medel = df_med['Medel Temp']
#print(prec_medel)
#print(temp_medel)

# Plot scatterplot för nederbörd av avg. månad
plt.figure()
plt.scatter(month, prec_m3, color='skyblue')
plt.title('Mederlvärde nederbörd månad')
plt.xlabel('Month')
plt.ylabel('m3')
plt.xticks(rotation=45)
#plt.show()

# Plot boxplot för nederbörd av avg. månad
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
ax.set_ylabel('Data')
plt.xticks(rotation=45)
plt.title('Boxplot för varje månad av nederbördsdata')
#plt.show()

# SVÅRA Plot medelvärdet för nederbörden för varje månad
avg_månad_med = []
for i in month_data:
    avg_månad_med.append(mean(i))
#print(avg_månad_med)
månad = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
plt.figure()
plt.bar(månad, avg_månad_med, color='skyblue')
plt.title('Mederlvärdeprec månad')
plt.xlabel('Month')
plt.ylabel('m3')
plt.xticks(rotation=45)
#plt.show()

# LÄTTA Plot medelvärdet av nederbörden för varje månad
prec_medel_m = [i * 0.001 for i in prec_medel]          # Gör om millimeter till meter
prec_medel_m3 = [i * roofarea for i in prec_medel_m]    # Gör ny lista med area X nederbörd --> m3 
månad = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#plt.plot(month, temp, color='skyblue')
plt.figure()
plt.bar(månad, prec_medel_m3, color='skyblue')
plt.title('Mederlvärdeprec månad')
plt.xlabel('Month')
plt.ylabel('m3')
plt.xticks(rotation=45)
#plt.show()
# Stäng alla diagramfönster

plt.close('all')
# Plot medelvärdet av temperaturen
månad = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#plt.plot(month, temp, color='skyblue')
plt.figure()
plt.bar(månad, temp_medel, color='skyblue')
plt.title('Mederlvärde temp månad')
plt.xlabel('Month')
plt.ylabel('Celcius')
plt.xticks(rotation=45)
plt.show()

print('')
'''