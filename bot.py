import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from sys import argv

import requests

from Penger.penger import Penger
import settings

import psutil


def get_current_time():
    return str(datetime.datetime.now())


def get_cpu_percent():
    return psutil.cpu_percent()


def get_virtual_memory_percent():
    return psutil.virtual_memory()[2]


def notify_about_new_ssh_connection():
    p = Penger(settings.token)
    user = argv[2]
    ip = argv[3]

    response = requests.get('https://ipinfo.io/' + ip + '/json')
    j = response.json()

    city = j['city']
    region = j['region']
    country = j['country']
    timezone = j['timezone']
    org = j['org']
    time = str(datetime.datetime.now())

    message = "User '" + user + "' just logged in." + '\n\n' + \
              time + '\n\n' + \
              "IP: " + ip + '\n\n' + \
              "City: " + city + '\n' + \
              "Region: " + region + '\n' + \
              "Country: " + country + '\n' + \
              "Timezone: " + timezone + '\n' + \
              "Org: " + org + '\n\n' + \
              "#sshConnection"

    p.sendMessage(settings.chat_id, message, disable_notification=True)


def write_to_base():
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()

    now = datetime.datetime.now()
    date = now.strftime("%d_%m_%Y")
    table_name = "data_" + date

    request = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' (' + \
              'time text,' + \
              'cpu_percent real,' + \
              'virtual_memory real' + \
              ')'
    cursor.execute(request)

    data = (get_current_time(), get_cpu_percent(), get_virtual_memory_percent())

    request = 'INSERT INTO ' + table_name + ' VALUES (?,?,?)'
    cursor.execute(request, data)
    conn.commit()

    print(data)

    conn.close()


def get_list_from_base_column(table_name, column_name):
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()

    request = 'SELECT ' + column_name + ' FROM ' + table_name
    cursor.execute(request)
    result = cursor.fetchall()
    conn.close()

    li = []

    for i in result:
        li.append(i[0])
    return li


def send_statistics_for_day(date=None):
    if date is None:
        now = datetime.datetime.now()
        date = now.strftime("%d_%m_%Y")
    table_name = "data_" + date

    time_list_str = get_list_from_base_column(table_name, 'time')
    time_list = []
    for x in time_list_str:
        time_list.append(datetime.datetime.fromisoformat(x))

    cpu_percent_list = get_list_from_base_column(table_name, 'cpu_percent')
    s = sum(cpu_percent_list) / len(cpu_percent_list)

    cpu_percent_mean = float('{:.2f}'.format(s))
    cpu_percent_max = max(cpu_percent_list)
    cpu_percent_min = min(cpu_percent_list)

    virtual_memory_list = get_list_from_base_column(table_name, 'virtual_memory')
    s = sum(virtual_memory_list) / len(virtual_memory_list)

    virtual_memory_mean = float('{:.2f}'.format(s))
    virtual_memory_max = max(virtual_memory_list)
    virtual_memory_min = min(virtual_memory_list)

    p = Penger(settings.token)

    message = "Report from " + date + "\n\n" + \
              "------------------CPU------------------" + "\n" + \
              "Mean: " + str(cpu_percent_mean) + "%" + "\n" + \
              "Max: " + str(cpu_percent_max) + "%" + "\n" + \
              "Min: " + str(cpu_percent_min) + "%" + "\n" + \
              "------------------MEM------------------" + "\n" + \
              "Mean: " + str(virtual_memory_mean) + "%" + "\n" + \
              "Max: " + str(virtual_memory_max) + "%" + "\n" + \
              "Min: " + str(virtual_memory_min) + "%" + "\n\n" + \
              "#report"

    create_graph(time_list, cpu_percent_list, virtual_memory_list, dpi=100)

    image = open('plot.png', 'rb')
    p.sendImage(settings.chat_id, image, message, disable_notification=True)
    image.close()


def create_graph(time_list, cpu_percent_list, virtual_memory_list, dpi=70, size_x=20, size_y=10):
    hour = mdates.HourLocator()
    time_fmt = mdates.DateFormatter('%H:%M')

    fig = plt.figure()
    fig.suptitle('Report from ' + str(datetime.datetime.today()))
    fig.set_size_inches(size_x, size_y)

    ax_1 = fig.add_subplot(2, 1, 1)
    ax_2 = fig.add_subplot(2, 1, 2)

    ax_1.set_title('CPU')
    ax_1.set_ylim([0, 100])
    ax_1.plot(time_list, cpu_percent_list)
    ax_1.grid(axis='y')
    ax_1.set_xlabel('time')
    ax_1.set_ylabel('%')
    ax_1.xaxis.set_major_locator(hour)
    ax_1.xaxis.set_major_formatter(time_fmt)

    ax_2.set_title('Virtual memory')
    ax_2.set_ylim([0, 100])
    ax_2.plot(time_list, virtual_memory_list)
    ax_2.grid(axis='y')
    ax_2.set_xlabel('time')
    ax_2.set_ylabel('%')
    ax_2.xaxis.set_major_locator(hour)
    ax_2.xaxis.set_major_formatter(time_fmt)

    plt.tight_layout()
    plt.savefig('plot.png', format='png', dpi=dpi)
    # plt.show()


if __name__ == '__main__':
    send_statistics_for_day()
