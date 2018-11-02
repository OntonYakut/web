#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyzabbix import ZabbixAPI
from app import app
import os
# import sys
import codecs
import time
import cx_Oracle
import json
import re

debug = False

# def get_items(Hostnameip):
#     return Hostnameip


def find_ci_in_sm(ci):
    try:
        os.environ['NLS_LANG'] = 'American_America.AL32UTF8'
        con = cx_Oracle.connect('SBT_OPIR2_REP/qdt4wh3ex9HhjJ@10.67.18.222:1523/SMREP')  # @UndefinedVariable
        cur = con.cursor()
        ci_query = u"""
            with t as
                (
                select distinct
                  p.logical_name as p_logical_name,
                  p.type as p_type,
                  nvl(p.subtype,'N\A') as p_subtype,
                  p.hpc_status as p_hpc_status,
                  (select listagg(i.ip_addresses,', ') within group (order by i.logical_name) 
                   from smprimary.DEVICE2A2 i where i.logical_name = p.logical_name) as p_ip_address
                 from
                  smprimary.cirelationsm1 r,
                  smprimary.device2m1 p
                 where p.logical_name=r.tps_related_cis
                  and p.type in ('server','infresource')
                 connect by NOCYCLE prior r.tps_related_cis=r.logical_name
                  start with r.tps_related_cis IN ('{}')
                )
                 select distinct
                  t.p_logical_name as ls_id,
                  t.p_ip_address as ls_ip_address
                 from t  where t.p_hpc_status != 'Удаленный'
                 and t.p_type ='server'
                 and t.p_subtype IN ('Виртуальный', 'LDOM', 'LPAR', 'Логический', 'nPAR')""".format(ci)

        cur.execute(ci_query)
        host_list = cur.fetchall()
        """ Ответ будет выглядеть так:
        [
            ('CI00755980', '10.116.118.220'), 
            ('CI00476468', '10.68.16.103'), 
            ('CI00755981', '10.116.118.221'), 
            ('CI00721261', '10.116.105.171'), 
        ]
        """
        # print(host_list)
        cur.close()
        con.close()

        # hosts_ci = [h[0] for h in host_list]
    except Exception as err:
        print('Ошибка соединения с репликой SM: ', err)
        host_list = []

        """ Возвращаем список:
        ['CI01088076', 'CI01088079', 'CI01088084', 'CI01088107', 'CI00867077']
        """

    return host_list


def get_host_result(filestring, config=app.config):
    if not filestring:
        return None
    ip_regexp = "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
    num_regexp = "{[0-9]+}"
    ci_regexp = "CI[0-9]{8}"
    item_regexp = "\[.*\]"
    
    is_ip = 0
    is_ci = 0
    string_info = str(filestring).splitlines()[0].split(' ')[0]
    if re.match(ip_regexp, string_info) is not None:
        is_ip = 1
    elif re.match(ci_regexp, string_info) is not None:
        is_ci = 1
        
    # The hostname at which the Zabbix web interface is available
    z = ZabbixAPI(config['ZABBIX_SERVER'])
    z.login(config['ZAPI_LOGIN'], config['ZAPI_PASSWORD'])

    # TODO Разобраться зачем name
    if is_ip:
        host_ids = z.host.get(output=['name', 'status'], filter={'ip': string_info})
    elif is_ci:
        # Делаем запрос в реплику SM
        # Вернет список: [('CI00755980', '10.116.118.220'), ('CI00755981', '10.116.118.221')]
        hosts_ci = find_ci_in_sm(string_info)

        ips = [h[1] for h in hosts_ci]

        interfaces = z.hostinterface.get(output=['ip'],
                                         filter={'ip': ips},
                                         selectHosts=['name', 'status'])

        host_ids = [h['hosts'][0] for h in interfaces]
    else:
        host_ids = z.host.get(output=['name', 'status'], search={'host': string_info})

    # Создаём список hostid
    ids = [h['hostid'] for h in host_ids if h['status'] == '0']

    host_all_info = z.host.get(output=['name'],
                               hostids=ids,
                               selectMacros='extend',
                               selectTriggers=['expression', 'description', 'comments', 'priority', 'status', 'tags'],
                               selectInterfaces=['ip'],
                               preservekeys=1)

    # Собираем все элементы данных
    item_dict = z.item.get(
        output=['hostid', 'name', 'key_', 'type', 'description', 'delay', 'history', 'trends', 'status'],
        webitems=1,
        hostids=ids)

    # Собираем все триггеры еще раз
    host_triggers = z.trigger.get(output=['expression', 'description', 'comments'],
                                  hostids=ids,
                                  expandExpression=1,
                                  expandComment=1,
                                  expandDescription=1,
                                  selectTags='extend',
                                  preservekeys=1)

    result = {}
    types = {
        '0': 'Zabbix агент',
        '1': 'SNMPv1 агент',
        '2': 'Zabbix траппер',
        '3': 'простая проверка',
        '4': 'SNMPv2 агент',
        '5': 'Zabbix внутренний',
        '6': 'SNMPv3 агент',
        '7': 'Zabbix агент (активный)',
        '8': 'Zabbix агрегированный',
        '9': 'веб элемент данных',
        '10': 'внешняя проверка',
        '11': 'монитор баз данных',
        '12': 'IPMI агент',
        '13': 'SSH агент',
        '14': 'TELNET агент',
        '15': 'вычисляемый',
        '16': 'JMX агент',
        '17': 'SNMP трап',
        '18': 'Зависимый элемент данных',
    }

    for h in host_all_info:
        # Меняем на развернутые выражения из второго запроса
        for t in host_all_info[h]['triggers']:
            t['description'] = host_triggers[t['triggerid']]['description']
            t['expression'] = host_triggers[t['triggerid']]['expression']
            t['comments'] = host_triggers[t['triggerid']]['comments']
            t['tags'] = host_triggers[t['triggerid']]['tags']
        host_all_info[h]['items'] = []
        result[h] = host_all_info[h]
        # Добавляем метрики в список метрик хоста
        for i in item_dict:
            if h == i['hostid']:
                result[h]['items'].append(i)

    for res in result:
        for item in result[res]['items']:
            if '$' in item['name']:
                # Составляем список всех параметров в метрике
                keysblock = re.findall(item_regexp, item['key_'])[0].replace('[', '').replace(']', '').split(',')
                # Для каждого параметра $1 $2 и т.д.
                for i in range(len(keysblock)):
                    # заменяем в имени item значение на параметр в метрике
                    item['name'] = item['name'].replace('${0}'.format(i+1), keysblock[i])
            # Рвскрываем {HOSTNAME}
            if '{HOST.IP}' in item['key_']:
                item['key_'] = item['key_'].replace('{HOST.IP}', result[res]['name'])
            if '{HOST.CONN}' in item['key_']:
                item['key_'] = item['key_'].replace('{HOST.CONN}', result[res]['name'])
            if '{HOST' in item['key_']:
                item['key_'] = item['key_'].replace('{HOST.NAME}', result[res]['name']) \
                    .replace('{HOST.HOST}', result[res]['name']) \
                    .replace('{HOSTNAME}', result[res]['name'])
            # TODO Возможно тут лучше подставлять IP-адрес
            if '{HOST.HOST}' in item['name']:
                item['name'] = item['name'].replace('{HOST.HOST}', result[res]['name'])
            # Раскрываем тип метрики
            item['type'] = types[item['type']]
        # Раскрываем {#HOSTNAME} в триггерах
        for tr in result[res]['triggers']:
            if '{#HOSTNAME}' in tr['description']:
                tr['description'] = tr['description'].replace('{#HOSTNAME}', result[res]['name'])
        result[res]['items'] = sorted(result[res]['items'], key=lambda x: x['status'])
        try:
            result[res]['triggers'] = sorted(sorted(sorted(result[res]['triggers'],
                                                           key=lambda x: x['priority'],
                                                           reverse=True),
                                                    key=lambda x: x['status']),
                                             key=lambda x: x['tags'], reverse=True)
        except Exception as err:
            result[res]['triggers'] = sorted(sorted(result[res]['triggers'],
                                                    key=lambda x: x['priority'],
                                                    reverse=True),
                                             key=lambda x: x['status'])
            print(res, err)
    return result
    

def get_templates(config=app.config):
    
    fileexists = True
    
    path_to_dep_txt = "./app/static/files/templates.txt"
    if [not os.path.isfile(path_to_dep_txt)] and [not os.access(path_to_dep_txt, os.R_OK)]:
        # create file {path_to_dep_txt}
        codecs.open(path_to_dep_txt, 'a', 'utf-8').close()
        # Marked file {path_to_dep_txt} as a Empty
        fileexists = False
    
    statbaf = os.stat(path_to_dep_txt)
    now = time.time()
    
    # Check that file is old, new or empty
    if [statbaf.st_mtime < now - 86400] or [not fileexists] or [statbaf.st_size == 0]:
    
        # The hostname at which the Zabbix web interface is available
        zapi = ZabbixAPI(config['ZABBIX_SERVER'])
        zapi.login(config['ZAPI_LOGIN'], config['ZAPI_PASSWORD'])

        templates = zapi.template.get(output="extend")
        
        template_depts = []

        def IsExists(TSList, txtString):
            found = False
            for TS in TSList:
                if txtString == TS:
                    found = True
                    break
            return found 
        
        for template in templates:
            if not IsExists(template_depts, template["name"]):
                template_depts.append(template["name"])

        with open(path_to_dep_txt, 'w') as f:
            for item in sorted(template_depts):
                f.write(u'{0}\n'.format(item))

        return sorted(template_depts)

    else:
        with open(path_to_dep_txt, 'r') as f:
            template_depts = f.read().splitlines()
    
    return sorted(template_depts)
    
    
def get_temp_result(resultdep, config=app.config):

    if debug:
        print(resultdep)
    zapi = ZabbixAPI(config['ZABBIX_SERVER'])
    zapi.login(config['ZAPI_LOGIN'], config['ZAPI_PASSWORD'])

    hostdeps = []
    templateid = ""

    templatename = zapi.template.get(output="extend")
    for template in templatename:
        if resultdep == template["name"]:
            templateid = template["templateid"]

    template_list = zapi.template.get(templateids=templateid,
                                      output="extend",
                                      selectItems="extend",
                                      selectDiscoveries="extend",
                                      selectTriggers="extend")
    if len(template_list) == 1:
        template = template_list[0]
        items_count = len(template['items'])
        triggers_count = len(template['triggers'])
        discoveries_count = len(template['discoveries'])
                     
        if debug:
            print("Items: " + str(items_count) + "\r\nTriggers: " + str(triggers_count) + "\r\nDiscoveries: " + str(discoveries_count) + "\r\n")
            print("№ п/п" + ";" + "Название метрики" + ";" + "Описание метрики" + ";" + "Ключ метрики" + ";" + "Интерал сбора (с.)" + ";" + "Время хранения сырых данных (дн.)" + ";" + "Время хранения аггрегированных часовых данных (дн.)")
        item_index = 0
        for item in template['items']:
            item_index += 1

            hostdeps.append({"number": str(item_index),
                             "name": item["name"],
                             "description": item["description"],
                             "key": item["key_"],
                             "delay": item["delay"],
                             "history": item["history"],
                             "trends": item["trends"]})

    hostdeps = json.dumps(hostdeps, ensure_ascii=False)
    hostdeps = json.loads(hostdeps)
    if debug:
        print(hostdeps)
    return hostdeps
