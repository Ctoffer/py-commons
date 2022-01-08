class Foo:
    pass

frozen_instances = set()

def __setattr__(self, name, value):
    if self in frozen_instances:
        raise AttributeError(f"Can not set '{name}' to '{value}' on instance {type(self).__name__}@{hex(id(self))}")

f = Foo()
frozen_instances.add(f)
Foo.__setattr__ = __setattr__
f.x = 5
print(f.x)