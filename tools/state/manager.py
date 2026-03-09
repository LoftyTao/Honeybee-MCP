import json
import os

from honeybee.model import Model

from .energy_resources import (
    build_serializable_model_dict,
    empty_energy_resource_store,
    load_energy_resource_store,
    strip_custom_energy_fields,
)
from .radiance_resources import (
    empty_radiance_resource_store,
    load_radiance_resource_store,
    merge_model_dict_with_radiance_resources,
)


class ModelManager:
    """Global model state shared by all tools."""

    def __init__(self):
        self.model = None
        self.source = None
        self.source_name = None
        self.energy_resource_store = empty_energy_resource_store()
        self.radiance_resource_store = empty_radiance_resource_store()

    def clear(self):
        self.model = None
        self.source = None
        self.source_name = None
        self.energy_resource_store = empty_energy_resource_store()
        self.radiance_resource_store = empty_radiance_resource_store()

    def load(self, hb_file: str, cleanup_irrational: bool = False):
        raw_dict = None
        if hb_file and os.path.exists(hb_file) and hb_file.lower().endswith(".hbjson"):
            with open(hb_file, "r", encoding="utf-8") as fp:
                raw_dict = json.load(fp)
            self.model = Model.from_dict(
                strip_custom_energy_fields(raw_dict),
                cleanup_irrational=cleanup_irrational,
            )
        else:
            self.model = Model.from_file(hb_file, cleanup_irrational=cleanup_irrational)
        self.source = "file"
        self.source_name = hb_file
        source_dict = raw_dict if raw_dict is not None else self.model.to_dict()
        self.energy_resource_store = load_energy_resource_store(source_dict, self.model)
        self.radiance_resource_store = load_radiance_resource_store(source_dict, self.model)
        return self.model

    def load_from_dict(
        self,
        data: dict,
        cleanup_irrational: bool = False,
        source: str = "dict",
        source_name: str = None,
    ):
        clean_data = strip_custom_energy_fields(data)
        self.model = Model.from_dict(clean_data, cleanup_irrational=cleanup_irrational)
        self.source = source
        self.source_name = source_name or data.get("identifier", "unknown")
        self.energy_resource_store = load_energy_resource_store(data, self.model)
        self.radiance_resource_store = load_radiance_resource_store(data, self.model)
        return self.model

    def serialized_model_dict(self):
        serialized = build_serializable_model_dict(self.model, self.energy_resource_store)
        return merge_model_dict_with_radiance_resources(
            serialized,
            self.model,
            self.radiance_resource_store,
        )


manager = ModelManager()
