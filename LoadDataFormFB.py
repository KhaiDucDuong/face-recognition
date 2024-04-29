# GROUP 3 [20110002, 20110405, 20110420] [Nguyen Xuan Loc, Ha Tan Tho, Nguyen Huynh Thanh Toan]
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QTableView
import sys

# Initialize Firebase app
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facialrecognitionsystem-3c1b7-default-rtdb.firebaseio.com/"
})

# Create a QApplication instance
app = QApplication(sys.argv)

# Load data from Firebase
ref = db.reference('Students')
data = ref.get()

# Create a standard item model and populate data
model = QStandardItemModel(len(data), 6)
model.setHorizontalHeaderLabels(["ID", "Name", "Age", "Family Role", "Job Status", "Total Open Door", "Last Opening Door Time"])
for i, key in enumerate(data):
    model.setItem(i, 0, QStandardItem(key))
    model.setItem(i, 1, QStandardItem(data[key]['name']))
    model.setItem(i, 2, QStandardItem(data[key]['age']))
    model.setItem(i, 3, QStandardItem(str(data[key]['family_role'])))
    model.setItem(i, 4, QStandardItem(str(data[key]['job_status'])))
    model.setItem(i, 5, QStandardItem(data[key]['total_open_door']))
    model.setItem(i, 6, QStandardItem(str(data[key]['last_opening_door_time'])))

# Create a table view and set model
table_view = QTableView()
table_view.setModel(model)

# Customize table view with CSS
table_view.setWindowTitle("Load data form firebase")
table_view.setFixedSize(925, 480)
table_view.resizeColumnsToContents()
table_view.setStyleSheet("""
    QTableView {
        border: 1px solid gray;
        background-color: #f2f2f2;
    }
    QTableView QHeaderView::section {
        background-color: #c27ba0;
        color: white;
        padding: 6px;
        border: none;
    }
    QTableView QHeaderView::section:nth-child(2),
    QTableView QHeaderView::section:nth-child(3),
    QTableView QHeaderView::section:nth-child(6) {
        background-color: #c90076;
    }
    QTableView::item {
        padding: 6px;
        border: none;
    }
    QTableView::item:nth-child(even) {
        background-color: #f2f2f2;
    }
    QTableView::item:nth-child(odd) {
        background-color: #ffffff;
    }
""")
# Show table view
table_view.show()
sys.exit(app.exec_())
