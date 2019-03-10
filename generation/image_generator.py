""" Generates four NLVR images for a set considering the rules of image generation. """
from data_structure.nlvr_image import NUM_BOXES, BOX_OBJECT_RATIO, NLVRObject, NLVRImage, ImageType, Shape, Color, Size
from typing import List

import numpy as np
import random

BOX_SIZE = 100
MAX_OBJECTS = {ImageType.SCATTER: 8, ImageType.TOWER: 4}
MAX_NUM_INTERSECTS = 100
MAX_NUM_TRIES = 25


def place_object(existing_objects: List[NLVRObject], size: Size, image_type: ImageType, modify_size: bool = True):
    """ Places an object in a box that contains other objects.

    existing_objects: The objects already in the box.
    size: The size of the object.
    image_type: The type of image (box or scatter image).
    modify_size: Whether the object's size can be modified to get it to fit.
    """
    actual_size: int = size.as_int() * BOX_SIZE / BOX_OBJECT_RATIO
    x_pos: int = -1
    y_pos: int = -1

    if image_type == ImageType.TOWER:
        x_pos = BOX_SIZE / 2 - actual_size / 2
        y_pos = BOX_SIZE - actual_size * (len(existing_objects) + 1) - len(existing_objects)
    else:
        intersects: bool = True
        num_intersects: int = 0

        # Keep trying to place the object for a limited number of times (MAX_NUM_INTERSECTS) before it doesn't
        # intersect with the existing objects.
        while intersects:
            x_pos = random.randint(0, BOX_SIZE - actual_size - 1)
            y_pos = random.randint(0, BOX_SIZE)

            # Modify the size and try again if there have been too many intersections
            if num_intersects > MAX_NUM_INTERSECTS:
                if modify_size:
                    size = Size.SMALL
                    actual_size = size.as_int() * BOX_SIZE / BOX_OBJECT_RATIO
                else:
                    break

            if x_pos + actual_size > BOX_SIZE:
                x_pos = BOX_SIZE - actual_size
            if y_pos + actual_size > BOX_SIZE:
                y_pos = BOX_SIZE - actual_size

            # See whether it intersects.
            intersects = False
            for obj in existing_objects:
                obj_x = obj.x_pos
                obj_y = obj.y_pos
                obj_size = obj.size.as_int() * BOX_SIZE / BOX_OBJECT_RATIO

                x_overlap = (x_pos >= obj_x and x_pos <= obj_x + obj_size) \
                    or (obj_x >= x_pos and obj_x <= x_pos + actual_size)
                y_overlap = (y_pos >= obj_y and y_pos <= obj_y + obj_size) \
                    or (obj_y >= y_pos and obj_y <= y_pos + actual_size)
                if not intersects:
                    intersects = x_overlap and y_overlap
            if intersects:
                num_intersects += 1
        if intersects:
            return None
    return x_pos, y_pos, size


def generate_image(image_type, base_image=None):
    """Generates a single image.
    
    Inputs:
        image_type (ImageType): The type of image to generate (scatter or tower).
        base_image (NLVRImage, optional): The image whose objects should be used
            to generate the new image. If not provided, objects are randomly
            chosen.

    Returns:
        NLVRImage, representing the generated image.
    """
    max_objects = MAX_OBJECTS[image_type]

    if base_image:
        # This code is assuming there will be three boxes in total.
        if NUM_BOXES != 3:
            raise ValueError("Expected the number of boxes to be 3.")

        # Try to re-place the objects that are in the base image.
        all_objects = base_image.objects()

        new_boxes = [[] for _ in range(NUM_BOXES)]
        matches_previous_environment = True
        final_boxes = []
        num_tries = 0

        # Keep trying to generate it until you find an image that doesn't match the original one.
        while matches_previous_environment and num_tries < MAX_NUM_TRIES:
            random.shuffle(all_objects)

            well_split = False

            # Make sure the objects are well-split among the boxes; i.e., you don't have too few or too many in one box.
            num_split_tries = 0
            while not well_split and num_split_tries < MAX_NUM_TRIES:
                first_split = int(random.randint(1, max_objects + 1)) 
                second_split = first_split + int(random.randint(1, max_objects + 1))

                new_boxes[0] = all_objects[:first_split]
                new_boxes[1] = all_objects[first_split:second_split]
                new_boxes[2] = all_objects[second_split:]

                if len(new_boxes[0]) <= max_objects \
                   and len(new_boxes[1]) <= max_objects \
                   and len(new_boxes[2]) <= max_objects \
                   and len(new_boxes[0]) >= 1 \
                   and len(new_boxes[1]) >= 1 \
                   and len(new_boxes[2]) >= 1:
                    well_split = True
                num_split_tries += 1
            if not well_split:
                return None

            final_boxes = []
            for box in new_boxes:
                placed_objects_correctly = False
                num_place_tries = 0
                while not placed_objects_correctly and num_place_tries < MAX_NUM_INTERSECTS:
                    placed_objects = []    
                    random.shuffle(box)
                    for obj in box:
                        results = place_object(placed_objects, obj.size, image_type, False)
                        if results:
                            x_pos, y_pos, _ = results
                            obj.set_position(int(x_pos), int(y_pos))
                            obj.set_box(placed_objects)
                            placed_objects.append(obj)
                    placed_objects_correctly = len(placed_objects) == len(box)
                    num_place_tries += 1
                if not placed_objects_correctly:
                    return None
                final_boxes.append(placed_objects)
            assert sum([len(box) for box in final_boxes]) == len(all_objects), \
                "Expected " + str(len(all_objects)) + " items, but got " \
                + str(sum([len(box) for box in final_boxes]))

            matches_previous_environment = base_image.is_equal(NLVRImage(final_boxes, image_type))
            num_tries += 1
        if matches_previous_environment:
            return None
        boxes = final_boxes       
    else:
        boxes = []
        found_split = False
        while not found_split:
            for i in range(NUM_BOXES): 
                num_objects = random.randint(1, max_objects)
                objects = []

                for j in range(num_objects):
                    if image_type == ImageType.SCATTER:
                        shape = random.choice([Shape.CIRCLE, Shape.TRIANGLE, Shape.SQUARE])
                        size = random.choice([Size.SMALL, Size.MEDIUM, Size.LARGE])
                    else:
                        shape = Shape.SQUARE
                        size = Size.MEDIUM

                    color = random.choice([Color.YELLOW, Color.BLACK, Color.BLUE])
                    
                    x_pos, y_pos, size = place_object(objects, size, image_type)

                    objects.append(NLVRObject(shape, color, size, int(x_pos), int(y_pos), objects))

                boxes.append(objects)
            if image_type == ImageType.TOWER and sum([len(box) for box in boxes]) == 3:
                found_split = False
            else:
                found_split = True

    return NLVRImage(boxes, image_type)


def generate_images(image_type_counts):
    """Generates a set of four images, in NLVR style.
    
    Returns:
        two lists each containing two NLVRImages.
    """
    type_keys = []
    inverse_counts = []
    for key, val in image_type_counts.items():
        type_keys.append(key)
        inverse_counts.append(val)
    inverse_counts = 1./np.array(inverse_counts)
    type_dist = inverse_counts / np.sum(inverse_counts)

    # Sample which kind of image to generate (tower or scatter), preferring the type that hasn't been generated yet
    if np.isnan(type_dist).any():
        image_type = random.choice([ImageType.SCATTER, ImageType.TOWER])
    else:
        image_type = type_keys[np.argmax(np.random.multinomial(1, type_dist))]

    # Generate the four images.
    first_true = generate_image(image_type)
    second_true = generate_image(image_type)

    first_false = generate_image(image_type, first_true)
    second_false = generate_image(image_type, second_true)

    if not (first_true and second_true and first_false and second_false):
        return None, image_type

    return ([first_true, second_true], [first_false, second_false]), image_type
