# ayon-batchpublisher
Addon for batch publisher tool allowing multiple products publishing.

Tools tries to guess final product type either by configured mapping for regular expression match in file path,
`ayon+settings://batchpublisher/pattern_to_product_type` or by extension to product type configured in `ayon+settings://batchpublisher/extensions_to_product_type`

It runs then regular Pyblish publish process.

Todo:
-----
- implement publish via Deadline
- make publishing process more abstracted to create some API
