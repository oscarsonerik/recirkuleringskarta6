import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean

'''
  Get Data. Is called from Streamlit.py
  - Reads csv.files
  - Load data into variables
  - Call on Water balance model
'''
def GetData(magazinsize, water_use, arean):
  '''
  Read Csv.files
  '''
  df_365 = pd.read_csv('SMHI\SMHI_modified3.csv')
  df_med_last_14 = pd.read_csv('SMHI\SMHI_2014_2020.csv',  delimiter=";", decimal=",")
  #df_med_last_14 = pd.read_csv('SMHI\SMHI_2014_2020_test.csv',  delimiter=";", decimal=",")
  df_med_last_14.insert(0, 'ID', range(len(df_med_last_14))) # Lägger till ID i första kolumnen
  """
  Load data into variable
  """
  roofarea = arean                                   # m2
  tanksize = magazinsize                                    # m3 
  wateruseday = water_use * 0.001   # Gör om l/day tll m3/day. (l = dm3 --> 1m3 = 1000dm3)
  ind = df_med_last_14["ID"]                       
  day = df_med_last_14['Dag siffra']               # Dag
  month = df_med_last_14['Månad siffra']           # Månad
  months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  year = df_med_last_14['År siffra']
  prec_mm = df_med_last_14['Nederbördsmängd']      # mm
  avrin_coef = 1          # !!! Kom ihåg att kolla upp avrin_coeff !!!
  prec_m = [i * avrin_coef * 0.001 for i in prec_mm]   # Gör om millimeter till meter
  prec_m3 = [i * roofarea for i in prec_m]             # Gör ny lista med area X nederbörd --> m3
  temp = df_med_last_14['Temperatur']                  # Celcius
  temp = [i for i in temp]
  volume_tank = 0
  tot_h2o_use = 0
  water_out = 0

  """
  Call on Water balance model and return
  """
  return WaterBalanceModel(ind, tanksize, volume_tank, tot_h2o_use, water_out, wateruseday, prec_m3, temp, roofarea)


"""
  Water Balance Model.
"""
#plt.bar(ind,prec_m3); plt.show(); plt.plot(ind,temp); plt.show()
# Modellen tar in data för år 2014-2022 och kör den för att sedan returnera hur/var vattnet befinner sig under de 9 åren.
# Modellen tar in regnvatten först i tanken (början av dagen), sedan tar den upp vatten till huset(slutet av dagen)
# Antar att: vattentank fryser inte, snö på taket smälter efter HBV-model
def WaterBalanceModel(ind, tanksize, volume_tank, tot_h2o_use, water_out, wateruseday, prec_m3, temp, roofarea):
  snow_amount = water_out_temp = 0
  apnd_upptag = [] # To track how much water is used from tank each day for 9 years
  apnd_water_out = [] # To rack how much water to fits in water tank each day for 9 years
  vattentanknivå = []
  for i in ind:
    # Minus degree
    if temp[i] < 0: # Kollar om det är snö eller regn
      # Påfyllnad
      snow_amount += prec_m3[i]      # Det är snö, bygger upp lager

      # Empty tank
      if wateruseday < volume_tank:      # Ska ändå kunna ta från tanken vid slutet av dagen vid minusgrader
        volume_tank -= wateruseday       # Tar bort vatten från tanken
        tot_h2o_use += wateruseday   # Fyller på countern i total användning av regnvatten
        apnd_upptag.append(wateruseday)
      else:
        apnd_upptag.append(volume_tank)
        tot_h2o_use += volume_tank
        volume_tank -= volume_tank           # Tömmer tanken på det vatten som finns kvar i tanken
      apnd_water_out.append(0) # Då inget vatten kommer in, inget vatten ut
     
     # Plus degree
    else: 
      # Fyller på tanken
      if snow_amount != 0:
        day_melt = 0
        snowmelt_m3 = Snowmelt(temp[i], roofarea) # Hur mycket snö som smält den dagen [m3]
        #print(f'amount snowmelt {snowmelt_m3}')
        if snow_amount > snowmelt_m3: # Om det finns mer snö på lagret än vad som smältet är dagens snowmelt = snowmelt_m3
          day_melt = snowmelt_m3
          snow_amount -= snowmelt_m3  # Tar bort den mängd som smälter från taklagret
        else:  # Om taklagret är mindre än det som kan smälta den dagen
          day_melt = snow_amount      # Dagens snösmältning är endast den mängd som finns på taket
          snow_amount = 0 
        avrinn_amount = day_melt + prec_m3[i]
      else:
        avrinn_amount = prec_m3[i]
      # Checkar om tanken får plats med allt vatten
      if tanksize > volume_tank + avrinn_amount:   
        volume_tank += avrinn_amount              # Beräknar volume_tankym, Antar att all snö smälter på en dag vid plusgrader
        apnd_water_out.append(0)  # Då inget vatten kommer in, inget vatten ut
      else: # Om inte allt vatten får plats i tanken
        utrymme = tanksize - volume_tank
        water_out += avrinn_amount - utrymme 
        water_out_temp += avrinn_amount - utrymme
        apnd_water_out.append(water_out_temp)
        water_out_temp = 0
        volume_tank += utrymme         # Beräknar volume_tank
      
      # Empty tank
      if wateruseday < volume_tank:           # Ta vatten från tanken vid slutet av dagen vid plusgrader
        apnd_upptag.append(wateruseday)
        volume_tank -= wateruseday            # Tar bort vatten från tanken
        tot_h2o_use += wateruseday        # Fyller på countern i total användning av regnvatten
      else:
        apnd_upptag.append(volume_tank)
        tot_h2o_use += volume_tank  # Fyller på countern i total anvädning av regnvatten (det som finns kvar i tanken)
        volume_tank -= volume_tank      # Tömmer tanken på det vatten som finns kvar i tanken
    vattentanknivå.append(volume_tank)

  return (tot_h2o_use, water_out, volume_tank, snow_amount, vattentanknivå, apnd_upptag, apnd_water_out, prec_m3)

'''
Empty Tank
'''
def EmptyTank():
  return 

'''
Snowmelt funciton
- Calculates the amount of snow that could melt on the roof for the day
'''
def Snowmelt(temp_dag, roofarea):
  Cm = 3.5                    # Koefficient
  Tt = 0                      # Tröskelvärde
  Ms = Cm * (temp_dag - Tt)   # mm   5 * 3,5 
  Ms = roofarea * Ms * 0.001  # m2 * mm * 0,001 = m3 --- 100 * (5 * 3,5 ) 
  return Ms                   # Returns in m3

'''
Make 365 avg year of watertanksystem
- Creates an average year of the 9 years that waas runned in the water balance model
'''
def Make365(upptag, losten, prec_m3):
  yearss = 9
  values_per_year = 365
  avg_year_prec_m3 = []
  avg_year_upptag = []
  avg_year_lost = []
  for i in range(0, values_per_year): # Run through each day in a year
      sum_prec_m3 = 0
      sum_upptag = 0
      sum_lost = 0
      for j in range(0,9): # Run through each year
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


'''
Divide into month distribution
- Divides the average 365 year so that it is distributed over all month in a year.
'''
def MonthDisp(avg_year_365):
  # Create lists over the distribution over the month from the average year set.
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
  mån_avg = []
  mån_avg.append(mån_avg_prec)
  mån_avg.append(mån_avg_upptag)
  mån_avg.append(mån_avg_lost)
  return mån_avg












'''
If we just want to run this script
'''
if __name__ == "__main__":
  arean = 100
  magazinsize = 5
  water_use = 100


  svar = GetData(magazinsize, water_use, arean)
  print(f'hej')
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
  plt.plot(svar[4]); plt.show()
      
  # Create a new data-set --> an average year based on the model run. New data-set created by Make365. 
  print("__Skapar ett nytt dataset - avg_2014-2022 år__\n")
  upptag = svar[5]
  losten = svar[6]
  prec_M3 = svar[7]
  avg_year_365 = Make365(upptag, losten, prec_M3)
  wateruseday = water_use * 0.001
  print(f"Vattenmängd som samlas in på takyta", round(sum(avg_year_365[2]),3), "m³/år.")
  print(f'Önskad mängd regnvatten utnyttjad: {round((wateruseday*365),3)} m³/år. ')
  print(f"Mängd regnvatten som inte får plats i vattentanken:", round(sum(avg_year_365[1]),3), " m³.\n")
  print(f'Din input ger {round(sum(avg_year_365[0]),3)} m³ utnyttjad regnvatten per år.') # Blir inte exakt rätt då vi inte hämtar något vatten första dagen om det inte är någon nederbörd. First data dilemma.
#print("Mängd regnvatten kvar i tanken efter körning:", round((svar[2]/9),4), " m³.")
  procent_upptag = sum(avg_year_365[0]) / (wateruseday*365)
  print(f'Regnvatten står för {round(procent_upptag,4)*100} % av önskat behov under året.')
  print(f'Mängd dricksvatten taget från kran {round((wateruseday*365) - sum(avg_year_365[0]),3)} m³/år.')
  
  print('')