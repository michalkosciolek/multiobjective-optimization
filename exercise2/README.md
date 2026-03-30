# Exercise 2 - documentation

## Overview

This algorithm solves a route shopping problem in an undirected graph. Program starts at the home node and visits stores to collect as many requested items as possible. After that, it returns home before time runs out.

#
## Requirements

### Python version
 - Minimum Python 3.9

 #
 ## Input data format

 You have to provide input file in the JSON format with the following structure:

 ```json
{
    "num_nodes": 6,
    "home_node": 0,
    "max_time": 110,
    "purchase_time": 5,
    "shopping_list": [
        "bread", 
        "milk", 
        "butter", 
        "apples", 
        "coffee"
    ],
    "edges": [
        [0, 1, 10], 
        [1, 2, 15], 
        [0, 2, 20],
        [2, 3, 10],
        [3, 4, 20], 
        [1, 4, 30],
        [4, 5, 5],  
        [2, 5, 25]
    ],
    "store_inventories": {
        "1": ["milk", "water", "eggs"],
        "2": ["bread", "apples", "soda"],
        "3": ["butter", "cheese"],
        "4": ["coffee", "tea"],
        "5": ["bread", "milk", "coffee", "cake"]
    }
}
 ```

 ### Fields description

**num_nodes** - Number of nodes in the graph.

**home_node** - Index of the starting node.

**max_time** - Maximum total time allowed for the whole trip.

**num_nodes** - Number of nodes in the graph.

**purchase_time** - Fixed time spent shopping at each visited store.

**edges** - Graph edges in the format `[start_node, end_node, travel_time]`.

**store_inventories** - Mapping from store node id to list of items available in that store.

#
### Running the program

```bash
python ex2.py
```

By default, program looks for the input file named `shopping_data.json` in the same directory as the source file. 

You can provide your own input file by adding its directory as an execution argument:

```bash
python ex.py path/to/file/input.json
```

#
### Program output

The program prints:
- items that were successfully collected
- shops where we stopped and bought something
- total time used
