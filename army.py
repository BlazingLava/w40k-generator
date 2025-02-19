from codex import Codex
from enums import Verbose


Battalion_Composition = {
    "HQ": (2, 3),
    "Troop": (3, 6),
    "Elite": (0, 6),
    "Fast_Attack": (0, 3),
    "Heavy_Support": (0, 3),
    "Flyer": (0, 2),
    "Dedicated_Transport": (0, 9e9),
    "Lord_of_War": (0, 0),
    "Fortification": (0, 0),
    "Other": (0, 9e9),
}

Patrol_Composition = {
    "HQ": (1, 3),
    "Troop": (2, 6),
    "Elite": (0, 4),
    "Fast_Attack": (0, 3),
    "Heavy_Support": (0, 3),
    "Flyer": (0, 3),
    "Dedicated_Transport": (0, 9e9),
    "Lord_of_War": (0, 1),
    "Fortification": (0, 0),
    "Other": (0, 9e9),
}


class Army:

    def __init__(self, faction, army_size, force_msu, no_proxy, detachment, verbose):
        self.list = []
        self.codex = Codex(faction)
        self.verbose = verbose

        self.detachment = detachment
        self.max_size = army_size
        self.force_msu = force_msu
        self.no_proxy = no_proxy

        # !!!!!!!!!!!!!!!!!!!!!!!!!!
        # Add other detachment types
        # !!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.detachment == "patrol":
            self.limits = Patrol_Composition
        elif self.detachment == "battalion":
            self.limits = Battalion_Composition

    def flexible_unit_limit(self, flexible_unit_name):
        """Checks a flexible unit's upper limit based on the associatied
        units. For example: A Ghost Ark is allowed per Warrior unit in a
        Necron army; A unit of 2 Cryptothralls is allowed per <Cryptek> in a
        Necron army.
        """
        max_units = 0
        for unit_name in self.codex.data(flexible_unit_name)["units"].split(","):
            unit_count = self.count(unit_name=unit_name.strip())
            max_units += unit_count
        return max_units

    @property
    def size(self):
        """Count the current army size in points.

        :param army_list: [description]
        :type army_list: [type]
        """
        size = 0
        for entry in self.list:
            unit_data = self.codex.data(entry["name"])
            size += entry["qty"] * unit_data["ppm"]
        return size

    @property
    def is_full(self):
        if self.size >= self.max_size:
            return True
        else:
            return False

    def count(self, null=None, unit_type_name=None, unit_name=None):
        """Counts the number of units of either the specified type or with the
        specified name in the army list.
        """
        if null is not None or (unit_type_name is None and unit_name is None):
            raise TypeError("A value must be assigned explicitly to either 'unit_type_name' or 'unit_name'.")

        count = 0
        for entry in self.list:
            unit_data = self.codex.data(entry["name"])
            if unit_type_name is not None and unit_data["cat"] == unit_type_name:
                count += 1
            elif unit_name is not None and unit_data["name"] == unit_name:
                count += 1
        return count

    def check(self, unit_type_name, model_name):
        unit_count = self.count(unit_type_name=unit_type_name)
        model_data = self.codex.data(model_name)
        if model_data["units"] != "None":
            unit_min = self.limits[unit_type_name][0]
            unit_max = self.flexible_unit_limit(model_data["name"])
        else:
            unit_min, unit_max = self.limits[unit_type_name]
        return unit_min, unit_count, unit_max

    @property
    def unit_types(self):
        types = set()
        for entry in self.list:
            types.add(self.codex.unit_type(entry["name"]))
        types = list(types)
        types.sort()
        return types

    def print(self):
        if self.verbose >= Verbose.Info.value:
            print()

        for unit_type in self.unit_types:
            print(f"{unit_type}:")
            for entry in self.list:
                entry_type = self.codex.unit_type(entry["name"])
                if entry_type == unit_type:
                    unit_data = self.codex.data(entry["name"])
                    print(f" - {entry['qty']} {entry['name']}", end="")
                    print(f" ({entry['qty'] * unit_data['ppm']} pts)")
        print(f"\nTotal: {self.size}\n\n")
