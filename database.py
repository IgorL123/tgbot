import psycopg2


def get_channels(amount_top=150, amount_bottom=30):
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="abcd0987",
        host="127.0.0.1",
        port="5433"
    )
    cur = con.cursor()
    from datetime import datetime
    now = datetime.today().day
    cur.execute("SELECT date,num_bottom from LASTDATE1")
    rows = cur.fetchall()
    num_of_bottom = 0 if rows[0][1] == (630 - amount_top) // amount_bottom else rows[0][1]
    cur.execute("UPDATE LASTDATE1 SET date = %s, num_bottom = %s WHERE date = %s",
                (now, num_of_bottom + 1, rows[0][0]))
    cur.execute("SELECT id,name,count_subs from TGCHANNELS2")
    rows = cur.fetchall()
    con.commit()
    con.close()
    rows = sorted(rows, key=lambda subs: subs[2], reverse=True)
    ch_top = []
    ch_bottom = []

    for i in range(len(rows)):
        border1 = amount_top + amount_bottom * num_of_bottom
        border2 = amount_top + amount_bottom * (num_of_bottom + 1)
        if border2 > len(rows) - 1:
            border2 = len(rows) - 1
        if border1 <= i < border2:
            ch_bottom.append(rows[i][1])
        if i < amount_top:
            ch_top.append(rows[i][1])

    return ch_top + ch_bottom


def get_user_choice(sender):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    sender = str(sender)
    cur.execute('SELECT * FROM USERCHOICE2 WHERE USERID = %s', (sender, ))
    u_choice = {}
    for row in cur:
        if row[0] == sender:
            u_choice['politics'] = row[1]
            u_choice['tech'] = row[2]
            u_choice['business'] = row[3]
            u_choice['entertainment'] = row[4]
            u_choice['sport'] = row[5]
    con.commit()
    con.close()
    return u_choice


def is_user_new(sender):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT USERID from USERCHOICE2 WHERE USERID = %s', (str(sender),))
    rows = cur.fetchall()
    con.commit()
    con.close()
    return len(rows) > 0


def create_new_user(sender, u_choice):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    insert = "INSERT INTO USERCHOICE2 (USERID,POLITICS,TECH,BUSINESS,ENTERTAINMENT,SPORT) VALUES (%s,%s,%s,%s,%s,%s)"
    cur.execute(insert, (str(sender), u_choice['politics'], u_choice['tech'], u_choice['business'],
                         u_choice['entertainment'], u_choice['sport']))
    con.commit()
    con.close()


def truncate_tempdata():
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('TRUNCATE TEMPDATA')
    con.commit()
    con.close()


def truncate_all_data():
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('TRUNCATE DATA')
    con.commit()
    con.close()


def delete_user(id):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('DELETE FROM USERCHOICE2 WHERE USERID = %s', (str(id),))
    con.commit()
    con.close()


def insert_to_database():
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT * from TEMPDATA")
    rows = cur.fetchall()
    insert = "INSERT INTO DATA (POSTID,ID,CHANNEL,POST) VALUES (%s,%s,%s,%s)"
    for row in rows:
        cur.execute(insert, (row[0], row[1], row[2], row[3]))
    con.commit()
    con.close()
