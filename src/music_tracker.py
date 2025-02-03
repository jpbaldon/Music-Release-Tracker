import sys
import json
import requests
import time
import csv
import math
import socket
import urllib3

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QProgressBar, QComboBox, QLabel, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from datetime import datetime, timedelta, date
from requests.exceptions import ConnectionError

DEFAULT_RESULTS_LIM = 50 #default number of results returned per API request
MAX_LIM_PER_CALL = 200 #defined by Apple
MAX_CALLS_PER_MIN = 20 #defined by Apple
itunes = "http://itunes.apple.com/search?entity=album&attribute=artistTerm"
artist_file = "artists.csv"
album_file = "albums.csv"
save_file = "save_data.json"

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(1200, 900)
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        MainWindow.resize(int(screen_size.width() * 0.8), int(screen_size.height() * 0.8))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        # Create the main layout
        self.mainLayout = QHBoxLayout(self.centralwidget)

        # Create the left layout
        self.leftLayout = QVBoxLayout()
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.leftLayout.addWidget(self.tabWidget)

        ########### Create Tab 1 ####################
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1Layout = QVBoxLayout(self.tab_1)
        self.tabWidget.addTab(self.tab_1, "Tab 1")

        #Create label for artist text field
        self.artistLabel = QLabel("Enter an artist name to follow (as it appears on itunes):", self.tab_1)
        self.tab_1Layout.addWidget(self.artistLabel)

        #Create Artist Text Field
        self.artistField = QtWidgets.QLineEdit(self.tab_1)
        self.tab_1Layout.addWidget(self.artistField)

        #Create Follow Artist Button
        self.followButton = QtWidgets.QPushButton(self.tab_1)
        self.followButton.clicked.connect(self.on_followButton_clicked)
        self.followButton.setFixedWidth(150)
        self.tab_1Layout.addWidget(self.followButton)

        #Followed Artists Table on the Followed Artists Tab
        self.artistTable = QtWidgets.QTableWidget(self.tab_1)
        self.artistTable.setGeometry(QtCore.QRect(50, 140, 371, 411))
        self.artistTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.artistTable.setColumnCount(1)
        self.artistTable.setRowCount(0)
        self.artistTable.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.artistTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.artistTable.verticalHeader().setDefaultSectionSize(10)
        self.tab_1Layout.addWidget(self.artistTable)

        #Create Unfollow Artist Button
        self.unfollowButton = QtWidgets.QPushButton(self.tab_1)
        self.unfollowButton.clicked.connect(lambda: self.on_removeButton_clicked(self.artistTable, artist_file))
        self.tab_1Layout.addWidget(self.unfollowButton)

        ##########Create Tab 2#############
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("Tab2")
        self.tab_2Layout = QVBoxLayout(self.tab_2)
        self.tabWidget.addTab(self.tab_2, "Tab 2")

        #Create time widget
        self.timeWidget = QtWidgets.QWidget(self.tab_2)
        self.timeLayout = QHBoxLayout(self.timeWidget)
        self.timeLayout.setObjectName("timelayout")
        self.timeWidget.setLayout(self.timeLayout)
        self.tab_2Layout.addWidget(self.timeWidget)

        #Create label for the time combo box
        self.timeLabel = QLabel("Search for results in the past:", self.timeWidget)
        self.timeLayout.addWidget(self.timeLabel, 0)

        #Create the time combo box
        self.timeComboBox = QtWidgets.QComboBox(self.timeWidget)
        self.timeComboBox.addItem("eternity")
        self.timeComboBox.addItem("year")
        self.timeComboBox.addItem("month")
        self.timeComboBox.addItem("week")
        self.timeComboBox.setFixedWidth(200)
        self.timeLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.timeLayout.setSpacing(1)
        self.timeLayout.addWidget(self.timeComboBox, 0)
        self.timeLayout.addStretch(1)

        #Create search button
        self.searchButton = QtWidgets.QPushButton(self.tab_2)
        self.searchButton.clicked.connect(lambda: self.on_searchButton_clicked("YES"))
        self.tab_2Layout.addWidget(self.searchButton)

        #Create the list of albums found from itunes
        self.albumTable = QtWidgets.QTableWidget(self.tab_2)
        self.albumTable.setGeometry(QtCore.QRect(50, 140, 371, 411))
        self.albumTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.albumTable.setColumnCount(3)
        self.albumTable.setRowCount(0)
        self.albumTable.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.albumTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.albumTable.verticalHeader().setDefaultSectionSize(10)
        self.albumTable.setHorizontalHeaderItem(0, QTableWidgetItem("Album"))
        self.albumTable.setHorizontalHeaderItem(1, QTableWidgetItem("Artist"))
        self.albumTable.setHorizontalHeaderItem(2, QTableWidgetItem("Release Date"))
        header = self.albumTable.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.resizeSection(0, 2)
        header.resizeSection(1, 1)
        header.resizeSection(2, 1)
        self.tab_2Layout.addWidget(self.albumTable)

        ################# Create the right layout #################
        self.rightLayout = QVBoxLayout()
        
        self.rightWidget = QtWidgets.QWidget(self.centralwidget)
        self.rightLayout.addWidget(self.rightWidget)

        self.outputText = QTextBrowser(self.rightWidget)
        self.outputText.setGeometry(QtCore.QRect(170, 400, 118, 23))
        self.rightLayout.addWidget(self.outputText)

        self.progressBar = QProgressBar(self.rightWidget)
        self.rightLayout.addWidget(self.progressBar)
        self.progressBar.setGeometry(QtCore.QRect(170, 500, 118, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.hide()
        
        # Add left and right layouts to the main layout
        self.mainLayout.addLayout(self.leftLayout, stretch=3)
        self.mainLayout.addLayout(self.rightLayout, stretch=2)

        # Set main widget layout
        self.centralwidget.setLayout(self.mainLayout)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 901, 20))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #Populate artists and albums from saved data
        self.populate_followed_artists()
        self.populate_new_albums()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        icon = QIcon("icon.png")
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowTitle(_translate("MainWindow", "Music Release Tracker"))
        self.followButton.setText(_translate("MainWindow", "Follow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "Followed Artists"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Albums to Check Out"))
        self.artistTable.horizontalHeaderItem(0).setText(_translate("MainWindow", "Artist List"))
        self.unfollowButton.setText(_translate("MainWindow", "Unfollow Highlighted Artists"))
        self.albumTable.horizontalHeaderItem(0).setText(_translate("MainWindow", "Album"))
        self.albumTable.horizontalHeaderItem(1).setText(_translate("MainWindow", "Artist"))
        self.albumTable.horizontalHeaderItem(2).setText(_translate("MainWindow", "Release Date"))
        self.searchButton.setText(_translate("MainWindow", "Search"))

    def on_followButton_clicked(self):
        artist_name = self.artistField.text()
        artist_dict = {"name": artist_name, "limit": DEFAULT_RESULTS_LIM, "date": None}
        add_dict_to_file(artist_file, artist_dict)
        self.create_new_artist_row(artist_name)

    def populate_followed_artists(self):
        artist_list = get_dict_list_from_file(artist_file)
        for artist in artist_list:
            self.create_new_artist_row(artist["name"])

    def populate_new_albums(self):
        album_list = get_dict_list_from_file(album_file)
        for album in album_list:
            self.create_new_album_row(album)

    def create_new_artist_row(self, artist_name):
        row_count = self.artistTable.rowCount()
        self.artistTable.insertRow(row_count)  # Insert a new row at the end
        new_item = QTableWidgetItem(artist_name)  # Create a new item
        new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
        self.artistTable.setItem(row_count, 0, new_item)

    def create_new_album_row(self, album):
        row_count = self.albumTable.rowCount()
        self.albumTable.insertRow(row_count)  # Insert a new row at the end
        new_item = QTableWidgetItem(album["name"])  # Create a new item
        new_item2 = QTableWidgetItem(album["artist"])  # Create a new item
        new_item3 = QTableWidgetItem(album["date"])  # Create a new item
        new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
        new_item2.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
        new_item3.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
        self.albumTable.setItem(row_count, 0, new_item)
        self.albumTable.setItem(row_count, 1, new_item2)
        self.albumTable.setItem(row_count, 2, new_item3)

    #removes selected rows from either the artist table or the album table
    def on_removeButton_clicked(self, table, file):
        selected_items = table.selectedItems()
        selected_rows = set()
        for item in selected_items:
            selected_rows.add(item.row())
        
        selected_rows_sorted = sorted(selected_rows, reverse=True) #reversed to prevent indexing issues during removal

        names_to_remove = [table.item(row, 0).text() for row in selected_rows_sorted]
        
        for row in selected_rows_sorted:
            table.removeRow(row)

        with open(file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader if row['name'] not in names_to_remove]

        write_dict_list_to_file(file, rows)

    def on_searchButton_clicked(self, greedy):
        artist_list = get_dict_list_from_file(artist_file)

        speedup_approved = False

        try:
            with open(save_file, 'r') as json_file:
                save_data = json.load(json_file)
                if(greedy):
                    speedup_approved = speedup_is_fine(artist_list, save_data)
        except FileNotFoundError as e:
            sys.exit(f"Error: {e}")

        with open(album_file, 'w'):
            pass
        self.albumTable.setRowCount(0)

        artist_num = 1
        self.progressBar.setProperty("value", 0)
        self.progressBar.show()
        
        for artist in artist_list:
            if(artist["limit"] == None):
                artist["limit"] = DEFAULT_RESULTS_LIM
            response = get_albums_of_artist(artist["name"], artist["limit"])
            try:
                o = response.json()
            except AttributeError as e:
                self.outputText.append("Exiting search.")
                return
            
            if "results" not in o or len(o["results"]) == 0:
                self.outputText.append(f"No albums found for {artist["name"]}.")
                continue
            num_collections_found = 0

            time_frame = self.timeComboBox.currentText()
            
            for result in o["results"]:
                num_collections_found += 1
                time_diff = date.today() - datetime.strptime(result["releaseDate"][0:10], "%Y-%m-%d").date()
                if(time_diff <= timedelta(weeks=1) and time_frame == "week") or (time_diff <= timedelta(days=30) and time_frame == "month") or (time_diff <= timedelta(days=366) and time_frame == "year") or time_frame == "eternity":
                    album = {"name": result["collectionName"], "artist": artist["name"], "date": result["releaseDate"][0:10]}
                    add_dict_to_file(album_file, album)
                #print(f"{artist['name']} released {result['collectionName']}")
            #sleep needed to prevent spamming the API more than the allowable amount
            if num_collections_found > int(artist["limit"]) - 1:
                artist["limit"] = min(int(artist["limit"]) + 5, 200)  #Potentially improve results next time this function is run by increasing the limit for this artist
            elif num_collections_found < int(artist["limit"]) - 10:
                artist["limit"] = int(artist["limit"]) - 5 #Potentially improve server response times next time this function is run
            artist["date"] = datetime.now()

            self.progressBar.setProperty("value", int(artist_num / len(artist_list) * 100))
            artist_num += 1

            #check if delay is needed to prevent spamming the API more than Apple allows
            if not speedup_approved:
                time.sleep(math.ceil(60/MAX_CALLS_PER_MIN))

        write_dict_list_to_file(artist_file, artist_list)

        save_data["number_of_artists_last_checked"] = len(artist_list)
        save_data["time_of_last_api_request"] = f"{datetime.now()}"

        with open(save_file, 'w') as json_file:
            json.dump(save_data, json_file, indent=4)

        self.populate_new_albums()

        self.outputText.append("Search completed.")

        self.progressBar.hide()

def speedup_is_fine(artist_list, save_data):

    if(datetime.now() - datetime.strptime(save_data["time_of_last_api_request"], "%Y-%m-%d %H:%M:%S.%f") > timedelta(minutes=1)):
        save_data["number_of_artists_last_checked"] = 0 #last search was greater than a minute ago, so we won't use the last search as a factor in deciding whether we should slow down the current search

    if(len(artist_list) + save_data["number_of_artists_last_checked"] <= MAX_CALLS_PER_MIN):
        ui.outputText.append("Speedup approved: few enough artists to ask the itunes server for data on all of them at once.")
        return True
    else:
        ui.outputText.append("Speedup denied: too many requests. App being intentionally slowed to avoid spamming itunes server. Consider shortening your list of followed artists if you require faster runtime in future.")
        return False

def get_albums_of_artist(name, limit):
    name.strip().replace(" ", "+")
    try:
        response = requests.get(f"{itunes}&limit={limit}&term={name}")
        response.raise_for_status()
        return response
    except ConnectionError as e:
        ui.outputText.append("Connection error. Check your internet connection and try again.")
        return []
    except socket.gaierror as e:
        ui.outputText.append("DNS resolution failed. Please check your network settings.")
        return []
    except urllib3.exceptions.NameResolutionError as e:
        ui.outputText.append("Failed to resolve hostname. Please try again later.")
        return []

def add_dict_to_file(file, dict):
    with open(file, 'a', newline="") as csv_file:
        csv_appender = csv.DictWriter(csv_file, fieldnames=dict.keys())
        if csv_file.tell() == 0:
            csv_appender.writeheader()
        csv_appender.writerow(dict)

def get_dict_list_from_file(file, should_print="NO"):
    try:
        with open(file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            dict_list = list(csv_reader)
            if should_print=="YES":
                for item in dict_list:
                    print(item["name"])
            return dict_list
    except FileNotFoundError as e:
        sys.exit(f"Error: {e}")

def write_dict_list_to_file(file, dict_list):
    with open(file, 'w') as csv_file:
        if(len(dict_list) > 0):
            csv_writer = csv.DictWriter(csv_file, fieldnames=dict_list[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(dict_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())