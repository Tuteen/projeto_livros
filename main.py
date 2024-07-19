from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from controller import AppController


if __name__ == "__main__":
    app = QApplication([])
    pixmap = QPixmap("logotipo.png")  # Substitua com o caminho correto para o seu logotipo
    pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Redimensionar o pixmap
    splash = QSplashScreen(pixmap)
    splash.setWindowOpacity(0)  # Iniciar com janela transparente
    splash.show()

    # Efeito de fade-in
    for opacity in range(1, 11):  # 10 passos de fade-in
        QTimer.singleShot(opacity * 100, lambda op=opacity: splash.setWindowOpacity(op * 0.1))
        QApplication.processEvents()

    def start_app():
        splash.close()  # Fechar a splash screen
        controller = AppController(app)  # Passar a instância de QApplication para o controlador
        controller.start()

    QTimer.singleShot(3000, start_app)  # Iniciar o app após 3 segundos

    app.exec()
