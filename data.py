
import MySQLdb

mysql = MySQLdb.connect(host="localhost", user="testuser", password="test007", db="devices")
cur = mysql.cursor()
cur.execute("SELECT id, model, hostname, ip_address, user, added_date FROM nw_devices")

nw = cur.fetchall()

for dev in nw:
    print(dev[1])

mysql.close()
