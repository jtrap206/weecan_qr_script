import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from printing.mock_printer import MockPrinter


def main():

    app = QApplication(sys.argv)

    printer = MockPrinter()

    window = MainWindow(
        printer=printer
    )

    window.setWindowTitle(
        "QR Code Printer"
    )

    window.resize(
        500,
        700
    )

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()


# import sys

# from PySide6.QtCore import Qt
# from PySide6.QtWidgets import(
#     QApplication,
#     QFileDialog,
#     QFormLayout,
#     QGroupBox,
#     QHBoxLayout,
#     QLabel,
#     QLineEdit,
#     QMainWindow,
#     QMessageBox,
#     QPushButton,
#     QSpinBox,
#     QVBoxLayout,
#     QWidget
# )


# class QRPrinterWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
        
#         self.setWindowTitle("WeCan QR Code Printer")
#         self.setMinimumSize(600, 550)
        
#         self.setup_ui()
        
#     def setup_ui(self):
        
#         # Main container
        
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
        
#         main_layout = QVBoxLayout(central_widget)
#         main_layout.setSpacing(20)
        
#         # Title
        
#         title = QLabel("QR CODE PRINTER")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("""
#                             QLabel{
#                               font-size: 24px;
#                               font-weight: bold;
#                               padding: 10px;  
#                             }
#                             """)
        
#         main_layout.addWidget(title)
        
#         # -------------------------------------------------- 
#         # QR DATA SECTION 
#         # --------------------------------------------------
        
#         qr_group = QGroupBox("QR Code")
        
#         qr_layout = QVBoxLayout()
        
#         self.url_input = QLineEdit()
        
#         self.url_input.setPlaceholderText("https://example.com/member/123")
        
#         qr_layout.addWidget(QLabel("QR / URL"))
#         qr_layout.addWidget(self.url_input)
        
#         # CSV button
        
#         csv_button = QPushButton("Import CSV")
        
#         # csv_button.clicked.connect(self.import_cs)
        
#         qr_layout.addWidget(csv_button)
        
#         qr_group.setLayout(qr_layout)
        
#         main_layout.addWidget(qr_group)
        
#         # -------------------------------------------------- 
#         # LABEL DIMENSIONS 
#         # --------------------------------------------------
        
#         label_group = QGroupBox("Physical Label")
        
#         label_layout = QFormLayout()
        
#         self.width_input = QSpinBox()
#         self.width_input.setRange(10, 108)
#         self.width_input.setValue(50)
#         self.width_input.setSuffix(" mm")
        
#         label_layout.addRow(
#             "Width:",
#             self.width_input
#         )
        
#         # Height
#         self.height_input = QSpinBox()
#         self.height_input.setRange(10, 300)
#         self.height_input.setValue(30)
#         self.height_input.setSuffix(" mm")
        
#         label_layout.addRow(
#             "Height:",
#             self.height_input
#         )
        
#         # QR size
#         self.qr_size_input = QSpinBox()
#         self.qr_size_input.setRange(5, 100)
#         self.qr_size_input.setValue(25)
#         self.qr_size_input.setSuffix(" mm")
                
#         label_layout.addRow(
#             "QR Size:",
#             self.qr_size_input
#         )
        
#         label_group.setLayout(label_layout)
#         main_layout.addWidget(label_group)
        
#         # -------------------------------------------------- 
#         # PRINT SETTINGS 
#         # --------------------------------------------------
        
#         print_group = QGroupBox("Print Settings")
#         print_layout = QFormLayout()
        
#         # Quantity
#         self.quantity_input = QSpinBox()
#         self.quantity_input.setRange(1, 100000)
#         self.quantity_input.setValue(1)
        
#         print_layout.addRow( 
#             "Quantity:", 
#             self.quantity_input 
#         )
        
#         # Printer
#         self.printer_input = QLineEdit()
#         self.printer_input.setText("Xprinter XP-470B")
        
#         print_layout.addRow( 
#             "Printer:", 
#             self.printer_input
#         )
        
#         print_group.setLayout(print_layout) 
#         main_layout.addWidget(print_group)
        
#         # -------------------------------------------------- 
#         # BUTTONS 
#         # --------------------------------------------------
        
#         button_layout = QHBoxLayout()
#         preview_button = QPushButton("Preview")
        
#         preview_button.clicked.connect(
#             self.preview
#         )
        
#         print_button = QPushButton("PRINT")
        
#         print_button.clicked.connect( 
#             self.print_qr 
#         )
        
#         print_button.setStyleSheet(""" 
#             QPushButton { 
#                 background-color: #14144f; 
#                 color: white; 
#                 font-size: 16px; 
#                 font-weight: bold; 
#                 padding: 12px; 
#                 border-radius: 8px; 
#             } 
            
#             QPushButton:hover { 
#                 background-color: #24246f; 
#             } 
#         """) 
        
#         button_layout.addWidget(preview_button) 
#         button_layout.addWidget(print_button) 
#         main_layout.addLayout(button_layout)
        
#         # -------------------------------------------------- 
#         # STATUS 
#         # -------------------------------------------------- 
        
#         self.status_label = QLabel("Status: Ready") 
        
#         self.status_label.setStyleSheet(""" 
#             QLabel { 
#                 padding: 10px; 
#                 font-size: 14px; 
#             } 
#         """) 
        
#         main_layout.addWidget(self.status_label)
        
#     # ------------------------------------------------------
#     # CSV IMPORT
#     # ------------------------------------------------------
#     def import_csv(self):
#         file_path, _ = QFileDialog.getOpenFileName(
#             self,
#             "Select CSV File",
#             "",
#             "CSV Files (*.csv)"
#         )

#         if file_path:
#             self.status_label.setText(
#                 f"CSV selected: {file_path}"
#             )

#             QMessageBox.information(
#                 self,
#                 "CSV Selected",
#                 "CSV file selected successfully.\n\n"
#                 "We will connect the CSV data to the "
#                 "printing system later."
#             )

#     # ------------------------------------------------------
#     # PREVIEW
#     # ------------------------------------------------------
#     def preview(self):
#         url = self.url_input.text()

#         width = self.width_input.value()
#         height = self.height_input.value()
#         qr_size = self.qr_size_input.value()

#         if not url:
#             QMessageBox.warning(
#                 self,
#                 "Missing URL",
#                 "Please enter a URL for the QR code."
#             )
#             return

#         QMessageBox.information(
#             self,
#             "Print Preview",
#             f"URL:\n{url}\n\n"
#             f"Label: {width} × {height} mm\n"
#             f"QR Size: {qr_size} mm"
#         )

#     def print_qr(self):
#         url = self.url_input.text()
#         quantity = self.quantity_input.value()
        
#         if not url: 
#             QMessageBox.warning( 
#                 self, "Missing URL", 
#                 "Please enter a URL before printing." 
#             ) 
#             return
        
#         self.status_label.setText( 
#             f"Ready to print {quantity} QR code(s)..." 
#         )
        
#         QMessageBox.information( 
#             self, "Printing", 
#             f"Printing {quantity} QR code(s).\n\n" 
#             f"URL:\n{url}\n\n" 
#             "Xprinter communication will be added next." 
#         )

        



# # ---------------------------------------------------------- 
# # APPLICATION ENTRY POINT 
# # ----------------------------------------------------------

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     window = QRPrinterWindow()
    
#     window.show()
    
#     sys.exit(app.exec())