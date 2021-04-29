from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from maintenance_mode.backends import AbstractStateBackend


class GCSDefaultStorageBackend(AbstractStateBackend):
    """Effectively a copy of the `DefaultStorageBackend` with Gcloud-related content tweaks."""

    def get_value(self) -> bool:
        """Retrieves the maintenance mode value using `default_storage`."""
        filename = settings.MAINTENANCE_MODE_STATE_FILE_NAME
        try:
            with default_storage.open(filename, 'r') as state_file:
                file_content = state_file.read()
                try:
                    file_content = file_content.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    pass
                return self.from_str_to_bool_value(file_content)
        except IOError:
            return False

    def set_value(self, value: bool):
        """Sets the maintenance mode value using `default_storage`.

        Assuming we're using Gcloud as the default storage, encodes the maintenance mode value
        as `bytes` in order to ensure better compatibility with Gcloud APIs (they operate over
        `bytes` rather than `str`).
        """
        filename = settings.MAINTENANCE_MODE_STATE_FILE_NAME
        if default_storage.exists(filename):
            default_storage.delete(filename)
        string_content: str = self.from_bool_to_str_value(value)
        content = ContentFile(string_content.encode('utf-8'))
        default_storage.save(filename, content)
