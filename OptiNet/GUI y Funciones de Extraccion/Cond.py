from PyQt6.QtWidgets import QMessageBox
import platform
if platform.system() == "Windows":
    from Funciones_windows import Datos, Control_Parental, datos_variantes
else:
    from Funciones_linux import Datos, Control_Parental, datos_variantes
