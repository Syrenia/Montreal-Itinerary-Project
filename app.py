import json

from flask import Flask
from flask import request
from flask import render_template
from gurobi_model import *
from prepare import *
import pandas as pd


# from flask import response
app = Flask(__name__)


@app.route('/')
def main():  
    favourite_name = pd.read_csv('data/attractions_cheap.csv', usecols=[1])
    favourite_name = list(favourite_name['attraction'].iloc[0:30])
    return render_template("index.html",favourite_name=favourite_name)


@app.route('/index', methods=["GET","POST"])
def index():
    favourite_name = pd.read_csv('data/attractions_cheap.csv', usecols=[1])
    favourite_name = list(favourite_name['attraction'].iloc[0:30])
    return render_template("index.html",favourite_name=favourite_name)


@app.route('/strategy', methods=["GET","POST"])
def strategy():
    doc_time_cheap = 'data/time_matrix_cheap.xlsx'
    doc_attractions_cheap = 'data/attractions_cheap.csv'
    doc_price_cheap = 'data/price_matrix_cheap.csv'
    doc_price_cheap_l = 'data/price_matrix_cheap_l.csv'

    doc_time_medium = 'data/time_matrix_medium.xlsx'
    doc_attractions_medium = 'data/attractions_medium.csv'
    doc_price_medium = 'data/price_matrix_medium.csv'
    doc_price_medium_l = 'data/price_matrix_medium_l.csv'

    doc_time_ex = 'data/time_matrix_expensive.xlsx'
    doc_attractions_ex = 'data/attractions_expensive.csv'
    doc_price_ex = 'data/price_matrix_expensive.csv'
    doc_price_ex_l = 'data/price_matrix_expensive_l.csv'

    time_limit = request.form['time_limit']
    fare_limit_o = request.form['budget_limit']
    days = int(request.form['days'])
    rooms = int(request.form['rooms'])
    adult = int(request.form['adult'])
    children = int(request.form['children'])
    category = request.values.getlist("category")
    favourite = request.values.getlist("favourite")
    print(category,favourite)
    #print(time_limit, fare_limit, days, rooms, adult, children, category, favourite)
    utility = prepare_utility(category,favourite)
    print('utility',utility)
    max_utility = 'NA'
    if fare_limit_o == 'no limit':
        fare_limit = 10000
    else:
        fare_limit = int(fare_limit_o)
    standard = fare_limit/days/(adult+children)
    print('standard',standard)
    if standard <= 100:
        Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Drive,Name,Category_Attraction,Fare_Attraction_c,Fare_Drive_l = prepare_data(doc_time_cheap, doc_attractions_cheap, doc_price_cheap, doc_price_cheap_l)
        if category == ['None'] and favourite == ['None']:  # obj = num of attractions
            if (days == 1):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, trans_oneday, trans_onetrip, ind = one_day(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, Category_Attraction)
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
                len = [0] * 3
                len[0] = int(obj+2)
            elif (days == 3):
                #onetrip here is threeday ticket
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, trans_oneday, trans_onetrip, len,ind = three_day(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, Category_Attraction)
                total_time += 4
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
        else:
            if (days == 1):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, trans_oneday, trans_onetrip,ind = one_day_utility(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, utility, Category_Attraction)
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
                len = [0] * 3
                len[0] = int(obj + 2)
                #max_utility=round(float(max_utility),2)
                max_utility = round(max_utility, 2)
            elif (days == 3):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, trans_oneday, trans_onetrip,len,ind = three_day_utility(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, utility, Category_Attraction)
                #max_utility = round(float(max_utility), 2)
                total_time += 4
                max_utility = round(max_utility, 2)

    elif standard > 100 and standard <= 400:
        Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Drive,Name,Category_Attraction,Fare_Attraction_c,Fare_Drive_l = prepare_data(doc_time_medium, doc_attractions_medium, doc_price_medium,doc_price_medium_l)
        if category == ['None'] and favourite == ['None']:  # obj = num of attractions
            if (days == 1):
                print('test')
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, trans_oneday, trans_onetrip,ind = one_day(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction,Fare_Attraction_c, Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, Category_Attraction)
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
                len = [0] * 3
                len[0] = int(obj+2)
                print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj, len, cat, ind)
            elif (days == 3):
                #onetrip here is threeday ticket
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, trans_oneday, trans_onetrip, len,ind = three_day(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, Category_Attraction)
                total_time += 4
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
        else:
            if (days == 1):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, trans_oneday, trans_onetrip,ind = one_day_utility(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, utility, Category_Attraction)
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
                len = [0] * 3
                len[0] = int(obj + 2)
                #max_utility=round(float(max_utility))
                max_utility = round(max_utility, 2)
            elif (days == 3):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, trans_oneday, trans_onetrip,len,ind = three_day_utility(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, utility, Category_Attraction)
                #max_utility = round(float(max_utility), 2)
                total_time += 4
                max_utility = round(max_utility, 2)

    else:
        Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Drive,Name,Category_Attraction,Fare_Attraction_c,Fare_Drive_l = prepare_data(doc_time_ex, doc_attractions_ex, doc_price_ex, doc_price_ex_l)
        if category == ['None'] and favourite == ['None']:  # obj = num of attractions
            if (days == 1):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, trans_oneday, trans_onetrip,ind = one_day(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction,Fare_Attraction_c, Fare_Drive,Fare_Drive_l, Name, int(time_limit), fare_limit, Category_Attraction)
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
                len = [0] * 3
                len[0] = int(obj+2)
            elif (days == 3):
                #onetrip here is threeday ticket
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, trans_oneday, trans_onetrip, len,ind = three_day(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, Category_Attraction)
                total_time += 4
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
        else:
            if (days == 1):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, trans_oneday, trans_onetrip,ind = one_day_utility(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, utility, Category_Attraction)
                #print(cycle, method, total_time, total_fare, hotel_fare, attraction_fare, obj)
                len = [0] * 3
                len[0] = int(obj + 2)
                #max_utility=round(float(max_utility))
                max_utility = round(max_utility, 2)
            elif (days == 3):
                cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, trans_oneday, trans_onetrip,len,ind = three_day_utility(adult,children,rooms,Time_Drive, Time_Walk, Time_Transit, Time_Attraction, Fare_Attraction, Fare_Attraction_c,Fare_Drive, Fare_Drive_l,Name, int(time_limit), fare_limit, utility, Category_Attraction)
                #max_utility = round(float(max_utility), 2)
                total_time += 4
                max_utility = round(max_utility, 2)

    return render_template("Strategy.html",time_limit = request.form['time_limit'],fare_limit = request.form['budget_limit'],days = request.form['days'],rooms = request.form['rooms'],adult = request.form['adult'],children = request.form['children'],solution=cycle, method=method, total_time=round(total_time,2), total_fare=round(total_fare,2), hotel_fare=hotel_fare, attraction_fare=round(attraction_fare,2), trans_fare=round(trans_fare,2), obj=int(obj), len=len,max_utility=max_utility,cat=cat,trans_oneday=int(trans_oneday), trans_onetrip=int(trans_onetrip),ind=ind,sd=standard)


@app.route('/transit')
def transit():  # put application's code here
    return render_template("transit.html")


@app.route('/contact')
def contact():  # put application's code here
    return render_template("contact.html")


@app.route('/hotel')
def hotel():  # put application's code here
    Hotel = pd.read_csv('data/hotels_new.csv')
    Name = list(Hotel['hotel'].iloc[0:3])
    Fare_Hotel = list(Hotel['nightly_price'])
    star = list(Hotel['star_rating'])
    return render_template("hotel.html",fh=Fare_Hotel,star=star,name=Name)


@app.route('/attractions')
def attractions():  # put application's code here
    Attraction = pd.read_csv('data/attractions_cheap.csv')
    print(1)
    Time_Attraction = list(Attraction['time_avg_hours'])
    print(2)
    Fare_Attraction = list(Attraction['price_adult'])
    print(3)
    Fare_Attraction_c = list(Attraction['price_child'])
    print(4)
    Category_Attraction = list(Attraction['category'])
    print(5)
    Name = list(Attraction['attraction'].iloc[0:30])
    print(6)
    Rate = list(Attraction['google_rating'])
    return render_template("Attractions.html", r=Rate,ta=Time_Attraction, fa=Fare_Attraction,fac=Fare_Attraction_c,ca=Category_Attraction,name=Name)

@app.route('/Entertainment')
def entertainment():
    Attraction = pd.read_csv('data/attractions_cheap.csv')
    Attraction = Attraction[Attraction.category=='Entertainment']
    Time_Attraction = list(Attraction['time_avg_hours'])
    Fare_Attraction = list(Attraction['price_adult'])
    Fare_Attraction_c = list(Attraction['price_child'])
    Category_Attraction = list(Attraction['category'])
    Name = list(Attraction['attraction'].iloc[0:30])
    Rate = list(Attraction['google_rating'])
    i = Attraction.index.tolist()
    for item in i:
        item = str(item)
    return render_template("entertainment.html",  r=Rate,ta=Time_Attraction, fa=Fare_Attraction, fac=Fare_Attraction_c,ca=Category_Attraction, name=Name, i=i)

@app.route('/Food')
def food():
    Attraction = pd.read_csv('data/attractions_cheap.csv')
    Attraction = Attraction[Attraction.category == 'Food']
    Time_Attraction = list(Attraction['time_avg_hours'])
    Fare_Attraction = list(Attraction['price_adult'])
    Fare_Attraction_c = list(Attraction['price_child'])
    Category_Attraction = list(Attraction['category'])
    Name = list(Attraction['attraction'].iloc[0:30])
    Rate = list(Attraction['google_rating'])
    i = Attraction.index.tolist()
    for item in i:
        item = str(item)
    return render_template("food.html",  r=Rate,ta=Time_Attraction, fa=Fare_Attraction, fac=Fare_Attraction_c,ca=Category_Attraction, name=Name,i=i)


@app.route('/Heritage')
def heritage():
    Attraction = pd.read_csv('data/attractions_cheap.csv')
    Attraction = Attraction[Attraction.category == 'Heritage']
    Time_Attraction = list(Attraction['time_avg_hours'])
    Fare_Attraction = list(Attraction['price_adult'])
    Fare_Attraction_c = list(Attraction['price_child'])
    Category_Attraction = list(Attraction['category'])
    Name = list(Attraction['attraction'].iloc[0:30])
    Rate = list(Attraction['google_rating'])
    i = Attraction.index.tolist()
    for item in i:
        item = str(item)
    return render_template("heritage.html",  r=Rate,ta=Time_Attraction, fa=Fare_Attraction, fac=Fare_Attraction_c,ca=Category_Attraction, name=Name,i=i)

@app.route('/Museum')
def museum():
    Attraction = pd.read_csv('data/attractions_cheap.csv')
    Attraction = Attraction[Attraction.category == 'Museum']
    Time_Attraction = list(Attraction['time_avg_hours'])
    Fare_Attraction = list(Attraction['price_adult'])
    Fare_Attraction_c = list(Attraction['price_child'])
    Category_Attraction = list(Attraction['category'])
    Name = list(Attraction['attraction'].iloc[0:30])
    Rate = list(Attraction['google_rating'])
    i = Attraction.index.tolist()
    for item in i:
        item = str(item)
    return render_template("museum.html",  r=Rate,ta=Time_Attraction, fa=Fare_Attraction, fac=Fare_Attraction_c,ca=Category_Attraction, name=Name,i=i)


@app.route('/Nature')
def nature():
    Attraction = pd.read_csv('data/attractions_cheap.csv')
    Attraction = Attraction[Attraction.category == 'Nature']
    Time_Attraction = list(Attraction['time_avg_hours'])
    Fare_Attraction = list(Attraction['price_adult'])
    Fare_Attraction_c = list(Attraction['price_child'])
    Category_Attraction = list(Attraction['category'])
    Name = list(Attraction['attraction'].iloc[0:30])
    Rate = list(Attraction['google_rating'])
    i = Attraction.index.tolist()
    for item in i:
        item = str(item)
    return render_template("nature.html",  r=Rate,ta=Time_Attraction, fa=Fare_Attraction, fac=Fare_Attraction_c,ca=Category_Attraction, name=Name,i=i)


if __name__ == '__main__':
    app.run()


