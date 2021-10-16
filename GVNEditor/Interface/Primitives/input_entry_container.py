from GVNEditor.Interface.Primitives.input_entry_base import InputEntryBase


class InputEntryContainer(InputEntryBase):
    def __init__(self, settings, children: list, refresh_func=None):
        super().__init__(settings, refresh_func)

    #@TODO: Does this class uh...need to exist? It basically does nothing special
    def Get(self):
        pass

    def Set(self, data, toggle_global=True) -> None:
        pass
