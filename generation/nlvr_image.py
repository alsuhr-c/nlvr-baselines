""" Class definitin of an NLVR image and its components."""
import json
import copy
import svgwrite

from enum import Enum
from PIL import Image, ImageDraw


NUM_BOXES = 3
BOX_OBJECT_RATIO = 10  # Ratio of box dimensions (assumed a square) to the smallest object size.


class ImageType(Enum):
    SCATTER = 1
    TOWER = 2


class Shape(Enum):
    CIRCLE = 1
    TRIANGLE = 2
    SQUARE = 3


class Color(Enum):
    YELLOW = 1
    BLACK = 2
    BLUE = 3

    def as_rgb(self):
        if self == Color.YELLOW:
            return 255, 255, 12, 255
        elif self == Color.BLACK:
            return 0, 0, 0, 255
        elif self == Color.BLUE:
            return 15, 131, 255, 255

    def as_hex(self):
        if self == Color.YELLOW:
            return "#FFFF0C"
        elif self == Color.BLACK:
            return "#000000"
        elif self == Color.BLUE:
            return "#0F83FF"


class Size(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    
    def as_int(self):
        if self == Size.SMALL:
            return 1
        elif self == Size.MEDIUM:
            return 2
        elif self == Size.LARGE:
            return 3


def distance(o1, o2):
    if o1 == o2:
        return 0
    ho1o2 = o2.x_pos - (o1.x_pos + o1.size.as_int() * 10)
    ho2o1 = o1.x_pos - (o2.x_pos + o2.size.as_int() * 10)
    h_dist = max([ho1o2, ho2o1])

    vo1o2 = o2.y_pos - (o1.y_pos + o1.size.as_int() * 10)
    vo2o1 = o1.y_pos - (o2.y_pos + o2.size.as_int() * 10)

    v_dist = max([vo1o2, vo2o1])

    return max(h_dist, v_dist)


class NLVRObject():
    def __init__(self, shape, color, size, x_pos, y_pos, box):
        self.shape = shape
        self.color = color
        self.size = size
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.box = box

    def set_box(self, box):
        self.box = box

    def is_touching(self, other_object):
        return other_object.box == self.box and self is not other_object and distance(self, other_object) <= 2

    def touching_bottom(self):
        return self.y_pos + self.size.as_int() == 100

    def touching_top(self):
        return self.y_pos == 0

    def touching_left(self):
        return self.x_pos == 0

    def touching_right(self):
        return self.x_pos + self.size.as_int() == 100

    def touching_wall(self):
        return self.touching_bottom() or self.touching_top() or self.touching_left() or self.touching_right()

    def as_dict(self):
        return {"shape": str(self.shape),
                "color": str(self.color),
                "size": str(self.size),
                "x_pos": str(self.x_pos),
                "y_pos": str(self.y_pos)}

    def copy(self):
        return copy.deepcopy(self)

    def set_position(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos

    def is_top(self):
        return self.y_pos <= min([obj.y_pos for obj in self.box])

    def is_bottom(self):
        return self.y_pos >= max([obj.y_pos for obj in self.box])


def object_from_dict(dictionary, box):
    shape = eval(dictionary["shape"])
    color = eval(dictionary["color"])
    size = eval(dictionary["size"])
    x_pos = int(dictionary["x_pos"])
    y_pos = int(dictionary["y_pos"])

    return NLVRObject(shape, color, size, x_pos, y_pos, box)


class NLVRImage:
    """Contains an NLVR image."""
    def __init__(self, boxes, image_type):
        self.boxes = boxes
        self.image_type = image_type

    def as_list(self):
        """Returns the list representation of the image.
        
        Returns
            list, representing the list representation of the image as a dictionary.
        """
        flat_image = []
        for box in self.boxes:
            flat_box = []
            for obj in box:
               flat_box.append(obj.as_dict())
            flat_image.append(sorted(flat_box, key=lambda x: x["y_pos"]))
        
        return sorted(flat_image, key=lambda x: len(x))

    def objects(self):
        """Returns all objects in the environment.

        Returns:
            list of NLVRObject, containing all objects in the environment.
        """
        all_objects = []
        for box in self.boxes:
            all_objects.extend([obj.copy() for obj in box])
        return all_objects

    def json(self):
        """Returns the JSON representation of the image.
        
        Returns
            str, representing the JSON representation of the image as a dictionary.
        """
        return json.dumps(self.as_list())

    def svg(self, box_size, filename, order=[0, 1, 2]):
        drawing = svgwrite.Drawing(filename=filename)
        for i in range(len(self.boxes)):
            x_start = int(box_size * i + box_size * i / 2)
            drawing.add(drawing.rect(insert=(x_start, 0),
                                     size=(box_size, box_size),
                                     fill="#C9C9C9"))
        for i in range(len(self.boxes) - 1):
            x_start = int(box_size * (i + 1) + box_size * i / 2)
            drawing.add(drawing.rect(insert=(x_start, 0),
                                     size=(box_size / 2, box_size),
                                     fill="#6D6D6D"))
        for box_idx, i in enumerate(order):
            box = self.boxes[i]
            x_offset = int(box_size * box_idx + box_size * box_idx / 2)
            for obj in box:
                x_start = x_offset + obj.x_pos
                y_start = obj.y_pos
                actual_size = obj.size.as_int() * box_size / BOX_OBJECT_RATIO
                x_end = x_start + actual_size
                y_end = y_start + actual_size
                
                if obj.shape == Shape.CIRCLE:
                    radius = int(actual_size / 2)
                    center = (x_start + radius, y_start + radius)
                    drawing.add(drawing.ellipse(center=center,
                                                r=(radius, radius),
                                                fill=obj.color.as_hex()))

                elif obj.shape == Shape.SQUARE:
                    drawing.add(drawing.rect(insert=(x_start, y_start),
                                             size=(actual_size, actual_size),
                                             fill=obj.color.as_hex()))
                elif obj.shape == Shape.TRIANGLE:
                    bottom_left = (x_start, y_end)
                    bottom_right = (x_end, y_end)
                    top = (x_end - int((x_end - x_start) / 2), y_start)
                    drawing.add(drawing.polygon(points=[bottom_left, bottom_right, top],
                                                fill=obj.color.as_hex()))

        drawing.save()

    def png(self, box_size, filename):
        """Renders the NLVRImage as a PNG."""
        img = Image.new('RGB', (int(box_size * len(self.boxes) + box_size * (len(self.boxes) - 1)/2), box_size))
        draw = ImageDraw.Draw(img)

        # Draw the base image: three boxes and two separating rectangles.
        for i in range(len(self.boxes)):
            x_start = int(box_size * i + box_size * i / 2)
            x_end = int(x_start + box_size)
            draw.rectangle([x_start, 0, x_end, box_size], fill=(201, 201, 201, 255))

        for i in range(len(self.boxes) - 1):
            x_start = int(box_size * (i + 1) + box_size * i / 2)
            x_end = int(x_start + box_size / 2)
            draw.rectangle([x_start, 0, x_end, box_size], fill=(109, 109, 109, 255))

        # Draw the objects in the boxes.
        for i, box in enumerate(self.boxes):
            x_offset = int(box_size * i + box_size * i / 2)
            for obj in box:
                x_start = x_offset + obj.x_pos
                y_start = obj.y_pos
                x_end = x_start + obj.size.as_int() * box_size / BOX_OBJECT_RATIO
                y_end = y_start + obj.size.as_int() * box_size / BOX_OBJECT_RATIO

                if obj.shape == Shape.CIRCLE:
                    draw.ellipse([x_start, y_start, x_end, y_end], fill=obj.color.as_rgb())    
                elif obj.shape == Shape.SQUARE:
                    draw.rectangle([x_start, y_start, x_end, y_end], fill=obj.color.as_rgb())
                elif obj.shape == Shape.TRIANGLE:
                    bottom_left = (x_start, y_end)
                    bottom_right = (x_end, y_end)
                    top = (x_end - int((x_end - x_start) / 2), y_start)
                    draw.polygon([bottom_left, bottom_right, top], fill=obj.color.as_rgb())
                    pass

        img.save(filename, "PNG")
    
    def is_equal(self, other_image):
        return self.json() == other_image.json()        


def image_from_list(box_list, image_type):
    new_boxes = []
    for box in box_list:
        new_box = []
        for obj in box:  
            new_box.append(object_from_dict(obj, new_box))
        new_boxes.append(new_box)

    return NLVRImage(new_boxes, image_type)
