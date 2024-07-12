import sys
import os
import datetime
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QCheckBox,
    QTableWidgetItem,
    QMenu,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon


basedir = os.path.dirname(__file__)


def load_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data


class TableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def find_logo(self, directory, logo_name):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == logo_name.lower():
                    return os.path.join(root, file)
        return None

    def initUI(self):
        self.setWindowTitle("D&S *.par File Generator")
        # Adjusted window size to 675x600 pixels
        self.setGeometry(100, 100, 675, 600)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        layout = QVBoxLayout()
        centralWidget.setLayout(layout)

        # Create the table
        self.table = QTableWidget()
        self.table.setRowCount(127)
        # 6 visible columns + 1 hidden column for lock bit
        self.table.setColumnCount(7)

        # Set headers
        headers = ["BK-M-K", "BK-2M-K", "BK-2DO",
                   "BK-2DI", "BK-4DO", "BK-4DI", "Lock"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnHidden(6, True)  # Hide the lock column

        # Center headers
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.header_menu)

        # Center headers
        for col in range(6):  # Only center the first 6 headers
            header_item = self.table.horizontalHeaderItem(col)
            header_item.setTextAlignment(Qt.AlignCenter)

        # Fill the table with checkboxes
        for row in range(self.table.rowCount()):
            for col in range(6):  # Only add checkboxes to the first 6 columns
                if row == 126 and col > 1:
                    continue
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(
                    lambda state, r=row, c=col: self.checkbox_state_changed(
                        state, r, c)
                )
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout()
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(5, 5, 5, 5)
                checkbox_widget.setLayout(checkbox_layout)
                self.table.setCellWidget(row, col, checkbox_widget)

            # Initialize the lock bit to 0
            lock_item = QTableWidgetItem("0")
            self.table.setItem(row, 6, lock_item)

        layout.addWidget(self.table)

        layout.addWidget(self.table)

        # Add save, load, and deselect all buttons
        actionButtonLayout = QHBoxLayout()

        self.saveButton = QPushButton("Save")
        self.saveButton.setIcon(
            QIcon(os.path.join(basedir, "icons", "speichern.png")))
        self.saveButton.clicked.connect(self.save_state)
        actionButtonLayout.addWidget(self.saveButton)

        self.loadButton = QPushButton("Load Data")
        self.loadButton.setIcon(
            QIcon(os.path.join(basedir, "icons", "ordner-speichern.png")))
        self.loadButton.clicked.connect(self.load_state)
        actionButtonLayout.addWidget(self.loadButton)

        self.deselectAllButton = QPushButton("Clean")
        self.deselectAllButton.setIcon(
            QIcon(os.path.join(basedir, "icons", "loschen.png")))
        self.deselectAllButton.clicked.connect(self.deselect_all)
        actionButtonLayout.addWidget(self.deselectAllButton)

        layout.addLayout(actionButtonLayout)

    def header_menu(self, index):
        menu = QMenu(self)
        select_all_action = menu.addAction("Select All")

        action = menu.exec_(QCursor.pos())
        if action == select_all_action:
            self.select_all(index)

    def checkbox_state_changed(self, state, row, col):
        if state == Qt.Checked:
            self.lock_checkboxes(row, col)
        else:
            self.unlock_checkboxes(row, col)

    def lock_checkboxes(self, row, col):
        # Lock the current row
        lock_item = self.table.item(row, 6)
        lock_item.setText("1")

        # Lock all other checkboxes in the same row
        for c in range(6):
            if c != col:
                checkbox_widget = self.table.cellWidget(row, c)
                if checkbox_widget:
                    checkbox = checkbox_widget.layout().itemAt(0).widget()
                    checkbox.setEnabled(False)

        # Lock the next row if checkbox is in columns 3 to 6
        if col in range(2, 6):  # Columns 3 to 6 (index 2 to 5)
            if row < self.table.rowCount() - 1:  # If there is a row below
                lock_item_next_row = self.table.item(row + 1, 6)
                lock_item_next_row.setText("1")
                for c in range(6):
                    checkbox_widget = self.table.cellWidget(row + 1, c)
                    if checkbox_widget:
                        checkbox = checkbox_widget.layout().itemAt(0).widget()
                        checkbox.setEnabled(False)

        # Lock columns 3 to 6 in the previous row
        if row > 0:  # If there is a row above
            for c in range(2, 6):  # Columns 3 to 6 (index 2 to 5)
                checkbox_widget = self.table.cellWidget(row - 1, c)
                if checkbox_widget:
                    checkbox = checkbox_widget.layout().itemAt(0).widget()
                    checkbox.setEnabled(False)

    def unlock_checkboxes(self, row, col):
        all_unchecked = True
        for c in range(6):
            checkbox_widget = self.table.cellWidget(row, c)
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                if checkbox.isChecked():
                    all_unchecked = False
                    break

        if all_unchecked:
            self.table.item(row, 6).setText("0")
            for c in range(6):
                checkbox_widget = self.table.cellWidget(row, c)
                if checkbox_widget:
                    checkbox = checkbox_widget.layout().itemAt(0).widget()
                    checkbox.setEnabled(True)

            # Unlock the next row if no checkbox in columns 3 to 6 is activated
            if col in range(2, 6) and row < self.table.rowCount() - 1:
                all_unchecked_next_row = True
                for c in range(6):
                    checkbox_widget = self.table.cellWidget(row + 1, c)
                    if checkbox_widget:
                        checkbox = checkbox_widget.layout().itemAt(0).widget()
                        if checkbox.isChecked():
                            all_unchecked_next_row = False
                            break
                if all_unchecked_next_row:
                    self.table.item(row + 1, 6).setText("0")
                    lock_item_two_rows = self.table.item(
                        row + 2, 6) if row + 2 < self.table.rowCount() else None
                    if lock_item_two_rows and lock_item_two_rows.text() == "1":
                        for c in range(2):
                            checkbox_widget = self.table.cellWidget(row + 1, c)
                            if checkbox_widget:
                                checkbox = checkbox_widget.layout().itemAt(0).widget()
                                checkbox.setEnabled(True)
                    else:
                        for c in range(6):
                            checkbox_widget = self.table.cellWidget(row + 1, c)
                            if checkbox_widget:
                                checkbox = checkbox_widget.layout().itemAt(0).widget()
                                checkbox.setEnabled(True)

            # Unlock columns 3 to 6 in the previous row if no checkbox is activated in that row
            if row > 0:
                all_unchecked_prev_row = True
                for c in range(6):
                    checkbox_widget = self.table.cellWidget(row - 1, c)
                    if checkbox_widget:
                        checkbox = checkbox_widget.layout().itemAt(0).widget()
                        if checkbox.isChecked():
                            all_unchecked_prev_row = False
                            break
                prev_row_item = self.table.item(
                    row-2, 6) if row-2 >= 0 else None
                if all_unchecked_prev_row and prev_row_item and prev_row_item.text() == "0":
                    self.table.item(row - 1, 6).setText("0")
                    for c in range(2, 6):
                        checkbox_widget = self.table.cellWidget(row - 1, c)
                        if checkbox_widget:
                            checkbox = checkbox_widget.layout().itemAt(0).widget()
                            checkbox.setEnabled(True)

        # Check if we need to keep columns 3 to 6 locked because of the row below
        if col in range(0, 2) and row < self.table.rowCount() - 1:
            if self.table.item(row + 1, 6).text() == "1":
                for cc in range(2, 6):
                    checkbox_widget_current_row = self.table.cellWidget(
                        row, cc)
                    if checkbox_widget_current_row:
                        checkbox_current_row = checkbox_widget_current_row.layout().itemAt(0).widget()
                        checkbox_current_row.setEnabled(False)

        # Check if we need to unlock columns 3 to 6 based on subsequent rows
        if col in range(2, 6) and row < self.table.rowCount() - 2:
            if not any(self.table.cellWidget(row + 2, c) and self.table.cellWidget(row + 2, c).layout().itemAt(0).widget().isChecked() for c in range(2, 6)):
                for c in range(2, 6):
                    checkbox_widget = self.table.cellWidget(row + 1, c)
                    if checkbox_widget:
                        checkbox_widget.layout().itemAt(0).widget().setEnabled(True)
                self.table.item(row + 1, 6).setText("0")

    def deselect_all(self):
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                checkbox_widget = self.table.cellWidget(row, col)
                if checkbox_widget:
                    checkbox = checkbox_widget.layout().itemAt(0).widget()
                    checkbox.setChecked(False)
                    checkbox.setEnabled(True)
            # Reset the locked column (assuming column 6 is the lock column)
            lock_item = self.table.item(row, 6)
            if lock_item:
                lock_item.setText("0")

    def select_all(self, col):
        for row in range(self.table.rowCount()):
            if col < 2 or (col >= 2 and row % 2 == 0):
                checkbox_widget = self.table.cellWidget(row, col)
                if checkbox_widget:
                    checkbox = checkbox_widget.layout().itemAt(0).widget()
                    if checkbox.isEnabled():
                        checkbox.setChecked(True)

    def save_state(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options
        )
        if fileName:
            try:
                # Save the .txt file
                with open(fileName, "w") as file:
                    for row in range(self.table.rowCount()):
                        states = []
                        # Exclude the lock column
                        for col in range(self.table.columnCount() - 1):
                            checkbox_widget = self.table.cellWidget(row, col)
                            if checkbox_widget:
                                checkbox = checkbox_widget.layout().itemAt(0).widget()
                                states.append(checkbox.isChecked())
                        if any(states):
                            file.write(f"{row + 1}: {states}\n")

                QMessageBox.information(
                    self, "Success", "File saved successfully.")

                # Generate the .par file
                base_name = os.path.splitext(fileName)[0]
                current_date = datetime.datetime.now().strftime("%d_%m_%Y")
                par_file_name = f"{base_name}_{current_date}.par"
                self.generate_par_file(par_file_name)

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not save file: {e}")

    def generate_par_file(self, par_file_name):
        try:
            # Load the JSON data
            D_And_S_Data = load_data(
                os.path.join(basedir, "data", "DSdata.json"))

            with open(par_file_name, "w", encoding="utf-8") as file:
                current_address = None
                for row in range(self.table.rowCount()):
                    # Exclude the lock column
                    for col in range(self.table.columnCount() - 1):
                        checkbox_widget = self.table.cellWidget(row, col)
                        if checkbox_widget:
                            checkbox = checkbox_widget.layout().itemAt(0).widget()
                            if checkbox.isChecked():
                                adresse = row + 1
                                for key, value in D_And_S_Data[col].items():
                                    if key != "Name" and value:
                                        if "+1" in key:
                                            address_value = key.replace(
                                                "Adresse+1", str(adresse + 1))
                                        else:
                                            address_value = key.replace(
                                                "Adresse", str(adresse))
                                        if current_address and current_address != adresse:
                                            file.write("\n")
                                        file.write(f".{address_value};\n")
                                        current_address = adresse

            QMessageBox.information(
                self, "Success", "PAR file generated successfully.")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Could not generate PAR file: {e}")

    def load_state(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Load File", "", "Text Files (*.txt);;All Files (*)", options=options
        )
        if fileName:
            try:
                with open(fileName, "r") as file:
                    for line in file:
                        parts = line.strip().split(": ")
                        row = int(parts[0]) - 1
                        states = eval(parts[1])
                        for col in range(len(states)):
                            checkbox_widget = self.table.cellWidget(row, col)
                            if checkbox_widget:
                                checkbox = checkbox_widget.layout().itemAt(0).widget()
                                checkbox.setChecked(states[col])
                QMessageBox.information(
                    self, "Success", "File loaded successfully.")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not load file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = TableApp()
    mainWindow.show()
    sys.exit(app.exec_())
