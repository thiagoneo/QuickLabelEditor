import os
import zpl
import sys,re
import confighelper
from PyQt5 import QtWidgets as qt
from PyQt5 import QtGui as gui
from PyQt5.QtCore import Qt
from qlabelwindow import Ui_MainWindow as ui
from settings import Ui_Dialog as SettingsDialog

class Window(qt.QMainWindow):

    def __init__(self):

        super(Window,self).__init__()

        self.load_config_file()

        self.ui = ui()
        self.ui.setupUi(self)
        self.setFixedSize(702, 435)

        self.lineCounter = 0
        self.ui.verticalLayout_2.setAlignment(Qt.AlignTop)
        self.add_line_edit()

        self.ui.btnPrint.clicked.connect(self.print_zpl_code)
        self.ui.actionAddLine.triggered.connect(self.add_line_edit)
        self.ui.actionRmLine.triggered.connect(self.remove_line_edit)
        self.ui.actionClearAll.triggered.connect(self.clear_all)
        self.ui.actionRmLine.setDisabled(True)
        self.ui.actionConfigs.triggered.connect(self.settings_dialog)



    def gen_zpl_code(self, text_lines, mini_label):

        self.load_default_settings()

        ajuste_y = int(self.verticalAdj)
        ajuste_x = int(self.horizontalAdj)

        l_height = self.labelHeight
        l_width = self.labelWidth
        l_dpmm = 8
        origin_x = 0
        font='0'
        o = 'N'
        alig = 'L'
        line_width=None
        max_line = 1

        l = zpl.Label(l_height, l_width, l_dpmm)

        if mini_label == True:

            font_height = 4
            font_width = 4

            if len(text_lines) <=4:
                line_spaces = 2.6
                origin_y = 3
            
            else:
                line_spaces = 1
                origin_y = 3

        else:
            line_spaces = 0
            if len(text_lines) == 1:
                font_height = 18
                font_width = 10
                origin_y = 8
            
            elif len(text_lines) == 2:
                font_height = 12
                font_width = 7
                origin_y = 4
            
            elif len(text_lines) == 3:
                font_height = 8
                font_width = 6
                origin_y = 3
            
            elif len(text_lines) == 4:
                font_height = 6
                font_width = 6
                origin_y = 3
            
            elif len(text_lines) == 5:
                font_height = 5
                font_width = 5
                origin_y = 3
        
        origin_y += ajuste_y
        origin_x += ajuste_x
        
        l.origin(origin_x,origin_y)
        l.change_international_font(28)


        for i in range(len(text_lines)):
            l.write_text(text_lines[i], font_height, font_width, font, o, line_width, max_line, alig)
            origin_y += (font_height + line_spaces)
            l.endorigin()
            l.origin(origin_x, origin_y)
        
        return (l.dumpZPL())
    
    def print_zpl_code(self):
        qtd = self.ui.spinQtd.value()
        linhas_texto = []
        mini_label = self.ui.boxMiniEtiqueta.isChecked()
        for i in range(self.lineCounter):
            widget_item = self.ui.verticalLayout_2.itemAt(i)
            widget = widget_item.widget()
            text = widget.text()
            linhas_texto.append(text)
        zplCode = self.gen_zpl_code(linhas_texto,mini_label)
        zplCode = str(zplCode).replace('^FO', '\n^FO')
        zplCode = zplCode.replace('^XZ', '\n^XZ')
        fileName = "/tmp/label.tmp"
        arq = open(fileName, "wt")
        arq.write(zplCode)
        arq.close()
        command = '''file=/tmp/$(hostname)_$(date "+%Y%m%d_%T.6N").zpl  ;\
             cat ''' + fileName + ''' > "${file}" ;\
             lp -h ''' + str(self.host) + ''' -d ''' + str(self.printer) + ''' -n ''' + str(qtd) + ''' "${file}"'''
        #print(zplCode)
        os.system(command)
        
    def add_line_edit(self):
        self.newLineEdit = qt.QLineEdit(self.ui.verticalLayoutWidget)
        self.newLineEdit.setObjectName("lineEdit" + str(self.lineCounter))
        self.ui.verticalLayout_2.addWidget(self.newLineEdit)
        self.lineCounter += 1
        if self.lineCounter >= 5:
            self.ui.actionAddLine.setDisabled(True)
        if self.ui.actionRmLine.isEnabled() == False:
            self.ui.actionRmLine.setEnabled(True)
    
    def remove_line_edit(self):
        self.lineToRemove = self.ui.verticalLayout_2.itemAt(self.lineCounter - 1)
        self.widget = self.lineToRemove.widget()
        self.widget.deleteLater()
        self.lineCounter -= 1
        if self.ui.actionAddLine.isEnabled() == False:
            self.ui.actionAddLine.setEnabled(True)
        if self.lineCounter <= 1:
            self.ui.actionRmLine.setDisabled(True)
    
    def clear_all(self):
        for i in range(self.lineCounter):
            widget_item = self.ui.verticalLayout_2.itemAt(i)
            widget = widget_item.widget()
            widget.clear()
    
    def settings_dialog(self):
        dialog = qt.QDialog()
        dialog.ui = SettingsDialog()
        dialog.ui.setupUi(dialog)
        dialog.setFixedSize(402,407)
        if os.path.isfile(confighelper.local_file):
            config = confighelper.read_config_file()
            labelWidth = config['Label']['width']
            labelHeight = config['Label']['height']
            topMargin = config['Label']['top_margin']
            leftMargin = config['Label']['left_margin']
            host = config['Device']['host']
            printer = config['Device']['printer']
            dialog.ui.spinLabelWidth.setValue(int(labelWidth))
            dialog.ui.spinLabelHeight.setValue(int(labelHeight))
            dialog.ui.spinVerticalAdj.setValue(int(topMargin))
            dialog.ui.spinHorizontalAdj.setValue(int(leftMargin))
            dialog.ui.lineHost.setText(host)
            dialog.ui.linePrinter.setText(printer)
        else:
            dialog.ui.spinLabelWidth.setValue(60)
            dialog.ui.spinLabelHeight.setValue(30)
            dialog.ui.spinVerticalAdj.setValue(3)
            dialog.ui.spinHorizontalAdj.setValue(10)
        dialog.ui.btnSave.accepted.connect(
            lambda: confighelper.write_config_file(
                str(dialog.ui.lineHost.text()),
                str(dialog.ui.linePrinter.text()),
                str(dialog.ui.spinLabelHeight.value()),
                str(dialog.ui.spinLabelWidth.value()),
                str(dialog.ui.spinVerticalAdj.value()),
                str(dialog.ui.spinHorizontalAdj.value())
            )
        )
        dialog.ui.btnSave.accepted.connect(dialog.close)
        dialog.ui.btnSave.accepted.connect(self.show_config_saved_dialog)
        dialog.ui.btnSave.rejected.connect(dialog.close)
        dialog.exec_()
        # dialog.show()

    def load_config_file(self):
        if not os.path.isfile(confighelper.local_file):
            self.settings_dialog()

    def show_config_saved_dialog(self):
        dlg = qt.QMessageBox(self)
        dlg.setWindowTitle("Informação")
        dlg.setIcon(qt.QMessageBox.Information)
        dlg.setText("Configuração salva com sucesso!")
        dlg.exec()
        
    def load_default_settings(self):
        config = confighelper.read_config_file()
        self.host = config['Device']['host']
        self.printer = config['Device']['printer']
        self.labelWidth = config['Label']['width']
        self.labelHeight = config['Label']['height']
        self.verticalAdj = config['Label']['top_margin']
        self.horizontalAdj = config['Label']['left_margin']


# Run Application

app = qt.QApplication([])
application = Window()
application.show()
app.exec()
