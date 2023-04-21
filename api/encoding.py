from dataclasses import asdict
from enum import Enum
import humps
import json


class ApiJsonEncoder:
    @staticmethod
    def encode(data, level: int = 0):
        def dict_factory(entries):
            def convert(value):
                # Use value of enum object
                if isinstance(value, Enum):
                    return value.value
                # Convert all elements of a tuple
                if isinstance(value, tuple):
                    return tuple(convert(v) for v in value)
                # Convert all elements of a list
                if isinstance(value, list):
                    return [convert(v) for v in value]
                return value
            # Remove "private" properties based on property name prefix
            return dict([(k, convert(v)) for (k, v) in entries if not k.startswith("_")])
        if isinstance(data, tuple) or isinstance(data, list):
            data = tuple(ApiJsonEncoder.encode(d, level + 1) for d in data)
        else:
            data = None if data is None else humps.camelize(
                asdict(data, dict_factory=dict_factory)) if not isinstance(data, dict) else data
        return json.dumps(data, indent=2) if level == 0 else data
