import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean
print('')
""" Read CSV 
# Read the CSV file into a DataFrame - Se till så att det är rätt format. Kommatecken eller inte.
"""
def GetData(magazinsize, water_use, arean):
  df_365 = pd.read_csv('SMHI\SMHI_modified3.csv')
  df_med = pd.read_csv('SMHI\SMHI_modified_medel.csv')
  df_med_last_14 = pd.read_csv('SMHI\SMHI_2014_2020.csv',  delimiter=";", decimal=",")
  df_med_last_14.insert(0, 'ID', range(len(df_med_last_14)))
  """
  # Load data into variable
  """
  months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  # roofarea = 20                                   # m2
  # tanksize = 50                                    # m3 
  # wateruseday = 350 * 0.001                        # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)
  roofarea = arean                                   # m2
  tanksize = magazinsize                                    # m3 
  wateruseday = water_use * 0.001                        # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)

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

  # Tester med variabler för robusethet och vid fel i koden
  # 1. Superstor tank --> Funkar
  # 2. Superliten tank --> Funkar
  # 3. Superhög användning per dag --> Funkar
  # 4. Superliten anvädning per dag --> Funkar
  # 5. Superlitet tak --> Funkar
  # 6. Superstort tak --> Funkar
  """
  Vattenbalansmodell
  """
  print("__Data mellan 2014-2022__")
  print(f'Vattenmängd som kommer in i systemet {round(sum(prec_m3),2)}')
  ret_svar = model_streamlit(ind, tanksize, vol_tank, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp, roofarea)
  print(f'Controll__prec_m3 sum: {round(sum(ret_svar[12]),2)}')
  return ret_svar

# plt.bar(ind,prec_m3)
# plt.show()
# plt.plot(ind,temp)
# plt.show()
# Modellen tar in data för år 2014-2022 och kör den för att sedan returnera hur/var vattnet befinner sig under de 9 åren.
# Modellen tar in regnvatten först i tanken (början av dagen), sedan tar den upp vatten till huset(slutet av dagen)

# Antaganden
# Antar att tanken inte fryser
# Antar att all snö på taket smälter på en dag vid plusgrader
def model_streamlit(ind, tanksize, vol_tank, tot_h2o_use, water_out, wateruseday, day, month, prec_m3, temp, roofarea):
  # Create lists to hold datainfo
  monthly_collected_water = []
  monthly_lost_water = []
  cumulative_total = 0
  cum_water_use = []
  vattentanknivå = []
  drink_water_use = 0
  tak_lager  = previous_h2o = previous_water_out = counter = current_tot_h2o_use = current_water_out = 0
  total_water = 0
  current_month = 1
  water_out_temp = 0
  apnd_upptag = []
  apnd_water_tank = []
  apnd_water_out = []

  for i in ind:
    # Minusgrader
    if temp[i] < 0: # Kollar om det är snö eller regn
      # Påfyllnad
      tak_lager += prec_m3[i]      # Det är snö, bygger upp lager
      # Tömma tank
      if wateruseday < vol_tank:      # Ska ändå kunna ta från tanken vid slutet av dagen vid minusgrader
        vol_tank -= wateruseday       # Tar bort vatten från tanken
        tot_h2o_use += wateruseday   # Fyller på countern i total användning av regnvatten
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
        apnd_upptag.append(wateruseday)
      else:
        ##drink_water_use += vol_tank   # Mängd vatten som tas från kranvatten istället
        apnd_upptag.append(vol_tank)
        tot_h2o_use += vol_tank
        vol_tank -= vol_tank           # Tömmer tanken på det vatten som finns kvar i tanken
               # Fyller på countern i total anvädning av regnvatten (det som finns kvar i tanken)
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
    # Plusgrader
      apnd_water_out.append(0)
    else: 
      # Påfyllnad
      day_melt = 0
      #print(temp[i])
      snowmelt_m3 = Snowmelt(temp[i], roofarea) # Hur mycket snö som smält den dagen [m3]
      #print(f'amount snowmelt {snowmelt_m3}')
      #cc += 1
      if tak_lager > snowmelt_m3: # Om det finns mer snö på lagret än vad som smältet är dagens snowmelt = snowmelt_m3
        day_melt = snowmelt_m3
        tak_lager -= snowmelt_m3  # Tar bort den mängd som smälter från taklagret
      else:  # Om taklagret är mindre än det som snöar
        day_melt = tak_lager      
        tak_lager = 0 
      avrinn_amount = day_melt + prec_m3[i]

      if tanksize > vol_tank + avrinn_amount:  # Checkar om tanken får plats med allt vatten 
        vol_tank += avrinn_amount              # Beräknar vol_tankym, Antar att all snö smälter på en dag vid plusgrader
        tak_lager = 0                                    # Nollställer tak_lager
        apnd_water_out.append(0)
      else: # Om inte allt vatten får plats i tanken
        utrymme = tanksize - vol_tank
        water_out += avrinn_amount - utrymme 
        water_out_temp += avrinn_amount - utrymme
        apnd_water_out.append(water_out_temp)
        water_out_temp = 0
        vol_tank += utrymme                # Beräknar vol_tankym, # Antar att all snö på taket smälter på en dag vid plusgrader
        tak_lager = 0                     # Nollställer tak_lager
      # Tömma tank
      if wateruseday < vol_tank:           # Ta vatten från tanken vid slutet av dagen vid plusgrader
        apnd_upptag.append(wateruseday)
        vol_tank -= wateruseday            # Tar bort vatten från tanken
        tot_h2o_use += wateruseday        # Fyller på countern i total användning av regnvatten
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
      else:
        # Skulle nog kunna skriva de två kommande rader som: vol_tank -= vol_tank # tot_h2o_use += vol_tank
        apnd_upptag.append(vol_tank)
        tot_h2o_use += min(wateruseday, vol_tank)  # Fyller på countern i total anvädning av regnvatten (det som finns kvar i tanken)
        cumulative_total += wateruseday
        cum_water_use.append(cumulative_total)
        ##drink_water_use += vol_tank   # Mängd vatten som tas från kranvatten istället
        vol_tank -= min(wateruseday, vol_tank)      # Tömmer tanken på det vatten som finns kvar i tanken
    vattentanknivå.append(vol_tank)

  return (tot_h2o_use, water_out, vol_tank, tak_lager, counter, monthly_collected_water, monthly_lost_water, cum_water_use, vattentanknivå, drink_water_use, apnd_upptag, apnd_water_out, prec_m3)

'''
Snowmelt funciton
'''
def Snowmelt(temp_dag, roofarea):
  Cm = 3.5                    # Koefficient
  Tt = 0                      # Tröskelvärde
  Ms = Cm * (temp_dag - Tt)   # mm
  Ms = roofarea * Ms * 0.001  # m2 * mm * 0,001 = m3
  return Ms # Returns in m3

def Make365(upptag, losten, prec_m3):
  yearss = 9
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
  return avg_year_upptag, avg_year_lost, avg_year_prec_m3

print('')