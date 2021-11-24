import os
from Utils import __version__
from jinja2 import Template
import yaml
import json

from worlds.AutoWorld import AutoWorldRegister
import Options

target_folder = os.path.join("WebHostLib", "static", "generated")


def create():
    def dictify_range(option):
        data = {option.range_start: 0, option.range_end: 0, "random": 0, "random-low": 0, "random-high": 0,
                option.default: 50}
        notes = {
            option.range_start: "minimum value",
            option.range_end: "maximum value"
        }
        return data, notes

    def default_converter(default_value):
        if isinstance(default_value, (set, frozenset)):
            return list(default_value)
        return default_value

    for game_name, world in AutoWorldRegister.world_types.items():
        res = Template(open(os.path.join("WebHostLib", "templates", "options.yaml")).read()).render(
            options={**world.options, **Options.per_game_common_options},
            __version__=__version__, game=game_name, yaml_dump=yaml.dump,
            dictify_range=dictify_range, default_converter=default_converter,
        )

        os.makedirs(os.path.join(target_folder, 'configs'), exist_ok=True)

        with open(os.path.join(target_folder, 'configs', game_name + ".yaml"), "w") as f:
            f.write(res)

        # Generate JSON files for player-settings pages
        player_settings = {
            "baseOptions": {
                "description": "Generated by https://archipelago.gg/",
                "game": game_name,
                "name": "Player",
            },
        }

        game_options = {}
        for option_name, option in world.options.items():
            if option.options:
                game_options[option_name] = this_option = {
                    "type": "select",
                    "displayName": option.displayname if hasattr(option, "displayname") else option_name,
                    "description": option.__doc__ if option.__doc__ else "Please document me!",
                    "defaultValue": None,
                    "options": []
                }

                for sub_option_id, sub_option_name in option.name_lookup.items():
                    this_option["options"].append({
                        "name": option.get_option_name(sub_option_id),
                        "value": sub_option_name,
                    })

                    if sub_option_id == option.default:
                        this_option["defaultValue"] = sub_option_name

                this_option["options"].append({
                    "name": "Random",
                    "value": "random",
                })

            elif hasattr(option, "range_start") and hasattr(option, "range_end"):
                game_options[option_name] = {
                    "type": "range",
                    "displayName": option.displayname if hasattr(option, "displayname") else option_name,
                    "description": option.__doc__ if option.__doc__ else "Please document me!",
                    "defaultValue": option.default if hasattr(option, "default") else option.range_start,
                    "min": option.range_start,
                    "max": option.range_end,
                }

        player_settings["gameOptions"] = game_options

        os.makedirs(os.path.join(target_folder, 'player-settings'), exist_ok=True)

        with open(os.path.join(target_folder, 'player-settings', game_name + ".json"), "w") as f:
            f.write(json.dumps(player_settings, indent=2, separators=(',', ': ')))
