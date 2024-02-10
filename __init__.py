# -*- coding: utf-8 -*-

"""
Rumi Allbert rumiallbert@gmail.com rumiallbert.com 2024
"""

import io
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from distutils.spawn import find_executable

import openai
import requests
from anki.hooks import addHook
from anki.lang import ngettext
from anki.sound import _packagedCmd, si
from anki.utils import checksum, noBundledLibs, tmpfile
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showText, tooltip
from bs4 import BeautifulSoup

from .designer.main import Ui_Dialog

# https://github.com/glutanimate/html-cleaner/blob/master/html_cleaner/main.py#L59
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import concurrent.futures
import warnings

# https://github.com/python-pillow/Pillow/issues/3352#issuecomment-425733696
warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)


from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import getText, showInfo


class ConfigUI(QDialog):
    def __init__(self, parent=None):
        super(ConfigUI, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle("DALL-E Image Fetcher Configuration")
        self.layout = QVBoxLayout(self)

        self.apiKeyLabel = QLabel("OpenAI API Key:")
        self.apiKeyEdit = QLineEdit()
        self.apiKeyEdit.setText(mw.addonManager.getConfig(__name__)["apiKey"])

        self.layout.addWidget(self.apiKeyLabel)
        self.layout.addWidget(self.apiKeyEdit)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save)
        self.layout.addWidget(self.saveButton)

    def save(self):
        config = mw.addonManager.getConfig(__name__)
        config["apiKey"] = self.apiKeyEdit.text()
        mw.addonManager.writeConfig(__name__, config)
        self.close()


def openConfig():
    dialog = ConfigUI(mw)
    dialog.exec_()


def onSetupMenus(browser):
    a = QAction("DALL-E Image Fetcher Configuration", browser)
    a.triggered.connect(openConfig)
    browser.form.menuEdit.addAction(a)


addHook("browser.setupMenus", onSetupMenus)

openai.api_key = mw.addonManager.getConfig(__name__)["apiKey"]


def getImages(nid, fld, prompt, img_width, img_height, img_count, fld_overwrite):
    try:
        # Use the OpenAI API to generate images with DALL-E
        response = openai.ImageCompletion.create(
            model="davinci", prompt=prompt, max_tokens=100
        )

        # Extract the images from the response
        images = response["choices"][0]["image"]["data"]

        # Return the images
        return images

    except openai.Error as e:
        # Handle the OpenAI API error
        showInfo(f"An error occurred while fetching images: {e}")


def onAddImages(browser):
    # Get the selected notes
    notes = browser.selectedNotes()

    # For each note
    for nid in notes:
        note = mw.col.getNote(nid)

        # Get the prompt from the note
        prompt = note.fields[0]

        # Get images for the prompt
        images = getImages(nid, "Image", prompt, 256, 256, 1, True)

        # Add the images to the note
        note.fields[1] = images
        note.flush()


# Add the menu item to the browser
def onSetupMenus(browser):
    a = QAction("Add Images", browser)
    a.triggered.connect(lambda: onAddImages(browser))
    browser.form.menuEdit.addAction(a)


addHook("browser.setupMenus", onSetupMenus)
