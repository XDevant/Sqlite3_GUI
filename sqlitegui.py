#!/usr/bin/env python
# coding: utf-8

# In[243]:


from tkinter import *
import sqlite3 as lite
import os
import csv
import pandas as pd

dip = ''
dep = ''
cip = dip
cep = dep
name = 'test.csv'

def text_inp():
    try:
        db = cdb_entry.get()
        con=lite.connect(db)
        con.row_factory = lite.Row
        with con:
            cur=con.cursor()
            try:
                cur.execute(sql_entry.get())
            except lite.OperationalError:
                listquerry.insert(END, 'OperationalError : table/selection may not exist ')
            rows=cur.fetchall()
            try:
                headers = list(rows[0].keys())
                listquerry.insert(END, headers)
            except IndexError:
                listquerry.insert(END, 'IndexError : Nothing was returned ')
        for row in rows:
            drow = list(row)
            listquerry.insert(END, drow)
    except TclError:
        listquerry.insert(END, 'TclError: check current DB')

def clear_listquerry():
    listquerry.delete(0,'end')

def display_csv():
    path = ccsvpath_entry.get()
    listcsv.delete(0, 'end')
    try:
        with os.scandir(path) as it:
            for entry in it:
                if '.csv' in entry.name and entry.is_file():
                    listcsv.insert(END,entry.name)
    except FileNotFoundError:
        with os.scandir() as it:
            for entry in it:
                if '.csv' in entry.name and entry.is_file():
                    listcsv.insert(END,entry.name)

def display_db():
    path = cdbpath_entry.get()
    listdb.delete(0, 'end')
    try:
        with os.scandir(path) as it:
            for entry in it:
                if '.sqlite' in entry.name and entry.is_file():
                    listdb.insert(END,entry.name)
    except FileNotFoundError:
        with os.scandir() as it:
            for entry in it:
                if '.sqlite' in entry.name and entry.is_file():
                    listdb.insert(END,entry.name)


def dbselect():
    try:
        test = cdbpath_entry.get()+listdb.selection_get()
        cdb_entry.delete(0, 'end')
        cdb_entry.insert(END,test)
        db = cdb_entry.get()
    except TclError:
        try:
            db = cdb_entry.get()
        except TclError:
            db = ':memory:'
    display_table(db)        

def display_table(db):
    con=lite.connect(db)        
    if db == ':memory:':
        with con:
            cur=con.cursor()
            cur.execute("SELECT name FROM sqlite_temp_master WHERE type='table' ORDER BY name;")
            rows=cur.fetchall()
    else:
        with con:
            cur=con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            rows=cur.fetchall()
    if len(rows) == 0:
        listquerry.insert(END,'--Create Table, Import csv or Load DB--')
    else:
        listtable.delete(0, 'end')
        for row in rows:
            listtable.insert(END,row)
    listdb.selection_clear(0,'end')
    
def load_csv():
    try:
        db = cdb_entry.get()
    except TclError:
        db = ':memory:'
    try:
        file = listcsv.selection_get()
        pathfile = cdbpath_entry.get()+file
        csv1 = pd.read_csv(pathfile)
        name = file[:-4]
        con=lite.connect(db)
        with con:
            try:
                csv1.to_sql(name=name, con=con, if_exists='fail')
            except ValueError:
                listquerry.insert(END,'--Table already in current DB--')
    except TclError:
        listquerry.insert(END,'--Select a .csv to load--')
    display_table(db)


def export_csv():
    try:
        db = cdb_entry.get()
    except TclError:
        db = ':memory:'
    con=lite.connect(db)
    con.row_factory = lite.Row
    with con:
        cur=con.cursor()
        cur.execute(sql_entry.get())
        rows=cur.fetchall()
    name = cdbpath_entry.get()+newcsv_entry.get()+'.csv'
    headers = list(rows[0].keys())
    data = [list(row) for row in rows]
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(name, index=False)
    display_csv()

def onselect(event, listbox):
    w = event.widget
    try:
        idx = int(w.curselection()[0])
    except IndexError:
        return
    if listbox is listdb:
        dbselect()
    if listbox is listdb:
        return
    
def dbpath(event):
    cdbpath_entry.insert(END,dbpath_entry.get())
    display_db()
def csvpath(event):
    ccsvpath_entry.insert(END,dbpath_entry.get())
    display_csv()   


mw = Tk()
mw.title("mini-sql-browser")

dbpath_lb=Label(mw,text='Db Path:',bg='lightCyan2')
db_lb=Label(mw,text='Databases:',bg='lightCyan2')
csv_lb=Label(mw,text='CSV Files:',bg='lightCyan2')
table_lb=Label(mw,text='Tables:',bg='lightCyan2')
dbpath_entry=Entry(mw,width=30)
dbpath_entry.bind('<Return>', dbpath)
csvpath_lb=Label(mw,text='.csv Path:',bg='lightCyan2')
csvpath_entry=Entry(mw,width=30)
csvpath_entry.bind('<Return>', csvpath)
sql_lb=Label(mw,text='SQlite query:',bg='lightCyan2')
sql_entry=Entry(mw,width=30)
newcsv_lb=Label(mw,text='name next .csv to be created',bg='lightCyan2')
newcsv_entry=Entry(mw,width=30)
newcsv_entry.insert(END,'new_csv')
cdb_entry=Entry(mw,width=30)
cdbpath_entry=Entry(mw,width=30)
ccsvpath_entry=Entry(mw,width=30)

listdb=Listbox(mw,height=8,width=30, selectmode='single')
listdb.bind('<<ListboxSelect>>', lambda e: onselect(e, listdb))
listcsv=Listbox(mw,height=8,width=30)
listcsv.bind('<<ListboxSelect>>', lambda e: onselect(e, listcsv))
listtable=Listbox(mw,height=8,width=30)
listtable.bind('<<ListboxSelect>>', lambda e: onselect(e, listtable))

listquerry=Listbox(mw,height=9,width=100,bg='burlywood1')
scroll_v=Scrollbar(mw,orient=VERTICAL,command=listquerry.yview)
listquerry['yscrollcommand']=scroll_v.set

sendbt= Button(mw, text='Push to send',bg='khaki1',command=text_inp)
clear_querry=Button(mw,text='Clear Listbox',bg='khaki2',command=clear_listquerry)
loadcsvbt = Button(mw,text='Load csv into table(s)',bg='khaki2',command=load_csv)
exportcsvbt = Button(mw,text='Export querry as csv',bg='khaki2',command=export_csv)

space_0=Label(mw,text='',bg='lightCyan2')
space_2=Label(mw,text='>',bg='lightCyan2')
space_4=Label(mw,text='',bg='lightCyan2')
space_6=Label(mw,text='<',bg='lightCyan2')
space_8=Label(mw,text='<',bg='lightCyan2')

display_db()
display_csv()

dbpath_lb.grid(row=0,column=1,sticky=(W,E))
dbpath_entry.grid(row=1,column=1,sticky=(W,E))
csvpath_lb.grid(row=2,column=1,sticky=(W,E))
csvpath_entry.grid(row=3,column=1,sticky=(W,E))
newcsv_lb.grid(row=4,column=1,sticky=(W,E))
newcsv_entry.grid(row=5,column=1,sticky=(W,E))
sql_lb.grid(row=6,column=1,sticky=(W,E))
sql_entry.grid(row=7,column=1,sticky=(W,E))
sendbt.grid(row=13,column=1)

db_lb.grid(row=0,column=3,sticky=(W,E))
csv_lb.grid(row=0,column=5,sticky=(W,E))
table_lb.grid(row=0,column=7,sticky=(W,E))
listdb.grid(row=1,column=3,rowspan=7)
listcsv.grid(row=1,column=5,rowspan=7)
listtable.grid(row=1,column=7,rowspan=7)

space_0.grid(row=0,column=0,rowspan=16,sticky=(N,S))
space_2.grid(row=0,column=2,rowspan=16,sticky=(N,S))
space_4.grid(row=0,column=4,rowspan=8,sticky=(N,S))
space_6.grid(row=0,column=6,rowspan=8,sticky=(N,S))
space_8.grid(row=0,column=6,rowspan=8,sticky=(N,S))

listquerry.grid(row=8,column=3,rowspan=8, columnspan=5)
listquerry.insert(END,"—Here comes the query-result:—")
scroll_v.grid(row=8,column=8,rowspan=8,sticky=(N,S))

clear_querry.grid(row=16,column=3)
loadcsvbt.grid(row=16,column=5)
exportcsvbt.grid(row=16,column=7)

mw.mainloop()


# In[ ]:





# In[ ]:





# In[ ]:




