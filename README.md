# Montreal-Itinerary-Project
Find and visualize one-day and three-day optimal itineraries for tourists visiting Montreal, using gurobi, flask, etc.

Hello, this is part of a course project, which aims to find the optimal itineraries for up to 5 tourists visting Montreal. I scrapped cost of Uberx and Uberxl, built the gurobi models and a website to visualize the solutions, so here are the codes.
1. uber_cost.py is the file used to scrap the costs, it was supposed to collect the costs automatically, but Uber will prevent searching after about 30-40 times fof search, so one needs to keep an eye on it.
2. time matrix is collected by me teammate using Google API, the py file is not included here.
3. gurobi_model.py contains 4 gurobi models used to solve the optimization problems. There are some differences between one-day and three-day trip's assumptions. For the two utility models, they just change the objective functions to maximize total utility instead of number of attractions.
4. prepare.py reads the local data and calculates the utility with parameters from the website
5. html files are all created based on a free template, I am not familiar with html and javascript, so I used a quite backward method to visualize the optimal itinerary, I will try to improve it later.
