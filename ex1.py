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

    best_strength_gained = paths[best_path][STRENGTH_GAINED]
    best_time = paths[best_path][TIME]
    print(
        f"Best choice is: {best_path} enemy path, with strength gained: {best_strength_gained} and time: {best_time} seconds"
    )
    return best_path


def fight_dragon(dragon_hp: int, best_path: dict):
    strength_gained = best_path[STRENGTH_GAINED]
    time = best_path[TIME]

    if strength_gained >= dragon_hp:
        print(
            f"You have defeated the dragon. Strength gained: {strength_gained}, time taken: {time} seconds."
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
