import datetime
import logging
import os
import re
import subprocess
import threading

import telebot
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from yt_dlp import YoutubeDL




def clean_filename(text: str) -> str:
    # запрещенные символы
    forbidden = '[/\\\:\*\?"<>\|]'
    # заменяем запрещенные символы на _
    clean_text = re.sub(forbidden, '-', text)
    return clean_text


def output_t(token, chat_id, msg):
    bot = telebot.TeleBot(token)
    if msg is not None:
        bot.send_message(chat_id=chat_id, text=msg)
    else:
        bot.send_message(chat_id=chat_id, text="running")
    bot.stop_polling()


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
        self.folder_label.setFixedWidth(240)
        # self.folder_label.setReadOnly(True)

        self.download_button = QPushButton(self)
        self.download_button.setText("Скачать")
        self.download_button.move(20, 140)
        self.download_button.clicked.connect(self.download_video)

        self.progressbar = QProgressBar(self)
        self.progressbar.setGeometry(20, 170, 280, 20)

    def download_and_convert(self, URL, path, progressbar):
        os.system('cls' if os.name == 'nt' else 'clear')
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        try:
            options = {
                'format': 'bestaudio[ext=mp3]/best',
                'extractaudio': True,
                'outtmpl': f"{path}/%(title)s_{date}.%(ext)s",
                'noplaylist': True,
                'progress_hooks': [lambda d: progressbar.setValue(int(d['downloaded_bytes'] * 100 / d['total_bytes']))]
            }

            logger = logging.getLogger(__name__)

            progressbar.setFormat("Загрузка видео")

            with YoutubeDL(options) as ydl:
                ydl.download([URL])

            progressbar.setFormat("Видео загружено")

            video_title = ydl.extract_info(URL, download=False).get('title', None)
            input_video = f"{path}/{clean_filename(video_title)}_{date}.mp4"
            output_audio = f"{path}/{clean_filename(video_title)}.mp3"

            progressbar.setFormat("Конвертирование в аудио файл")

            if os.path.isfile(output_audio):
                os.remove(output_audio)

            subprocess.call(["ffmpeg", "-i", input_video, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_audio])

            os.remove(input_video)

            progressbar.setFormat("Успешно завершено")

        except KeyError as k:
            output_t(token, id, "(ОШИБКА) \nв директорию качается тот же файл\n" + str(k))
            logger.exception("Ошибка: %s", str(k))

        except Exception as e:
            output_t(token, id, str(e))
            logger.exception("Ошибка: %s", str(e))



    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку")
        self.folder_label.setText(folder_path)

    def download_video(self):
        if not self.line_edit.text():
            reply = QMessageBox.warning(self, "Пустая ссылка",
                                         "Укажите правильную ссылку на видео YouTube",
                                         QMessageBox.Ok)

        elif not self.folder_label.text():
            reply = QMessageBox.warning(self, "Пустой путь",
                                         "Нажмите на кнопку <Куда скачать> и выберете место куда скачать аудио",
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
    try:
        output_t(token, id, msg=None)
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()
    except Exception as e:
        output_t(token, id, str(e))