from sqlhelper import sqlhelper

sql = sqlhelper('host')



temp = sql.get_all_data(time_interval=10)
	
# temperature = [(ts, value) for ts, type, value in temp]

print [line for line in temp]