import toml


class TomlConfig:
    def __init__(self, base_filename: str = 'config.toml', updated_filename: str = 'upd_config.toml') -> None:
        self._base_filename = base_filename
        self._base_toml = toml.load(self._base_filename)
        self._updated_filename = updated_filename
        self._updated_toml = toml.load(self._base_filename)
        self._param_types = dict()
        self._set_param_types()
        self._all_keys = list()
        self._set_all_keys()

    def _set_param_types(self):
        with open(self._base_filename) as cfile:
            for line in cfile:
                if line.startswith('#') or line.startswith('[') or line == "\n":
                    continue
                line_details = line.split()
                if line_details[1] == '=':
                    self._param_types[line_details[0]] = line_details[-1].strip()

    def _set_all_keys(self):
        for section in self._base_toml.values():
            for k in section.keys():
                self._all_keys.append(k)

    def _pretty_type(self, key: str, value):
        if self._param_types[key].startswith('u') or self._param_types[key] == 'Epoch':
            return int(value)
        elif self._param_types[key].startswith('f'):
            return value
        else:
            print(self._param_types[key])
            raise RuntimeError('Unknown type in .toml file')

    def get(self):
        return self._base_toml

    def get_all_keys(self) -> list:
        return self._all_keys

    def get_values_list(self) -> list:
        mapping = dict()
        for section in self._base_toml.values():
            for key, value in section.items():
                mapping[key] = value
        result = list()
        for key in self._all_keys:
            result.append(mapping[key])
        return result

    def reset(self):
        self._updated_toml = toml.load(self._base_filename)

    def save(self):
        with open(self._updated_filename, 'w') as file:
            updated_string = toml.dump(self._updated_toml, file)
        return updated_string

    def set(self, updated_data: dict):
        self.reset()
        updated_data_set = set(updated_data)
        for section in self._updated_toml.values():
            sections_keys = set(section.keys()) & updated_data_set
            for key in sections_keys:
                section[key] = self._pretty_type(key, updated_data[key])
        self.save()

    def set_values_list(self, updated_values_array: list):
        self.reset()
        new_values = dict(zip(self._all_keys, updated_values_array))
        for section in self._updated_toml.values():
            for key in section.keys():
                section[key] = self._pretty_type(key, new_values[key])
        self.save()

    def for_each(self, func):
        self.reset()
        for section in self._updated_toml.values():
            for key, value in section.items():
                section[key] = self._pretty_type(key, func(key, value))
                yield self.save()
                section[key] = value
        self.reset()

    def for_each_if(self, func, filter_func=lambda _k, _v: True):
        self.reset()
        for section in self._updated_toml.values():
            for key, value in section.items():
                if filter_func(key, value):
                    section[key] = self._pretty_type(key, func(key, value))
                    yield self.save()
                    section[key] = value
        self.reset()


if __name__ == '__main__':
    tml = TomlConfig()
    conf = tml.get()
    tml.save()

    tml.set({
        "NUM_THREADS": 6,
        "DEFAULT_TICKS_PER_SLOT": 1020,
        "ITER_BATCH_SIZE": 500,
        "RECV_BATCH_MAX_CPU": 21,
        "DEFAULT_HASHES_PER_SECOND": 34343434334,
        "DEFAULT_TICKS_PER_SECOND": 790,
    })

    for _ in tml.for_each_if(lambda k, v: v * 1.1):
        input('req_')
        print('next')
