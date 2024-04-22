import sys
import serial
import time
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
import numpy as np
from scipy.signal import convolve2d
from igmp2 import Ui_MainWindow
import playsound
import threading


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args,*kwargs)
        self.setupUi(self)
        self.temperatura = 25

        self.audio_end = "C:\\Users\\RW Productions\\Desktop\\Universidad\\2024\\Semestre 1\\TIC 2\\MP1\\Actividad_2\\Mozart_Lacrimosa.mp3"

        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.leer_puerto_serial)
        self.timer2.setInterval(10)
        self.timer2.start()

        self.N = 100
        self.grid = np.random.choice([0, 100], (self.N, self.N), p=[0.8, 0.2])

        self.timer = QTimer(self)
        self.timer.setInterval(100)
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

        self.v_temp = True
        self.cancion_reproduciendo = False

    def paintEvent(self, event):
        cell_width = self.width() // self.N
        cell_height = self.height() // self.N

        image = QImage(self.width(), self.height(), QImage.Format.Format_RGB32)
        painter = QPainter(image)

        for i in range(self.N):
            for j in range(self.N):
                life = self.grid[i][j]
                color = self.life_to_color(life)
                painter.fillRect(i * cell_width, j * cell_height, cell_width, cell_height, color)

        painter.end()

        pixmap = QPixmap.fromImage(image)
        self.label_juego.setPixmap(pixmap)

    def life_to_color(self, life):
        if 1 <= life <= 50:
            return QColor(255, 0, 0)  # Rojo si la vida es menor o igual a 10
        elif 51 <= life <= 100:
            return QColor(0, 255, 0)
        elif life == 0:
            return QColor(0, 0, 0)  # Negro para las células muertas
        else:
            return QColor(0, 0, 0)  # Blanco para cualquier otro caso

    def update_game(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])

        if self.temperatura > 27:  # Humbral de calor
            self.grid = self.grid - 34  # debe ser 30
            self.grid = np.where((self.grid < 0), 0, self.grid)

        if self.temperatura < 20:  # Humbral de frio
            self.grid = self.grid + 10
            self.grid = np.where((self.grid < 0), 0, self.grid)
            self.grid = np.where((self.grid > 100), 100, self.grid)

        convolved = convolve2d(self.grid > 0, kernel, mode='same', boundary='wrap')

        new_grid = np.where((self.grid > 0) & ((convolved < 2) | (convolved > 3)), self.grid - 30, self.grid)
        new_grid = np.where((self.grid == 0) & (convolved == 3), 100, new_grid)
        new_grid = np.where((new_grid < 0), 0, new_grid)
        self.grid = np.where((self.grid > 100), 100, self.grid)

        self.grid = new_grid

        # Contar el número de células vivas en la nueva matriz
        alive_cells = np.count_nonzero(self.grid)

        # Mostrar el número de células vivas
        print("Número de células vivas:", alive_cells)

        # Enviar comandos a Arduino según el número de células vivas
        if alive_cells >= 1000:
            self.serial_port.write(b'E')  # Envía el comando para el color azul
        elif 600 <= alive_cells <= 999:
            self.serial_port.write(b'S')  # Envía el comando para el color verde
        else:
            self.serial_port.write(b'A')  # Envía el comando para el color rojo

        if alive_cells == 0 and not self.cancion_reproduciendo:
            self.cancion_reproduciendo = True
            threading.Thread(target=self.muerte).start()

        if alive_cells > 1:
            self.cancion_reproduciendo = False
            threading.Thread(target=self.test).start()

        self.dato_muerte = alive_cells

        self.update()

    def muerte(self):
        if self.cancion_reproduciendo:
            playsound.playsound(self.audio_end)

        if self.dato_muerte > 1 and self.cancion_reproduciendo == True:
            # Detén la reproducción del audio
            playsound.playsound(None)

            self.cancion_reproduciendo = False

    def test(self):
        if self.dato_muerte > 1 and self.cancion_reproduciendo == True:
            # Detén la reproducción del audio
            playsound.playsound(None)

            self.cancion_reproduciendo = False


    def leer_puerto_serial(self):
        # Leer los datos del puerto serial
        mensaje = self.serial_port.readline().strip().decode('utf-8')
        #print("hola xd")

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
            #self.temperatura = float(mensaje[2:])  # Extrae la temperatura de la línea recibida y conviértela a flotante
            #print("Temperatura recibida:", self.temperatura)

            if self.v_temp == True:
                self.temperatura = float(mensaje[2:])  # Extrae la temperatura de la línea recibida y conviértela a flotante
                print("Temperatura recibida:", self.temperatura)
                temperatura_t = 'temp =' + str(self.temperatura) + '°C'
                self.label_temp.setText(temperatura_t)

            if self.v_temp == False:
                self.temperatura = self.verticalSlider.value()
                # Obtener el valor actual del slider
                valor_slider = self.verticalSlider.value()
                self.verticalSlider.valueChanged.connect(self.cambiar_temp_xd)

                # Convertir el valor del slider a una cadena de texto
                temperatura_texto = 'Temp = ' + str(valor_slider) + '°C'

                # Establecer la nueva temperatura en el QLabel
                self.label_temp.setText(temperatura_texto)

    def cambiar_temp_xd(self, value):

        self.temperatura = value
        self.label_temp.setText(str(self.temperatura))

    def reiniciar_programa(self):
        print("El botón de reinicio fue presionado")
        self.N = 100
        self.grid = np.random.choice([0, 100], (self.N, self.N), p=[0.8, 0.2])
        self.timer.start()

    def b_sanadora(self):
        print("Enviando bomba sanadora")

        x = np.random.randint(0, self.N - 21)
        y = np.random.randint(0, self.N - 21)

        for i in range(x, x + 21):
            for j in range(y, y + 21):
                if self.grid[i, j] == 0:
                    self.grid[i, j] = 70
                elif 1 <= self.grid[i, j] <= 50:
                    self.grid[i, j] = self.grid[i, j] + 50
                else:
                    self.grid[i, j] = 100

    def b_atomica(self):
        print("Enviando bomba atómica")

        x = np.random.randint(0, self.N - 21)
        y = np.random.randint(0, self.N - 21)

        for i in range(x, x + 21):
            for j in range(y, y + 21):
                if 0 <= self.grid[i, j] <= 100:
                    self.grid[i, j] = 0

    def actualizar_temperatura(self):
        self.v_temp = not self.v_temp

    def closeEvent(self, event):
        # Detener la reproducción del audio antes de cerrar la ventana
        if self.cancion_reproduciendo:
            playsound.playsound(None)
        
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowTitle("Juego de la Vida de Conway")
    app.exec()
