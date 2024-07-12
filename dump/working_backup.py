import sys
import os
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
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor


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
        actionButtonLayout.addWidget(self.saveButton)

        self.loadButton = QPushButton("Load Data")
        actionButtonLayout.addWidget(self.loadButton)

        self.deselectAllButton = QPushButton("Alles Abwählen")
        self.deselectAllButton.clicked.connect(self.deselect_all)
        actionButtonLayout.addWidget(self.deselectAllButton)

        layout.addLayout(actionButtonLayout)

    def header_menu(self, index):
        menu = QMenu(self)
        select_all_action = menu.addAction("Alles auswählen")

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
                if all_unchecked_prev_row and self.table.item(row-2, 6).text() == "0":
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
            for col in range(6):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = TableApp()
    mainWindow.show()
    sys.exit(app.exec_())