import mimetypes
import os
import sgtk
from tank import TankError
from tank_vendor import six

HookBaseClass = sgtk.get_hook_baseclass()


class BasicSceneCollector(HookBaseClass):

    def process_file(self, settings, parent_item, path):
        """
        Analyzes the given file and creates one or more items
        to represent it.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance
        :param path: Path to analyze

        :returns: The main item that was created, or None if no item was created
            for the supplied path
        """

        publish_templates_setting = settings.get("Publish Templates")
        publish_templates = {}
        if publish_templates_setting:
            publish_templates = publish_templates_setting.value

        # handle files and folders differently
        if os.path.isdir(path):
            file_items = self._collect_folder(parent_item, path)
            for file_item in file_items:
                file_item.properties["publish_templates"] = publish_templates
            return None
        else:
            file_item = self._collect_file(parent_item, path)
            file_item.properties["publish_templates"] = publish_templates
            return file_item
