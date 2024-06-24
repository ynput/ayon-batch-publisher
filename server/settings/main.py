from ayon_server.settings import BaseSettingsModel, SettingsField



class ProductTypeSmartSelectModel(BaseSettingsModel):
    _layout = "expanded"
    name: str = SettingsField("", title="Resulting product type")
    extensions: list[str] = SettingsField(
        default_factory=list, title="Extensions"
    )


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
    """Use regex pattern for file name and path or extensions to get product type"""  # noqa
    pattern_to_product_type: list[PatternToProductTypeModel] = SettingsField(
        default_factory=list,
        title="File pattern to product type",
        description="Insert regex pattern to decypher product type from "
                    "published files"
    )

    extensions_to_product_type: list[ProductTypeSmartSelectModel] = (
        SettingsField(
            default_factory=list,
            title="Extensions to product type",
            description="Set extensions matching to product type"
        )
    )


DEFAULT_BATCHPUBLISHER_SETTING = {
  "pattern_to_product_type": [
    {
      "pattern": ".*/fbx",
      "is_sequence": False,
      "product_type": "model"
    }
  ],
  "extensions_to_product_type": [
    {
      "name": "render",
      "extensions": [
        ".exr",
        ".dpx",
        ".tif",
        ".tiff",
        ".jpg",
        ".jpeg"
      ]
    },
    {
      "name": "pointcache",
      "extensions": [
        ".abc"
      ]
    },
    {
      "name": "camera",
      "extensions": [
        ".abc",
        ".fbx"
      ]
    },
    {
      "name": "reference",
      "extensions": [
        ".mov",
        ".mp4",
        ".mxf",
        ".avi",
        ".wmv"
      ]
    },
    {
      "name": "workfile",
      "extensions": [
        ".nk",
        ".ma",
        ".mb",
        ".hip",
        ".sfx",
        ".mocha",
        ".psd"
      ]
    }
  ]
}

