import cv2
import numpy as np
import os
import time
import sqlite3
from sklearn import preprocessing
from sklearn.metrics import pairwise
from matplotlib import pyplot as plt
from imutils import paths
import face_recognition
import pyfingerprint
import pyautogui

class BiometricAuth:
    def __init__(self, db_name="biometric_auth.db"):
        self.db_name = db_name
        self.camera = cv2.VideoCapture(0)
        self.conn = sqlite3.connect(self.db_name)
        self.create_user_table()

    def create_user_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users
                          (id INTEGER PRIMARY KEY,
                           name TEXT,
                           fingerprint BLOB,
                           image BLOB)''')
        self.conn.commit()

    def capture_image(self, user_id):
        ret, frame = self.camera.read()
        if ret:
            img_name = f"user_{user_id}.png"
            cv2.imwrite(img_name, frame)
            return img_name
        return None

    def enroll_fingerprint(self):
        try:
            f = pyfingerprint.PyFingerprint('/dev/ttyUSB0')
            if not f.verifyPassword():
                raise ValueError("Fingerprint sensor password is incorrect!")

            print("Place your finger on the sensor...")
            while not f.readImage():
                pass

            f.convertImage(0x01)
            result = f.searchTemplate()
            position_number = result[0]

            if position_number >= 0:
                print("This fingerprint is already enrolled!")
            else:
                print("Place the same finger again...")
                while not f.readImage():
                    pass

                f.convertImage(0x02)

                if f.compareCharacteristics() == 0:
                    raise Exception("Fingers do not match!")

                f.createTemplate()
                position_number = f.storeTemplate()

                print("Fingerprint enrolled successfully!")
                return position_number
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def add_user(self, name):
        user_id = self.get_next_user_id()
        img_name = self.capture_image(user_id)
        fingerprint_id = self.enroll_fingerprint()

        if img_name and fingerprint_id is not None:
            with open(img_name, 'rb') as img_file:
                img_blob = img_file.read()
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Users (name, fingerprint, image) VALUES (?, ?, ?)",
                           (name, fingerprint_id, img_blob))
            self.conn.commit()
            print("User added successfully!")
        else:
            print("Failed to add user.")

    def get_next_user_id(self):
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT MAX(id) FROM Users").fetchone()
        return (result[0] + 1) if result[0] is not None else 1

    def authenticate_user(self, username):
        cursor = self.conn.cursor()
        user = cursor.execute("SELECT * FROM Users WHERE name=?", (username,)).fetchone()
        if user:
            print(f"User found: {user[1]}")
            self.verify_fingerprint(user[2])
        else:
            print("User not found!")

    def verify_fingerprint(self, stored_fingerprint):
        try:
            f = pyfingerprint.PyFingerprint('/dev/ttyUSB0')
            if not f.verifyPassword():
                raise ValueError("Fingerprint sensor password is incorrect!")

            print("Place your finger on the sensor...")
            while not f.readImage():
                pass

            f.convertImage(0x01)
            result = f.searchTemplate()
            position_number = result[0]

            if position_number == stored_fingerprint:
                print("Authentication successful!")
            else:
                print("Authentication failed!")
        except Exception as e:
            print(f"Error: {str(e)}")

    def display_registered_users(self):
        cursor = self.conn.cursor()
        users = cursor.execute("SELECT name FROM Users").fetchall()
        print("Registered Users:")
        for user in users:
            print(user[0])

    def close(self):
        self.camera.release()
        self.conn.close()

def main():
    auth_system = BiometricAuth()

    while True:
        print("1. Add User")
        print("2. Authenticate User")
        print("3. Display Registered Users")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter user name: ")
            auth_system.add_user(name)
        elif choice == '2':
            username = input("Enter user name to authenticate: ")
            auth_system.authenticate_user(username)
        elif choice == '3':
            auth_system.display_registered_users()
        elif choice == '4':
            auth_system.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()