#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vobject
import sys
import io
import requests
import time
import sqlite3
import os
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning, InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


if len(sys.argv) != 2:
    raise ValueError("Please specify exactly one vCard or txt file.")

tag = re.compile(r"</?a\b[^>]*>")
nml = re.compile(r"^\"?(.+?)\"? +<([^>]+)>")

breachedaccount = "https://haveibeenpwned.com/api/v2/breachedaccount/"
breaches = "https://haveibeenpwned.com/api/v2/breaches"

def get_json(url):
    response = requests.get(url)
    if response.status_code == 404:
        return []
    txt = response.text.strip()
    if len(txt)==0:
        return []
    try:
        js = response.json()
        return js
    except ValueError:
        print txt
    return []

def get_info(mail):
    time.sleep(2)
    return get_json(breachedaccount+mail)


fname = sys.argv[1]
stream = io.open(fname,"r", encoding="utf-8")

if fname.endswith(".vcf"):
    vcards = vobject.readComponents(stream)
else:
    vcards = []
    for l in stream.readlines():
        l = l.strip()
        if len(l)>0 and "@" in l:
            m = nml.match(l)
            j = vobject.vCard()
            j.add('EMAIL')
            if m:
                j.add('FN')
                j.fn.value = m.group(1).strip()
                j.email.value = m.group(2).strip()
            else:
                j.email.value = l
            vcards.append(j)
            

path = os.path.dirname(os.path.abspath(__file__))

db_path = path + "/pwned.db"
con = sqlite3.connect(db_path)
with open(path + '/schema.sql', 'r') as schema:
    c = con.cursor()
    qry = schema.read()
    c.executescript(qry)
    con.commit()
    c.close()

for r in get_json(breaches):
    d = tag.sub("", r["Description"]).strip()
    info = ", ".join(r["DataClasses"])
    c = con.cursor()
    c.execute(
        "insert into ataques (id, titulo, dominio, descripcion, info) values (?, ?, ?, ?, ?)", (r["Name"], r["Title"], r["Domain"], d, info))
    c.close()
    con.commit()
con.close()
con = None

id_persona = 0

def insert_persona(nombre):
    global id_persona
    global con
    id_persona += 1
    if not con:
        con = sqlite3.connect(db_path)
    c = con.cursor()
    c.execute(
        "insert into personas (id, nombre) values (?, ?)", (id_persona, nombre))
    c.close()
    con.commit()


def insert_mail(mail):
    c = con.cursor()
    c.execute(
        "insert into correos (id, persona) values (?, ?)", (mail, id_persona))
    c.close()
    con.commit()

def insert_tocado(mail, ataque):
    d = tag.sub("", r["Description"]).strip()
    c = con.cursor()
    c.execute(
        "insert into tocados (correo, ataque) values (?, ?)", (mail, ataque))
    c.close()
    con.commit()

repetido = []

for vcard in vcards:
    insertado = False
    name = None
    mails = []
    emails = []
    ataques = []
    for p in vcard.getChildren():
        if p.name == "FN":
            name = p.value
        if p.name == "EMAIL":
            m = p.value.lower().strip()
            if len(m)>0 and m not in mails and m not in repetido:
                mails.append(m)
                repetido.append(m)
    if len(mails)>0:
        for m in mails:
            rs = get_info(m)
            if len(rs)>0:
                if not insertado:
                    insert_persona(name)
                    insertado = True
                insert_mail(m)
                emails.append(m)
                for r in rs:
                    a = r["Name"]
                    if a not in ataques:
                        ataques.append(a)
                    insert_tocado(m, a)
                    
    if con:
        if name:
            print name
        print ", ".join(emails)
        print ", ".join(ataques)
        print ""
        con.close()
        con = None

