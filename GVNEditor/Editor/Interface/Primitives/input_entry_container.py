from Editor.Interface.Primitives.input_entry_base import InputEntryBase


class InputEntryContainer(InputEntryBase):
    def __init__(self, settings, children: list, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

    def Get(self):
        pass

    def Set(self, data, toggle_global=True) -> None:
        pass

    def MakeUneditable(self):
        pass
