from __future__ import annotations
import sys

sys.path.insert(0, r"C:\Users\petrk\Documents\ayon\ayon-docker\backend")
sys.path.insert(0, r"C:\Users\petrk\Documents\ayon\ayon-jira")
from server.templates import _set_env_vars, run_endpoint

if __name__ == "__main__":
    _set_env_vars()

    placeholder_map = {"Tier1CharacterNameOutfitName": "Character1",
                       "Tier1CharacterName": "Character1"}  # possible not importatn
    project_name = "temp_project_sftp"
    run_endpoint(
        project_name,
        "Tier_1_Outfit",
        placeholder_map,
        ["Characters/Character1"]
    )