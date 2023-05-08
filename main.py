
# Author    : Mustafa ERGUL
# Program   : MQTT APP

import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QPlainTextEdit
import time
from paho import mqtt
import paho.mqtt.client as mqtt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = None
        self.resize(600, 400)

        # IP ve Port Kısmı
        self.ip_edit = QLineEdit()
        self.ip_edit.setFont(QFont('Arial', 12))
        self.ip_edit.setText("192.168.1.41")
        self.port_edit = QLineEdit()
        self.port_edit.setFont(QFont('Arial', 12))
        self.port_edit.setText("1883")
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFont(QFont('Arial', 12))
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setFont(QFont('Arial', 12))

        # QPlainTextEdit widget'ı oluştur
        self.message_log = QPlainTextEdit(self)
        self.message_log.setReadOnly(True)
        self.message_log.setFont(QFont('Arial', 12))
        self.message_log.setGeometry(20, 150, 550, 200)

        # Topic Kısmı
        self.topic_edit = QLineEdit()
        self.topic_edit.setText("GenISys")
        self.topic_edit.setFont(QFont('Arial', 12))

        # Publisher Kısmı
        self.file_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.publish_button = QPushButton("Publish")
        self.browse_button.setFont(QFont('Arial', 12))
        self.publish_button.setFont(QFont('Arial', 12))

        # Sysyem Information
        self.cpu_label = QLineEdit()
        self.cpu_label.setReadOnly(True)
        self.cpu_label.setFont(QFont('Arial', 12))
        self.xtal_label = QLineEdit()
        self.xtal_label.setReadOnly(True)
        self.xtal_label.setFont(QFont('Arial', 12))
        self.apb_label = QLineEdit()
        self.apb_label.setReadOnly(True)
        self.apb_label.setFont(QFont('Arial', 12))


        # Layoutları ayarlayalım
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("IP:"))
        conf_layout.addWidget(self.ip_edit)
        conf_layout.addWidget(QLabel("Port:"))
        conf_layout.addWidget(self.port_edit)


        connect_layout = QHBoxLayout()
        connect_layout.addWidget(self.connect_button)
        connect_layout.addWidget(self.disconnect_button)

        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("Topic:"))
        topic_layout.addWidget(self.topic_edit)

        publisher_layout = QHBoxLayout()
        publisher_layout.addWidget(QLabel("File Path:"))
        publisher_layout.addWidget(self.file_path_edit)
        publisher_layout.addWidget(self.browse_button)
        publisher_layout.addWidget(self.publish_button)

        system_layout = QHBoxLayout()
        system_layout.addWidget(QLabel("CPU:"))
        system_layout.addWidget(self.cpu_label)
        system_layout.addWidget(QLabel("XTAL:"))
        system_layout.addWidget(self.xtal_label)
        system_layout.addWidget(QLabel("APB:"))
        system_layout.addWidget(self.apb_label)

        message_layout = QVBoxLayout()
        message_layout.addWidget(self.message_log)

        main_layout = QVBoxLayout()
        main_layout.addLayout(conf_layout)
        main_layout.addLayout(connect_layout)
        main_layout.addLayout(topic_layout)
        main_layout.addLayout(publisher_layout)
        main_layout.addLayout(message_layout)
        main_layout.addLayout(system_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Sinyalleri bağlayalım
        self.connect_button.clicked.connect(self.connect_to_broker)
        self.disconnect_button.clicked.connect(self.disconnect_from_broker)
        self.browse_button.clicked.connect(self.browse_file)
        self.publish_button.clicked.connect(self.publish_file)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.message_log.appendPlainText("Connected to MQTT broker")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            topic = self.topic_edit.text()
            self.client.subscribe(topic)
            time.sleep(1)
            topic = "CPU"
            self.client.subscribe(topic)
            time.sleep(1)
            topic = "XTAL"
            self.client.subscribe(topic)
            time.sleep(1)
            topic = "APB"
            self.client.subscribe(topic)
            time.sleep(1)
        else:
            self.message_log.appendPlainText(f"Connection failed with error code {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc == 0:
            self.message_log.appendPlainText("Disconnected from broker")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
        else:
            self.message_log.appendPlainText(f"Disconnection failed with error code {rc}")

    def connect_to_broker(self):
        ip = self.ip_edit.text()
        port = int(self.port_edit.text())

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        try:
            self.client.connect(ip, port)
            self.message_log.appendPlainText(f"Broker IP: {ip}, Port: {port}")
            self.client.loop_start()
            #self.message_log.appendPlainText(f"Subscribed to topic: {topic}")
            time.sleep(2)
        except ConnectionRefusedError:
            self.message_log.appendPlainText("Bağlantı hatası: Broker'a bağlanılamıyor.")
            return

    def disconnect_from_broker(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.client.on_disconnect = self.on_disconnect
            self.client = None

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_path:
            self.file_path_edit.setText(file_path)

    def publish_file(self):
        file_path = self.file_path_edit.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a file.")
            return

        try:
            with open(file_path, "rb") as f:
                image_bytes = bytearray(f.read())
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        topic = self.topic_edit.text()
        if not topic:
            QMessageBox.warning(self, "Error", "Please enter a topic.")
            return

        if self.client:
            result, _ = self.client.publish(topic, payload=image_bytes, qos=0)
            if result == mqtt.MQTT_ERR_SUCCESS:
                QMessageBox.information(self, "Success", "File published successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to publish file.")
        else:
            QMessageBox.warning(self, "Error", "Not connected to broker.")

    def on_message(self, client, userdata, msg):
        #message = f"{msg.topic}: {msg.payload.decode()}\n"
        # QPlainTextEdit widget'ına mesajı ekle
        if f"{msg.topic}" == "CPU":
            self.cpu_label.setText(f"{msg.payload.decode()} MHz")
        elif f"{msg.topic}" == "XTAL":
            self.xtal_label.setText(f"{msg.payload.decode()} MHz")
        elif f"{msg.topic}" == "APB":
            self.apb_label.setText(f"{msg.payload.decode()} Hz")
        elif f"{msg.topic}" == "GenISys":
            self.message_log.appendPlainText(f"Submitted Photo : {msg.payload}\n")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setApplicationName('MQTT App by Mustafa Ergül')
    window.show()
    sys.exit(app.exec_())
