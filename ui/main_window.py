from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QListWidget,
    QHBoxLayout,
    QProgressBar,
    QMessageBox,
    QGroupBox,
)

from qr.generator import generate_qr as create_qr_pixmap
from printing.printer import Printer
from printing.csv_loader import load_urls_from_csv, BulkItem

def apply_styles(self):
    self.setStyleSheet("""
        QWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-family: "Segoe UI", "SF Pro Text", sans-serif;
            font-size: 13px;
        }

        QGroupBox {
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 10px;
            margin-top: 14px;
            padding: 12px 10px 10px 10px;
            font-weight: 600;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: #a6adc8;
        }

        QLabel {
            color: #a6adc8;
            font-weight: 500;
        }

        QLineEdit, QSpinBox {
            background-color: #11111b;
            border: 1px solid #313244;
            border-radius: 8px;
            padding: 8px 10px;
            color: #cdd6f4;
            selection-background-color: #89b4fa;
        }
        QLineEdit:focus, QSpinBox:focus {
            border: 1px solid #89b4fa;
        }

        QPushButton {
            background-color: #313244;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            color: #cdd6f4;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #45475a;
        }
        QPushButton:pressed {
            background-color: #585b70;
        }
        QPushButton:disabled {
            background-color: #181825;
            color: #6c7086;
        }

        /* Primary actions */
        QPushButton#generateBtn {
            background-color: #89b4fa;
            color: #1e1e2e;
        }
        QPushButton#generateBtn:hover {
            background-color: #b4befe;
        }

        QPushButton#printBtn, QPushButton#printAllBtn {
            background-color: #a6e3a1;
            color: #1e1e2e;
        }
        QPushButton#printBtn:hover, QPushButton#printAllBtn:hover {
            background-color: #94e2d5;
        }

        QPushButton#cancelBtn {
            background-color: #f38ba8;
            color: #1e1e2e;
        }
        QPushButton#cancelBtn:hover {
            background-color: #eba0ac;
        }

        QListWidget {
            background-color: #11111b;
            border: 1px solid #313244;
            border-radius: 8px;
            padding: 4px;
            outline: none;
        }
        QListWidget::item {
            padding: 6px 8px;
            border-radius: 4px;
        }
        QListWidget::item:selected {
            background-color: #313244;
        }

        QProgressBar {
            background-color: #11111b;
            border: 1px solid #313244;
            border-radius: 6px;
            text-align: center;
            color: #cdd6f4;
            height: 18px;
        }
        QProgressBar::chunk {
            background-color: #a6e3a1;
            border-radius: 5px;
        }

        QLabel#previewLabel {
            background-color: #ffffff;
            border: 1px solid #313244;
            border-radius: 12px;
            padding: 8px;
        }
    """)


# ─────────────────────────────────────────────
# Bulk print worker (runs on a background thread)
# ─────────────────────────────────────────────
class BulkPrintWorker(QThread):
    progress = Signal(int, int, str)   # current, total, data
    finished_ok = Signal(int)          # printed count
    failed = Signal(str)

    def __init__(
        self,
        printer: Printer,
        items: list[BulkItem],
        width_mm: float,
        height_mm: float,
        qr_size_mm: float,
    ):
        super().__init__()
        self.printer = printer
        self.items = items
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.qr_size_mm = qr_size_mm
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        total = len(self.items)
        printed = 0
        try:
            for i, item in enumerate(self.items, start=1):
                if self._cancel:
                    break
                self.progress.emit(i, total, item.data)
                self.printer.print_qr(
                    data=item.data,
                    width_mm=self.width_mm,
                    height_mm=self.height_mm,
                    qr_size_mm=self.qr_size_mm,
                    quantity=item.quantity,
                )
                printed += 1
            self.finished_ok.emit(printed)
        except Exception as e:
            self.failed.emit(str(e))


# ─────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────
class MainWindow(QWidget):

    def __init__(self, printer: Printer):
        super().__init__()

        self.printer = printer
        self._bulk_items: list[BulkItem] = []
        self._worker: BulkPrintWorker | None = None

        self.setup_ui()

    def setup_ui(self):
        _setup_ui(self)


def _setup_ui(self):
    self.setWindowTitle("QR Code Printer")
    self.resize(780, 720)

    # ── Left: Preview ──────────────────────────────────────
    preview_group = QGroupBox("Preview")
    preview_layout = QVBoxLayout(preview_group)

    self.preview_label = QLabel("QR preview will appear here")
    self.preview_label.setObjectName("previewLabel")
    self.preview_label.setMinimumSize(280, 280)
    self.preview_label.setAlignment(Qt.AlignCenter)
    self.preview_label.setScaledContents(True)

    preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
    preview_layout.addStretch()

    # ── Right: Controls ────────────────────────────────────
    controls = QVBoxLayout()
    controls.setSpacing(10)

    # URL + Generate
    url_group = QGroupBox("QR Data")
    url_layout = QVBoxLayout(url_group)

    self.url_input = QLineEdit()
    self.url_input.setPlaceholderText("Enter URL or any text for the QR code")

    self.generate_button = QPushButton("Generate QR")
    self.generate_button.setObjectName("generateBtn")

    url_layout.addWidget(QLabel("URL / Data"))
    url_layout.addWidget(self.url_input)
    url_layout.addWidget(self.generate_button)

    # Dimensions
    dims_group = QGroupBox("Label Settings")
    dims_layout = QVBoxLayout(dims_group)

    self.width_input = QSpinBox()
    self.width_input.setRange(10, 108)
    self.width_input.setValue(50)
    self.width_input.setSuffix(" mm")

    self.height_input = QSpinBox()
    self.height_input.setRange(10, 300)
    self.height_input.setValue(30)
    self.height_input.setSuffix(" mm")

    self.qr_size_input = QSpinBox()
    self.qr_size_input.setRange(5, 100)
    self.qr_size_input.setValue(25)
    self.qr_size_input.setSuffix(" mm")

    self.quantity_input = QSpinBox()
    self.quantity_input.setRange(1, 100000)
    self.quantity_input.setValue(1)

    # Compact 2-column grid for spinboxes
    from PySide6.QtWidgets import QFormLayout
    form = QFormLayout()
    form.setSpacing(8)
    form.addRow("Label Width", self.width_input)
    form.addRow("Label Height", self.height_input)
    form.addRow("QR Size", self.qr_size_input)
    form.addRow("Quantity", self.quantity_input)
    dims_layout.addLayout(form)

    self.print_button = QPushButton("PRINT")
    self.print_button.setObjectName("printBtn")
    dims_layout.addWidget(self.print_button)

    # Bulk
    bulk_group = QGroupBox("Bulk print from CSV")
    bulk_layout = QVBoxLayout(bulk_group)

    self.load_csv_button = QPushButton("Load CSV…")
    self.bulk_status = QLabel("No CSV loaded")
    self.bulk_list = QListWidget()
    self.bulk_list.setMaximumHeight(110)

    self.progress_bar = QProgressBar()
    self.progress_bar.setVisible(False)

    bulk_btn_row = QHBoxLayout()
    self.print_all_button = QPushButton("Print All")
    self.print_all_button.setObjectName("printAllBtn")
    self.print_all_button.setEnabled(False)

    self.cancel_bulk_button = QPushButton("Cancel")
    self.cancel_bulk_button.setObjectName("cancelBtn")
    self.cancel_bulk_button.setEnabled(False)

    bulk_btn_row.addWidget(self.print_all_button)
    bulk_btn_row.addWidget(self.cancel_bulk_button)

    bulk_layout.addWidget(self.load_csv_button)
    bulk_layout.addWidget(self.bulk_status)
    bulk_layout.addWidget(self.bulk_list)
    bulk_layout.addWidget(self.progress_bar)
    bulk_layout.addLayout(bulk_btn_row)

    # Assemble right column
    controls.addWidget(url_group)
    controls.addWidget(dims_group)
    controls.addWidget(bulk_group)
    controls.addStretch()

    # ── Main horizontal layout ─────────────────────────────
    main = QHBoxLayout()
    main.setContentsMargins(16, 16, 16, 16)
    main.setSpacing(16)
    main.addWidget(preview_group, stretch=2)
    main.addLayout(controls, stretch=3)

    self.setLayout(main)

    apply_styles(self)

    # ── Single print ───────────────────────────────────────
    def generate_qr(self):
        data = self.url_input.text().strip()
        if not data:
            return

        qr_pixmap = create_qr_pixmap(data)
        self.preview_label.setPixmap(qr_pixmap)

    def print_qr(self):
        data = self.url_input.text().strip()
        if not data:
            return

        self.printer.print_qr(
            data=data,
            width_mm=self.width_input.value(),
            height_mm=self.height_input.value(),
            qr_size_mm=self.qr_size_input.value(),
            quantity=self.quantity_input.value(),
        )

    # ── Bulk print ─────────────────────────────────────────
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV with QR URLs",
            "",
            "CSV files (*.csv);;All files (*)",
        )
        if not path:
            return

        try:
            items = load_urls_from_csv(path)
        except Exception as e:
            QMessageBox.critical(self, "CSV error", f"Could not read CSV:\n{e}")
            return

        if not items:
            QMessageBox.warning(self, "Empty CSV", "No valid URLs found in the file.")
            return

        self._bulk_items = items
        self.bulk_list.clear()

        for item in items[:50]:
            suffix = f"  ×{item.quantity}" if item.quantity > 1 else ""
            self.bulk_list.addItem(item.data + suffix)

        if len(items) > 50:
            self.bulk_list.addItem(f"… and {len(items) - 50} more")

        total_labels = sum(i.quantity for i in items)
        self.bulk_status.setText(
            f"Loaded {len(items)} rows  ({total_labels} labels)  —  {Path(path).name}"
        )
        self.print_all_button.setEnabled(True)

    def print_all(self):
        if not self._bulk_items:
            return

        if self._worker and self._worker.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self._bulk_items))
        self.print_all_button.setEnabled(False)
        self.load_csv_button.setEnabled(False)
        self.cancel_bulk_button.setEnabled(True)

        self._worker = BulkPrintWorker(
            printer=self.printer,
            items=self._bulk_items,
            width_mm=self.width_input.value(),
            height_mm=self.height_input.value(),
            qr_size_mm=self.qr_size_input.value(),
        )
        self._worker.progress.connect(self._on_bulk_progress)
        self._worker.finished_ok.connect(self._on_bulk_finished)
        self._worker.failed.connect(self._on_bulk_failed)
        self._worker.start()

    def cancel_bulk(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self.bulk_status.setText("Cancelling…")

    def _on_bulk_progress(self, current: int, total: int, data: str):
        self.progress_bar.setValue(current)
        self.bulk_status.setText(f"Printing {current}/{total}: {data[:60]}…")

    def _on_bulk_finished(self, printed: int):
        self.progress_bar.setVisible(False)
        self.print_all_button.setEnabled(True)
        self.load_csv_button.setEnabled(True)
        self.cancel_bulk_button.setEnabled(False)
        self.bulk_status.setText(f"Done — printed {printed} item(s)")
        QMessageBox.information(
            self, "Bulk print", f"Successfully printed {printed} item(s)."
        )

    def _on_bulk_failed(self, message: str):
        self.progress_bar.setVisible(False)
        self.print_all_button.setEnabled(True)
        self.load_csv_button.setEnabled(True)
        self.cancel_bulk_button.setEnabled(False)
        QMessageBox.critical(self, "Print error", message)

    self.generate_button.clicked.connect(
        lambda checked=False: generate_qr(self)
    )
    self.print_button.clicked.connect(
        lambda checked=False: print_qr(self)
    )
    self.load_csv_button.clicked.connect(
        lambda checked=False: load_csv(self)
    )
    self.print_all_button.clicked.connect(
        lambda checked=False: print_all(self)
    )
    self.cancel_bulk_button.clicked.connect(
        lambda checked=False: cancel_bulk(self)
    )