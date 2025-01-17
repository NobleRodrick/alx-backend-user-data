#!/usr/bin/env python3
"""
Base module.
"""
import uuid
from os import path
import json
from datetime import datetime
from typing import TypeVar, List, Iterable


TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATA = {}


class Base():
    """
    Base class.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """
        Initialize a Base instance.
        """
        defined_class = str(self.__class__.__name__)
        if DATA.get(defined_class) is None:
            DATA[defined_class] = {}

        self.id = kwargs.get('id', str(uuid.uuid4()))
        if kwargs.get('created_at') is not None:
            self.created_at = datetime.strptime(kwargs.get('created_at'),
                                                TIMESTAMP_FORMAT)
        else:
            self.created_at = datetime.utcnow()
        if kwargs.get('updated_at') is not None:
            self.updated_at = datetime.strptime(kwargs.get('updated_at'),
                                                TIMESTAMP_FORMAT)
        else:
            self.updated_at = datetime.utcnow()

    def __eq__(self, other: TypeVar('Base')) -> bool:
        """
        Equality.
        """
        if type(self) != type(other):
            return False
        if not isinstance(self, Base):
            return False
        return (self.id == other.id)

    def to_json(self, for_serialization: bool = False) -> dict:
        """
        Convert the object a JSON dictionary.
        """
        result = {}
        for key, value in self.__dict__.items():
            if not for_serialization and key[0] == '_':
                continue
            if type(value) is datetime:
                result[key] = value.strftime(TIMESTAMP_FORMAT)
            else:
                result[key] = value
        return result

    @classmethod
    def load_from_file(cls):
        """
        Load all objects from file.
        """
        defined_class = cls.__name__
        file_path = ".db_{}.json".format(defined_class)
        DATA[defined_class] = {}
        if not path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            objs_json = json.load(f)
            for obj_id, obj_json in objs_json.items():
                DATA[defined_class][obj_id] = cls(**obj_json)

    @classmethod
    def save_to_file(cls):
        """
        Save all objects to file.
        """
        defined_class = cls.__name__
        file_path = ".db_{}.json".format(defined_class)
        objs_json = {}
        for obj_id, obj in DATA[defined_class].items():
            objs_json[obj_id] = obj.to_json(True)

        with open(file_path, 'w') as f:
            json.dump(objs_json, f)

    def save(self):
        """
        Save current object.
        """
        defined_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()
        DATA[defined_class][self.id] = self
        self.__class__.save_to_file()

    def remove(self):
        """
        used to remove an object.
        """
        defined_class = self.__class__.__name__
        if DATA[defined_class].get(self.id) is not None:
            del DATA[defined_class][self.id]
            self.__class__.save_to_file()

    @classmethod
    def count(cls) -> int:
        """
        will count all objects
        """
        defined_class = cls.__name__
        return len(DATA[defined_class].keys())

    @classmethod
    def all(cls) -> Iterable[TypeVar('Base')]:
        """
        Will return all objects
        """
        return cls.search()

    @classmethod
    def get(cls, id: str) -> TypeVar('Base'):
        """
        Return one object by ID.
        """
        defined_class = cls.__name__
        return DATA[defined_class].get(id)

    @classmethod
    def search(cls, attributes: dict = {}) -> List[TypeVar('Base')]:
        """
        Search all objects with matching attributes.
        """
        defined_class = cls.__name__
        def _search(obj):
            if len(attributes) == 0:
                return True
            for k, v in attributes.items():
                if (getattr(obj, k) != v):
                    return False
            return True

        return list(filter(_search, DATA[defined_class].values()))
