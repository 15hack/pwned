# -*- encoding: utf-8 -*-

import yaml
import sqlite3
import sys
from smtplib import SMTP_SSL
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr
import getpass


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
        c.execute("select distinct correo from tocados")
        rs = c.fetchall()
        c.close()
        out = []
        for r in rs:
                out.append(r[0])
        return out

txt=u'''Hola

Recibes este correo porque tu dirección de email %s aparece en la base de datos https://haveibeenpwned.com/
Esta web es un servicio para comprobar si una dirección de correo ha sido comprometida en algún ataque informático.

Por ejemplo, si te has registrado en la red social X con tu correo %s y esa red social ha sufrido un ataque en el que se ha filtrado los usuarios de esa web, tu cuenta esta comprometida no solo en ese sitio web si no en todos aquellos en los que te hayas registrado con el mismo correo y la misma contraseña.

En concreto, tu correo aparece en los siguientes ataques: %s.

Por ello, como eres usuario con esta dirección de correo en alguno de los servicios de 15hack, te pedimos que revises en https://haveibeenpwned.com/ la gravedad de tu exposición y si lo estimas necesario cambies la contraseña tanto en los servicios que aparezcan en haveibeenpwned.com como en los que estés usando en 15hack.

Muchas gracias, y esperamos que este aviso te sea útil.'''

header_charset = 'UTF-8'
body_charset = 'UTF-8'

password = getpass.getpass('Password: ')

smtp = SMTP_SSL(config['server'])
smtp.login(config['login'], password)


def send(to):
	uto=unicode(to)
	body = txt % (uto, uto, get_ataques(to))

	msg = MIMEText(body, 'plain', body_charset)
	msg['From'] = config['from']
	msg['To'] = to
	msg['Subject'] = Header(u'Tu dirección de correo puede estar comprometida, por favor, revisla.', header_charset)

	smtp.sendmail(config['from'], to, msg.as_string())

atacados = get_atacados()

for a in atacados:
	send(a)
	sys.exit(0)

smtp.quit()
