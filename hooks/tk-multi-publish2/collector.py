import mimetypes
import os
import sgtk
from tank import TankError
from tank_vendor import six

logger = sgtk.platform.get_logger(__name__)

HookBaseClass = sgtk.get_hook_baseclass()

ACCEPTABLE_TYPES = [
    "anim", "blocking", "comp", "concept", "cutref", "diwip", "dmp", "edit", "fx",
    "layout", "light", "lookdev", "model", "optical", "plate", "postvis", "previs",
    "reference", "scan", "techvis", "test", "wedge",
]


class BasicSceneCollector(HookBaseClass):
    """
    Extend the default collector to potentially prelink a task to an asset.
    """

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
                # --- begin customization
                self._link_item_to_task(file_item)
                # --- end customization
            return None
        else:
            file_item = self._collect_file(parent_item, path)
            file_item.properties["publish_templates"] = publish_templates
            # --- begin customization
            self._link_item_to_task(file_item)
            # --- end customization
            return file_item

    def _link_item_to_task(self, file_item):
        """
        This function will connect the file_item with a task if one is found
        based on the filename.
        """
        path = file_item.properties["path"]
        publisher = self.parent
        sg = publisher.shotgun

        # get path components assuming the file structure is
        # single file:  LAX_0020_comp_v002.mov
        # sequence:     LAX_0020_comp_v002.%04d.exr
        # subtask:      LAX_0020_comp_pipe_v002.mov
        file_name = publisher.util.get_file_path_components(path)["filename"]
        scene, shot, task, subtask, *rest = file_name.split("_")

        project_id = file_item.context.project["id"]
        # if there is no subtask, the version and file extension are in subtask
        # an rest is empty. Therefore, if a rest is given, we have a subtask
        entity_name = "_".join(filter(None, [scene, shot, task, subtask if rest else None]))
        response = sg.text_search(entity_name, {"Task": []}, [project_id])

        if not response["matches"]:
            # we did not find any tasks. search for a shot at least
            entity_name = "_".join([scene, shot])
            response = sg.text_search(entity_name, {"Shot": []}, [project_id])

        # we can only link a task if the matches are unambiguous, therefore
        # iterate over all of them and do a name matching
        match = None
        for match in response["matches"]:
            if match["name"] == entity_name:
                entity_type = match["type"]
                entity_id = match["id"]
                new_ctx = publisher.sgtk.context_from_entity(entity_type, entity_id)
                file_item.context = new_ctx

                logger.info(f'Successfully linked asset "{file_name}" to {entity_type} "{entity_name}"')
                # we found a match, let"s leave now
                break

        # store task information from filename for later use in upload_version
        if match and match["type"] == "Task" or task in ACCEPTABLE_TYPES:
            file_item.properties["version_type"] = task
    # --- end customization
