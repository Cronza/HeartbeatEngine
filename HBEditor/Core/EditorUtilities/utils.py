import yaml
from PyQt6 import QtGui
from HBEditor.Core.Logger import logger


def ValidateClipboard(source_name: str, data_type: any) -> any:
    """
    Validates the data currently held by the clipboard before returning it.

    The data held by the clipboard is required to be structured as: {'source': '<string_identifier>', 'data': '<any>'}.
    This format ensures the context is respected through checking the 'source' identifier, and ensuring the data is of
    the type 'data_type'
    """
    data = QtGui.QGuiApplication.clipboard().text()

    if data:
        try:
            conv_data = yaml.load(data, Loader=yaml.FullLoader)
        except Exception as exc:
            logger.Log("Failed to paste from clipboard - Data invalid")
            return None

        if isinstance(conv_data, dict):
            if 'source' not in conv_data or 'data' not in conv_data:
                logger.Log("Failed to paste from clipboard - Data invalid")
                return None

            elif conv_data['source'] != source_name:
                logger.Log("Failed to paste from clipboard - Data invalid for current context")
                return None

            elif not isinstance(conv_data['data'], data_type):
                logger.Log("Failed to paste from clipboard - Data not of the expected data")
                return None

            # Validation complete. Return the data
            return conv_data['data']
