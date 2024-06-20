from ayon_server.settings import BaseSettingsModel, SettingsField



class PatternToProductTypeModel(BaseSettingsModel):
    """Regular expression pattern to published product type"""
    _layout = "expanded"
    pattern: str = SettingsField(
        "",
        title="Regex pattern"
    )
    is_sequence: bool = SettingsField(
        True,
        title="Is sequence"
    )
    product_type: str = SettingsField(
        "",
        title="Resulting product type"
    )


class BatchpublisherSettings(BaseSettingsModel):
    """BatchPublisher Project Settings."""
    pattern_to_product_type: list[PatternToProductTypeModel] = SettingsField(
        default_factory=list,
        title="File pattern to product type",
        description="Insert regex pattern to decypher product type from "
                    "published files"
    )

    extensions_to_product_type:


DEFAULT_BATCHPUBLISHER_SETTING = {
  "pattern_to_product_type": [
    {
      "pattern": ".*fbx",
      "is_sequence": False,
      "product_type": "model"
    }
  ]
}
