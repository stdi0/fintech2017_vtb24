# coding: utf8
import psycopg2
import re
import time
import urllib.request
import urllib.parse
import lxml.html as html
from robobrowser import RoboBrowser
from pytg import Telegram
from pytg.utils import coroutine

BOT_ID = 399714569
isolation_level = {}

def authorization(code, sender_id): 
    try:
        conn = psycopg2.connect("dbname='mylocaldb' user='postgres' host='localhost' password='joo0shaij'")
        cursor = conn.cursor()
    except:
        print('I am unable to connect to the database')
    access_token = ''
    data = urllib.parse.urlencode({'grant_type': 'authorization_code', 'code': code, 'redirect_uri': 'http://127.0.0.1:5000', 'client_id': '770296883857801006116', 'client_secret': 'f70c090fa2c049dea463342338653bde261ce5ddc1d0497c815b542f7ac83299'}).encode()
    request = urllib.request.Request('http://82.202.199.51/token', data=data)
    request.add_header('Host', '127.0.0.1:5000')
    try:
        resp = urllib.request.urlopen(request)
        html = resp.read()
        result = json.loads(html.decode('utf-8'))
        access_token = result['access_token']

        request = urllib.request.Request('http://82.202.199.51/accounts')
        request.add_header('Host', '127.0.0.1:5000')
        request.add_header('Authorization', 'Bearer ' + access_token)
        resp = urllib.request.urlopen(request)
        html = resp.read()
        result = json.loads(html.decode('utf-8'))
        try:
            cursor.execute("UPDATE Users SET is_registered = True WHERE id = " + "'" + str(sender_id) + "'" + ";") 
            cursor.execute("INSERT INTO Accounts (Acc, BIC, ClientID, INN, KPP, Name_Bank, Name_org) VALUES (%s, %s, %s, %s, %s, %s, %s)", (result[0]['Acc'], result[0]['BIC'], result[0]['ClientID'], result[0]['INN'], result[0]['KPP'], result[0]['Name_Bank'], result[0]['Name_org']))
            conn.commit()
        except Exception as e:
            print('Exception 1', e)

    except Exception as e:
        print('Exception: ', e)
        sender.msg(u'user#'+str(sender_id), u"Время действия токена закончено! Напишите свои логин и пароль, через запятую, в формате 'логин, пароль' для продолжения. Для работы с ограниченными функционалом напишите 'отмена'.")
        return True
    return True

def add_contact_and_send_message(msg, sender_id, s):
    global isolation_level
    try:
        conn = psycopg2.connect("dbname='mylocaldb' user='postgres' host='localhost' password='joo0shaij'")
        cursor = conn.cursor()
    except:
        print('I am unable to connect to the database')
    contact = sender.contact_add(msg['text'], u'Test', u'Test')
    try:
        contact = sender.contact_add(msg['text'],contact[0]['last_name'], contact[0]['first_name'])
    except:
        pass
    if not contact:
        sender.msg(u'user#'+str(sender_id), u"Пользователь с данным номером телефона на найден, попробуйте ввести другой номер.")
        return True
    partner_id, partner_last_name, partner_first_name, partner_is_registered   = contact[0]['peer_id'], contact[0]['last_name'], contact[0]['first_name'], False
    if 'phone' in contact[0]:
        partner_phone = contact[0]['phone']
    else:
        partner_phone = 'None'
                    
    isolation_level.update({partner_id: 2})
    #cursor.execute("INSERT INTO Users (id, phone, last_name, first_name, is_registered) VALUES (%s, %s, %s, %s, %s)", (partner_id, partner_phone, partner_last_name, partner_first_name, partner_is_registered))
    #conn.commit()
    sender.msg(u'user#'+str(sender_id), u"Сообщение партнеру отправлено!")
    sender.msg(contact[0]['print_name'], u"Здравствуйте, Вас привествует бот ВТБ24. " + s + u" отправил Вам платежное поручение. Являетесь ли Вы клиентом нашего банка? Ответьте 'да' или 'нет'.") 
    return True

@coroutine
def main_loop(receiver):  
    global isolation_level
    try:
        conn = psycopg2.connect("dbname='mylocaldb' user='postgres' host='localhost' password='joo0shaij'")
        cursor = conn.cursor()
    except:
        print('I am unable to connect to the database')
    
    try:
        while True: 
            msg = (yield)
            if msg['event'] != "message":
                continue
            sender_id = msg['sender']['peer_id']
            receiver_id = msg['receiver']['peer_id']
            if sender_id != BOT_ID and receiver_id == BOT_ID:
                if msg['event'] != "message":
                    continue 
                sender_id = msg['sender']['peer_id']
                receiver_id = msg['receiver']['peer_id']
                if sender_id != BOT_ID and receiver_id == BOT_ID: 
                    s = msg['sender']['first_name'] + ' ' + msg['sender']['last_name']
                    if sender_id in isolation_level:
                        if isolation_level[sender_id] == 0:
                            if msg['text'].lower() == 'партнер':
                                sender.msg(u'user#'+str(sender_id), u"Напишите номер телефона партнера.'")
                                isolation_level[sender_id] = 20
                                continue
                            else:
                                sender.msg(u'user#'+str(sender_id), u"Для отправки платежного поручения партнеру напишите 'партнер'")
                                continue
                        elif isolation_level[sender_id] == 20:
                            if msg['text'].lower() == 'назад':
                                isolation_level[sender_id] = 0
                                continue
                            else:
                                add_contact_and_send_message(msg, sender_id, s)
                                sender.msg(u'user#'+str(sender_id), u"Чтобы вернуться, напишите 'назад'.")
                        elif isolation_level[sender_id] == 10:
                            if msg['text'].lower() == 'назад':
                                isolation_level[sender_id] = -1
                                continue
                            else:
                                add_contact_and_send_message(msg, sender_id, s)
                                sender.msg(u'user#'+str(sender_id), u"Чтобы вернуться, напишите 'назад'.")
                        elif isolation_level[sender_id] == -1:
                            if msg['text'].lower() == 'логин':
                                sender.msg(u'user#'+str(sender_id), u"Пожалуйста, напишите свои логин и пароль, через запятую, в формате 'логин, пароль' для продолжения.")
                                isolation_level[sender_id] = 1
                            elif msg['text'].lower() == 'партнер':
                                sender.msg(u'user#'+str(sender_id), u"Напишите номер партнера. Для входа напишите 'логин'.")
                                isolation_level[sender_id] = 10
                                continue
                            else:
                                sender.msg(u'user#'+str(sender_id), u"Ограниченный функционал. Для входа напишите 'логин', для отправки платежного поручения партнеру напишите 'партнер'.")
                                continue
                        elif isolation_level[sender_id] == 1:
                            if msg['text'].lower() == 'отмена':
                                isolation_level[sender_id] = -1
                                continue
                            result = re.findall(r'(.*),\s*(.*)', msg['text'])
                            try:
                                login = result[0][0]
                                password = result[0][1]
                            except Exception as e:
                                sender.msg(u'user#'+str(sender_id), u"Логин или пароль неверный. Повторите попытку. Для работы с органиченными функционалом напишите 'отмена'.")
                                continue

                            page = html.parse('http://82.202.199.51/auth?response_type=code&scope=all&client_id=770296883857801006116&redirect_uri=http://127.0.0.1:5000&state=RANDOM_STATE').getroot()
                            form = page.forms[0]
                            meta = form.fields['meta']

                            data = urllib.parse.urlencode({'meta': meta, 'login': login, 'password': password}).encode()
                            request = urllib.request.Request('http://82.202.199.51/login', data=data)

                            resp = urllib.request.urlopen(request)

                            page = html.parse(resp).getroot()
                            form = page.forms[0]
                            meta = form.fields['meta']

                            #RoboBrowser
                            try:
                                browser = RoboBrowser(history=True)
                                browser.open('http://67.205.176.154:5000/sms')
                                form = browser.get_form(0)
                                form["meta"].value = meta
                                form["otp_token"].value = '123456'
                                browser.submit_form(form)
                                result = re.findall(r'code=(.*)\s', str(e))
                            except Exception as e:
                                print('EXCEPTION', e)
                                result = re.findall(r'code=(.*) \(', str(e))
                                if result:
                                    print('Code: ' + result[0])
                                    isolation_level[sender_id] = 0
                                    sender.msg(u'user#'+str(sender_id), u"Вы успешно авторизованы! Для отправки платежного поручения партнеру напишите 'партнер'.")
                                else:
                                    sender.msg(u'user#'+str(sender_id), u"Логин или пароль неверный. Повторите попытку. Для работы с органиченными функционалом напишите 'отмена'.")
                                    continue
                        elif isolation_level[sender_id] == 2:
                            if msg['text'].lower() == 'да':
                                sender.msg(u'user#'+str(sender_id), u"Пожалуйста, напишите свои логин и пароль, через запятую, в формате 'логин, пароль' для продолжения.")
                                isolation_level[sender_id] = 1
                            elif msg['text'].lower() == 'нет':
                                sender.msg(u'user#'+str(sender_id), u"Для Вас доступен ограниченный функционал.")
                                isolation_level[sender_id] = -1
                            else:
                                sender.msg(u'user#'+str(sender_id), u"Пожалуйста, сообщите, являетесь ли Вы клиентом нашего банка? Ответьте 'да' или 'нет'.")
                                continue
                    else:
                        sender.msg(u'user#'+str(sender_id), u"Пожалуйста, сообщите, являетесь ли вы клиентом нашего банка? Ответьте 'да' или 'нет'.")
                        isolation_level.update({sender_id: 2})
    except GeneratorExit:
        pass
    except KeyboardInterrupt:
        pass
    else:
        pass
    cursor.close()
    conn.close()



if __name__ == '__main__':
    while True:
        try:
            tg = Telegram(
                telegram="/root/tg/bin/telegram-cli",
                pubkey_file="/root/tg/tg-server.pub")
            receiver = tg.receiver
            sender = tg.sender
            receiver.start()
            receiver.message(main_loop(receiver))
            receiver.stop()
        except:
            continue
