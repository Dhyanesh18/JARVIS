from vosk import Model, KaldiRecognizer
import pyaudio
import json
import pyttsx3
import webbrowser
import urllib.parse
from googleapiclient.discovery import build
import sys 
import math 
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QGraphicsOpacityEffect, QFrame, QDialog, QVBoxLayout, QProgressBar, QLineEdit, QComboBox, QMessageBox, QWidget, QScrollArea
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient, QIcon , QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QRect
import threading
import psutil
import speedtest
import time
from datetime import datetime
import GPUtil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import joblib
from pyqtgraph import PlotWidget
import numpy as np
import requests
import random
import os
import shutil



class JarvisUI(QMainWindow):     
    def __init__(self):         
        super().__init__()         
        self.setWindowTitle("J.A.R.V.I.S")         
        self.setGeometry(100, 100, 500, 300)  
        self.setFixedSize(500,300)
        self.setWindowFlags(Qt.Window)  
        self.setWindowIcon(QIcon('artifacts/logo.png'))  
        self.is_speaking = False 
        self.animation_timer = QTimer(self)  
        self.animation_timer.timeout.connect(self.update_animation)         
        self.animation_timer.start(16)                  
        self.animation_time = 0  
        self.listening = True
        self.awake = False
        self.last_command_time = time.time()
        self.lock = threading.Lock()
        self.first_time = True

        self.assistant = None

        # Todo button
        self.todo_button = QPushButton(self)  
        self.todo_button.setIcon(QIcon('artifacts/todo.png'))  
        self.todo_button.setIconSize(QSize(27, 27))  
        self.todo_button.move(170, 264)
        self.todo_button.setStyleSheet("""
        background-color: transparent;
        border: none;
        border-radius: 50%;
        """)
        original_icon2 = QIcon('artifacts/todo.png')
        pixmap2 = original_icon2.pixmap(QSize(30, 30))
        opacity_pixmap2 = QPixmap(pixmap2.size())
        opacity_pixmap2.fill(Qt.transparent)
        painter2 = QPainter(opacity_pixmap2)
        painter2.setOpacity(0.6) 
        painter2.drawPixmap(0, 0, pixmap2)
        painter2.end()
        self.todo_button.setIcon(QIcon(opacity_pixmap2))
        self.todo_button.clicked.connect(self.open_todo_menu)

        self.todo_button = QPushButton(self)  
        self.todo_button.setIcon(QIcon('artifacts/todo.png'))  
        self.todo_button.setIconSize(QSize(30, 30))  
        self.todo_button.move(235, 264)
        self.todo_button.setStyleSheet("""
        background-color: transparent;
        border: none;
        border-radius: 50%;
        """)

        # Folder or file search button
        original_icon2 = QIcon('artifacts/folder.png')
        pixmap2 = original_icon2.pixmap(QSize(27, 27))
        opacity_pixmap2 = QPixmap(pixmap2.size())
        opacity_pixmap2.fill(Qt.transparent)
        painter2 = QPainter(opacity_pixmap2)
        painter2.setOpacity(0.5) 
        painter2.drawPixmap(0, 0, pixmap2)
        painter2.end()
        self.todo_button.setIcon(QIcon(opacity_pixmap2))
        self.todo_button.clicked.connect(self.open_file_folder_search)


        # Mic Button
        self.mic_button = QPushButton(self)  
        self.mic_button.setIcon(QIcon('artifacts/mic.png'))  
        self.mic_button.setIconSize(QSize(30, 30))  
        self.mic_button.setStyleSheet("""
        background-color: transparent;
        border: none;
        border-radius: 50%;
        """)
        original_icon = QIcon('artifacts/mic.png')
        pixmap = original_icon.pixmap(QSize(30, 30))
        opacity_pixmap = QPixmap(pixmap.size())
        opacity_pixmap.fill(Qt.transparent)
        painter = QPainter(opacity_pixmap)
        painter.setOpacity(0.7) 
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        self.mic_button.setIcon(QIcon(opacity_pixmap))
        self.mic_button.setToolTip('Click to Toggle Speaking State')

        self.mic_button.clicked.connect(self.listen_again)

        self.download_speed = None
        self.upload_speed = None
        self.speed_test_time = 0
        self.start_periodic_speed_test()

        self.weather_api = '83503428086170fd0221e87102ee5e2a'
        location = self.get_location()
        self.city = location['city']
        self.latitude = location['latitude']
        self.longitude = location['longitude']
        self.weather = None
        self.temperature = None
        self.country = None

        self.start_periodic_weather_report()

        # Center jarvis logo in the main window
        self.label = QLabel(self)
        pixmap = QPixmap("artifacts/jarvis1.png")
        scaled_pixmap = pixmap.scaled(
            170, 170,  # max width and height
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 11, 500, 268)

        self.speech_text = None

        # Stark industries logo
        self.label2 = QLabel(self)
        pixmap2 = QPixmap("artifacts/stark.png")
        scaled_pixmap2 = pixmap2.scaled(
            200,150,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.label2.setPixmap(scaled_pixmap2)
        self.label2.setGeometry(3,267,150,20)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.60) 
        self.label2.setGraphicsEffect(opacity_effect)
        
        # Audio Visualization for input sound
        self.plot_widget = PlotWidget(self)
        self.plot_widget.setBackground(None)
        self.plot_widget.setStyleSheet("background: transparent; border: none;")
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.hideAxis('left')
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setInteractive(False)
        self.plot_widget.setYRange(-3000, 3000, padding=0)
        self.plot_widget.setGeometry(380,30,100,30)
        self.audio_curve = self.plot_widget.plot(pen=(0,200,255))
        self.audio_data = np.zeros(1024, dtype=np.int16)

        # Input box for commands, when audio input isnt viable
        layout = QVBoxLayout(self)
        font = QFont('Orbitron',2)
        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText(" Command")
        self.command_input.setStyleSheet(self.get_transparent_style())
        self.command_input.setFont(font)
        self.command_input.setGeometry(390,187,75,15)
        layout.addWidget(self.command_input)

        button_style = """
            background-color: rgb(0, 180, 210);
            color: rgb(0, 0, 78);
            font-size: 11px;
            font-weight: bold;
            border: 1px solid rgb(0, 180, 210);
        """

        # Enter button for processing the command given in the above input box
        search_button = QPushButton("▶", self)
        search_button.setStyleSheet(button_style)
        search_button.clicked.connect(self.get_command)
        search_button.setFont(font)
        search_button.setGeometry(465, 187, 15, 15)
        layout.addWidget(search_button)

        # Box around the audio viualization plot, for aesthetics
        transparent_box = QFrame(self)
        transparent_box.setGeometry(388,30,83,30)
        transparent_box.setStyleSheet("""
            QFrame{
                background-color: transparent;
                border: 1px solid rgb(0,120,140);
                border-radius: 0px;
            }
        """)

        # Disk usage for C drive
        self.disk_label = QLabel(self)
        self.disk_label.setText("C:")
        self.disk_label.setGeometry(405, 60, 80, 20) 
        self.disk_progress_bar = QProgressBar(self)
        self.disk_progress_bar.setGeometry(400, 80, 80, 12) 
        self.disk_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgb(0, 120, 140);
                border-radius: 2px;
                background: transparent;
                text-align: center;
                font-family: Orbitron;
                font-bold: true;
                font-size: 10px;
                color: rgb(254, 254, 254);
            }
            QProgressBar::chunk {
                background-color: rgb(0, 155, 197);
                border-radius: 2px;
            }
        """)
        self.update_disk_usage()
        # Add a timer to periodically update disk usage stats
        self.disk_usage_timer = QTimer(self)
        self.disk_usage_timer.timeout.connect(self.update_disk_usage)
        self.disk_usage_timer.start(3600000)


        # Disk usage for D drive
        self.disk_label_d = QLabel(self)
        self.disk_label_d.setText("D:")  
        self.disk_label_d.setGeometry(400, 95, 80, 20)  
        self.disk_progress_bar_d = QProgressBar(self)
        self.disk_progress_bar_d.setGeometry(400, 115, 80, 12)  
        self.disk_progress_bar_d.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgb(0, 120, 140);
                border-radius: 2px;
                background: transparent;
                text-align: center;
                font-family: Orbitron;
                font-bold: true;
                font-size: 10px;
                color: rgb(254, 254, 254);
            }
            QProgressBar::chunk {
                background-color: rgb(0, 155, 197);
                border-radius: 2px;
            }
        """)
        self.update_disk_usage_d()
        self.disk_usage_timer_d = QTimer(self)
        self.disk_usage_timer_d.timeout.connect(self.update_disk_usage_d)
        self.disk_usage_timer_d.start(3600000)
    
    # Initialize the assistant object for using the assistant's methods
    def get_assistant(self, assistant):
        self.assistant = assistant

    def get_command(self):
        """Process the command given in the input box"""
        command = self.command_input.text().strip()
        self.command_input.clear()
        self.assistant.process_text_command(command)

    def get_transparent_style(self):
        """Style for transparent input fields and the task list"""
        return """
            background: transparent;
            color: rgb(0, 180, 210);
            font-size: 9px;
            font-weight: bold;
            border: 1px solid rgb(0, 180, 210);
        """        

    def open_todo_menu(self):
        """Initialize and open the To-Do menu class"""
        self.todo_window = TodoUI()
        self.todo_window.exec_()

    def open_file_folder_search(self):
        """Initialize and open the File/Folder search menu class"""
        self.file_folder_search_window = FileFolderSearchUI()
        self.file_folder_search_window.exec_()

    def update_disk_usage_d(self):
        """Function to update the disk usage for D drive constantly"""
        try:
            total, used, free = shutil.disk_usage("D:/") 
            percent_used = int((used / total) * 100)  
            self.disk_progress_bar_d.setValue(percent_used)
            font = QFont('Orbitron', 2)
            font.setBold(True)
            self.disk_label_d.setFont(font)
            self.disk_label_d.setStyleSheet("""
                color: rgb(0,160,200);
                font-size: 10px;
            """)
            self.disk_label_d.setText(
                f"D: {used // (1024**3)}/{total // (1024**3)} GB"
            )
        except Exception as e:
            print(f"Error updating disk usage: {e}")

    def update_disk_usage(self):
        """Function to update the disk usage for C drive constantly"""
        try:
            total, used, free = shutil.disk_usage("C:/") 
            percent_used = int((used / total) * 100)  

            # Update the progress bar and label
            self.disk_progress_bar.setValue(percent_used)
            font = QFont('Orbitron', 2)
            font.setBold(True)
            self.disk_label.setFont(font)
            self.disk_label.setStyleSheet("""
                color: rgb(0,160,200);
                font-size: 10px;
            """)
            self.disk_label.setText(
                f"C: {used // (1024**3)}/{total // (1024**3)} GB"
            )
        except Exception as e:
            print(f"Error updating disk usage: {e}")

    def update_audio_visualization(self, audio_samples):
        """Update the audio visualization plot with new audio samples"""
        if len(audio_samples) > len(self.audio_data):
            audio_samples = audio_samples[:len(self.audio_data)]  # Truncate to match size
        elif len(audio_samples) < len(self.audio_data):
            padding = np.zeros(len(self.audio_data) - len(audio_samples), dtype=np.int16)
            audio_samples = np.concatenate((padding, audio_samples))  # Pad to match size

        # Shift existing data and append new audio_samples
        self.audio_data = np.roll(self.audio_data, -len(audio_samples))
        self.audio_data[-len(audio_samples):] = audio_samples

        # Update the plot with the new data
        self.audio_curve.setData(self.audio_data)

    def get_location(self):
        """Get the location of the user using the IP address"""
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            if response.status_code == 200 and data['status'] == 'success':
                city = data['city']
                country = data['country']
                latitude = data['lat']
                longitude = data['lon']
                return {
                    "city": city,
                    "country": country,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            else:
                print("Failed to get location")
                return None
        except Exception as e:
            print(f"Error fetching location")
            return None
        
    def start_periodic_weather_report(self):
        """Start a thread to periodically fetch weather data"""
        def weather_report():
            while True:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.weather_api}&units=metric"
                response = requests.get(url)
                data = response.json()

                if response.status_code == 200:
                    self.temperature = data['main']['temp']
                    self.weather = data['weather'][0]['description'].capitalize()
                    self.country = data['sys']['country']
                    time.sleep(1200)
        weather_thread = threading.Thread(target=weather_report, daemon=True)
        weather_thread.start()

    def start_periodic_speed_test(self):
        """Start a thread to periodically run network speed tests"""
        def run_speed_test():
            while True:
                try:
                    st = speedtest.Speedtest()
                    self.download_speed = st.download()/1_000_000
                    self.upload_speed = st.upload()/1_000_000
                    self.speed_test_time = time.time()
                except Exception:
                    self.download_speed = None
                    self.upload_speed = None
                
                time.sleep(300)
        speed_thread = threading.Thread(target=run_speed_test, daemon = True)
        speed_thread.start()

    def draw_system_vitals(self, painter, x, y, width):
        """Draw system vitals on the screen"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        gpus = GPUtil.getGPUs()
        i=0;

        for gpu in gpus:
            if i!=1:
                gputotal = gpu.memoryTotal
                gpuused = gpu.memoryUsed
                gputemp = gpu.temperature

        gpu_usage = (gpuused/gputotal)*100
        gpu_usage = round(gpu_usage,2)

        font = QFont('Orbitron',6)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0,180,200))
        painter.drawText(18, 10, 100, 20, Qt.AlignCenter, "SYSTEM VITALS")
        painter.drawText(375,10,110,20, Qt.AlignCenter, "SIGNAL ANALYZER")

        font_size = 7
        font = QFont('Orbitron', font_size)
        font.setBold(True)
        painter.setFont(font)

        def get_color(usage):
            if usage > 80:
                return QColor(255, 0, 0)  # Red for high usage
            elif usage > 60:
                return QColor(255, 165, 0)  # Orange for medium usage
            else:
                return QColor(0, 255, 0)  # Green for low usage

        # Draw CPU usage
        cpu_color = get_color(cpu_usage)
        painter.setPen(cpu_color)
        painter.drawText(int(x), int(y), int(width), 20, Qt.AlignLeft, f"CPU: {cpu_usage}%")

        # Draw Memory usage
        memory_color = get_color(memory_usage)
        painter.setPen(memory_color)
        painter.drawText(int(x), int(y) + 20, int(width), 20, Qt.AlignLeft, f"RAM: {memory_usage}%")

        # Draw GPU usage
        gpu_color = get_color(gpu_usage)
        painter.setPen(gpu_color)
        painter.drawText(int(x), int(y) + 40, int(width), 20, Qt.AlignLeft, f"GPU: {gpu_usage}%")

        # Calculate the current time and date
        current_time = datetime.now()
        current_date = current_time.day
        current_month = current_time.month
        month_str = {
            1:"January",
            2:"February",
            3:"March",
            4:"April",
            5:"May",
            6:"June",
            7:"July",
            8:"August",
            9:"September",
            10:"October",
            11:"November",
            12:"December"
        }
        current_month = month_str[current_month]

        current_hour = current_time.hour
        current_minute = current_time.minute
        if current_minute < 10:
            current_minute = "0" + str(current_minute)
        else:
            current_minute = str(current_minute)
        if current_hour < 10:
            current_hour = "0" + str(current_hour)
        else:
            current_hour = str(current_hour)

        # Draw GPU temperature
        if gputemp > 80:
            gpu_color = QColor(255,0,0)
        elif gputemp > 50:
            gpu_color = QColor(255,165,0)
        else:
            gpu_color = QColor(0,255,0)
        painter.setPen(gpu_color)
        painter.drawText(int(x), int(y) + 60, int(width), 20, Qt.AlignLeft, f"TEMP: {gputemp}°C")

        # Draw network speed
        if self.download_speed is not None and self.upload_speed is not None:
            speed_color = QColor(0,150,180)
            painter.setPen(speed_color)
            painter.drawText(int(x), int(y+85), int(width+10), 20, Qt.AlignLeft, f"D: {self.download_speed:.2f} Mbps")
            painter.drawText(int(x), int(y+105), int(width+10), 20, Qt.AlignLeft, f"U: {self.upload_speed:.2f} Mbps")

        # Draw battery status
        battery = psutil.sensors_battery()
        percent = battery.percent
        charging = battery.power_plugged

        time_left = battery.secsleft
        if time_left == psutil.POWER_TIME_UNLIMITED:
            time_left_str = "Unlimited (plugged in)"
        elif time_left == psutil.POWER_TIME_UNKNOWN or time_left < 0:
            time_left_str = "Unknown"
        else:
            hours = time_left // 3600
            minutes = (time_left % 3600) // 60
            time_left_str = f"{hours}h {minutes}m"

        charging_status = "Charging" if charging else "Not Charging"
        if charging_status == "Charging":
            time_left_str = "Plugged in"
            status_color = QColor(0,230,0)
        else:
            time_left_str = "Not plugged"
            status_color = QColor(220,0,0)

        font = QFont('Orbitron',6)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0,180,200))
        painter.drawText(int(x), int(y+130), int(width), 20, Qt.AlignLeft, f"BATTERY: {percent}%")
        painter.setPen(status_color)
        painter.drawText(int(x), int(y+145), int(width+20), 20, Qt.AlignLeft, f"Status: {time_left_str}")


        # Draw the CLOCK FACE in the main window
        font = QFont('Orbitron',15)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0,180,200))
        painter.drawText(205, 0, 90, 35, Qt.AlignCenter, f"{current_hour}:{current_minute}")
        
        font = QFont('Orbitron',6)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0,180,200))
        painter.drawText(206, 20, 90, 35, Qt.AlignCenter, f"{current_date} {current_month}")

        # Draw the system uptime
        font = QFont('Orbitron',5)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0,180,200))
        uptime = self.get_uptime()
        painter.drawText(398, 125, 90, 35, Qt.AlignCenter, "SYSTEM  UPTIME")
        
        font = QFont('Orbitron',6)
        font.setBold(True)
        painter.setFont(font)
        uptime_color = QColor(0,180,200)
        if uptime[1] > 48:
            uptime_color = QColor(255,0,0)
        elif uptime[1] > 6:
            uptime_color = QColor(255,165,0)
        else:
            uptime_color = QColor(0,255,0)
        painter.setPen(uptime_color)
        painter.drawText(393, 148, 90, 35, Qt.AlignRight, uptime[0])

        # Draw the listening status
        if self.listening:
            painter.setPen(QColor(0,225,0))
            painter.drawText(383, 165, 100, 35, Qt.AlignRight, "SYSTEM ONLINE")
        else:
            painter.setPen(QColor(255,0,0))
            painter.drawText(383, 165, 100, 35, Qt.AlignRight, "SYSTEM OFFLINE")

        # Draw the weather and location details
        if self.latitude is not None and self.longitude is not None and self.temperature is not None and self.weather is not None:
            font = QFont('Orbitron',6)
            font.setBold(True)
            cordinate_color = QColor(0,150,180)
            painter.setPen(cordinate_color)
            painter.setFont(font)
            painter.drawText(int(x+357), int(y+160), int(width+10), 20, Qt.AlignRight, f"LATITUDE: {self.latitude}")
            painter.drawText(int(x+347), int(y+173), int(width+20), 20, Qt.AlignRight, f"LONGITUDE:{self.longitude}")
            font = QFont('Orbitron',5)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(int(x+357), int(y+143), int(width+10), 20, Qt.AlignRight, f"{self.weather.upper()}")
            painter.drawText(int(x+362), int(y+110), int(width+5),20, Qt.AlignRight, f"{self.city}")
            font = QFont('Orbitron',12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(int(x+367), int(y+120), int(width), 40, Qt.AlignRight, f"{round(self.temperature)}°C")

        # Display the realtime responses by the bot on screen
        if self.speech_text is not None:
            font = QFont('Orbitron',5)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(0,180,200))
            bounding_rect = QRect(150, 210, 210, 80)
            painter.drawText(bounding_rect, Qt.AlignCenter | Qt.TextWordWrap, self.speech_text)

    # Update the animation timer for the pulsating circle
    def update_animation(self):         
        self.animation_time += 0.20         
        self.update()      

    def get_uptime(self):
        """Get the system uptime in hours, minutes, and seconds"""
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = int(current_time - boot_time)
        
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_hours = hours

        if hours < 9:
            hours = "0"+str(hours)
        if minutes < 9:
            minutes = "0"+str(minutes)
        if seconds < 9:
            seconds = "0"+str(seconds)
        return [f"{hours} h {minutes} m {seconds} s", uptime_hours]

    def listen_again(self):
        """Start listening again when the mic button is clicked when not listening already"""
        if self.listening == False:
            start_listening_again(self)

    def set_speaking_state(self, speaking):
        """Set the speaking state of the assistant"""
        self.is_speaking = speaking

    def wake_up(self):
        """Wake up the assistant when a wake word is detected"""
        with self.lock:
            self.awake = True
            self.last_command_time = time.time()
            print("Jarvis is now awake")

    def go_to_sleep(self):
        """Put the assistant to sleep when inactive for a while"""
        with self.lock:
            self.awake = False
            print("Jarvis has gone to sleep")

    def update_last_command_time(self):
        """Update the last command time to the current time"""
        with self.lock:
            self.last_command_time = time.time()

    def check_inactivity(self):
        """Check if the assistant is inactive for a while and put it to sleep"""
        if time.time() - self.last_command_time > 120 and self.awake == True:
            print("Jarvis is inactive for 2 minutes and went to sleep")
            self.go_to_sleep()

    def inactivity_monitor_helper(self):
        """Helper function to monitor inactivity of the assistant"""
        inactivity_monitor(self)

    def paintEvent(self, event):   
        """Override the paint event to draw custom graphics"""      
        painter = QPainter(self)         
        painter.setRenderHint(QPainter.Antialiasing)                  
        # Create gradient background
        gradient = QRadialGradient(             
            QPoint(self.width() // 2, self.height() // 2),              
            max(self.width(), self.height())         
        )         
        gradient.setColorAt(0, QColor(0, 16, 16))         
        gradient.setColorAt(1, QColor(0, 0, 51))         
        painter.fillRect(self.rect(), gradient)  # Set background gradient

        # Adjust the vertical positioning by reducing the y-coordinate
        center = QPoint(self.width() // 2, self.height() // 2 - 5)  # Move up by 20 pixels

        # Dynamic base and max radii based on window size
        base_radius = min(self.width(), self.height()) * 0.10  # 10% of smaller window dimension
        max_radius = min(self.width(), self.height()) * 0.20  # 20% of smaller window dimension

        radius = base_radius + (max_radius - base_radius) * (1 if self.is_speaking else 0) * (1 +                         
                   (0.5 * (1 + math.sin(self.animation_time * 2.5))))  # Dynamic circle size and animation effect

        outer_opacity = 0.2        
        outer_radius = max_radius + (min(self.width(), self.height()) * 0.1)
        outer_gradient = QRadialGradient(center, outer_radius)         
        outer_gradient.setColorAt(0, QColor(50, 250, 255, int(outer_opacity * 255)))         
        outer_gradient.setColorAt(1, QColor(50, 150, 255, int(outer_opacity * 0.7 * 255)))                  

        outer_pen = QPen(outer_gradient, 3)         
        painter.setPen(outer_pen)         
        painter.drawEllipse(center, outer_radius, outer_radius)  # Draw outer circle

        inner_opacity = 0.9 if self.is_speaking else 0         
        inner_gradient = QRadialGradient(center, radius)         
        inner_gradient.setColorAt(0, QColor(50, 250, 255, int(inner_opacity * 255)))         
        inner_gradient.setColorAt(1, QColor(50, 150, 255, int(inner_opacity * 0.7 * 255)))          
        
        inner_pen = QPen(inner_gradient, 3.5)         
        painter.setPen(inner_pen)         
        painter.drawEllipse(center, radius, radius)  # Draw inner circle

        laptop_pixmap = QPixmap()
        try:
            laptop_pixmap.load('artifacts/laptop_v.png')
            # Check if pixmap is loaded successfully
            if laptop_pixmap.isNull():
                print("Warning: Could not load laptop_vitals.png")
                # Create a placeholder pixmap
                laptop_pixmap = QPixmap(200, 200)
                laptop_pixmap.fill(QColor(50, 50, 50))  # Dark gray placeholder
        except Exception as e:
            print(f"Error loading laptop image: {e}")
            # Create a placeholder pixmap
            laptop_pixmap = QPixmap(200, 200)
            laptop_pixmap.fill(QColor(50, 50, 50))  # Dark gray placeholder

        # Calculate image dimensions
        image_width = min(self.width() * 0.25, laptop_pixmap.width())  # 20% of window width or image width
        image_height = min(self.height() * 0.25, laptop_pixmap.height())  # 40% of window height or image height

        # Position the image on the left side
        image_x = 20  # 20 pixels from the left edge
        image_y = (self.height()*0.25) - (image_height//2) - 20  # Vertically centered

        scaled_pixmap = laptop_pixmap.scaled(
            int(image_width), 
            int(image_height), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        # Draw the laptop image
        painter.drawPixmap(
            QRect(int(image_x), int(image_y), 
            scaled_pixmap.width(), scaled_pixmap.height()), 
            scaled_pixmap
        )

        self.draw_system_vitals(painter, image_x, image_y + scaled_pixmap.height() + 10, scaled_pixmap.width())

        # Adjust mic button position and size dynamically
        button_size = 25 
        button_x =  240 
        button_y =  265
        button_y = max(button_size, button_y)
        # Update mic button geometry and icon size
        self.mic_button.setGeometry(int(button_x), int(button_y), int(button_size), int(button_size))
        self.mic_button.setIconSize(QSize(int(button_size), int(button_size)))
        self.mic_button.show()

class TodoUI(QDialog):
    """
    Class to create a To-Do list menu which can be used the manage
    the tasks in the todo list using keyboard input
    """
    def __init__(self, json_file="tasks.json"):
        super().__init__()
        self.json_file = json_file  
        self.tasks = self.load_tasks()  
        self.setWindowTitle("To-Do Menu")
        self.setGeometry(600, 100, 500, 300)  
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.Window)

        layout = QVBoxLayout(self) # Layout

        # Task Input Fields
        font = QFont('Orbitron',6)
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter task name")
        self.task_input.setStyleSheet(self.get_transparent_style())
        self.task_input.setFont(font)
        layout.addWidget(self.task_input)

        # description input field
        self.desc_input = QLineEdit(self)
        self.desc_input.setPlaceholderText("Enter task description")
        self.desc_input.setStyleSheet(self.get_transparent_style())
        self.desc_input.setFont(font)
        layout.addWidget(self.desc_input)

        # priority dropdown
        self.priority_input = QComboBox(self)
        self.priority_input.addItems(["Low", "Medium", "High"])
        self.priority_input.setStyleSheet(self.get_transparent_style())
        self.priority_input.setFont(font)
        layout.addWidget(self.priority_input)

        # status dropdown
        self.status_input = QComboBox(self)
        self.status_input.addItems(["Pending", "In Progress"])
        self.status_input.setStyleSheet(self.get_transparent_style())
        self.status_input.setFont(font)
        layout.addWidget(self.status_input)

        # Scrollable Task List
        self.task_list_widget = QWidget(self)
        self.task_list_layout = QVBoxLayout(self.task_list_widget)
        self.task_list_layout.setSpacing(10)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.task_list_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(self.get_transparent_style())
        layout.addWidget(self.scroll_area)

        # Buttons
        button_style = """
            background-color: rgb(0, 180, 210);
            color: rgb(0, 0, 78);
            font-size: 14px;
            font-weight: bold;
            border: 1px solid rgb(0, 180, 210);
            border-radius: 5px;
            padding: 5px;
        """
        # Button to add a task
        add_button = QPushButton("Add Task", self)
        add_button.setStyleSheet(button_style)
        add_button.clicked.connect(self.add_task)
        add_button.setFont(font)
        layout.addWidget(add_button)

        # Button to remove selected tasks
        remove_button = QPushButton("Remove Task", self)
        remove_button.setStyleSheet(button_style)
        remove_button.clicked.connect(self.remove_task)
        remove_button.setFont(font)
        layout.addWidget(remove_button)

        # Button to save tasks to JSON file
        save_button = QPushButton("Save Tasks", self)
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_tasks)
        save_button.setFont(font)
        layout.addWidget(save_button)

        self.load_tasks_into_list()

    def get_transparent_style(self):
        """Style for transparent input fields and the task list"""
        return """
            background: transparent;
            color: rgb(0, 180, 210);
            font-size: 14px;
            font-weight: bold;
            border: none;
        """

    def add_task(self):
        """Add a task to the list and JSON structure"""
        task_name = self.task_input.text().strip()
        desc = self.desc_input.text().strip()
        priority = self.priority_input.currentText()
        status = self.status_input.currentText()

        if not task_name:
            QMessageBox.warning(self, "Input Error", "Task name cannot be empty!")
            return
        if task_name in self.tasks:
            QMessageBox.warning(self, "Duplicate Task", "Task name already exists!")
            return
        # Add to tasks dictionary
        self.tasks[task_name] = {"desc": desc, "priority": priority, "status": status}
        # Update the list widget
        self.add_task_to_list_widget(task_name, priority, status)

        # Clear input fields
        self.task_input.clear()
        self.desc_input.clear()
        self.priority_input.setCurrentIndex(0)
        self.status_input.setCurrentIndex(0)

    def remove_task(self):
        """Remove selected tasks from the list and JSON structure"""
        selected_items = self.task_list_widget.findChildren(QLabel)
        selected_labels = [item for item in selected_items if item.property("selected")]

        if not selected_labels:
            QMessageBox.warning(self, "Selection Error", "No task selected!")
            return

        for label in selected_labels:
            task_name = label.property("task_name")
            if task_name in self.tasks:
                del self.tasks[task_name]  # Remove from tasks dictionary
            self.task_list_layout.removeWidget(label)  # Remove from layout
            label.deleteLater()

    def save_tasks(self):
        """Save tasks to the JSON file after making any changes"""
        try:
            with open(self.json_file, "w") as file:
                json.dump(self.tasks, file, indent=4)
            QMessageBox.information(self, "Success", "Tasks saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save tasks: {e}")

    def load_tasks(self):
        """Load tasks from the JSON file"""
        try:
            with open(self.json_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}  
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tasks: {e}")
            return {}

    def load_tasks_into_list(self):
        """Load tasks from the dictionary into the scrollable list widget"""
        for task_name, details in self.tasks.items():
            priority = details.get("priority", "Unknown")
            status = details.get("status", "Unknown")
            self.add_task_to_list_widget(task_name, priority, status)

    def add_task_to_list_widget(self, task_name, priority, status):
        """Add a task to the scrollable list widget"""
        task_label = QLabel(f"{task_name} (Priority: {priority}, Status: {status})", self)
        task_label.setStyleSheet("""
            background: transparent;
            color: rgb(0, 180, 210);
            font-size: 14px;
            font-weight: bold;
            border: 1px solid rgb(0, 180, 200);
            border-radius: 5px;
            padding: 5px;
        """)
        task_label.setProperty("task_name", task_name)
        task_label.setProperty("selected", False)
        task_label.mousePressEvent = lambda event: self.toggle_task_selection(task_label)
        font = QFont('Orbitron',6)
        task_label.setFont(font)
        self.task_list_layout.addWidget(task_label)

    def toggle_task_selection(self, task_label):
        """Toggle selection of a task in the scrollable list"""
        is_selected = task_label.property("selected")
        if is_selected:
            task_label.setStyleSheet(task_label.styleSheet().replace("color: rgb(0, 250, 250);", "color: rgb(0, 180, 210);"))
            task_label.setProperty("selected", False)
        else:
            task_label.setStyleSheet(task_label.styleSheet().replace("color: rgb(0, 180, 210);", "color: rgb(0, 250, 250);"))
            task_label.setProperty("selected", True)

    def paintEvent(self, event):
        """Draw the gradient background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QRadialGradient(
            QPoint(self.width() // 2, self.height() // 2),
            max(self.width(), self.height())
        )
        gradient.setColorAt(0, QColor(0, 16, 16))
        gradient.setColorAt(1, QColor(0, 0, 51))
        painter.fillRect(self.rect(), gradient)

        outline_pen = QPen(QColor(50, 250, 255, 100), 2)
        painter.setPen(outline_pen)
        painter.drawRect(self.rect())

class FileFolderSearchUI(QDialog):
    """Class to create a file/folder search menu to search for files or folders in a directory or create the same"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File/Folder Search")
        self.setGeometry(600, 100, 500, 300)
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.Window)

        # Layout
        layout = QVBoxLayout(self)

        font = QFont('Orbitron', 6)

        # Input Fields
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter file or folder name")
        self.name_input.setStyleSheet(self.get_transparent_style())
        self.name_input.setFont(font)
        layout.addWidget(self.name_input)

        self.type_selector = QComboBox(self)
        self.type_selector.addItems(["File", "Folder"])
        self.type_selector.setStyleSheet(self.get_transparent_style())
        self.type_selector.setFont(font)
        layout.addWidget(self.type_selector)

        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText("Enter directory to search in")
        self.location_input.setStyleSheet(self.get_transparent_style())
        self.location_input.setFont(font)
        layout.addWidget(self.location_input)

        # Buttons
        button_style = """
            background-color: rgb(0, 180, 210);
            color: rgb(0, 0, 78);
            font-size: 14px;
            font-weight: bold;
            border: 1px solid rgb(0, 180, 210);
            border-radius: 5px;
            padding: 5px;
        """
        # Button to search for a file or folder
        search_button = QPushButton("Search", self)
        search_button.setStyleSheet(button_style)
        search_button.clicked.connect(self.search)
        search_button.setFont(font)
        layout.addWidget(search_button)

        # Button to create a file or folder
        create_button = QPushButton("Create", self)
        create_button.setStyleSheet(button_style)
        create_button.clicked.connect(self.create)
        create_button.setFont(font)
        layout.addWidget(create_button)

    def get_transparent_style(self):
        """Style for transparent input fields"""
        return """
            background: transparent;
            color: rgb(0, 180, 210);
            font-size: 14px;
            font-weight: bold;
            border: none;
        """

    def search(self):
        """Search for a file or folder in the specified directory. Function is called by the search button"""
        folder = self.type_selector.currentText()
        name = self.name_input.text()
        location = self.location_input.text()

        if not os.path.exists(location):
            print("Invalid directory path")
            return
        if folder == "File":
            for root, dirs, files in os.walk(location):
                if name in files:
                    print(f"File found: {os.path.join(root, name)}")
                    path = os.path.join(root, name)
                    os.startfile(path) 
                    return
        elif folder == "Folder":
            for root, dirs, files in os.walk(location):
                if name in dirs:
                    print(f"Folder found: {os.path.join(root, name)}")
                    path = os.path.join(root, name)
                    os.startfile(path) 
                    return
        print("No match found")

    def create(self):
        """Create a file or folder in the specified directory. Function is called by the create button"""
        folder = self.type_selector.currentText()
        name = self.name_input.text()
        location = self.location_input.text()
        if location == "":
            location = os.getcwd()
        if not os.path.exists(location):
            QMessageBox.warning("Invalid directory path")
            return
        if folder == "File":
            with open(os.path.join(location, name), "w") as file:
                print(f"File created: {os.path.join(location, name)}")
        elif folder == "Folder":
            os.makedirs(os.path.join(location, name))
            print(f"Folder created: {os.path.join(location, name)}")

    def paintEvent(self, event):
        """Draw the gradient background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QRadialGradient(
            QPoint(self.width() // 2, self.height() // 2),
            max(self.width(), self.height())
        )
        gradient.setColorAt(0, QColor(0, 16, 16))
        gradient.setColorAt(1, QColor(0, 0, 51))
        painter.fillRect(self.rect(), gradient)

        outline_pen = QPen(QColor(50, 250, 255, 100), 2)
        painter.setPen(outline_pen)
        painter.drawRect(self.rect())



class JarvisAssistant:
    """Main class that contains the functionalities of the assistant, 
        including speech recognition,
        intent classification,
        processing of intent,
        text-to-speech etc...
    The JarvisUI class object is passed so that it can interact with the UI class and its attributes and functions
    """
    def __init__(self,ui):
        # Initialize Vosk model and recognizers
        self.ui = ui
        self.model = Model(r"D:\INSTALATIONS\Vosk\vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        self.recognizer.SetGrammar(
            '["hello","hey","hi","play","search","google","increase","decrease","volume","jarvis","exit","quit","speak faster","speak softer","louder","quieter","good night","good morning","wake up","good bye","look up","internet","time","what","whats","the","time","is","weekend","india","chat","day","date","today","todays","mute","system","reduce","can","you","temperature","weather","how","hows","report","outside","it","thanks","thank","you","for","help","there","list","my","tasks","are","high","medium","low","pending","in","progress","priority","open"]'
        )
        self.query_recognizer = KaldiRecognizer(self.model, 16000)
        self.directory_recognizer = KaldiRecognizer(self.model, 16000)
        self.directory_recognizer.SetWords(True)
        self.directory_recognizer.SetGrammar('["downloads","screenshots","images","c","drive","d","installations","coding","semester","google","youtube","whats","app","v","s","code","mail","git","hub","chat","bin"]')
        # Initialize microphone and audio streams
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192
        )
        self.query_stream = None
        self.directory_stream = None

        self.model_path='intent_classifier.joblib'
        self.vectorizer_path = 'tfidf_vectorizer.joblib'
        self.label_encoder_path = 'label_encoder.joblib'

        try:
            self.classifier = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.label_encoder = joblib.load(self.label_encoder_path)
        except FileNotFoundError as e:
            print(f"Error loading model: {e}")
            print("Ensure you have trained and saved the model")
            raise

        # Initialize Text-to-Speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 220)
        self.engine.setProperty("volume", 0.9)

        # Initialize YouTube API client (replace with the user's API key)
        self.youtube = build("youtube", "v3", developerKey="AIzaSyA8kUp6Sl64Y5pHYgKQF7gL4RZ1Cw5Og0M")

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        self.ui.get_assistant(self)

    def get_volume(self):
        """Get the current system volume"""
        return round(self.volume.GetMasterVolumeLevelScalar() * 100, 2)

    def set_volume(self,volume_percent):
        """Set the system volume to the specified percentage"""
        volume = max(0, min(volume_percent, 100)) / 100.0
        self.volume.SetMasterVolumeLevelScalar(volume, None)

    def temp(self):
        """Get the current temperature and weather conditions"""
        self.speak(f"The current temperature is {self.ui.temperature}°Celcius with {self.ui.weather} conditions")
        return f"The current temperature is {self.ui.temperature}°Celcius with {self.ui.weather} conditions"

    def increase_volume(self,increment=10):
        """Increase the system volume by the specified increment"""
        current = self.get_volume()
        new_volume = min(current + increment, 100)
        self.set_volume(new_volume)
        return new_volume

    def decrease_volume(self, decrement=10):
        """Decrease the system volume by the specified decrement"""
        current = self.get_volume()
        new_volume = max(current-decrement,0)
        self.set_volume(new_volume)
        return new_volume

    def mute_toggle(self):
        """Toggle the system volume mute state"""
        is_muted = bool(self.volume.GetMute())
        self.volume.SetMute(not is_muted, None)
        return not is_muted

    def speak(self, text):
        """Convert text to speech, also maintains a lock to prevent multiple speech commands from overlapping"""
        with self.ui.lock:
            self.ui.set_speaking_state(True) # Used to synchronize the pulsating circle with the speech of the assistant
            self.engine.say(text)
            self.ui.speech_text = text
            self.engine.runAndWait()
            self.ui.set_speaking_state(False)

    def increase_speech_rate(self):
        """Increase speech rate of the assistant"""
        curr_rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", curr_rate + 10)
        print(f"Current speech rate = {curr_rate + 10}")

    def decrease_speech_rate(self):
        """Decrease speech rate of the assistant"""
        curr_rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", curr_rate - 10)
        print(f"Current speech rate = {curr_rate - 10}")

    def increase_speech_volume(self):
        """Increase speech volume of the assistant"""
        curr_vol = self.engine.getProperty("volume")
        if curr_vol < 1.0:
            self.engine.setProperty("volume", min(1.0, curr_vol + 0.1))
            print(f"Current speech volume = {min(1.0, curr_vol + 0.1)}")
        else:
            print("Volume is already at the maximum")

    def decrease_speech_volume(self):
        """Decrease speech volume of the assistant"""
        curr_vol = self.engine.getProperty("volume")
        if curr_vol > 0.0:
            self.engine.setProperty("volume", max(0.0, curr_vol - 0.1))
            print(f"Current speech volume = {max(0.0, curr_vol - 0.1)}")
        else:
            print("Volume is already at the minimum")

    def browser_search(self, query):
        """Perform a Google search for the specified query"""
        if query:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            try:
                webbrowser.open(search_url)
                self.speak("Here are the search results")
            except Exception as e:
                self.speak(f"I couldn't open the browser. Error: {str(e)}")
        else:
            print("Jarvis: No query detected!")

    def play_youtube_video(self, query):
        """Search and play a YouTube video for the specified query"""
        if query:
            try:
                search_response = (
                    self.youtube.search()
                    .list(q=query, type="video", part="id,snippet", maxResults=1)
                    .execute()
                )

                if search_response["items"]:
                    video_id = search_response["items"][0]["id"]["videoId"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    webbrowser.open(video_url)
                    self.speak(f"Playing {query}")
                else:
                    print("Jarvis: No videos found for your query")
                    self.speak("I couldn't find any videos matching your query")
            except Exception as e:
                self.speak(f"Error while playing the video. Error: {str(e)}")
        else:
            print("Jarvis: No query detected!")


    def detect_intent(self, text, confidence_threshold=0.16):
        """Detect the intent of the user input text using the trained classifier"""
        if "open" in text:
                directory = self.listen_directory()
                self.open(directory)
                return None  
        if text in ["hows the weather","whats the temperature","what is the temperature","hows it outside","how is it outside","whats the weather report"]:
            return "temp"
        elif text in ["thanks jarvis","thanks","thank you","thank you jarvis","thanks for the help"]:
            return "thanks"
        elif text in ["can you list my tasks","can you please list my tasks","can you list my hey priority tasks","list my hey priority tasks","can you list my high priority tasks","can you list my high priority tasks","list my tasks","what are my tasks","can you give my tasks","list my high priority tasks","list my low priority tasks","list my pending tasks","can you list my low priority tasks","can you list my medium priority tasks","can you list my pending tasks","can you list my tasks in progress","can you list my in progress tasks"]:
            if "priority" in text or "pending" in text  or "in progress" in text:
                self.filter_tasks(text)
                return None
            else:
                return "tasks"
        # Vectorize the input text
        text_vectorized = self.vectorizer.transform([text])
        # Predict the intent
        prediction = self.classifier.predict(text_vectorized)
        # Get the intent probabilities
        probabilities = self.classifier.predict_proba(text_vectorized)[0]
        # Get the intent label
        intent = self.label_encoder.inverse_transform(prediction)[0]
        # Get the confidence score
        confidence = max(probabilities)
        # If confidence is below threshold, set intent to 'unknown'
        if confidence < confidence_threshold:
            intent = 'unknown'
    
        return intent


    def listen_query(self):
        """Listen for the user query and return the recognized text in a infinite while loop, breaks when specific keywords are detected"""
        print("Jarvis: Listening for query...")
        if self.query_stream is None:
            self.query_stream = self.mic.open(
                format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192
            )
        while True:
            data = self.query_stream.read(4096, exception_on_overflow=False)
            if self.query_recognizer.AcceptWaveform(data):
                result = json.loads(self.query_recognizer.Result())
                self.query_stream.stop_stream()
                self.query_stream.close()
                self.query_stream = None
                query = result.get("text", "").strip()
                print(f"Searching for : {query}")
                return result.get("text", "").strip()

    def listen_directory(self):
        """Listen for the directory or application name and return the recognized text"""
        print("Jarvis: Listening for directory or application...")
        if self.directory_stream is None:
            self.directory_stream = self.mic.open(
                format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192
            )
        while True:
            data = self.directory_stream.read(4096, exception_on_overflow=False)
            if self.directory_recognizer.AcceptWaveform(data):
                result = json.loads(self.directory_recognizer.Result())
                self.directory_stream.stop_stream()
                self.directory_stream.close()
                self.directory_stream = None
                query = result.get("text", "").strip()
                print(f"Opening the directory : {query}")
                return result.get("text", "").strip()

    def first_greet(self):
        """Initial greeting when encountering greet intent for 1st time after starting the app.
        Greet the user based on the current time of the day"""
        currtime = datetime.now().time()
        hrs = currtime.hour
        self.ui.first_time = False
        if hrs < 12:
            self.speak("Good Morning sir. Let's gets started with the day")
        elif hrs < 15:
            self.speak("Good Afternoon sir. How's the day going so far?")
        elif hrs < 18:
            self.speak("Good Evening sir. Hope everything went smoothly today")
        else:
            self.speak("Good Night sir. Let me know if there's anything you need before you rest")

    def list_tasks(self, data):
        """List the tasks from the JSON file"""
        print(f"{data}")
        for key, value in data.items():
            print(f"{key}")
            self.speak(f"{key}")
            descp = value["desc"]
            prior = value["priority"]
            stats = value["status"]
            print(f"description: {descp}, priority:{prior}, status: {stats} ")
            self.speak(f"description: {descp}, priority:{prior}, status: {stats} ")

    def filter_tasks(self, text):
        """Filter the tasks based on the priority or status"""
        with open("tasks.json", 'r') as file:
            data = json.load(file)
        filtered_data = data.copy()
        if "low" in text:
            filtered_data = {k: v for k, v in data.items() if v["priority"] == "Low"}
        elif "high" in text or "hey" in text:
            filtered_data = {k: v for k, v in data.items() if v["priority"] == "High"}
        elif "pending" in text:
            filtered_data = {k: v for k, v in data.items() if v["status"] == "Pending"}
        elif "in progress" in text:
            filtered_data = {k: v for k, v in data.items() if v["status"] == "In progress"}
        self.list_tasks(filtered_data)
    
    def open(self, directory):
        """Open the specified directory or application"""
        if directory == "downloads":
            downloads_path = os.path.expanduser("~/Downloads")
            os.startfile(downloads_path)
        elif directory == "screenshots" or directory == "screenshots":
            screenshots_path = os.path.expanduser("~/Pictures/Screenshots")
            os.startfile(screenshots_path)
        elif directory == "c drive" or directory == "c":
            os.startfile("C:\\")
        elif directory == "d drive" or directory == "d":
            os.startfile("D:\\")
        elif directory == "installations":
            if os.path.exists("D:\\INSTALATIONS"):
                os.startfile("D:\\INSTALATIONS")
        elif directory == "coding":
            if os.path.exists("D:\\Coding"):
                os.startfile("D:\\Coding")
        elif directory == "semester":
            if os.path.exists("D:\\Sem-4"):
                os.startfile("D:\\Sem-4")
        elif directory == "whats app":
            url = "https://web.whatsapp.com/"
            webbrowser.open(url)
        elif directory == "youtube":
            url = "https://www.youtube.com/"
            webbrowser.open(url)
        elif directory == "google":
            google_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            os.startfile(google_path)
        elif directory == "v s code":
            vscode_path = r"D:\VSCode\Microsoft VS Code\Code.exe"
            os.startfile(vscode_path)
        elif directory == "mail":
            url = "https://mail.google.com/mail/u/0/#inbox"
            webbrowser.open(url)
        elif directory == "git hub" or directory == "git":
            url = "https://github.com"
            webbrowser.open(url)
        elif directory == "chat":
            url = "https://chatgpt.com"
            webbrowser.open(url)
        elif directory == "bin":
            os.system('explorer shell:::{645FF040-5081-101B-9F08-00AA002F954E}')
        else:
            print("No directory given")
            self.speak("No directory given")

    def thanks(self):
        """Respond to the user's thanks with a random response"""
        thanks_responses = [
            "You're welcome sir",
            "Always at your service sir",
            "My pleasure sir",
            "Of course sir. Let me know if there's anything else",
            "No thanks needed sir. I'm here to help",
            "Anytime sir",
            "Glad to assist sir",
            "You're most welcome sir",
            "Happy to help sir",
            "It's what I'm here for sir",
            "No problem sir. But a promotion wouldn't hurt",
            "Anytime sir. After all, I am your favorite assistant"
        ]
        response = random.choice(thanks_responses)
        print(f"Jarvis: {response}")
        self.speak(response)


    def greet(self):
        """Respond to the user's greeting with a random response"""
        casual_responses = [
            "Yes sir. I'm listening",
            "I'm awake sir",
            "Listening sir. How can I assist?",
            "At your service sir",
            "I'm here sir. What can I do for you?"
        ]
        response = random.choice(casual_responses)
        print(f"Jarvis: {response}")
        self.speak(response)

    def listen(self):
        """Continuously listen and process commands from the user until the user says 'exit' or similar words"""
        self.speak("Jarvis is online")
        if self.ui.first_time:
            self.first_greet()
        while True:
            data = self.stream.read(4096, exception_on_overflow=False)
            audio_samples = np.frombuffer(data, dtype=np.int16)
            try:
                self.ui.update_audio_visualization(audio_samples)
            except RuntimeError as e:
                print(f"RuntimeError: {e}")
                break
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                command = result.get("text", "")
                if command == "" or command == "hey":
                    continue
                print(f"User: {command.capitalize()}")
                
                if command in ["exit","good bye","bye","good night","see you later","quit","shut down","night","bye jarvis"]:
                    print("Jarvis: Goodbye, sir!")
                    self.speak("Goodbye sir!")
                    self.cleanup()
                    self.ui.listening = False
                    break

                if command in ["hey jarivs","wake up","hello jarvis","hey jarvis","good morning","jarvis"]:
                    self.ui.wake_up()
                    print("Jarvis: Hello sir! How can I assist you?")
                    self.speak("Hello sir! How can I assist you?")
                    continue
                if not self.ui.awake:
                    continue
                intent = self.detect_intent(command)
                self.ui.update_last_command_time()
                self.process_intent(intent)

    def process_text_command(self, command):
        """ Function to process the text input commands from the user"""
        if command in ["hey jarivs","wake up","hello jarvis","hey jarvis","good morning","jarvis"]:
                    self.ui.wake_up()
                    print("Jarvis: Hello sir! How can I assist you?")
                    self.speak("Hello sir! How can I assist you?")
                    return
        if not self.ui.awake:
                    return
        if "play" in command:
            query_index = command.index("play")
            com = command.split(" ")
            query = ""
            for s in com[query_index+1:]:
                query += s + " "
            query = query.rstrip()
            self.play_youtube_video(query)
        elif "search" in command:
            query_index = command.index("search")
            com = command.split(" ")
            query = ""
            for s in com[query_index+1:]:
                query += s + " "
            query = query.rstrip()
            self.browser_search(query)
        elif "open" in command:
            dir_index = command.index("open")
            com = command.split(" ")
            dir = ""
            for s in com[dir_index+1:]:
                dir += s + " "
            dir = dir.rstrip()
            self.open(dir)
        else:
            self.process_intent(self.detect_intent(command))    


    def time(self):
        """Get the current time and speak it"""
        current_time = datetime.now().time()
        hrs = current_time.hour
        mins = current_time.minute
        sec = current_time.second
        amorpm = "a m"
        if hrs >= 12:
            amorpm = "p m"  
            if hrs != 12:
                hrs = hrs - 12
        print(f"Jarvis : The time is {hrs} {mins} {amorpm[0:3:2]} {sec} seconds sir")
        self.speak(f"The time is {hrs} {mins} {amorpm} {sec} seconds sir")

    def date(self):
        """Get the current date and speak it"""
        current_date = datetime.now()
        date = current_date.day  
        month = current_date.month
        year = current_date.year
        month_map = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 
                    7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
        month_word = month_map[month]
        self.speak(f"Today is {date} {month_word} {year}")

    def process_intent(self, intent):
        """Process the detected intent and perform the corresponding action"""
        if intent == None:
            return None
        if intent == "greet":
            self.greet()
        elif intent == "search":
            query = self.listen_query()
            self.browser_search(query)
        elif intent == "youtube":
            query = self.listen_query()
            self.play_youtube_video(query)
        elif intent == "increaseVol":
            self.increase_speech_volume()
        elif intent == "decreaseVol":
            self.decrease_speech_volume()
        elif intent == "increaseRate":
            self.increase_speech_rate()
        elif intent == "decreaseRate":
            self.decrease_speech_rate()
        elif intent == "time":
            self.time()
        elif intent == "date":
            self.date()
        elif intent == "incSysVol":
            vol = self.increase_volume()
            print(f"Current volume : {vol}")
        elif intent == "decSysVol":
            vol = self.decrease_volume()
            print(f"Current volume : {vol}")
        elif intent == "mute":
            mute = self.mute_toggle()
            if mute:
                mute = "Mute"
            else:
                mute = "Unmute"
            print(f"{mute}d system volume")
            self.speak(f"{mute}d system volume")
        elif intent == "temp":
            self.temp()
        elif intent == "thanks":
            self.thanks()
        elif intent == "tasks":
            with open('tasks.json','r') as file:
                data = json.load(file)
            self.list_tasks(data)
        else:
            print("Jarvis: Sorry sir, I didn't understand that command")
            self.speak("Sorry sir, I didn't understand that command")

    def cleanup(self):
        """Clean up resources before exiting"""
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        print("Resources cleaned up. Jarvis is offline")
        self.speak("Jarvis is offline")

def inactivity_monitor(ui):
    """Monitor the inactivity of the user and reset the assistant if the user is inactive for a certain period"""
    while True:
        time.sleep(1) # Sleep for 1 second and check again
        ui.check_inactivity()

def start_listening_again(ui):
    """Start the assistant listening again after the mic button is clicked, if not listening already"""
    ui.listening = True
    assistant = JarvisAssistant(ui)
    assistant_thread = threading.Thread(target= assistant.listen)
    assistant_thread.daemon = True
    assistant_thread.start()

def main():     
    """Main function of the application"""
    """Create the UI and start the application"""
    app = QApplication(sys.argv)
    ui = JarvisUI()
    ui.show()

    """Create the JarvisAssistant object in a seperate thread, while passing the UI object as an argument"""
    assistant = JarvisAssistant(ui)
    assistant_thread = threading.Thread(target = assistant.listen)
    assistant_thread.daemon = True # Daemonize the thread to stop it when the main program exits
    assistant_thread.start()
    
    """Create the inactivity monitor thread"""
    inactivity_thread = threading.Thread(target = ui.inactivity_monitor_helper)
    inactivity_thread.daemon = True # Daemonize the thread to stop it when the main program exits
    inactivity_thread.start()

    sys.exit(app.exec_())


if __name__ == "__main__":     
    main() # Start the application