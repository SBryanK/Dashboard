# Website E-commerce Dashboard

This website is created using a tool called streamlit in the Python programming language.
The dashboard is intended for PIKKAT Partners and the PIKKAT Operation Team to understand the performance of PIKKAT partner stores based on parameters in the form of customized CSVs

Users will be asked to authenticate users by entering the Username and Password they have previously created, this is intended to maintain the security of users who can enter the PIKKAT website

In registering new users, several requirements are given that need to be met so that the name, password and telephone number provided have a uniform format and have a fairly high level of security from hacking. then provides the option to load a CSV file with parameters that have been adjusted with parameters that can be changed as needed.

Connecting with the type of database service used
(The 3 most popular are POSTGRESQL, MYSql, MongoDB)
Provides the ability to return to the Data Input page if you want to repeat the data loading session or connect to a new database. In addition, the ability to set the desired time span to observe the performance of the store from time to time with the initial data benchmark with the final data provided is also provided. The date range can be adjusted when connected to the database

This website can filter the data to be displayed based on the level of options starting from province, district, sub-district, to store name. Each time you select a level, you will be given a display of 5 products with the highest sales based on your choice. And also 5 stores with the most sales performance. Every time you change the area option you want to monitor, the data will automatically change the area identification and adjust the number of stores available. The graph can be enlarged by pressing the enlarge button in the upper right corner of the graph

Upon selecting a store, the user will be taken to the main display of the PIKKAT Partner Store Dashboard. There is information about 1. Total store income 2. Average store income per day 3. Number of items sold 4. Graph of the 5 most sold items 5. Graph of the store's monthly income. An option button is also provided to return to the data input page. Then every time the date range is changed, the data will automatically change automatically. This provides the ability to iteratively analyze data periodically, the monthly revenue graph will also adjust to the amount of data specified.
