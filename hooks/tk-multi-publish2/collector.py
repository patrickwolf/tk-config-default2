import mimetypes
import os
import sgtk
from tank import TankError
from tank_vendor import six

logger = sgtk.platform.get_logger(__name__)

HookBaseClass = sgtk.get_hook_baseclass()


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
        path = file_item.properties['path']
        publisher = self.parent

        # get path components assuming the file structure is
        # single file:  LAX_0020_comp_v002.mov
        # sequence:     LAX_0020_comp_v002.%04d.exr
        # subtask:      LAX_0020_comp_pipe_v002.mov
        file_name = publisher.util.get_file_path_components(path)['filename']
        scene, shot, task, subtask, *rest = file_name.split('_')

        parts = [scene, shot, task]
        # if there is no subtask, the version and file extension are in subtask
        # an rest is empty. Therefore, if a rest is given, we have a subtask
        if rest:
            parts.append(subtask)

        task_str = '_'.join(parts)

        project_id = file_item.context.project['id']
        response = publisher.shotgun.text_search(task_str, {'Task': []}, [project_id])
        matches = response['matches']

        # we can only link a task if the matches are unambiguous
        for match in matches:
            if match['name'] == task_str:
                task_id = matches[0]['id']
                new_ctx = publisher.sgtk.context_from_entity('Task', task_id)
                file_item.context = new_ctx

                logger.info(f'Successfully linked asset "{file_name}" to task "{new_ctx.task["name"]}"')
                # we found a match, let's leave the
                break

        # store task information from filename for later use in upload_version
        file_item.properties['task'] = task
