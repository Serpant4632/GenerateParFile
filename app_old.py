import sys
import os
import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QLabel,
    QCheckBox,
    QSizePolicy,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class CheckboxTable(QWidget):
    def __init__(self, rows, columns, headers):
        super().__init__()
        self.initUI(rows, columns, headers)

    def initUI(self, rows, columns, headers):
        layout = QVBoxLayout()

        # Header Layout with Logo
        headerLayout = QHBoxLayout()
        for header in headers:
            label = QLabel(header)
            label.setFixedWidth(120)
            label.setAlignment(Qt.AlignCenter)
            headerLayout.addWidget(label)

        # Add the logo in the top-right corner
        logo = QLabel()
        # Replace with the path to your logo
        pixmap = QPixmap("img/LukeWareLogo.jpeg")
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignRight)
        headerLayout.addWidget(logo)

        layout.addLayout(headerLayout)

        # Scroll Area Layout
        scrollArea = QScrollArea()
        scrollAreaWidget = QWidget()
        self.scrollLayout = QGridLayout()
        self.scrollLayout.setSpacing(10)

        self.checkboxes = []

        for row in range(rows):
            row_checkboxes = []
            for col in range(columns):
                if col == 0:
                    label = QLabel(f"{row + 1}")
                    label.setFixedWidth(120)
                    label.setAlignment(Qt.AlignCenter)
                    self.scrollLayout.addWidget(label, row, col)
                else:
                    checkbox = QCheckBox()
                    if row == 126 and col in [3, 4, 5, 6]:
                        # checkbox.setEnabled(False)
                        # checkbox.setVisible(False)
                        # skip last 4 checkboxes in row 126 (Adr. 127)
                        continue
                    checkbox.setSizePolicy(
                        QSizePolicy.Fixed, QSizePolicy.Fixed)
                    checkbox.stateChanged.connect(
                        lambda state, r=row, c=col: self.checkbox_state_changed(
                            state, r, c)
                    )
                    self.scrollLayout.addWidget(
                        checkbox, row, col, alignment=Qt.AlignCenter)
                    row_checkboxes.append(checkbox)
            self.checkboxes.append(row_checkboxes)

        scrollAreaWidget.setLayout(self.scrollLayout)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollAreaWidget)
        layout.addWidget(scrollArea)

        # Add Save and Load Buttons
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save_state)
        layout.addWidget(self.saveButton)

        self.loadButton = QPushButton("Load Data")
        self.loadButton.clicked.connect(self.load_state)
        layout.addWidget(self.loadButton)

        self.setLayout(layout)

    def checkbox_state_changed(self, state, row, col):
        def set_row_enabled(row, enabled, skip_cols=[]):
            if 0 <= row < len(self.checkboxes):
                for c, checkbox in enumerate(self.checkboxes[row]):
                    if c not in skip_cols:
                        checkbox.setEnabled(enabled)
                        # checkbox.setVisible(enabled)

        def set_specific_cols_enabled(row, cols, enabled):
            if 0 <= row < len(self.checkboxes):
                for c in cols:
                    if 0 <= c < len(self.checkboxes[row]):
                        self.checkboxes[row][c].setEnabled(enabled)
                        # self.checkboxes[row][c].setVisible(enabled)

        def are_all_unchecked(row):
            if 0 <= row < len(self.checkboxes):
                return all(not cb.isChecked() for cb in self.checkboxes[row])
            return True

        def any_checked_in_cols(row, cols):
            if 0 <= row < len(self.checkboxes):
                return any(self.checkboxes[row][c].isChecked() for c in cols if 0 <= c < len(self.checkboxes[row]))
            return False

        def block_adjacent_rows(row, col):
            # Block entire next row and columns 3 to 6 in the previous row
            if col in [3, 4, 5, 6]:
                if row > 0:
                    set_specific_cols_enabled(row - 1, [2, 3, 4, 5], False)
                if row < len(self.checkboxes) - 1:
                    set_row_enabled(row + 1, False)

        def unblock_adjacent_rows(row, col):
            # Unblock columns 3 to 6 in the row before and entire next row if no other columns are checked
            if col in [3, 4, 5, 6]:
                if row > 0 and are_all_unchecked(row - 1):
                    set_specific_cols_enabled(row - 1, [2, 3, 4, 5], True)
                if row < len(self.checkboxes) - 1 and are_all_unchecked(row + 1):
                    set_row_enabled(row + 1, True)

        if state == Qt.Checked:
            # Uncheck any other checkbox in the same row
            for c in range(len(self.checkboxes[row])):
                if c != col - 1 and self.checkboxes[row][c].isChecked():
                    self.checkboxes[row][c].setChecked(False)

            set_row_enabled(row, False, skip_cols=[col-1])
            if 0 <= col - 1 < len(self.checkboxes[row]):
                # Keep the clicked checkbox enabled
                self.checkboxes[row][col - 1].setEnabled(True)

            if col in [1, 2]:
                set_specific_cols_enabled(row, [2, 3, 4, 5], False)
                set_specific_cols_enabled(row - 1, [2, 3, 4, 5], False)

            if col in [3, 4, 5, 6]:
                block_adjacent_rows(row, col)

        else:
            if are_all_unchecked(row):
                set_row_enabled(row, True)

            if col in [1, 2]:
                if are_all_unchecked(row):
                    set_specific_cols_enabled(row, [2, 3, 4, 5], True)
                    set_specific_cols_enabled(row - 1, [2, 3, 4, 5], True)

            if col in [3, 4, 5, 6]:
                unblock_adjacent_rows(row, col)
                if are_all_unchecked(row):
                    set_row_enabled(row + 1, True)
                    set_specific_cols_enabled(row - 1, [2, 3, 4, 5], True)

        # Ensure that if there's a checked box in the next row, columns 3-6 cannot be checked
        if state == Qt.Checked and col in [3, 4, 5, 6]:
            if any_checked_in_cols(row + 1, [1, 2, 3, 4, 5, 6]):
                self.checkboxes[row][col - 1].setChecked(False)
                set_row_enabled(row + 1, False)

    def save_state(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options
        )
        if fileName:
            try:
                # Save the .txt file
                with open(fileName, "w") as file:
                    for row in range(len(self.checkboxes)):
                        if any(cb.isChecked() for cb in self.checkboxes[row]):
                            states = [cb.isChecked()
                                      for cb in self.checkboxes[row]]
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
        data = {
            "Name": ["BK-M-K", "BK-2M-K", "BK-2DO", "BK-2DI", "BK-4DO", "BK-4DI"],
            "Adresse/R1": [True, True, True, False, True, False],
            "Adresse/R2": [False, True, True, False, True, False],
            "Adresse/R3": [False, False, False, False, True, False],
            "Adresse/R4": [False, False, False, False, True, False],
            "Adresse/1": [True, True, False, True, False, True],
            "Adresse/2": [False, True, False, True, False, True],
            "Adresse/3": [False, True, False, False, False, True],
            "Adresse/4": [True, True, False, False, False, True],
            "Adresse+1/1": [False, False, True, False, True, False],
            "Adresse+1/2": [False, False, True, False, True, False],
            "Adresse+1/3": [False, False, False, False, True, False],
            "Adresse+1/4": [False, False, False, False, True, False]
        }

        try:
            with open(par_file_name, "w", encoding="utf-8") as file:
                current_address = None
                for row in range(len(self.checkboxes)):
                    for col in range(len(self.checkboxes[row])):
                        if self.checkboxes[row][col].isChecked():
                            adresse = row + 1
                            for key, values in data.items():
                                if key != "Name" and values[col]:
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
                        for col in range(1, len(states) + 1):
                            self.checkboxes[row][col -
                                                 1].setChecked(states[col - 1])
                QMessageBox.information(
                    self, "Success", "File loaded successfully.")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not load file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    headers = ["Adresse", "BK-M-K", "BK-2M-K",
               "BK-2DO", "BK-2DI", "BK-4DO", "BK-4DI"]
    rows = 127
    columns = len(headers)

    mainWidget = CheckboxTable(rows, columns, headers)
    mainWidget.setWindowTitle("D&S Parameterdatei Konfigurator")
    mainWidget.resize(800, 600)
    mainWidget.show()

    sys.exit(app.exec_())
