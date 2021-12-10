import gurobipy as gp
from gurobipy import *


def one_day(noa,noc,nor,Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Attraction_c,Fare_Drive,Fare_Drive_l,Name,time_limit,fare_limit,Category_Attraction):
    Fare_Transit_Oneday = 10
    Fare_Transit_Onetrip = 3.5
    N = 33  #including airport and dummy
    NA = 31 #just attractions and the hotel
    Time_Limit = time_limit*3600
    Fare_Limit = fare_limit
    for i in range(30):
        if Fare_Attraction_c[i] == 'Unavailable':
            Fare_Attraction_c[i] = 9999
        Fare_Attraction[i] = noa*float(Fare_Attraction[i])
        Fare_Attraction_c[i] = noc*float(Fare_Attraction_c[i])
    Fare_Attraction[30] = nor*float(Fare_Attraction[30])
    print(Fare_Attraction, Fare_Attraction_c)
    M = 10000
    if (noa+noc) >= 4:
        Fare_Drive = Fare_Drive_l
    for i in range(31):
        for j in range(31):
            if i !=j:
                Time_Drive[i][j] = Time_Drive[i][j] + 420

    model = gp.Model("Basic Model-one person one day")

    X1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=[Name[i]+" to "+Name[j] for i in range(NA) for j in range(NA)])
    P1 = model.addVars(NA,vtype=GRB.BINARY,lb=0,ub=1,name=Name[0:NA])

    Method_Drive1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=['Drive: Attraction'+str(i)+" to Attraction"+str(j) for i in range(NA) for j in range(NA)])
    Method_Walk1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=['Walk: Attraction'+str(i)+" to Attraction"+str(j) for i in range(NA) for j in range(NA)])
    Method_Transit1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=['Transit: Attraction'+str(i)+" to Attraction"+str(j) for i in range(NA) for j in range(NA)])

    U1 = model.addVars(NA, vtype=GRB.INTEGER,lb=1,ub=(NA-1),name=['u'+str(i) for i in range(NA)])

    y = model.addVar(vtype=GRB.BINARY,name='To decide Transit')
    fare_tt = model.addVar(vtype=GRB.BINARY,name='Transit-oneday')
    tt = model.addVar(vtype=GRB.INTEGER,name='Transit-onetrip')
    fare_h = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='hotel fare')
    fare_a = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='attraction fare')
    fare = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='total fare')
    time = model.addVar(vtype=GRB.CONTINUOUS,lb=0, name='total time')

    # Day1
    for i in range(NA):
        model.addConstr(sum(X1[i, j] for j in range(NA)) == P1[i], name='Day1-From Place' + str(i))
    for j in range(NA):
        model.addConstr(sum(X1[i, j] for i in range(NA)) == P1[j], name='Day1-To Place' + str(j))

    for i in range(NA):
        model.addConstr(X1[i, i] == 0, name='Not itself')

    for i in range(NA - 1):
        for j in range(NA - 1):
            model.addConstr((U1[i] - U1[j] + NA * X1[i, j]) <= (NA - 1), name='No subtour')

    model.addConstr(P1[30] == 1, name='Hotel')

    for i in range(NA):
        for j in range(NA):
            model.addConstr((Method_Drive1[i, j] + Method_Walk1[i, j] + Method_Transit1[i, j]) == X1[i, j],
                            name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk1[i, j]) <= 30 * 60, name='Walking limit')

    time_a1 = sum(Time_Attraction[i] * P1[i] for i in range(NA)) * 3600
    time_t1 = sum((Time_Drive[i][j] * Method_Drive1[i, j] + Time_Walk[i][j] * Method_Walk1[i, j] + Time_Transit[i][j] *
                   Method_Transit1[i, j]) for i in range(NA) for j in range(NA))
    model.addConstr(time_t1 + time_a1 <= Time_Limit, name='Day 1:Time limit')

    #model.addConstr(fare_a == sum(noa*Fare_Attraction[i] * P1[i] for i in range(30)) + sum(noc*Fare_Attraction_c[i] * P1[i] for i in range(30)))
    #model.addConstr(fare_a == noa*sum( Fare_Attraction[i] * P1[i] for i in range(30)) + noc*sum( Fare_Attraction_c[i] * P1[i] for i in range(30)))
    model.addConstr(fare_a == sum( Fare_Attraction[i]*P1[i] for i in range(30)) + sum( Fare_Attraction_c[i]*P1[i] for i in range(30)), name='fare attraction')
    fare_td = sum(Fare_Drive[i][j] * (Method_Drive1[i, j]) for i in range(NA) for j in range(NA))

    model.addConstr(tt == sum(Method_Transit1[i, j] for i in range(NA) for j in range(NA)), name='tansit times')

    model.addConstr(tt >= 3 - M * (1 - y), name='>=3')
    model.addConstr(tt <= 2 + M * (y), name='<=2')
    model.addConstr(fare_tt >= 1 - M * (1 - y),name='1-1')
    model.addConstr(fare_tt <= 1 + M * (1 - y),name='1-2')
    model.addConstr(fare_tt >= -M * (y),name='0-1')
    model.addConstr(fare_tt <= M * (y),name='0-2')

    fare_t = fare_td + noa*(Fare_Transit_Oneday * fare_tt + Fare_Transit_Onetrip * tt * (1 - fare_tt)) + noc*(Fare_Transit_Oneday * fare_tt + (Fare_Transit_Onetrip-1) * tt * (1 - fare_tt))
    model.addConstr(fare_a + fare_t + fare_h <= Fare_Limit, name='Fare limit')

    model.addConstr(fare_h == Fare_Attraction[30], name='hotel fare')
    model.addConstr((fare_a + fare_t + fare_h) == fare, name='total fare')
    model.addConstr((time_a1 + time_t1) / 3600 == time, name='total time')

    model.update()
    obj = sum(P1[i] for i in range(30))

    model.setObjective(obj, GRB.MAXIMIZE)
    #model.setParam(GRB.Param.PoolSearchMode, 2)
    #model.setParam(GRB.Param.PoolSolutions, 3)
    model.optimize()
    '''
    model.computeIIS()
    model.write('model.ilp')
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s'% c.constrName)
    '''
    index_h = 30
    if Name[30] == 'Hotel Casa Bella':
        index_h = 30
    elif Name[30] == 'Hotel Monville':
        index_h = 31
    else:
        index_h = 32


    ind = [[]] * 3
    ind[0].append(index_h)
    cycle = [[]] * 3
    cycle[0].append(Name[30])

    method = [[]] * 3
    cat = [[]] * 3
    cat[0].append('Hotel')
    k = 30
    k_hotel = 30
    flag = 0
    for i in range(31):
        if flag == 1:
            break
        for j in range(31):
            name = Name[k] + " to " + Name[j]
            if model.getVarByName(name).x > 0.1:
                cycle[0].append(Name[j])
                ind[0].append(j)
                cat[0].append(Category_Attraction[j])
                drive = 'Drive: Attraction' + str(k) + " to Attraction" + str(j)
                walk = 'Walk: Attraction' + str(k) + " to Attraction" + str(j)
                transit = 'Transit: Attraction' + str(k) + " to Attraction" + str(j)
                if model.getVarByName(drive).x > 0.1:
                    method[0].append("drive")
                elif model.getVarByName(walk).x > 0.1:
                    method[0].append("walk")
                else:
                    method[0].append("transit")
                k = j
                if k == k_hotel:
                    flag = 1
                    break
    method[0].append('end')
    ind[0][-1] = index_h
    print(ind)
    cat[0][-1] = "Hotel"
    total_time = model.getVarByName('total time').x
    total_fare = model.getVarByName('total fare').x
    hotel_fare = model.getVarByName('hotel fare').x
    attraction_fare = model.getVarByName('attraction fare').x
    transit_oneday = model.getVarByName('Transit-oneday').x
    if (model.getVarByName('Transit-onetrip').x >= 3):
        transit_onetrip = 0
    else:
        transit_onetrip = model.getVarByName('Transit-onetrip').x
    trans_fare = total_fare-hotel_fare-attraction_fare
    obj = model.objVal

    return cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, transit_oneday, transit_onetrip, ind



def one_day_utility(noa,noc,nor,Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Attraction_c,Fare_Drive,Fare_Drive_l,Name,time_limit,fare_limit,utility,Category_Attraction):
    Fare_Transit_Oneday = 10
    Fare_Transit_Onetrip = 3.5
    N = 33  #including airport and dummy
    NA = 31 #just attractions and the hotel
    Time_Limit = time_limit*3600
    Fare_Limit = fare_limit
    for i in range(30):
        if Fare_Attraction_c[i] == 'Unavailable':
            Fare_Attraction_c[i] = 9999
        Fare_Attraction[i] = noa*float(Fare_Attraction[i])
        Fare_Attraction_c[i] = noc*float(Fare_Attraction_c[i])
    Fare_Attraction[30] = nor*float(Fare_Attraction[30])
    print(Fare_Attraction, Fare_Attraction_c)
    M = 10000
    if (noa+noc) >= 4:
        Fare_Drive = Fare_Drive_l
    print(Fare_Drive)
    for i in range(31):
        for j in range(31):
            if i !=j:
                Time_Drive[i][j] = Time_Drive[i][j] + 420

    model = gp.Model("Basic Model-one person one day utility")

    X1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=[Name[i]+" to "+Name[j] for i in range(NA) for j in range(NA)])
    P1 = model.addVars(NA,vtype=GRB.BINARY,lb=0,ub=1,name=Name[0:NA])

    Method_Drive1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=['Drive: Attraction'+str(i)+" to Attraction"+str(j) for i in range(NA) for j in range(NA)])
    Method_Walk1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=['Walk: Attraction'+str(i)+" to Attraction"+str(j) for i in range(NA) for j in range(NA)])
    Method_Transit1 = model.addVars(NA,NA,vtype=GRB.BINARY,lb=0,ub=1,name=['Transit: Attraction'+str(i)+" to Attraction"+str(j) for i in range(NA) for j in range(NA)])

    U1 = model.addVars(NA, vtype=GRB.INTEGER,lb=1,ub=(NA-1),name=['u'+str(i) for i in range(NA)])

    y = model.addVar(vtype=GRB.BINARY,name='To decide Transit')
    fare_tt = model.addVar(vtype=GRB.BINARY,name='Transit-oneday')
    tt = model.addVar(vtype=GRB.INTEGER, name='Transit-onetrip')
    fare_h = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='hotel fare')
    fare_a = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='attraction fare')
    fare = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='total fare')
    time = model.addVar(vtype=GRB.CONTINUOUS,lb=0, name='total time')

    # Day1
    for i in range(NA):
        model.addConstr(sum(X1[i, j] for j in range(NA)) == P1[i], name='Day1-From Place' + str(i))
    for j in range(NA):
        model.addConstr(sum(X1[i, j] for i in range(NA)) == P1[j], name='Day1-To Place' + str(j))

    for i in range(NA):
        model.addConstr(X1[i, i] == 0, name='Not itself')

    for i in range(NA - 1):
        for j in range(NA - 1):
            model.addConstr((U1[i] - U1[j] + NA * X1[i, j]) <= (NA - 1), name='No subtour')

    model.addConstr(P1[30] == 1, name='Hotel')

    for i in range(NA):
        for j in range(NA):
            model.addConstr((Method_Drive1[i, j] + Method_Walk1[i, j] + Method_Transit1[i, j]) == X1[i, j],
                            name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk1[i, j]) <= 30 * 60, name='Walking limit')

    time_a1 = sum(Time_Attraction[i] * P1[i] for i in range(NA)) * 3600
    time_t1 = sum((Time_Drive[i][j] * Method_Drive1[i, j] + Time_Walk[i][j] * Method_Walk1[i, j] + Time_Transit[i][j] *
                   Method_Transit1[i, j]) for i in range(NA) for j in range(NA))
    model.addConstr(time_t1 + time_a1 <= Time_Limit, name='Day 1:Time limit')

    model.addConstr(fare_a == sum(Fare_Attraction[i] * (P1[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P1[i]) for i in range(30)))
    fare_td = sum(Fare_Drive[i][j] * (Method_Drive1[i, j]) for i in range(NA) for j in range(NA))

    model.addConstr(tt == sum(Method_Transit1[i, j] for i in range(NA) for j in range(NA)))

    model.addConstr(tt >= 3 - M * (1 - y))
    model.addConstr(tt <= 2 + M * (y))
    model.addConstr(fare_tt >= 1 - M * (1 - y))
    model.addConstr(fare_tt <= 1 + M * (1 - y))
    model.addConstr(fare_tt >= -M * (y))
    model.addConstr(fare_tt <= M * (y))

    fare_t = fare_td + noa*(Fare_Transit_Oneday * fare_tt + Fare_Transit_Onetrip * tt * (1 - fare_tt)) + noc*(Fare_Transit_Oneday * fare_tt + (Fare_Transit_Onetrip-1) * tt * (1 - fare_tt))
    model.addConstr(fare_a + fare_t +fare_h <= Fare_Limit, name='Fare limit')

    model.addConstr(Fare_Attraction[30] * P1[30] == fare_h, name='hotel fare')
    model.addConstr((fare_a + fare_t + fare_h) == fare, name='total fare')
    model.addConstr((time_a1 + time_t1) / 3600 == time, name='total time')

    model.update()
    obj = sum(utility[i]*P1[i] for i in range(30))

    model.setObjective(obj, GRB.MAXIMIZE)
    model.setParam(GRB.Param.PoolSearchMode, 2)
    model.setParam(GRB.Param.PoolSolutions, 5)
    model.optimize()
    model.setParam(GRB.Param.SolutionNumber, 1)
    print("Optimal Soultion:")
    for v in model.getVars():
        if v.xn > 0:
            print(v.varName, "=", round(v.xn, 2))
    model.setParam(GRB.Param.SolutionNumber, 3)
    print("Optimal Soultion:")
    for v in model.getVars():
        if v.xn > 0:
            print(v.varName, "=", round(v.xn, 2))
    model.setParam(GRB.Param.SolutionNumber, 4)
    print("Optimal Soultion:")
    for v in model.getVars():
        if v.xn > 0:
            print(v.varName, "=", round(v.xn, 2))


    if Name[30] == 'Hotel Casa Bella':
        index_h = 30
    elif Name[30] == 'Hotel Monville':
        index_h = 31
    else:
        index_h = 32

    ind = [[]] * 3
    ind[0].append(index_h)
    cycle = [[]]*3
    cycle[0].append(Name[30])

    method = [[]]*3
    cat = [[]]*3
    cat[0].append('Hotel')
    k = 30
    k_hotel = 30
    flag = 0
    for i in range(31):
        if flag == 1:
            break
        for j in range(31):
            name = Name[k] + " to " + Name[j]
            if model.getVarByName(name).x > 0.1:
                cycle[0].append(Name[j])
                ind[0].append(j)
                cat[0].append(Category_Attraction[j])
                drive = 'Drive: Attraction' + str(k) + " to Attraction" + str(j)
                walk = 'Walk: Attraction' + str(k) + " to Attraction" + str(j)
                transit = 'Transit: Attraction' + str(k) + " to Attraction" + str(j)
                if model.getVarByName(drive).x > 0.1:
                    method[0].append("drive")
                elif model.getVarByName(walk).x > 0.1:
                    method[0].append("walk")
                else:
                    method[0].append("transit")
                k = j
                if k == k_hotel:
                    flag = 1
                    break
    method[0].append('end')
    cat[0][-1] = "Hotel"
    ind[0][-1] = index_h
    total_time = model.getVarByName('total time').x
    total_fare = model.getVarByName('total fare').x
    hotel_fare = model.getVarByName('hotel fare').x
    attraction_fare = model.getVarByName('attraction fare').x
    transit_oneday = model.getVarByName('Transit-oneday').x
    if(model.getVarByName('Transit-onetrip').x >= 3):
        transit_onetrip = 0
    else:
        transit_onetrip = model.getVarByName('Transit-onetrip').x
    trans_fare = total_fare-hotel_fare-attraction_fare
    obj = len(cycle[0])-2
    max_utility = model.objVal
    print(cycle)
    print(method)
    print(cat)
    return cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility,cat, transit_oneday, transit_onetrip,ind



def three_day(noa,noc,nor,Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Attraction_c,Fare_Drive,Fare_Drive_l,Name,time_limit,fare_limit,Category_Attraction):
    Fare_Transit_Oneday = 10
    Fare_Transit_Onetrip = 3.5
    N = 33  #including airport and dummy
    NA = 31 #just attractions and the hotel
    Time_Limit = time_limit*3600
    Fare_Limit = fare_limit
    for i in range(30):
        if Fare_Attraction_c[i] == 'Unavailable':
            Fare_Attraction_c[i] = 9999
        Fare_Attraction[i] = noa*float(Fare_Attraction[i])
        Fare_Attraction_c[i] = noc*float(Fare_Attraction_c[i])
    Fare_Attraction[30] = nor*float(Fare_Attraction[30])
    print(Fare_Attraction, Fare_Attraction_c)
    M = 10000
    if (noa+noc) >= 4:
        Fare_Drive = Fare_Drive_l
    for i in range(31):
        for j in range(31):
            if i !=j:
                Time_Drive[i][j] = Time_Drive[i][j] + 420

    model = gp.Model("Extensive Model-one person three days")

    X1 = model.addVars(N,N,vtype=GRB.BINARY,lb=0,ub=1,name=['Day1'+Name[i]+" to "+Name[j] for i in range(N) for j in range(N)])
    X2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day2'+Name[i]+" to "+Name[j] for i in range(NA) for j in range(NA)])
    X3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day3'+Name[i]+" to "+Name[j] for i in range(N) for j in range(N)])
    P1 = model.addVars(N,vtype=GRB.BINARY,lb=0,ub=1,name=['Day1'+Name[i] for i in range(N)])
    P2 = model.addVars(NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day2' + Name[i] for i in range(NA)])
    P3 = model.addVars(N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day3' + Name[i] for i in range(N)])

    Method_Drive1 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 1-Drive: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Walk1 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 1-Walk: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Transit1 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 1-Transit: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])

    Method_Drive2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 2-Drive: Attraction' + str(i) + " to Attraction" + str(j) for i in range(NA) for j in range(NA)])
    Method_Walk2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 2-Walk: Attraction' + str(i) + " to Attraction" + str(j) for i in range(NA) for j in range(NA)])
    Method_Transit2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 2-Transit: Attraction' + str(i) + " to Attraction" + str(j) for i in range(NA) for j in range(NA)])

    Method_Drive3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 3-Drive: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Walk3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 3-Walk: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Transit3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 3-Transit: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])

    U1 = model.addVars(N, vtype=GRB.INTEGER, lb=1, ub=(N - 1), name=['Day1-u' + str(i) for i in range(N)])
    U2 = model.addVars(NA, vtype=GRB.INTEGER, lb=1, ub=(NA - 1), name=['Day2-u' + str(i) for i in range(NA)])
    U3 = model.addVars(N, vtype=GRB.INTEGER, lb=1, ub=(N - 1), name=['Day3-u' + str(i) for i in range(N)])

    y1 = model.addVar(vtype=GRB.BINARY)
    y2 = model.addVar(vtype=GRB.BINARY)
    y3 = model.addVar(vtype=GRB.BINARY)
    y4 = model.addVar(vtype=GRB.BINARY)
    fare_tt1 = model.addVar(vtype=GRB.BINARY, name='Day1:transit')
    fare_tt2 = model.addVar(vtype=GRB.BINARY, name='Day2:transit')
    fare_tt3 = model.addVar(vtype=GRB.BINARY, name='Day3:transit')
    fare_tt = model.addVar(vtype=GRB.CONTINUOUS, name='transit fare')
    fare_h = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='hotel fare')
    fare_a = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='attraction fare')
    fare = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='total fare')
    time = model.addVar(vtype=GRB.CONTINUOUS,lb=0, name='total time')
    A1 = model.addVar(vtype=GRB.INTEGER,lb=0, name='Day1')
    A2 = model.addVar(vtype=GRB.INTEGER, lb=0, name='Day2')
    A3 = model.addVar(vtype=GRB.INTEGER, lb=0, name='Day3')

    # Day1
    for i in range(N):
        model.addConstr(sum(X1[i, j] for j in range(N)) == P1[i], name='Day1-From Place' + str(i) + '=P[i]')
    for j in range(N):
        model.addConstr(sum(X1[i, j] for i in range(N)) == P1[j], name='Day1-To Place' + str(j) + '=P[i]')

    for i in range(N):
        model.addConstr(X1[i, i] == 0, name='Not itself')

    for i in range(N - 1):
        for j in range(N - 1):
            model.addConstr((U1[i] - U1[j] + N * X1[i, j]) <= (N - 1), name='No subtour')

    model.addConstr(P1[30] == 1, name='One hotel')
    model.addConstr(P1[31] == 1, name='From Airport')
    model.addConstr(P1[32] == 1, name='Dummy')
    model.addConstr(X1[32, 31] == 1, name='Dummy-Airport')
    model.addConstr(X1[30, 32] == 1, name='Hotel-Dummy')
    model.addConstr(Method_Walk1[32, 31] == 1, name='walk:Dummy-Airport')
    model.addConstr(Method_Walk1[30, 32] == 1, name='walk:Hotel-Dummy')

    for i in range(N):
        for j in range(N):
            model.addConstr((Method_Drive1[i, j] + Method_Walk1[i, j] + Method_Transit1[i, j]) == X1[i, j], name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk1[i, j]) <= 30 * 60, name='Walking limit')

    time_a1 = sum(Time_Attraction[i] * P1[i] for i in range(N)) * 3600
    time_t1 = sum((Time_Drive[i][j] * Method_Drive1[i, j] + Time_Walk[i][j] * Method_Walk1[i, j] + Time_Transit[i][j] * Method_Transit1[i, j]) for i in range(N) for j in range(N))
    time1 = time_a1 + time_t1
    model.addConstr(time_t1 + time_a1 <= Time_Limit-2*3600, name='Day 1:Time limit')
    fare_a1 = sum(Fare_Attraction[i] * (P1[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P1[i]) for i in range(30))
    fare_td1 = sum(Fare_Drive[i][j] * (Method_Drive1[i, j]) for i in range(N) for j in range(N))
    fare_1 = fare_a1 + fare_td1

    # Day2

    for i in range(NA):
        model.addConstr(sum(X2[i, j] for j in range(NA)) == P2[i], name='Day2-From Place' + str(i) + '=P[i]')
    for j in range(NA):
        model.addConstr(sum(X2[i, j] for i in range(NA)) == P2[j], name='Day2-To Place' + str(j) + '=P[i]')

    for i in range(NA):
        model.addConstr(X2[i, i] == 0, name='Not itself')

    for i in range(NA - 1):
        for j in range(NA - 1):
            model.addConstr((U2[i] - U2[j] + NA * X2[i, j]) <= (NA - 1), name='No subtour')

    model.addConstr(P2[30] == 1, name='One hotel')

    for i in range(NA):
        for j in range(NA):
            model.addConstr((Method_Drive2[i, j] + Method_Walk2[i, j] + Method_Transit2[i, j]) == X2[i, j], name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk2[i, j]) <= 30 * 60, name='Walking limit')

    time_a2 = sum(Time_Attraction[i] * P2[i] for i in range(NA)) * 3600
    time_t2 = sum((Time_Drive[i][j] * Method_Drive2[i, j] + Time_Walk[i][j] * Method_Walk2[i, j] + Time_Transit[i][j] * Method_Transit2[i, j]) for i in range(NA) for j in range(NA))
    time2 = time_a2 + time_t2
    model.addConstr(time_t2 + time_a2 <= Time_Limit, name='Day 2:Time limit')
    fare_a2 = sum(Fare_Attraction[i] * (P2[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P2[i]) for i in range(30))
    fare_td2 = sum(Fare_Drive[i][j] * (Method_Drive2[i, j]) for i in range(NA) for j in range(NA))
    fare_2 = fare_a2 + fare_td2

    # Day3
    for i in range(N):
        model.addConstr(sum(X3[i, j] for j in range(N)) == P3[i], name='Day3-From Place' + str(i) + '=P[i]')
    for j in range(N):
        model.addConstr(sum(X3[i, j] for i in range(N)) == P3[j], name='Day3-To Place' + str(j) + '=P[i]')

    for i in range(N):
        model.addConstr(X3[i, i] == 0, name='Not itself')

    for i in range(N - 1):
        for j in range(N - 1):
            model.addConstr((U3[i] - U3[j] + N * X3[i, j]) <= (N - 1), name='No subtour')

    model.addConstr(P3[30] == 1, name='One hotel')
    model.addConstr(P3[31] == 1, name='From Airport')
    model.addConstr(P3[32] == 1, name='Dummy')
    model.addConstr(X3[32, 30] == 1, name='Dummy-Hotel')
    model.addConstr(X3[31, 32] == 1, name='Airport-Dummy')
    model.addConstr(Method_Walk3[32, 30] == 1, name='walk:Dummy-Hotel')
    model.addConstr(Method_Walk3[31, 32] == 1, name='walk:Airport-Dummy')

    for i in range(N):
        for j in range(N):
            model.addConstr((Method_Drive3[i, j] + Method_Walk3[i, j] + Method_Transit3[i, j]) == X3[i, j],name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk3[i, j]) <= 30 * 60, name='Walking limit')

    time_a3 = sum(Time_Attraction[i] * P3[i] for i in range(N)) * 3600
    time_t3 = sum((Time_Drive[i][j] * Method_Drive3[i, j] + Time_Walk[i][j] * Method_Walk3[i, j] + Time_Transit[i][j] * Method_Transit3[i, j]) for i in range(N) for j in range(N))
    time3 = time_a3 + time_t3
    model.addConstr(time_t3 + time_a3 <= Time_Limit-2*3600, name='Day 3:Time limit')
    fare_a3 = sum(Fare_Attraction[i] * (P3[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P3[i]) for i in range(30))
    fare_td3 = sum(Fare_Drive[i][j] * (Method_Drive3[i, j]) for i in range(N) for j in range(N))
    fare_3 = fare_a3 + fare_td3

    # General
    for i in range(30):
        model.addConstr((P1[i] + P2[i] + P3[i]) <= 1)

    model.addConstr(fare_h == 2*Fare_Attraction[30],name='hotel fare')
    model.addConstr(fare_a == fare_a1+fare_a2+fare_a3, name='attraction fare')
    model.addConstr(fare_1 + fare_2 + fare_3 + fare_h + (noa+noc)*fare_tt <= Fare_Limit, name='Fare limit')

    model.addConstr((fare_1 + fare_2 + fare_3 + fare_h + (noa+noc)*fare_tt) == fare, name='total fare')
    model.addConstr((time1 + time2 + time3) / 3600 == time, name='total time')

    # If three days all includes transit method, then three-day ticket(20.5), otherwise, one-day ticket(10) for each day
    tt1 = sum(Method_Transit1[i, j] for i in range(N) for j in range(N))
    tt2 = sum(Method_Transit2[i, j] for i in range(NA) for j in range(NA))
    tt3 = sum(Method_Transit3[i, j] for i in range(N) for j in range(N))
    model.addConstr(tt1 >= 1 - M * (1 - y1))
    model.addConstr(tt1 <= 0 + M * (y1))
    model.addConstr(fare_tt1 >= 1 - M * (1 - y1))
    model.addConstr(fare_tt1 <= 1 + M * (1 - y1))
    model.addConstr(fare_tt1 >= -M * (y1))
    model.addConstr(fare_tt1 <= M * (y1))

    model.addConstr(tt2 >= 1 - M * (1 - y2))
    model.addConstr(tt2 <= 0 + M * (y2))
    model.addConstr(fare_tt2 >= 1 - M * (1 - y2))
    model.addConstr(fare_tt2 <= 1 + M * (1 - y2))
    model.addConstr(fare_tt2 >= -M * (y2))
    model.addConstr(fare_tt2 <= M * (y2))

    model.addConstr(tt3 >= 1 - M * (1 - y3))
    model.addConstr(tt3 <= 0 + M * (y3))
    model.addConstr(fare_tt3 >= 1 - M * (1 - y3))
    model.addConstr(fare_tt3 <= 1 + M * (1 - y3))
    model.addConstr(fare_tt3 >= -M * (y3))
    model.addConstr(fare_tt3 <= M * (y3))

    model.addConstr(fare_tt1 + fare_tt2 + fare_tt3 >= 3 - M * (1 - y4))
    model.addConstr(fare_tt1 + fare_tt2 + fare_tt3 <= 2 + M * (y4))
    model.addConstr(fare_tt >= 20.5 - M * (1 - y4))
    model.addConstr(fare_tt <= 20.5 + M * (1 - y4))
    model.addConstr(fare_tt >= 10 * (fare_tt1 + fare_tt2 + fare_tt3) - M * (y4))
    model.addConstr(fare_tt <= 10 * (fare_tt1 + fare_tt2 + fare_tt3) + M * (y4))

    model.addConstr(A1 == sum(P1[i] for i in range(30)))
    model.addConstr(A2 == sum(P2[i] for i in range(30)))
    model.addConstr(A3 == sum(P3[i] for i in range(30)))

    model.update()
    obj = sum(P1[i] + P2[i] + P3[i] for i in range(30))

    model.setObjective(obj, GRB.MAXIMIZE)
    model.setParam('TimeLimit', 20)
    #model.setParam(GRB.Param.PoolSearchMode, 2)
    #model.setParam(GRB.Param.PoolSolutions, 3)
    model.optimize()

    index_h = 30
    if Name[30] == 'Hotel Casa Bella':
        index_h = 30
    elif Name[30] == 'Hotel Monville':
        index_h = 31
    else:
        index_h = 32

    index_a = 33

    ind1 = [index_a]
    cycle1 = [Name[31]]
    method1 = []
    cat1 = []
    cat1.append('Airport')
    k1 = 31
    k2 = 30
    k3 = 30
    k_hotel = 30
    k_airport = 31
    flag = 0
    for i in range(32):
        if flag == 1:
            break
        for j in range(32):
            name1 = 'Day1'+ Name[k1] + " to " + Name[j]
            if model.getVarByName(name1).x > 0.1:
                cycle1.append(Name[j])
                ind1.append(j)
                cat1.append(Category_Attraction[j])
                drive1 = 'Day 1-Drive: Attraction' + str(k1) + " to Attraction" + str(j)
                walk1 = 'Day 1-Walk: Attraction' + str(k1) + " to Attraction" + str(j)
                transit1 = 'Day 1-Transit: Attraction' + str(k1) + " to Attraction" + str(j)
                if model.getVarByName(drive1).x > 0.1:
                    method1.append("drive")
                elif model.getVarByName(walk1).x > 0.1:
                    method1.append("walk")
                else:
                    method1.append("transit")
                k1 = j
                if k1 == k_hotel:
                    flag = 1
                    break
    method1.append('end')
    cat1[-1] = "Hotel"
    ind1[-1] = index_h

    cycle2 = [Name[30]]
    ind2 = [index_h]
    method2 = []
    cat2 = []
    cat2.append('Hotel')
    flag = 0
    for i in range(31):
        if flag == 1:
            break
        for j in range(31):
            name2 = 'Day2'+ Name[k2] + " to " + Name[j]
            print("test", name2)
            print(model.getVarByName(name2).x)
            if model.getVarByName(name2).x > 0.1:
                cycle2.append(Name[j])
                ind2.append(j)
                cat2.append(Category_Attraction[j])
                drive2 = 'Day 2-Drive: Attraction' + str(k2) + " to Attraction" + str(j)
                walk2 = 'Day 2-Walk: Attraction' + str(k2) + " to Attraction" + str(j)
                transit2 = 'Day 2-Transit: Attraction' + str(k2) + " to Attraction" + str(j)
                if model.getVarByName(drive2).x > 0.1:
                    method2.append("drive")
                elif model.getVarByName(walk2).x > 0.1:
                    method2.append("walk")
                else:
                    method2.append("transit")
                k2 = j
                if k2 == k_hotel:
                    flag = 1
                    break
    method2.append('end')
    cat2[-1] = "Hotel"
    ind2[-1] = index_h

    cycle3 = [Name[30]]
    ind3 = [index_h]
    method3 = []
    cat3 = []
    cat3.append('Hotel')
    flag = 0
    for i in range(32):
        if flag == 1:
            break
        for j in range(32):
            name3 = 'Day3'+ Name[k3] + " to " + Name[j]
            if model.getVarByName(name3).x > 0.1:
                cycle3.append(Name[j])
                ind3.append(j)
                cat3.append(Category_Attraction[j])
                drive3 = 'Day 3-Drive: Attraction' + str(k3) + " to Attraction" + str(j)
                walk3 = 'Day 3-Walk: Attraction' + str(k3) + " to Attraction" + str(j)
                transit3 = 'Day 3-Transit: Attraction' + str(k3) + " to Attraction" + str(j)
                if model.getVarByName(drive3).x > 0.1:
                    method3.append("drive")
                elif model.getVarByName(walk3).x > 0.1:
                    method3.append("walk")
                else:
                    method3.append("transit")
                k3 = j
                if k3 == k_airport:
                    flag = 1
                    break
    method3.append('end')
    cat3[-1] = "Airport"
    ind3[-1] = index_a

    total_time = model.getVarByName('total time').x
    total_fare = model.getVarByName('total fare').x
    hotel_fare = model.getVarByName('hotel fare').x
    attraction_fare = model.getVarByName('attraction fare').x
    transit_threeday = 0
    transit_oneday = 0
    if (model.getVarByName('transit fare').x == 20.5):
        transit_threeday = 1
    else:
        transit_oneday = model.getVarByName('transit fare').x/10
    trans_fare = total_fare-hotel_fare-attraction_fare
    obj = model.objVal
    cycle,method,cat,len,ind = [],[],[],[],[]
    cycle.append(cycle1)
    cycle.append(cycle2)
    cycle.append(cycle3)
    method.append(method1)
    method.append(method2)
    method.append(method3)
    cat.append(cat1)
    cat.append(cat2)
    cat.append(cat3)
    len1 = int(model.getVarByName('Day1').x+2)
    len2 = int(model.getVarByName('Day2').x+2)
    len3 = int(model.getVarByName('Day3').x+2)
    len.append(len1)
    len.append(len2)
    len.append(len3)
    ind.append(ind1)
    ind.append(ind2)
    ind.append(ind3)
    print("Optimal Soultion:")
    for v in model.getVars():
        if v.x > 0:
            print(v.varName, "=", round(v.x, 2))
    print("matrix")
    print(cycle)
    print(method)
    print(cat)
    print(ind)
    print(len)

    return cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, cat, transit_oneday, transit_threeday,len,ind


def three_day_utility(noa,noc,nor,Time_Drive,Time_Walk,Time_Transit,Time_Attraction,Fare_Attraction,Fare_Attraction_c,Fare_Drive,Fare_Drive_l,Name,time_limit,fare_limit,utility,Category_Attraction):
    Fare_Transit_Oneday = 10
    Fare_Transit_Onetrip = 3.5
    N = 33  #including airport and dummy
    NA = 31 #just attractions and the hotel
    Time_Limit = time_limit*3600
    Fare_Limit = fare_limit
    for i in range(30):
        if Fare_Attraction_c[i] == 'Unavailable':
            Fare_Attraction_c[i] = 9999
        Fare_Attraction[i] = noa * float(Fare_Attraction[i])
        Fare_Attraction_c[i] = noc * float(Fare_Attraction_c[i])
    Fare_Attraction[30] = nor * float(Fare_Attraction[30])
    print(Fare_Attraction, Fare_Attraction_c)
    M = 10000
    if (noa + noc) >= 4:
        Fare_Drive = Fare_Drive_l
    for i in range(31):
        for j in range(31):
            if i != j:
                Time_Drive[i][j] = Time_Drive[i][j] + 420

    model = gp.Model("Extensive Model-one person three days")

    X1 = model.addVars(N,N,vtype=GRB.BINARY,lb=0,ub=1,name=['Day1'+Name[i]+" to "+Name[j] for i in range(N) for j in range(N)])
    X2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day2'+Name[i]+" to "+Name[j] for i in range(NA) for j in range(NA)])
    X3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day3'+Name[i]+" to "+Name[j] for i in range(N) for j in range(N)])
    P1 = model.addVars(N,vtype=GRB.BINARY,lb=0,ub=1,name=['Day1'+Name[i] for i in range(N)])
    P2 = model.addVars(NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day2' + Name[i] for i in range(NA)])
    P3 = model.addVars(N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day3' + Name[i] for i in range(N)])

    Method_Drive1 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 1-Drive: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Walk1 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 1-Walk: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Transit1 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 1-Transit: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])

    Method_Drive2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 2-Drive: Attraction' + str(i) + " to Attraction" + str(j) for i in range(NA) for j in range(NA)])
    Method_Walk2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 2-Walk: Attraction' + str(i) + " to Attraction" + str(j) for i in range(NA) for j in range(NA)])
    Method_Transit2 = model.addVars(NA, NA, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 2-Transit: Attraction' + str(i) + " to Attraction" + str(j) for i in range(NA) for j in range(NA)])

    Method_Drive3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 3-Drive: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Walk3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 3-Walk: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])
    Method_Transit3 = model.addVars(N, N, vtype=GRB.BINARY, lb=0, ub=1, name=['Day 3-Transit: Attraction' + str(i) + " to Attraction" + str(j) for i in range(N) for j in range(N)])

    U1 = model.addVars(N, vtype=GRB.INTEGER, lb=1, ub=(N - 1), name=['Day1-u' + str(i) for i in range(N)])
    U2 = model.addVars(NA, vtype=GRB.INTEGER, lb=1, ub=(NA - 1), name=['Day2-u' + str(i) for i in range(NA)])
    U3 = model.addVars(N, vtype=GRB.INTEGER, lb=1, ub=(N - 1), name=['Day3-u' + str(i) for i in range(N)])

    y1 = model.addVar(vtype=GRB.BINARY)
    y2 = model.addVar(vtype=GRB.BINARY)
    y3 = model.addVar(vtype=GRB.BINARY)
    y4 = model.addVar(vtype=GRB.BINARY)
    fare_tt1 = model.addVar(vtype=GRB.BINARY, name='Day1:transit')
    fare_tt2 = model.addVar(vtype=GRB.BINARY, name='Day2:transit')
    fare_tt3 = model.addVar(vtype=GRB.BINARY, name='Day3:transit')
    fare_tt = model.addVar(vtype=GRB.CONTINUOUS, name='transit fare')
    fare_h = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='hotel fare')
    fare_a = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='attraction fare')
    fare = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='total fare')
    time = model.addVar(vtype=GRB.CONTINUOUS,lb=0, name='total time')
    A1 = model.addVar(vtype=GRB.INTEGER,lb=0, name='Day1')
    A2 = model.addVar(vtype=GRB.INTEGER, lb=0, name='Day2')
    A3 = model.addVar(vtype=GRB.INTEGER, lb=0, name='Day3')

    # Day1
    for i in range(N):
        model.addConstr(sum(X1[i, j] for j in range(N)) == P1[i], name='Day1-From Place' + str(i) + '=P[i]')
    for j in range(N):
        model.addConstr(sum(X1[i, j] for i in range(N)) == P1[j], name='Day1-To Place' + str(j) + '=P[i]')

    for i in range(N):
        model.addConstr(X1[i, i] == 0, name='Not itself')

    for i in range(N - 1):
        for j in range(N - 1):
            model.addConstr((U1[i] - U1[j] + N * X1[i, j]) <= (N - 1), name='No subtour')

    model.addConstr(P1[30] == 1, name='One hotel')
    model.addConstr(P1[31] == 1, name='From Airport')
    model.addConstr(P1[32] == 1, name='Dummy')
    model.addConstr(X1[32, 31] == 1, name='Dummy-Airport')
    model.addConstr(X1[30, 32] == 1, name='Hotel-Dummy')
    model.addConstr(Method_Walk1[32, 31] == 1, name='walk:Dummy-Airport')
    model.addConstr(Method_Walk1[30, 32] == 1, name='walk:Hotel-Dummy')

    for i in range(N):
        for j in range(N):
            model.addConstr((Method_Drive1[i, j] + Method_Walk1[i, j] + Method_Transit1[i, j]) == X1[i, j], name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk1[i, j]) <= 30 * 60, name='Walking limit')

    time_a1 = sum(Time_Attraction[i] * P1[i] for i in range(N)) * 3600
    time_t1 = sum((Time_Drive[i][j] * Method_Drive1[i, j] + Time_Walk[i][j] * Method_Walk1[i, j] + Time_Transit[i][j] * Method_Transit1[i, j]) for i in range(N) for j in range(N))
    time1 = time_a1 + time_t1
    model.addConstr(time_t1 + time_a1 <= Time_Limit-2*3600, name='Day 1:Time limit')
    fare_a1 = sum(Fare_Attraction[i] * (P1[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P1[i]) for i in range(30))
    fare_td1 = sum(Fare_Drive[i][j] * (Method_Drive1[i, j]) for i in range(N) for j in range(N))
    fare_1 = fare_a1 + fare_td1

    # Day2

    for i in range(NA):
        model.addConstr(sum(X2[i, j] for j in range(NA)) == P2[i], name='Day2-From Place' + str(i) + '=P[i]')
    for j in range(NA):
        model.addConstr(sum(X2[i, j] for i in range(NA)) == P2[j], name='Day2-To Place' + str(j) + '=P[i]')

    for i in range(NA):
        model.addConstr(X2[i, i] == 0, name='Not itself')

    for i in range(NA - 1):
        for j in range(NA - 1):
            model.addConstr((U2[i] - U2[j] + NA * X2[i, j]) <= (NA - 1), name='No subtour')

    model.addConstr(P2[30] == 1, name='One hotel')

    for i in range(NA):
        for j in range(NA):
            model.addConstr((Method_Drive2[i, j] + Method_Walk2[i, j] + Method_Transit2[i, j]) == X2[i, j], name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk2[i, j]) <= 30 * 60, name='Walking limit')

    time_a2 = sum(Time_Attraction[i] * P2[i] for i in range(NA)) * 3600
    time_t2 = sum((Time_Drive[i][j] * Method_Drive2[i, j] + Time_Walk[i][j] * Method_Walk2[i, j] + Time_Transit[i][j] * Method_Transit2[i, j]) for i in range(NA) for j in range(NA))
    time2 = time_a2 + time_t2
    model.addConstr(time_t2 + time_a2 <= Time_Limit, name='Day 2:Time limit')
    fare_a2 = sum(Fare_Attraction[i] * (P2[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P2[i]) for i in range(30))
    fare_td2 = sum(Fare_Drive[i][j] * (Method_Drive2[i, j]) for i in range(NA) for j in range(NA))
    fare_2 = fare_a2 + fare_td2

    # Day3
    for i in range(N):
        model.addConstr(sum(X3[i, j] for j in range(N)) == P3[i], name='Day3-From Place' + str(i) + '=P[i]')
    for j in range(N):
        model.addConstr(sum(X3[i, j] for i in range(N)) == P3[j], name='Day3-To Place' + str(j) + '=P[i]')

    for i in range(N):
        model.addConstr(X3[i, i] == 0, name='Not itself')

    for i in range(N - 1):
        for j in range(N - 1):
            model.addConstr((U3[i] - U3[j] + N * X3[i, j]) <= (N - 1), name='No subtour')

    model.addConstr(P3[30] == 1, name='One hotel')
    model.addConstr(P3[31] == 1, name='From Airport')
    model.addConstr(P3[32] == 1, name='Dummy')
    model.addConstr(X3[32, 30] == 1, name='Dummy-Hotel')
    model.addConstr(X3[31, 32] == 1, name='Airport-Dummy')
    model.addConstr(Method_Walk3[32, 30] == 1, name='walk:Dummy-Hotel')
    model.addConstr(Method_Walk3[31, 32] == 1, name='walk:Airport-Dummy')

    for i in range(N):
        for j in range(N):
            model.addConstr((Method_Drive3[i, j] + Method_Walk3[i, j] + Method_Transit3[i, j]) == X3[i, j],name='One method')
            model.addConstr((Time_Walk[i][j] * Method_Walk3[i, j]) <= 30 * 60, name='Walking limit')

    time_a3 = sum(Time_Attraction[i] * P3[i] for i in range(N)) * 3600
    time_t3 = sum((Time_Drive[i][j] * Method_Drive3[i, j] + Time_Walk[i][j] * Method_Walk3[i, j] + Time_Transit[i][j] * Method_Transit3[i, j]) for i in range(N) for j in range(N))
    time3 = time_a3 + time_t3
    model.addConstr(time_t3 + time_a3 <= Time_Limit-2*3600, name='Day 3:Time limit')
    fare_a3 = sum(Fare_Attraction[i] * (P3[i]) for i in range(30))+sum(Fare_Attraction_c[i] * (P3[i]) for i in range(30))
    fare_td3 = sum(Fare_Drive[i][j] * (Method_Drive3[i, j]) for i in range(N) for j in range(N))
    fare_3 = fare_a3 + fare_td3

    # General
    for i in range(30):
        model.addConstr((P1[i] + P2[i] + P3[i]) <= 1)

    model.addConstr(fare_h == 2*Fare_Attraction[30],name='hotel fare')
    model.addConstr(fare_a == fare_a1+fare_a2+fare_a3, name='attraction fare')
    model.addConstr(fare_1 + fare_2 + fare_3 + fare_h + (noa+noc)*fare_tt <= Fare_Limit, name='Fare limit')

    model.addConstr((fare_1 + fare_2 + fare_3 + fare_h + (noa+noc)*fare_tt) == fare, name='total fare')
    model.addConstr((time1 + time2 + time3) / 3600 == time, name='total time')

    # If three days all includes transit method, then three-day ticket(20.5), otherwise, one-day ticket(10) for each day
    tt1 = sum(Method_Transit1[i, j] for i in range(N) for j in range(N))
    tt2 = sum(Method_Transit2[i, j] for i in range(NA) for j in range(NA))
    tt3 = sum(Method_Transit3[i, j] for i in range(N) for j in range(N))
    model.addConstr(tt1 >= 1 - M * (1 - y1))
    model.addConstr(tt1 <= 0 + M * (y1))
    model.addConstr(fare_tt1 >= 1 - M * (1 - y1))
    model.addConstr(fare_tt1 <= 1 + M * (1 - y1))
    model.addConstr(fare_tt1 >= -M * (y1))
    model.addConstr(fare_tt1 <= M * (y1))

    model.addConstr(tt2 >= 1 - M * (1 - y2))
    model.addConstr(tt2 <= 0 + M * (y2))
    model.addConstr(fare_tt2 >= 1 - M * (1 - y2))
    model.addConstr(fare_tt2 <= 1 + M * (1 - y2))
    model.addConstr(fare_tt2 >= -M * (y2))
    model.addConstr(fare_tt2 <= M * (y2))

    model.addConstr(tt3 >= 1 - M * (1 - y3))
    model.addConstr(tt3 <= 0 + M * (y3))
    model.addConstr(fare_tt3 >= 1 - M * (1 - y3))
    model.addConstr(fare_tt3 <= 1 + M * (1 - y3))
    model.addConstr(fare_tt3 >= -M * (y3))
    model.addConstr(fare_tt3 <= M * (y3))

    model.addConstr(fare_tt1 + fare_tt2 + fare_tt3 >= 3 - M * (1 - y4))
    model.addConstr(fare_tt1 + fare_tt2 + fare_tt3 <= 2 + M * (y4))
    model.addConstr(fare_tt >= 20.5 - M * (1 - y4))
    model.addConstr(fare_tt <= 20.5 + M * (1 - y4))
    model.addConstr(fare_tt >= 10 * (fare_tt1 + fare_tt2 + fare_tt3) - M * (y4))
    model.addConstr(fare_tt <= 10 * (fare_tt1 + fare_tt2 + fare_tt3) + M * (y4))

    model.addConstr(A1 == sum(P1[i] for i in range(30)))
    model.addConstr(A2 == sum(P2[i] for i in range(30)))
    model.addConstr(A3 == sum(P3[i] for i in range(30)))

    model.update()
    obj = sum(utility[i]*(P1[i] + P2[i] + P3[i]) for i in range(30))

    model.setObjective(obj, GRB.MAXIMIZE)
    #model.setParam(GRB.Param.PoolSearchMode, 2)
    #model.setParam(GRB.Param.PoolSolutions, 3)
    model.setParam('TimeLimit', 20)
    model.optimize()

    index_h = 30
    if Name[30] == 'Hotel Casa Bella':
        index_h = 30
    elif Name[30] == 'Hotel Monville':
        index_h = 31
    else:
        index_h = 32

    index_a = 33

    ind1 = [index_a]
    cycle1 = [Name[31]]
    method1 = []
    cat1 = []
    cat1.append('Airport')
    k1 = 31
    k2 = 30
    k3 = 30
    k_hotel = 30
    k_airport = 31
    flag = 0
    for i in range(32):
        if flag == 1:
            break
        for j in range(32):
            name1 = 'Day1' + Name[k1] + " to " + Name[j]
            if model.getVarByName(name1).x > 0.1:
                cycle1.append(Name[j])
                ind1.append(j)
                cat1.append(Category_Attraction[j])
                drive1 = 'Day 1-Drive: Attraction' + str(k1) + " to Attraction" + str(j)
                walk1 = 'Day 1-Walk: Attraction' + str(k1) + " to Attraction" + str(j)
                transit1 = 'Day 1-Transit: Attraction' + str(k1) + " to Attraction" + str(j)
                if model.getVarByName(drive1).x > 0.1:
                    method1.append("drive")
                elif model.getVarByName(walk1).x > 0.1:
                    method1.append("walk")
                else:
                    method1.append("transit")
                k1 = j
                if k1 == k_hotel:
                    flag = 1
                    break
    method1.append('end')
    cat1[-1] = "Hotel"
    ind1[-1] = index_h

    cycle2 = [Name[30]]
    ind2 = [index_h]
    method2 = []
    cat2 = []
    cat2.append('Hotel')
    flag = 0
    for i in range(31):
        if flag == 1:
            break
        for j in range(31):
            name2 = 'Day2' + Name[k2] + " to " + Name[j]
            print("test", name2)
            print(model.getVarByName(name2).x)
            if model.getVarByName(name2).x > 0.1:
                cycle2.append(Name[j])
                ind2.append(j)
                cat2.append(Category_Attraction[j])
                drive2 = 'Day 2-Drive: Attraction' + str(k2) + " to Attraction" + str(j)
                walk2 = 'Day 2-Walk: Attraction' + str(k2) + " to Attraction" + str(j)
                transit2 = 'Day 2-Transit: Attraction' + str(k2) + " to Attraction" + str(j)
                if model.getVarByName(drive2).x > 0.1:
                    method2.append("drive")
                elif model.getVarByName(walk2).x > 0.1:
                    method2.append("walk")
                else:
                    method2.append("transit")
                k2 = j
                if k2 == k_hotel:
                    flag = 1
                    break
    method2.append('end')
    cat2[-1] = "Hotel"
    ind2[-1] = index_h

    cycle3 = [Name[30]]
    ind3 = [index_h]
    method3 = []
    cat3 = []
    cat3.append('Hotel')
    flag = 0
    for i in range(32):
        if flag == 1:
            break
        for j in range(32):
            name3 = 'Day3' + Name[k3] + " to " + Name[j]
            if model.getVarByName(name3).x > 0.1:
                cycle3.append(Name[j])
                ind3.append(j)
                cat3.append(Category_Attraction[j])
                drive3 = 'Day 3-Drive: Attraction' + str(k3) + " to Attraction" + str(j)
                walk3 = 'Day 3-Walk: Attraction' + str(k3) + " to Attraction" + str(j)
                transit3 = 'Day 3-Transit: Attraction' + str(k3) + " to Attraction" + str(j)
                if model.getVarByName(drive3).x > 0.1:
                    method3.append("drive")
                elif model.getVarByName(walk3).x > 0.1:
                    method3.append("walk")
                else:
                    method3.append("transit")
                k3 = j
                if k3 == k_airport:
                    flag = 1
                    break
    method3.append('end')
    cat3[-1] = "Airport"
    ind3[-1] = index_a

    total_time = model.getVarByName('total time').x
    total_fare = model.getVarByName('total fare').x
    hotel_fare = model.getVarByName('hotel fare').x
    attraction_fare = model.getVarByName('attraction fare').x
    transit_threeday = 0
    transit_oneday = 0
    if (model.getVarByName('transit fare').x == 20.5):
        transit_threeday = 1
    else:
        transit_oneday = model.getVarByName('transit fare').x / 10
    trans_fare = total_fare - hotel_fare - attraction_fare
    max_utility = model.objVal
    cycle, method, cat, len, ind = [], [], [], [], []
    cycle.append(cycle1)
    cycle.append(cycle2)
    cycle.append(cycle3)
    method.append(method1)
    method.append(method2)
    method.append(method3)
    cat.append(cat1)
    cat.append(cat2)
    cat.append(cat3)
    len1 = int(model.getVarByName('Day1').x + 2)
    len2 = int(model.getVarByName('Day2').x + 2)
    len3 = int(model.getVarByName('Day3').x + 2)
    len.append(len1)
    len.append(len2)
    len.append(len3)
    ind.append(ind1)
    ind.append(ind2)
    ind.append(ind3)
    print("Optimal Soultion:")
    for v in model.getVars():
        if v.x > 0.1:
            print(v.varName, "=", round(v.x, 2))
    obj = int(model.getVarByName('Day1').x+model.getVarByName('Day2').x+model.getVarByName('Day3').x)
    print("matrix")
    print(cycle)
    print(method)
    print(cat)
    print(ind)
    print(len)

    return cycle, method, total_time, total_fare, hotel_fare, attraction_fare, trans_fare, obj, max_utility, cat, transit_oneday, transit_threeday,len,ind
