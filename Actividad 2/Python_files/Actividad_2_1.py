import sys
from igmp2 import Ui_MainWindow
import serial
import time
from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import convolve2d

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args,*kwargs)
        self.setupUi(self)

        arduino = 0
        
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.leer_puerto_serial)
        self.timer2.setInterval(10)
        self.timer2.start()

        self.N = 100
        self.grid = np.random.choice([0, 1], self.N*self.N, p=[0.8, 0.2]).reshape(self.N, self.N)
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_game)
        self.timer.start()

        # Establecer valores mínimo y máximo
        self.verticalSlider.setMinimum(0)
        self.verticalSlider.setMaximum(100)

        self.temp.clicked.connect(self.actualizar_temperatura)

        # Configurar la comunicación serial con Arduino
        self.serial_port = serial.Serial('COM4', 9600, timeout=0)  # Ajustar el puerto serial según corresponda
        time.sleep(1)  # Esperar a que se establezca la conexión

        # Llamado de los botones de la interfaz
        self.bomba_atomica.clicked.connect(self.b_atomica)
        self.bomba_vida.clicked.connect(self.b_sanadora)

    def paintEvent(self, event):
        cell_width = self.width() // self.N
        cell_height = self.height() // self.N

        image = QImage(self.width(), self.height(), QImage.Format.Format_RGB32)
        painter = QPainter(image)

        for i in range(self.N):
            for j in range(self.N):
                color = QColor(0, 0, 0) if self.grid[i][j] == 0 else QColor(255, 255, 255)
                painter.fillRect(i * cell_width, j * cell_height, cell_width, cell_height, color)

        painter.end()

        pixmap = QPixmap.fromImage(image)
        self.label_juego.setPixmap(pixmap)

    def update_game(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        
        convolved = convolve2d(self.grid, kernel, mode='same', boundary='wrap')
        
        birth = (convolved == 3) & (self.grid == 0)
        survive = ((convolved == 2) | (convolved == 3)) & (self.grid == 1)
        
        self.grid[:, :] = 0
        self.grid[birth | survive] = 1
        
        # Contar la cantidad de células vivas
        alive_cells = np.sum(self.grid)

        # Imprimir las células vivas en consola
        print("Número de células vivas:", alive_cells)

        # Enviar comandos a Arduino según el número de células vivas
        if alive_cells >= 1000:
            self.serial_port.write(b'E')  # Envía el comando para el color azul
        elif 600 <= alive_cells <= 999:
            self.serial_port.write(b'S')  # Envía el comando para el color verde
        else:
            self.serial_port.write(b'A')  # Envía el comando para el color rojo

        self.update()

    def closeEvent(self, event):
        # Cerrar el puerto serial al cerrar la aplicación
        self.serial_port.close()
        event.accept()

    def reiniciar_programa(self):
        print("El botón de reinicio fue presionado")
        self.N = 100
        self.grid = np.random.choice([0, 1], self.N*self.N, p=[0.8, 0.2]).reshape(self.N, self.N)

        self.timer.start()

    def b_sanadora(self):
        print("Enviando bomba sanadora")
    
        x = np.random.randint(0, self.N - 21)
        y = np.random.randint(0, self.N - 21)

        for i in range(x, x + 21):
            for j in range(y, y + 21):
                if self.grid[i, j] == 0:
                    self.grid[i, j] = 1


    def b_atomica(self):
        print("Enviando bomba atómica")

        x = np.random.randint(0, self.N - 21)
        y = np.random.randint(0, self.N - 21)

        for i in range(x, x + 21):
            for j in range(y, y + 21):
                if self.grid[i, j] == 1:
                    self.grid[i, j] = 0

    def actualizar_temperatura(self):
        # Obtener el valor actual del slider
        valor_slider = self.verticalSlider.value()
        arduino = 0
        
        # Convertir el valor del slider a una cadena de texto
        temperatura_texto = 'Temp = ' + str(valor_slider) + '°C'
        
        # Establecer la nueva temperatura en el QLabel
        self.label_temp.setText(temperatura_texto)

    def leer_puerto_serial(self):
        # Leer los datos del puerto serial
        mensaje = self.serial_port.readline().strip().decode('utf-8')
        
        # Si se recibe el mensaje de reinicio desde Arduino, reiniciar el programa
        if mensaje == "Reiniciar":
            print("Mensaje de reinicio recibido")  # Impresión de verificación
            self.reiniciar_programa()  # Llamar a la función para reiniciar el programa

        if mensaje == "b-0":
            print("Mensaje de Bomba sanadora recivido")  # Impresión de verificación
            self.b_sanadora()

        if mensaje == "a-0":
            print("Mensaje de Bomba atómica recivido")  # Impresión de verificación
            self.b_atomica()

        if mensaje.startswith('t-'):
            temperatura = float(mensaje[2:])  # Extrae la temperatura de la línea recibida y conviértela a flotante
            print("Temperatura recibida:", temperatura)

            temperatura_t = 'temp =' + str( temperatura) + '°C'
            self.label_temp.setText(temperatura_t)

            if temperatura < 26:
                print("¡Hace frío!")
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowTitle("Juego de la Vida de Conway")
    app.exec()