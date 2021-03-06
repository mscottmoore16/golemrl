from config import *

from creature import Creature
from event import Event

class BodyPart(Creature):
    def __init__(self,golem,name,
                 word_slots,
                 health,agility,armor,perception,size,strength,speed,
                 vital=False,
                 traits=[]):
        self.golem = golem
        self.name = name
        self.base_max_health = health
        self.health = health
        self.vital = vital
        self.traits = traits
        self.words = [None for i in range(word_slots)]

        self.status_effects = []

        self.base_word_slots = word_slots
        self.base_agility = agility
        self.base_armor = armor
        self.base_perception = perception
        self.base_size = size
        self.base_strength = strength
        self.base_speed = speed

    @property
    def entity(self):
        return self.golem.owner
    @property
    def game(self):
        return self.entity.game

    @property
    def max_health(self):
        return self.base_max_health + self.health_mod

    @property
    def agility(self):
        return self.base_agility + self.agility_mod
    @property
    def armor(self):
        return self.base_armor + self.armor_mod
    @property
    def perception(self):
        return self.base_perception + self.perception_mod
    @property
    def size(self):
        return self.base_size + self.size_mod
    @property
    def strength(self):
        return self.base_strength + self.strength_mod
    @property
    def speed(self):
        return self.base_speed + self.speed_mod
    @property
    def word_slots_mod(self):
        return sum([se.word_slots_mod for se in self.status_effects])
    @property
    def word_slots(self):
        slots = self.base_word_slots + self.word_slots_mod
        return max(0,slots)


    @property
    def full_name(self):
        full_name = self.name
        for trait in self.traits:
            if trait.prefix:
                full_name = trait.prefix + ' ' + full_name
            if trait.suffix:
                full_name = full_name + ' ' + trait.suffix
        return full_name

    @property
    def intact(self):
        return self.health > 0
    @property
    def damaged(self):
        return self.health < self.max_health

    def update(self):
        se_to_remove = []
        for se in self.status_effects:
            remove = se.update()
            if remove:
                se_to_remove.append(se)
        for se in se_to_remove:
            self.remove_status_effect(se)

    def take_damage(self,damage_dealt,degree):
        if self.intact:
            damage_received = damage_dealt*degree - self.armor
            if damage_received < 0: damage_received = 0
            self.health -= damage_received
            if self.health <= 0:
                self.health = 0
                return (damage_received, self.vital)
            else:
                return (damage_received, False)
        else:
            return (0,False)

    def heal(self,amount):
        if self.health+amount <= self.max_health:
            self.health += amount

    def check_word_slots(self):
        while self.word_slots > len(self.words):
            self.words.append(None)
        while self.word_slots < len(self.words):
            if None in self.words:
                self.words.remove(None)
            else:
                self.erase(self.game.rng.choose(self.words))

    def inscribe(self,word):
        if word not in self.words and None in self.words:
            self.words[self.words.index(None)] = word
            return self.entity.notify(Event(EVENT_INSCRIBE,
                                           actor = self.entity,
                                           body_part = self,
                                           word = word))

    def erase(self,word):
        if word in self.words:
            self.words[self.words.index(word)] = None
            return self.entity.notify(Event(EVENT_ERASE,
                                           actor = self.entity,
                                           body_part = self,
                                           word = word))

    def has_word(self,word):
        return word in self.words

    def can_add(self,trait):
        properly_applied = trait.applied_to in self.name
        requirements_met = (not trait.replaces or
                            trait.replaces in self.traits)

        already_applied = trait in self.traits
        for t in self.traits:
            if t.in_replace_chain(trait):
                already_applied = True

        canceled = False
        for t in self.traits:
            if trait in t.cancels:
                not_canceled = True

        return (properly_applied and
                requirements_met and
                not already_applied and
                not canceled and
                trait.cost != None)

    def can_remove(self,trait):
        return (trait in self.traits and
                trait.removal_cost != None)

    def add_trait(self,trait,force=False):
        if force or self.can_add(trait):
            if trait.replaces:
                self.remove_trait(trait.replaces)
            self.traits.append(trait)
            self.add_status_effect(trait.effect)
            #self.health += trait.health_mod
            self.check_word_slots()
            if not force: #WARNING, this might cause trouble, but for now it seems like we're best not raising an event when we force a trait (ie player starting traits, and a trait that's added as a result of trait that replaced it being removed
                return self.entity.notify(Event(EVENT_ADD_TRAIT,
                                               actor=self.entity,
                                               body_part=self,
                                               trait=trait) )
        else: return Event(EVENT_NONE)

    def remove_trait(self,trait,force=False):
        if force or self.can_remove(trait):
            if trait.replaces:
                self.add_trait(trait.replaces, True)
            self.traits.remove(trait)
            self.remove_status_effect(trait.effect)
            #self.health -= trait.health_mod
            self.check_word_slots()
            if not force:
                return self.entity.notify(Event(EVENT_REMOVE_TRAIT,
                                               actor = self.entity,
                                               body_part = self,
                                               trait = trait))
