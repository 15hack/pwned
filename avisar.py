# -*- encoding: utf-8 -*-

import yaml
import sqlite3
import sys
from smtplib import SMTP_SSL
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr
import getpass
import glob
import codecs
from smtplib import SMTPRecipientsRefused, SMTPDataError
import time

config = None
with file("smtp.yaml", 'r') as f:
	config = yaml.load(f)

con = sqlite3.connect("pwned.db")

def get_ataques(to):
	c = con.cursor()
	c.execute("select titulo from ataques where id in (select ataque from tocados where correo=?)", (to,))
	rs = c.fetchall()
	c.close()
	out = []
	for r in rs:
		out.append(r[0])
	return unicode(", ".join(out))

def get_atacados():
        c = con.cursor()
        c.execute("select id from correos where avisado = 0")
        rs = c.fetchall()
        c.close()
        out = []
        for r in rs:
                out.append(r[0])
        return out

def set_avisado(correo):
        c = con.cursor()
        c.execute("update correos set avisado = 1 where id = ?", (correo,))
        c.close()
	con.commit()

bodies=[]
for txt in sorted(glob.glob("body/*.txt")):
	with codecs.open(txt, "r", "utf-8") as f:
		bodies.append(f.read().strip())


def get_body(to):
        uto=unicode(to)
        ataques = get_ataques(to)
	body = u""
	for b in bodies:
		b = b % (uto, uto, ataques)
		body = body + b + u"\n\n\n"
	return body.strip()

charset = 'UTF-8'

password = getpass.getpass('Password: ')

smtp = SMTP_SSL(config['server'])
smtp.login(config['login'], password)


def send(to):
	body = get_body(to)

	msg = MIMEText(body, 'plain', charset)
	msg['From'] = config['from']
	msg['To'] = to
	msg['Subject'] = Header(u'Tu dirección de correo puede estar comprometida, por favor, revisla.', charset)

	smtp.sendmail(config['from'], to, msg.as_string())

atacados = get_atacados()

for a in atacados:
	print a,
	try:
		send(a)
		set_avisado(a)
		print "OK"
	except SMTPRecipientsRefused as e:
		print str(e)
	except SMTPDataError as e:
		if e.smtp_code == 450:
			atacados.append(a)
			print "SLEEP"
			time.sleep(300)
		else:
			print str(e)
		
smtp.quit()
