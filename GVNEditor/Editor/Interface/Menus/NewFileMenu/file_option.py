from PyQt5.QtWidgets import QListWidgetItem


class FileOption(QListWidgetItem):
    def __init__(self, settings, icon, file_type, display_text, description_text, parent):
        super().__init__(icon, display_text, parent)

        self.setFont(settings.paragraph_font)

        self.file_type = file_type
        self.description_text = description_text

    def GetDescription(self):
        """ Returns the description text for this entry """
        return self.description_text

    def GetFileType(self):
        """ Returns the file type stored in this class """
        return self.file_type
