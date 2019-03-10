// Sorts the items in a box
function sortItems(box) {
  // Sort the items by sorting the JSOn representation of them
  if (box.length > 1) {
    box_sorted = [ ]
    for (var i = 0; i < box.length; i++) {
      box_sorted.push(JSON.stringify(box[i]))
    }
  
    box_sorted.sort()
    return JSON.stringify(box_sorted)
  }
  
  return JSON.stringify(box)
}
    
// Sorts an environment (with three boxes)
function sortEnvironment(environment) {
  environment_sorted = [ ]

  // For each box, sort its items.
  for (var i = 0; i < 3; i++) {
    environment_sorted.push(sortItems(environment[i]))
  }
  
  // Then sort the sorted boxes. 
  environment_sorted.sort()
  return JSON.stringify(environment_sorted)
}
  
// Used to tell whether two environments are equal. 
function isEqual(environment_a, environment_b) {
  if (environment_a.length != environment_b.length) {
    return false;
  }
  
  // Sort each environment
  sorted_a = sortEnvironment(environment_a)
  sorted_b = sortEnvironment(environment_b)
  
  return sorted_a == sorted_b
}

function generateBox(context, loc, config, num_objects) {
  // Choose a number of blocks to place.
  var num_blocks = Math.floor(Math.random() * num_objects + 1);
  var cur_loc = 0;
  var rects = [ ]
  var shapes = [ ]

  // For each block, choose a shape and color
  for (i = 0; i < num_blocks; i ++) {
    var which_shape = Math.floor(Math.random() * 3);
    var which_color = Math.floor(Math.random() * 3);

    var color = "Black";
    if (which_color == 1) {
      color = "#0099ff";
    } else if (which_color == 2) {
      color = "Yellow";
    }

    context.fillStyle = color;

    // Choose a random size
    var size = Math.floor(Math.random() * 3) * 10 + 10;

    // Get the bounds of the box, depending on which one it is
    // (left/middle/right)
    var start_x = 0;
    var start_y = 0;
    var x_bound = 100;
    var y_bound = 100;
    if (loc == 1) {
      start_x = 150;
      start_y = 0;
      x_bound = 250;
      y_bound = 100;
    } else if (loc == 2) {
      start_x = 300;
      start_y = 0;
      x_bound = 400;
      y_bound = 100;
    }

    var x_loc = 0;
    var y_loc = 0;

    // config = 1 is a tower environment; config = 2 is scatter images
    if (config == 1) {
      if (i == 0) {
        cur_loc = 80;
      }
      size = 20;
      which_shape = 0;
      x_loc = 40;
      y_loc = cur_loc;
      cur_loc = cur_loc - size - 1;
    } else {
      var intersects = true;
      var num_intersects = 0;

      // make sure none of the blocks intersect
      while (intersects) {
        // pick a new location for the block
        x_loc = Math.floor(Math.random() * 100);
        y_loc = Math.floor(Math.random() * 100);

        // make boxes smaller if it's taking too long
        if (num_intersects > 100) {
          size = 10;
        }

        // reposition items if they extend beyond the canvas
        if (x_loc + size > 100) {
          x_loc = 100 - size;
        }

        if (y_loc + size > 100) {
          y_loc = 100 - size;
        } 

        // get actual location in the convas (not relative to the box)
        ac_x = x_loc + start_x;
        ac_y = y_loc + start_y;

        intersects = false;

        // make sure they don't intersect with any of the other items
        for (i = 0; i < rects.length; i ++) {
          var test_rect = rects[i]

          var test_x = test_rect[0]
          var test_y = test_rect[1]
          var test_size = test_rect[2]

          // check for overlap
          var x_overlap = (ac_x >= test_x && ac_x <= test_x + test_size) || (test_x >= ac_x && test_x <= ac_x + size);
          var y_overlap = (ac_y >= test_y && ac_y <= test_y + test_size) || (test_y >= ac_y && test_y <= ac_y + size);
          if (intersects == false) {
            intersects = x_overlap && y_overlap;
          }
        }

        if (intersects == true) {
          num_intersects += 1
        }
      }
    }

    if (x_loc + size > 100) {
      x_loc = 100 - size;
    }

    if (y_loc + size > 100) {
      y_loc = 100 - size;
    }

    // get the actual final exact location
    var final_x = start_x + x_loc;
    var final_y = start_y + y_loc;

    // render the item and save the data to the dictionary
    shape = {"color": color, "size": size, "x_loc": x_loc, "y_loc": y_loc}
    if (which_shape == 0) {
      context.fillRect(final_x, final_y, size, size);
      shape["type"] = "square"

      shapes.push(shape)
    } else if (which_shape == 1) {
      context.beginPath();
      context.arc(final_x + size / 2, final_y + size / 2, size / 2, 0, Math.PI * 2, true);
      context.closePath();
      context.fill();
      shape["type"] = "circle"

      shapes.push(shape)
    } else if (which_shape == 2) {
      context.beginPath();
      context.moveTo(final_x, final_y + size);
      context.lineTo(final_x + size, final_y + size);
      context.lineTo(final_x + size / 2, final_y);
      context.closePath();
      context.fill();
      shape["type"] = "triangle"

      shapes.push(shape)
    }

    // this just keeps track of the parameters of the shapes already in the box
    rects.push([final_x, final_y, size, size]);
  }

  // return all of the items in the box, represented as a dictionary
  return shapes
}

function generateBaseEnvironment(context) {
  // puts grey boxes in environment
  context.fillStyle = "Grey";
  context.fillRect(0, 0, 600, 600);

  context.fillStyle = "LightGrey";
  context.fillRect(0, 0, 200, 200);
  context.fillRect(300, 0, 200, 200);
  context.fillRect(600, 0, 200, 200);
}

function generateEnvironment(context, config, num_objects, environments) {
  generateBaseEnvironment(context);

  matches_any = true

  // make sure the environment you generate is not the same as other
  // environments in the set
  while (matches_any) {
    boxes = [ ]

    for (loc = 0; loc < 3; loc ++) {
      box = generateBox(context, loc, config, num_objects)
      boxes.push(box)
    }
  
    matches_any = false
    for (var i = 0; i < environments.length; i ++) {
      if (isEqual(boxes, environments[i])) {
        matches_any = true
      }
    }
  }

  return boxes 
}

// shuffle function for arrays
function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  while (0 !== currentIndex) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;
  
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

// Displays objects in an environment.
function placeObjects(context, loc, objects, config) {
  num_objects = objects.length

  var cur_loc = 0;
  var rects = [ ]
  var shapes = [ ]

  // Randomly shuffle the objects list.
  shuffle(objects)

  for (i = 0; i < num_objects; i ++) {
    // Get the object properties: color and size
    object_to_place = objects[i]

    var color = object_to_place.color;
    context.fillStyle = color;

    var size = object_to_place.size;

    // Get location and bounds of current box
    var start_x = 0;
    var start_y = 0; 
    var x_bound = 100;
    var y_bound = 100;

    if (loc == 1) {
      start_x = 150;
      start_y = 0;
      x_bound = 250;
      y_bound = 100;
    } else if (loc == 2) {
      start_x = 300;
      start_y = 0;
      x_bound = 400;
      y_bound = 100;
    }

    var x_loc = 0;
    var y_loc = 0;

    if (config == 1) {
      if (i == 0) {
        cur_loc = 80;
      }
      size = 20;
      which_shape = 0;
      x_loc = 40;
      y_loc = cur_loc;
      cur_loc = cur_loc - size - 1;
    } else if (config == 2) {
      size = 20;
      y_loc = 300 - size;
      x_loc = cur_loc;
      cur_loc = cur_loc + size + 1;
    } else {
      // Randomly place objects in the box
      var intersects = true;
      var num_intersects = 0;
      while (intersects) {
        x_loc = Math.floor(Math.random() * 100);
        y_loc = Math.floor(Math.random() * 100);

        if (num_intersects > 100) {
          size = 10;
        }

        if (x_loc + size > 100) {
          x_loc = 100 - size;
        }

        if (y_loc + size > 100) {
          y_loc = 100 - size;
        }

        ac_x = x_loc + start_x;
        ac_y = y_loc + start_y;

        intersects = false;

        // Make sure there are no intersections with other shapes
        for (i = 0; i < rects.length; i ++) {
          var test_rect = rects[i]
          var test_x = test_rect[0]
          var test_y = test_rect[1]

          var test_size = test_rect[2]

          var x_overlap = (ac_x >= test_x && ac_x <= test_x + test_size) || (test_x >= ac_x && test_x <= ac_x + size);
          var y_overlap = (ac_y >= test_y && ac_y <= test_y + test_size) || (test_y >= ac_y && test_y <= ac_y + size);
          if (intersects == false) {
            intersects = x_overlap && y_overlap;
          }
        }

        if (intersects == true) {
          num_intersects += 1
        }
      }
    }

    if (x_loc + size > 100) {
      x_loc = 100 - size;
    }

    if (y_loc + size > 100) {
      y_loc = 100 - size;
    }

    var final_x = start_x + x_loc;
    var final_y = start_y + y_loc;

    if (object_to_place.type == "square") {
      context.fillRect(final_x, final_y, size, size);

      shape = {"type":"square", "color":color, "size":size, "x_loc":x_loc, "y_loc":y_loc }
      shapes.push(shape)
    } else if (object_to_place.type == "circle") {
      context.beginPath();
      context.arc(final_x + size / 2, final_y + size / 2, size / 2, 0, Math.PI * 2, true);
      context.closePath();
      context.fill();
      shape = {"type":"circle", "color":color, "size":size, "x_loc":x_loc, "y_loc":y_loc }
      shapes.push(shape)
    } else if (object_to_place.type == "triangle") {
      context.beginPath();
      context.moveTo(final_x, final_y + size);
      context.lineTo(final_x + size, final_y + size);
      context.lineTo(final_x + size / 2, final_y);
      context.closePath();
      context.fill();
      shape = {"type":"triangle", "color":color, "size":size, "x_loc":x_loc, "y_loc":y_loc }
      shapes.push(shape)
    }

    rects.push([final_x, final_y, size, size]);
  }

  return shapes
}

// Get random objects/properties but do not place them on the screen
function generateObjects(context, max_objects) {
  var num_objects = Math.floor(Math.random() * max_objects * 3 + 3);
  var objects = [ ]
  for (var i = 0; i < num_objects; i ++) {
    // Generate type.
    var type = Math.floor(Math.random() * 3);
    var shape = ""
    if (type == 0) {
      shape = "square"
    } else if (type == 1) {
      shape = "circle"
    } else if (type == 2) {
      shape = "triangle"
    }
    
    // Generate color.
    var color_num = Math.floor(Math.random() * 3);
    var color = ""
    if (color_num == 0) {
      color = "Black";
    } else if (color_num == 1) {
      color = "#0099ff";
    } else if (color_num == 2) {
      color = "Yellow";
    }
    
    // Generate size.
    var size = Math.floor(Math.random() * 3) * 10 + 10;
    
    // For now place as -1, -1 location.
    var obj_var = {"type":shape, "color":color, "size":size, "x_loc":-1, "y_loc":-1 }
    objects.push(obj_vat)
  }

  return JSON.stringify(objects)
}

// Given a set of objects, we want to re-place the objects in different
// locations
function generateEnvironmentWithObjects(context, objects, config, max_objects_per_box, environments) {
  generateBaseEnvironment(context);

  // Get a list of objects from the list split in sets
  all_objects = [ ]
  for (i = 0; i < 3; i ++) {
    for (j = 0; j < objects[i].length; j ++) {
      all_objects.push(objects[i][j])
    }
  }
      
  sets = [ ]
  matches_any = true

  // Make sure the new boxes do not match the old environments
  while (matches_any) {
    shuffle(all_objects)
    
    var well_split = false
    var first_split = 0
    var second_split = 0
    
    // Make sure the number of items in each box is within the bounds
    while (!well_split) {
      console.log(all_objects.length)
      first_split = Math.floor(Math.random() * max_objects_per_box + 1)
      second_split = first_split + Math.floor(Math.random() * max_objects_per_box + 1)
      
      var num_in_second = second_split - first_split
      var num_in_third = all_objects.length - second_split
      console.log(first_split)
      console.log(second_split)
      if (num_in_second <= max_objects_per_box && num_in_third <= max_objects_per_box && num_in_second >= 1 && num_in_third >= 1) {
        well_split = true
      }
    }
    
    // After shuffling objects, sort them into the new boxes
    first_set = [ ]
    second_set = [ ]
    third_set = [ ]
    for (i = 0; i < all_objects.length; i++) {
      if (i < first_split) {
        first_set.push(all_objects[i])
      } else if (i >= first_split && i < second_split) {
        second_set.push(all_objects[i])
      } else if (i >= second_split) {
        third_set.push(all_objects[i])
      }
    }
    
    obj_set = [ first_set, second_set, third_set ]
    console.log(first_set.length)
    console.log(second_set.length)
    console.log(third_set.length)
    
    // Place the objects in a box with new locations
    for (loc = 0; loc < 3; loc ++) {
      console.log("placing objects")
      shapes = placeObjects(context, loc, obj_set[loc], config)
      sets.push(shapes)
    }
    
    matches_any = false
    for (i = 0; i < environments.length; i++) {
      if (isEqual(sets, environments[i])) {
        matches_any = true
      }
    }
  }

  return sets
  }
  
// draws a set of objects in a context
function draw_objects(context, objects) {
  generateBaseEnvironment(context)

  shuffled_objects = shuffle(objects)

  for (i = 0; i < shuffled_objects.length; i ++) {
    for (j = 0; j < shuffled_objects[i].length; j ++) {
      var shape = shuffled_objects[i][j]
      var type = shape["type"]
      var color = shape["color"]
      var size = shape["size"]
      var x_loc = shape["x_loc"]
      var y_loc = shape["y_loc"]
      
      var start_x = 0;
      var start_y = 0;
      if (i == 1) {
        start_x = 150;
        start_y = 0;
      } else if (i == 2) {
        start_x = 300;
        start_y = 0;
      }
    
      final_x = start_x + x_loc
      final_y = start_y + y_loc
      
      context.fillStyle = color
      if (type == "square") {
        context.fillRect(final_x, final_y, size, size);
      } else if (type == "circle") {
        context.beginPath();
        context.arc(final_x + size / 2, final_y + size / 2, size / 2, 0, Math.PI * 2, true);
        context.closePath();
        context.fill();
      } else if (type == "triangle") {
        context.beginPath();
        context.moveTo(final_x, final_y + size);
        context.lineTo(final_x + size, final_y + size);
        context.lineTo(final_x + size / 2, final_y);
        context.closePath();
        context.fill();
      }
    }
  }
}

