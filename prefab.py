class Prefab:
    def __init__(self,prefab_id, map_data, char_to_tile):
        self.prefab_id = prefab_id
        self.map_data = map_data
        self.char_to_tile = char_to_tile

    @property
    def h(self):
        return len(self.map_data)
    @property
    def w(self):
        return len(self.map_data[0])

    def get_map_data(self,rng,flip_x=False,flip_y=False):
        data = []
        char_varieties = {}
        for s in self.map_data:
            row=[]
            for char in s:
                if char in self.char_to_tile:
                    if type(self.char_to_tile[char])==list:
                        if char not in char_varieties:
                            char_varieties[char]=rng.get_int(0,len(self.char_to_tile[char]))
                        row.append(self.char_to_tile[char][char_varieties[char]])
                    else:
                        row.append(self.char_to_tile[char])
                else:
                    row.append(None)
            data.append(row)
        if flip_x:
            for row in data:
                row.reverse()
        if flip_y:
            data.reverse()
                
        return data
