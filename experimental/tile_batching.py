import json

from pygame import Vector2
import time


class Rect:
    def __init__(self, pos, size):
        self.pos = Vector2(pos)
        self.size = Vector2(size)


class Tile(Rect):
    ...


class Air(Rect):
    ...


class Batch:
    def __init__(self, batch_type, pos, size):
        self.type = batch_type
        self.pos = Vector2(pos)
        self.size = Vector2(size)

    def __str__(self):
        return f"type: {self.type.__name__}, pos: {self.pos}, size:{self.size}"

    def increment_x(self):
        self.pos.x += 1
        self.size.x += 1

    def convert(self):
        return self.type(self.pos * tile_size, self.size * tile_size)


IDs = {
    "#": Tile,
    " ": Air
}

tile_size = Vector2(32, 32)

with open("../gamedata/levels/0_0.json") as file:
    example_level = json.loads(file.read())["layout"]


def unpack_level(level):
    batches = []  # set()

    for y, row in enumerate(level):
        temp_batches = [Batch(None, (0, 0), (0, 0))]
        for x, tile in enumerate(row):
            tile_type = IDs[tile]
            if temp_batches[-1].type != tile_type:
                temp_batches.append(Batch(tile_type, (x, y), (1, 1)))
            else:
                temp_batches[-1].size.x += 1

        for batch in temp_batches:
            if batch.type is None:
                continue
            batches.append(batch)

    objects = {}
    for i, batch in enumerate(batches):
        objects[f"batch_{i}"] = batch.convert()

    return objects


if __name__ == "__main__":
    start = time.time()
    unpack_level(example_level)
    end = time.time()
    print(f"done in {(end - start) * 1000}ms")
