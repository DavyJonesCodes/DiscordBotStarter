import re
import json
import os
from collections.abc import MutableMapping


class JsonDB:
    """A simple JSON-backed database class."""

    def __init__(self, filename='data.json'):
        """
        Initializes the database by loading data from a specified JSON file.

        :param filename: The path to the JSON file used for data storage. Defaults to 'data.json'.
        """
        if not os.path.isabs(filename):
            # If the filename is not an absolute path, set it to the directory of the script file
            script_dir = os.path.dirname(os.path.realpath(__file__))
            filename = os.path.join(script_dir, filename)
        self.filename = filename
        self._data = self.load_data()

    def load_data(self) -> dict:
        """
        Loads and returns the data from the JSON file specified by self.filename.

        If the file does not exist or contains invalid JSON, this method returns an empty dictionary.

        :return: A dictionary containing the data loaded from the JSON file.
        """
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_data(self):
        """
        Saves the current state of self._data to the JSON file specified by self.filename.

        The data is formatted with an indentation of 4 spaces for readability.
        """
        with open(self.filename, 'w') as file:
            json.dump(self._data, file, indent=4)

    def reload_data(self):
        """
        Reloads the data from the JSON file specified by self.filename.

        This method updates the in-memory data with the contents of the JSON file.
        """
        self._data = self.load_data()

    def __setitem__(self, key: str, value):
        """
        Sets the value for a given key in the database and immediately saves the updated data to the JSON file.

        :param key: The key under which the value is stored.
        :param value: The value to be stored.
        """
        self._data[key] = value
        self.save_data()

    def __getitem__(self, key: str):
        """
        Retrieves the value for a given key from the database.

        :param key: The key whose value is to be retrieved.
        :return: The value associated with the given key.
        """
        self.reload_data()
        value = self._data.get(key)
        if isinstance(value, dict):
            return NestedDict(self, [key])
        return value

    def __delitem__(self, key: str):
        """
        Deletes the entry associated with the given key from the database and saves the updated data to the JSON file.

        :param key: The key whose entry is to be deleted.
        """
        del self._data[key]
        self.save_data()

    def get(self, key: str):
        """
        Retrieves the value for a given key from the database, similar to __getitem__.

        :param key: The key whose value is to be retrieved.
        :return: The value associated with the given key.
        """
        self.reload_data()
        return self._data.get(key)

    def keys(self, query: str = "") -> list:
        """
        Searches for and returns a list of keys that match a given query string or regex pattern.

        :param query: A string or regex pattern to match against the keys. If empty, all keys are returned.
        :return: A list of keys that match the query.
        """
        if not query:
            query = ""

        # Trying to compile the query into a regex pattern. If it fails, treat it as a normal string.
        try:
            pattern = re.compile(query)
        except re.error:
            pattern = None

        matching_keys = [key for key in list(self._data.keys()) if (pattern.search(key) if pattern else query in key)]

        return matching_keys


class NestedDict(MutableMapping):
    """A helper class to manage nested dictionaries within the JsonDB class."""

    def __init__(self, parent, path):
        """
        Initializes a NestedDict instance.

        :param parent: The parent JsonDB instance.
        :param path: A list representing the path to the nested dictionary.
        """
        self.parent = parent
        self.path = path

    def _resolve_path(self):
        """
        Resolves the path to the nested dictionary within the parent dictionary.

        :return: The dictionary at the end of the path.
        """
        d = self.parent._data
        for key in self.path:
            d = d.setdefault(key, {})
        return d

    def __getitem__(self, key):
        """
        Retrieves the value for a given key from the nested dictionary.

        :param key: The key to retrieve the value for.
        :return: The value associated with the key.
        """
        resolved = self._resolve_path()
        value = resolved[key]
        if isinstance(value, dict):
            return NestedDict(self.parent, self.path + [key])
        return value

    def __setitem__(self, key, value):
        """
        Sets the value for a given key in the nested dictionary and saves the data to the JSON file.

        :param key: The key to set the value for.
        :param value: The value to set.
        """
        resolved = self._resolve_path()
        resolved[key] = value
        self.parent.save_data()

    def __delitem__(self, key):
        """
        Deletes the key-value pair for a given key from the nested dictionary and saves the data to the JSON file.

        :param key: The key to delete the value for.
        """
        resolved = self._resolve_path()
        del resolved[key]
        self.parent.save_data()

    def __iter__(self):
        """
        Returns an iterator over the keys of the nested dictionary.

        :return: An iterator over the keys of the nested dictionary.
        """
        resolved = self._resolve_path()
        return iter(resolved)

    def __len__(self):
        """
        Returns the number of items in the nested dictionary.

        :return: The number of items in the nested dictionary.
        """
        resolved = self._resolve_path()
        return len(resolved)

    def get(self, key, default=None):
        """
        Retrieves the value for a given key from the nested dictionary. If the key does not exist, returns the default value.

        :param key: The key to retrieve the value for.
        :param default: The default value to return if the key does not exist.
        :return: The value associated with the key, or the default value if the key does not exist.
        """
        resolved = self._resolve_path()
        return resolved.get(key, default)

    def __repr__(self):
        """
        Returns a string representation of the nested dictionary.

        :return: A string representation of the nested dictionary.
        """
        return repr(self._resolve_path())
