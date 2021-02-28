from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import psutil
import sys
import time
import subprocess
import speedtest
import threading

style_sheet = '''
              QLabel {
                        font: 16px;
              }
              QLabel#usage_title {
                        border: 0px;
                        font: 18px bold;
              }
              QLabel#usage_label {
                        font: 16px bold;
                        background: white;
                        border-width: 1px;
              }
              QLabel#free_title {
                        border: 0px;
                        font: 18px bold;
              }
              QLabel#free_label {
                        font: 16px bold;
                        background: white;
                        border-width: 1px;
              }
              QLabel#disk_usage_labels {
                        font: 16px bold;
                        background: white;
                        border: #DDDDDD;
              }
              QLabel#disk_title_labels {
                        font: 16px bold;
                        background: #DDDDDD;
                        border: #DDDDDD;
              }
              QFrame {
                background-color: #DDDDDD;
                border: 1px solid black; 
                border-radius: 15px;
                border-width: 2px;
              }
              '''


class Performance:
    @staticmethod
    def getPerformance():
        processor_usage = psutil.cpu_percent(2)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        return processor_usage, memory_usage

    @staticmethod
    def getDisk():
        disk_usage = psutil.disk_usage('c://')
        total = disk_usage.total / 1000 / 1000 / 1000
        used = disk_usage.used / 1000 / 1000 / 1000
        free = disk_usage.free / 1000 / 1000 / 1000
        perc = disk_usage.percent
        return round(total, 2), round(used, 2), round(free,2), perc

    @staticmethod
    def getBattery():
        battery_status = psutil.sensors_battery()
        perc_left = battery_status.percent
        seconds_left = battery_status.secsleft
        is_plugged = battery_status.power_plugged
        return perc_left, seconds_left, is_plugged


class Wifi():
    def __init__(self):
        wifis_meta = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'])
        data = wifis_meta.decode('utf-8', errors="backslashreplace")

    @staticmethod
    def getSpeed():
        # All internet related data tests is being done against speedtest.net
        speed = speedtest.Speedtest()
        try:
            s_t = time.time()
            speed.download()
            speed.upload()
            speed.results.share()
            results = speed.results.dict()
            t_t = time.time() - s_t
            print(t_t)
        except Exception as e:
            print(f'Error while getting internet data results ({e}) - check https://www.speedtest.net')
        download = results['download'] // 1000 // 1000
        uplaod = results['upload'] // 1000 // 1000
        ping = results['ping']
        server = results['server']['sponsor'] + ': ' + results['server']['host']
        isp = results['client']['isp']
        print(download, uplaod, ping, server, isp)
        return (download, uplaod, ping, server, isp)




class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.performance = Performance()
        self.thread = QThreadPool()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Performance Track")
        self.setGeometry(100, 100, 500, 200)
        self.setWidgets()
        self.handleWorker()
        self.show()

    def setWidgets(self):

        cpu_frame = QFrame()
        ram_frame = QFrame()
        disk_frame = QFrame()

        # CPU/RAM usage labels
        cpu_usage_title = QLabel('CPU usage:')
        ram_usage_title = QLabel('RAM usage:')
        cpu_usage_title.setObjectName('usage_title')
        ram_usage_title.setObjectName('usage_title')
        self.cpu_usage_label = QLabel()
        self.cpu_usage_label.setObjectName('usage_label')
        self.ram_usage_label = QLabel()
        self.ram_usage_label.setObjectName('usage_label')

        # CPU/RAM free label
        cpu_free_title = QLabel('CPU free:')
        ram_free_title = QLabel('RAM free:')
        cpu_free_title.setObjectName('free_title')
        ram_free_title.setObjectName('free_title')
        title_labels = [cpu_free_title, ram_free_title, cpu_usage_title, ram_usage_title]
        for title in title_labels:
            title.setAlignment(Qt.AlignCenter)
        self.cpu_free = QLabel()
        self.ram_free = QLabel()
        self.cpu_free.setObjectName('free_label')
        self.ram_free.setObjectName('free_label')

        # Disk data labels
        disk_main_title = QLabel('Disk:')
        total_title = QLabel('Total:')
        disk_usage_title = QLabel('Used:')
        disk_free_title = QLabel('Free:')
        self.disk_total_value = QLabel()
        self.disk_usage_value = QLabel()
        self.disk_free_value = QLabel()
        disk_title_labels = [disk_main_title, total_title, disk_usage_title,disk_free_title]
        disk_usage_labels = [self.disk_usage_value, self.disk_free_value, self.disk_total_value]
        for label in disk_title_labels:
            label.setObjectName('disk_title_labels')
            label.setAlignment(Qt.AlignCenter)
        for label in disk_usage_labels:
            label.setObjectName('disk_usage_labels')
            label.setAlignment(Qt.AlignCenter)

        disk_data_frame = QFrame()
        disk_data_layout = QHBoxLayout()
        disk_data_layout.addWidget(total_title)
        disk_data_layout.addWidget(self.disk_total_value)
        disk_data_layout.addWidget(disk_usage_title)
        disk_data_layout.addWidget(self.disk_usage_value)
        disk_data_layout.addWidget(disk_free_title)
        disk_data_layout.addWidget(self.disk_free_value)
        disk_data_frame.setLayout(disk_data_layout)

        disk_frame_layout = QVBoxLayout()
        disk_frame_layout.addWidget(disk_main_title)
        disk_frame_layout.addWidget(disk_data_frame)

        disk_frame.setLayout(disk_frame_layout)


        cpu_layout = QVBoxLayout()
        ram_layout = QVBoxLayout()

        cpu_layout.addWidget(cpu_usage_title)
        cpu_layout.addWidget(self.cpu_usage_label)
        cpu_layout.setSpacing(15)
        cpu_layout.addWidget(cpu_free_title)
        cpu_layout.addWidget(self.cpu_free)

        ram_layout.addWidget(ram_usage_title)
        ram_layout.addWidget(self.ram_usage_label)
        ram_layout.setSpacing(15)
        ram_layout.addWidget(ram_free_title)
        ram_layout.addWidget(self.ram_free)

        cpu_frame.setLayout(cpu_layout)
        ram_frame.setLayout(ram_layout)

        internet_speed_frame = QFrame()
        speed_dlg_button = QPushButton("Internet\nSpeed")
        speed_dlg_button.clicked.connect(SpeedDlg)
        internet_layout = QHBoxLayout()
        internet_layout.addStretch(4)
        internet_layout.addWidget(speed_dlg_button)
        internet_speed_frame.setLayout(internet_layout)

        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 0)
        main_layout.addWidget(cpu_frame, 0, 0)
        main_layout.addWidget(ram_frame, 0, 1)
        main_layout.addWidget(disk_frame, 1, 0, 2, 0)
        main_layout.addWidget(internet_speed_frame, 3, 0, 2, 0)
        print(main_layout.columnStretch(0))

        self.setLayout(main_layout)

    def get_usage(self):
        while True:
            try:
                usage = self.performance.getPerformance()
                self.cpu_usage_label.setText(str(usage[0]))
                self.ram_usage_label.setText(str(usage[1]))
                self.cpu_free.setText(str(round(100 - usage[0], 2)))
                self.ram_free.setText(str(round(100 - usage[1], 2)))

                labels = [self.cpu_usage_label, self.ram_usage_label, self.cpu_free, self.ram_free]
                for label in labels:
                    label.setAlignment(Qt.AlignCenter)
            except Exception as e:
                print(e)
                pass

    def get_disk(self):
        while True:
            try:
                disk = self.performance.getDisk()
                self.disk_total_value.setText(str(disk[0]))
                self.disk_usage_value.setText(str(disk[1]))
                self.disk_free_value.setText(str(disk[2]))
            except Exception as e:
                print(e)
                pass
            time.sleep(60)

    def handleWorker(self):
        if self.cpu_free and self.cpu_usage_label and self.ram_free and self.ram_usage_label:
            self.perf_worker = ProgressThread(self.get_usage)
            self.thread.start(self.perf_worker)
        else:
            self.perf_worker.running = False

        if self.disk_free_value and self.disk_total_value and self.disk_usage_value:
            self.disk_worker = ProgressThread(self.get_disk)
            self.thread.start(self.disk_worker)




class ProgressThread(QRunnable):
    def __init__(self, func):
        super(ProgressThread, self).__init__()
        self.func = func
        self.running = True
    @pyqtSlot()
    def run(self):
        while self.running:
            self.func()


speeddlg_style = '''
        QLabel#title_labels {
            font: 18px bold;
            
        }
        
        QLabel#data_labels {
            font: 15px;    
        }
        QPushButton#test_btn{
            font: 18px;
            background: #DDDDDD;
        }
'''


class SpeedDlg(QDialog):
    def __init__(self):
        super(SpeedDlg, self).__init__()
        self.initDlg()

    def initDlg(self):
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Internet Speed')
        self.setupDlg()
        self.setStyleSheet(speeddlg_style)

        self.exec_()

    def setupDlg(self):

        counter_frame = QFrame()
        approx_label = QLabel("Approx. Time:")
        self.approx = QLabel()
        self.approx.setAlignment(Qt.AlignLeft)
        approx_label.setAlignment(Qt.AlignRight)

        approx_layout = QHBoxLayout()
        approx_layout.addStretch(2)
        approx_layout.addWidget(approx_label)
        approx_layout.addWidget(self.approx)
        counter_frame.setLayout(approx_layout)


        speed_frame = QFrame()
        download_title_label = QLabel("Download:")
        upload_title_label = QLabel("Upload:")
        ping_title_label = QLabel("Ping:")

        self.download_data = QLabel()
        self.upload_data = QLabel()
        self.ping_data = QLabel()

        speed_frame_layout = QHBoxLayout()
        speed_frame_layout.addWidget(download_title_label)
        speed_frame_layout.addWidget(self.download_data)
        speed_frame_layout.addWidget(upload_title_label)
        speed_frame_layout.addWidget(self.upload_data)
        speed_frame_layout.addWidget(ping_title_label)
        speed_frame_layout.addWidget(self.ping_data)

        speed_frame.setLayout(speed_frame_layout)

        connection_data_frame = QFrame()

        server_title_label = QLabel("Server:")
        self.server_data = QLabel()
        isp_title_label = QLabel("ISP:")
        self.isp_data = QLabel()

        connection_layout = QHBoxLayout()
        connection_layout.addWidget(server_title_label)
        connection_layout.addWidget(self.server_data)
        connection_layout.addSpacing(30)
        connection_layout.addWidget(isp_title_label)
        connection_layout.addWidget(self.isp_data)

        connection_data_frame.setLayout(connection_layout)

        self.data_labels = [self.download_data, self.upload_data, self.ping_data,
                            self.server_data, self.isp_data]
        [label.setObjectName('data_labels') for label in self.data_labels]
        [label.setAlignment(Qt.AlignBottom|Qt.AlignLeft) for label in self.data_labels]

        self.title_labels = [download_title_label, upload_title_label, ping_title_label,
                             server_title_label, isp_title_label]
        [label.setObjectName('title_labels') for label in self.title_labels]
        [label.setAlignment(Qt.AlignBottom|Qt.AlignRight) for label in self.title_labels]

        test_data_frame = QFrame()
        test_button = QPushButton('Start Testing')
        test_button.setObjectName('test_btn')
        test_button.clicked.connect(self.handleConnectionThread)

        test_frame_layout = QHBoxLayout()
        test_frame_layout.addWidget(test_button)
        test_data_frame.setLayout(test_frame_layout)


        main_layout = QVBoxLayout()
        main_layout.addWidget(counter_frame)
        main_layout.addWidget(speed_frame)
        main_layout.addWidget(connection_data_frame)
        main_layout.addWidget(test_data_frame)


        self.setLayout(main_layout)

    def handleConnectionThread(self):
        counter_thread = threading.Thread(target=self.approxCount)
        counter_thread.start()
        internet_speed_thread = threading.Thread(target=self.getConnectionData)
        internet_speed_thread.start()

    def getConnectionData(self):
        [label.clear() for label in self.data_labels]
        self.internet_speed = Wifi.getSpeed()
        print(self.internet_speed)
        # Set Download speed
        self.download_data.setText(str(self.internet_speed[0]))
        # Set upload speed
        self.upload_data.setText(str(self.internet_speed[1]))
        # Set ping
        self.ping_data.setText(str(self.internet_speed[2]))

        ## Set connection data
        self.server_data.setText(str(self.internet_speed[4]))
        self.isp_data.setText(str(self.internet_speed[3]))
        self.counting = False

    def approxCount(self):
        self.counting = True
        for i in range(1, 40):
            if not self.counting:
                self.approx.setText('Done')
                break
            self.approx.setText(str(26-i))
            time.sleep(1)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    win.setStyleSheet(style_sheet)
    print(win.thread.activeThreadCount())
    sys.exit(app.exec_())
    print(win.thread.activeThreadCount())
