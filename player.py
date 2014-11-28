import libtcodpy as libtcod
from config import *
import logging

from event import Event
from thing import Thing

logger = logging.getLogger('thing')

class Player(Thing):
    def __init__(self,*args,**kwargs):
        Thing.__init__(self,*args,**kwargs)
        self.materials = {}

    def harvest_corpse(self):
        """Harvests corpse at player tile, returns EVENT_HARVEST
        If there were no corpses, returns EVENT_NONE"""
        try:
            thing = filter(lambda thing: thing.creature and not thing.creature.alive, self.owner.get_things_at(*self.pos))[0]
            self.add_materials(thing.creature.materials)
            self.owner.things.remove(thing)
            return Event(EVENT_HARVEST, majority_material=thing.creature.majority_material)
        except IndexError:
            return Event(EVENT_NONE)

    def add_materials(self,materials):
        for material in materials:
            if material in self.materials:
                self.materials[material] += materials[material]
            else:
                self.materials[material] = materials[material]