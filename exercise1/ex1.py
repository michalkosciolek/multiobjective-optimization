TIME = "time"
STRENGTH_GAINED = "strength_gained"
STEPS = "steps"


def read_paths_from_file(file_path: str) -> dict:
    paths = {}
    with open(file_path, "r") as file:
        dragon_hp = int(file.readline().strip())
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 4:
                path_name = parts[0].strip()
                time = int(parts[1].strip())
                strength_gained = int(parts[2].strip())
                steps = int(parts[3].strip())
                paths[path_name] = {
                    TIME: time,
                    STRENGTH_GAINED: strength_gained,
                    STEPS: steps,
                }
    return dragon_hp, paths


def choose_path(paths: dict) -> str:
    if not paths:
        raise ValueError("No paths available to choose from")

    best_path = None
    best_ratio = 0

    for path, attributes in paths.items():
        ratio = attributes[STRENGTH_GAINED] / attributes[TIME]
        if ratio > best_ratio:
            best_ratio = ratio
            best_path = path

    print(f"Best choice is {best_path} enemy path.")
    return best_path


def fight_dragon(dragon_hp: int, path: dict):
    current_strength = 0
    current_time = 0
    current_steps = 0

    while True:
        if current_strength < dragon_hp and current_steps <= path[STEPS]:
            current_strength += path[STRENGTH_GAINED]
            current_time += path[TIME]
            current_steps += 1
        else:
            break

    if current_strength >= dragon_hp:
        print(
            f"You have defeated the dragon after {current_steps} steps and {current_time} seconds with {current_strength} strength."
        )
    else:
        print("You cannot defeat the dragon")


def play_game():
    input_file = input("Enter the path to the input file: ")
    dragon_hp, paths = read_paths_from_file(input_file)

    chosen_path = choose_path(paths)
    fight_dragon(dragon_hp, paths[chosen_path])


if __name__ == "__main__":
    play_game()
