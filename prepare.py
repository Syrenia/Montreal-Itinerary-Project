import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler


def prepare_utility(category,favourite):
    attractions = pd.read_csv('data/attractions_cheap.csv')
    '''
    # Method1 to calculate utility
    standardizer = StandardScaler()
    attractions['utility'] = standardizer.fit_transform(attractions['google_rating'])
    for i in range(30):
        if attractions['category'].iloc[i] == category:
            attractions['utility'].iloc[i] += 5
        if attractions['attraction'].iloc[i] == favourite:
            attractions['utility'].iloc[i] += 15
    '''
    '''
    # Method2 to calculate utility
    mmizer = MinMaxScaler()
    mm = mmizer.fit_transform(attractions[['google_rating', 'time_avg_hours']])
    attractions[['u3','u4']] = mm 
    '''
    
    # Method3 to calculate utility, 'tg' is the product of 'google_rating'/max('google_rating') and 'time_avg_hours'/max('time_avg_hours')
    u = attractions['tg']
    for i in range(30):
        if attractions['category'].iloc[i] in category:
            attractions['tg'].iloc[i] += 0.5
        if attractions['attraction'].iloc[i] in favourite:
            attractions['tg'].iloc[i] += 100

    return attractions['tg'].tolist()

def prepare_data(doc_time,doc_attractions,doc_price,doc_price_l):
    Time_Drive = pd.read_excel(doc_time, sheet_name='time_driving')
    Time_Walk = pd.read_excel(doc_time, sheet_name='time_walking')
    Time_Transit = pd.read_excel(doc_time, sheet_name='time_transit')

    Time_Drive = Time_Drive.drop(columns = 'Unnamed: 0')
    Time_Walk = Time_Walk.drop(columns = 'Unnamed: 0')
    Time_Transit = Time_Transit.drop(columns = 'Unnamed: 0')

    Time_Drive = np.asarray(Time_Drive)
    Time_Walk = np.asarray(Time_Walk)
    Time_Transit = np.asarray(Time_Transit)

    Time_Attraction = pd.read_csv(doc_attractions, usecols=[7])
    Time_Attraction = list(Time_Attraction['time_avg_hours'])

    Fare_Attraction = pd.read_csv(doc_attractions, usecols=[4])
    Fare_Attraction = list(Fare_Attraction['price_adult'])

    Fare_Attraction_c = pd.read_csv(doc_attractions, usecols=[5])
    Fare_Attraction_c = list(Fare_Attraction_c['price_child'])

    Fare_Drive = pd.read_csv(doc_price)
    Fare_Drive = Fare_Drive.drop(columns = 'Unnamed: 0')
    Fare_Drive = np.asarray(Fare_Drive)

    Fare_Drive_l = pd.read_csv(doc_price_l)
    Fare_Drive_l = Fare_Drive_l.drop(columns='Unnamed: 0')
    Fare_Drive_l = np.asarray(Fare_Drive_l)

    Name = pd.read_csv(doc_attractions, usecols=[1])
    Name = list(Name['attraction'].iloc[0:33])

    Category_Attraction = pd.read_csv(doc_attractions, usecols=[3])
    Category_Attraction = list(Category_Attraction['category'])
    
    return Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Drive,Name,Category_Attraction,Fare_Attraction_c,Fare_Drive_l
