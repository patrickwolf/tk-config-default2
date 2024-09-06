# Copyright (c) 2024 Yeti Tools Software
#
# CONFIDENTIAL AND PROPRIETARY 

import os
import pprint
import traceback

import sgtk
from sgtk.util.filesystem import copy_file, ensure_folder_exists
from sgtk.platform.qt import QtGui, QtCore

HookBaseClass = sgtk.get_hook_baseclass()


class BasicFilePublishPlugin(HookBaseClass):

    @property
    def settings(self):
        settings = super(BasicFilePublishPlugin, self).settings or {}

        # define the settings the custom plugin UI will set
        settings["artist"] = {
            "type": "dict",
            "default": None,
            "description": "The artist that will be set on the task."
        }
        settings["playlist"] = {
            "type": "dict",
            "default": None,
            "description": "The playlist to which the version will be assigned to."
        }
        return settings


    def create_settings_widget(self, parent):
        # Create our custom widget and return it.
        # It is actually a collection of widgets parented to a single widget.
        self.review_widget = ReviewWidget(parent, self.parent.shotgun)
        return self.review_widget


    def get_ui_settings(self, widget):
        # This will get called when the selection changes in the UI.
        # We need to gather the settings from the UI and return them
        return {"artist": widget.artist,
                "playlist": widget.playlist}


    def set_ui_settings(self, widget, settings, items=None):
        # The plugin task has just been selected in the UI, so we must set the UI state given the settings.
        # It's possible this is the first time the plugin task has been selected, in which case we won't have
        # any settings passed.
        # There also maybe multiple plugins selected in which case there might be a mix of states
        # The current implementation simply sets the settings for each settings block, so the end state of the UI
        # will represent that of the last selected item.
        for setting_block in settings:
            if (artist := setting_block.get("artist")):
                widget.artist = artist

            if (playlist := setting_block.get("playlist")):
                widget.playlist = playlist

    def publish(self, settings, item):
        if (artist := settings.get("artist")):
            item.properties['artist'] = artist.value

        if (playlist := settings.get("playlist")):
            item.properties["playlist"] = playlist.value

        HookBaseClass.publish(self, settings, item)


class ReviewWidget(QtGui.QWidget):

    def __init__(self, parent, sg):

        super(ReviewWidget, self).__init__(parent)

        self._setup_ui()

        self._populate_artists(sg, self.artist_cmbx)
        self._populate_playlists(sg, self.playlist_cmbx)

    @property
    def artist(self):
        """
        Extract the Shotgun user data from the widget and return it.
        Should return something like {u'type': u'HumanUser', u'id': 190, u'name': u'Bob'}.
        :return: dict
        """
        index = self.artist_cmbx.currentIndex()
        return self.artist_cmbx.itemData(index)

    @artist.setter
    def artist(self, value):
        """
        When passed the Shotgun user data, it looks up the combobox index that matches this data and
        sets it to the current index.
        :param value:
        :return: Void
        """
        index = self.artist_cmbx.findData(value)
        self.artist_cmbx.setCurrentIndex(index)

    @property
    def playlist(self):
        """
        Extract the Shotgun user data from the widget and return it.
        Should return something like {u'type': u'HumanUser', u'id': 190, u'name': u'Bob'}.
        :return: dict
        """
        index = self.playlist_cmbx.currentIndex()
        return self.playlist_cmbx.itemData(index)

    @playlist.setter
    def playlist(self, value):
        """
        When passed the Shotgun user data, it looks up the combobox index that matches this data and
        sets it to the current index.
        :param value:
        :return: Void
        """
        index = self.playlist_cmbx.findData(value)
        self.playlist_cmbx.setCurrentIndex(index)

    def _setup_ui(self):
        """
        Creates and lays out all the Qt widgets
        :return:
        """
        self.artist_cmbx = QtGui.QComboBox()
        self.playlist_cmbx = QtGui.QComboBox()

        layout = QtGui.QFormLayout()
        layout.addRow("Artist", self.artist_cmbx)
        layout.addRow("Playlist", self.playlist_cmbx)
        self.setLayout(layout)

    def _populate_artists(self, sg, combobox):
        """
        Populate the artist combobox with all the available artists found on the project.
        :param sg: Shotgun API instance
        :param combobox: The QCombobox that should be populated with users.
        :return: Void
        """

        # Get the current scene context
        current_context = sgtk.platform.current_engine().context

        # Instead of hardcoding the artist group id, we could find it by name, which causes
        # another request, or specify it in settings maybe.
        #group_id = sg.find('Group', [['code', 'is', 'artist']])
        # as per request we disable filtering for the artist group altogether
        #group = ["groups", "is", {"type":"Group", "id": 5}]

        # only find people assigned to the current project
        project = ["projects", "is", current_context.project]

        artists = sg.find("HumanUser", filters=[project], fields=["name"])

        # Add an option so the user doesn't have to assign to someone.
        combobox.addItem("---")

        # Now add all the found users to the artist combo box.
        for artist in artists:
            combobox.addItem(artist["name"], artist)

    def _populate_playlists(self, sg, combobox):
        """
        Populate the playlist combobox with all the available playlists found on the project.
        :param sg: Shotgun API instance
        :param combobox: The QCombobox that should be populated with users.
        :return: Void
        """

        # Get the current scene context
        current_context = sgtk.platform.current_engine().context

        # only find playlists assigned to the current project
        status = ["sg_playlist_status", "not_in", ("clsd", "dlvr", "cmpt")]
        project = ["project", "is", current_context.project]

        playlists = sg.find("Playlist", filters=[status, project], fields=["id", "code"])

        # Add an option so the user doesn't have to assign to someone.
        combobox.addItem("---")

        # Now add all the found users to the playlist combo box.
        for playlist in sorted(playlists, key=lambda pl: pl["code"]):
            combobox.addItem(playlist["code"], playlist)
