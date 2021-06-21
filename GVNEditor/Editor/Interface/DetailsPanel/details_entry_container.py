from Editor.Interface.DetailsPanel.details_entry_base import DetailsEntryBase


class DetailsEntryContainer(DetailsEntryBase):
    def __init__(self, settings, children: list, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

    def Get(self):
        pass

    def Set(self, data, toggle_global=True) -> None:
        pass

    def MakeUneditable(self):
        pass

    #def AddEntry(self, entry):
        #""" Given a tuple of <entry_name>, <data_widget>, add them to the container """

        # Add a new, empty row
        #self.input_widget.insertRow(self.input_widget.rowCount())

        # Populate the row with each element of this particular detail
        #new_row = self.input_widget.rowCount() - 1
        #self.input_widget.setItem(new_row, 0, entry[0])
        #self.input_widget.setCellWidget(new_row, 1, entry[1])

        #self.input_widget.resizeRowToContents(new_row)


        # TEMP
        #for row in range(0, self.input_widget.rowCount()):
        #    thing = self.input_widget.cellWidget(row, 1)
        #    print(thing.height())
        #    self.input_widget.setMinimumSize(500,500)
            #self.input_widget.size().setHeight((500))
            #self.input_widget.setFixedHeight(500)
            #self.input_widget.adjustSize()
            #self.input_widget.sizeAdjustPolicy()

        #self.input_widget.adjustSize()
        #print(self.input_widget.sizeHint())

        #self.



