import pygame

from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.save_slot import SaveSlot


class SavesList(Renderable):
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        self.bounds = [0, 0]

        # Override certain keys
        renderable_data['center_align'] = False
        renderable_data['key'] = '!&SAVES_LIST&!'  # Create a unique key as nothing should attempt to reference it

        # Run parent implementation which will perform recalculations with the aforementioned parameters
        super().__init__(renderable_data, parent, process_data)
        self.visible = False

        # Create a save slot equal to the configured total in the engine settings
        for slot_id in range(0, settings.save_slots):
            new_slot = SaveSlot(
                {
                    'key': f"!&SAVE_SLOT_{slot_id}&!",
                    'position': [0.1, self.renderable_data['slot_spacing'] * slot_id],
                    'center_align': False,
                    'z_order': self.renderable_data['z_order'] + 2,
                    'bounds': [1.0, 1.0]  # Always use the full space of the list
                },
                slot_id=slot_id,
                parent=self
            )

            self.children.append(new_slot)
            settings.scene.active_renderables.Add(new_slot)

    def ApplyRenderableData(self):
        if 'bounds' in self.renderable_data:
            self.bounds = self.renderable_data['bounds']
            self.surface = pygame.Surface(self.ConvertNormToScreen(self.bounds))

        # Run the parent implementation to ensure all changes are considered, and the surfaces are recalculated
        super().ApplyRenderableData()
