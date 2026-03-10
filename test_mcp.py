import json
from tools.load_model import load_model
from tools.operations.query_bus import query
from tools.operations.add_bus import add
from tools.operations.apply_bus import apply

def run():
    print("=== START ===")
    res_load = load_model("src/sample/Revit_Sample.hbjson")
    print("=== LOAD ===")
    print(json.dumps(res_load, indent=2))
    
    if not res_load.get("success"):
        return

    res_query = query(target_type="model", fields=["identifier", "display_name", "rooms", "floor_area"])
    print("=== QUERY ===")
    print(json.dumps(res_query, indent=2))

    rooms = query(target_type="model", fields=["rooms"])["data"]["rooms"]
    if rooms:
        res_apply = apply(operation="hvac", target_type="room", identifiers=[rooms[0]], values={"system_category": "Ideal"})
        print("=== APPLY ===")
        print(json.dumps(res_apply, indent=2))

    faces = query(target_type="model", fields=["faces"])["data"]["faces"]
    if faces and len(faces) >= 2:
        res_add = add(operation="apertures_by_ratio", target_type="face", identifiers=[faces[0], faces[1]], params={"ratio": 0.4})
        print("=== ADD ===")
        print(json.dumps(res_add, indent=2))

if __name__ == "__main__":
    run()
