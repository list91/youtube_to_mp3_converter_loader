import logging

import telebot
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from yt_dlp import YoutubeDL
import subprocess
import threading
import re

def output_t(token, chat_id, msg):
    bot = telebot.TeleBot(token)

    bot.send_message(chat_id=chat_id, text="running")
    bot.send_message(chat_id=chat_id, text=msg)

    bot.stop_bot()

class MainWindow(QMainWindow):
   def __init__(self):
       super().__init__()

       self.setWindowTitle("Скачивание видео c YouTube")
       self.resize(350, 200)
       self.label = QLabel(self)
       self.label.setText("Вставить ссылку на видео")
       self.label.move(20, 30)

       self.line_edit = QLineEdit(self)
       self.line_edit.move(20, 60)
       self.line_edit.resize(280, 30)

       self.folder_button = QPushButton(self)
       self.folder_button.setText("Куда скачать")
       self.folder_button.move(20, 100)
       self.folder_button.clicked.connect(self.choose_folder)

       self.folder_label = QLabel(self)
       self.folder_label.move(120, 104)

       self.download_button = QPushButton(self)
       self.download_button.setText("Скачать")
       self.download_button.move(20, 140)
       self.download_button.clicked.connect(self.download_video)

       self.progressbar = QProgressBar(self)
       self.progressbar.setGeometry(20, 170, 280, 20)

   def download_and_convert(self, URL, path, progressbar):
       options = {
           'format': 'bestaudio[ext=mp3]/best',
           'extractaudio': True,
           'outtmpl': f'{path}/%(title)s.%(ext)s',
           'noplaylist': True,
           'progress_hooks': [lambda d: progressbar.setValue(int(d['downloaded_bytes'] * 100 / d['total_bytes']))]
       }
       logger = logging.getLogger(__name__)
       try:
           progressbar.setFormat("Загрузка видео")
           with YoutubeDL(options) as ydl:
               ydl.download([URL])
           progressbar.setFormat("Видео загружено")
           video_title = ydl.extract_info(URL, download=False).get('title', None)
           input_video = f"{path}/{video_title}.mp4"
           output_audio = f"{path}/{video_title}.mp3"
           progressbar.setFormat("Конвертируем в аудио файл")
           subprocess.call(
               ["ffmpeg", "-i", input_video, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_audio])
           progressbar.setFormat("Успешно завершено")
       except Exception as e:
           logger.exception("Ошибка: %s", str(e))

   def choose_folder(self):
       folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку")
       self.folder_label.setText(folder_path)

   def showq(self):
       reply = QMessageBox.warning(self, "ntcnfsfjk",
                                    "sekjfen",
                                    QMessageBox.Ok)

   def download_video(self):
       if not self.line_edit.text():
           reply = QMessageBox.warning(self, "Пустая ссылка",
                                        "укажите правильную ссылку на видео YouTube",
                                        QMessageBox.Ok)

       elif not self.folder_label.text():
           reply = QMessageBox.warning(self, "Пустой путь", "нажмите на кнопку <Выбрать папку> и выберете место куда скачать аудио",
                                        QMessageBox.Ok)

       # Проверка правильности ссылки с помощью регулярного выражения
       url_pattern = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$"
       if not re.match(url_pattern, self.line_edit.text()):
           reply = QMessageBox.warning(self, "Некорректная ссылка",
                                       "Укажите правильную ссылку на видео YouTube",
                                        QMessageBox.Ok)

       else:
           progress_thread = threading.Thread(target=self.download_and_convert, args=(self.line_edit.text(), self.folder_label.text(), self.progressbar))
           progress_thread.start()


if __name__ == "__main__":
   app = QApplication([])
   window = MainWindow()
   window.show()
   app.exec_()