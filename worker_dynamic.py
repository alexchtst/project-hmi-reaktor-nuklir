# worker_dynamic.py
import argparse
import json
import base64
from module.digsilentpf_module import run_dynamic_simulation
import os
from data.pathloader import DATA

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--project_name", required=True)
    parser.add_argument("--case_name", required=True)
    parser.add_argument("--start_time", type=float, required=True)
    parser.add_argument("--stop_time", type=float, required=True)
    parser.add_argument("--step_size", type=float, required=True)
    parser.add_argument("--start_calc", type=float, required=False, default=None)
    parser.add_argument("--events_config", required=False, default=None)
    parser.add_argument("--output_dir", required=False, default=DATA)
    
    args = parser.parse_args()

    # Decode events_config from base64 JSON
    events_config = None
    if args.events_config:
        try:
            events_json = base64.b64decode(args.events_config).decode('utf-8')
            events_config = json.loads(events_json)
        except Exception as e:
            print(f"[WARNING]: Failed to decode events_config: {str(e)}")

    success, message, result_path = run_dynamic_simulation(
        digsilent_path=args.digsilent_path,
        proj_name=args.project_name,
        case_name=args.case_name,
        start_time_simulation=args.start_time,
        stop_time_simulation=args.stop_time,
        step_size=args.step_size,
        start_calc=args.start_calc,
        events_config=events_config,
        output_dir=DATA
    )

    if success:
        print(f"FINISH|SUCCESS|DYNAMICSIMULATION|{message}|{result_path}")
    else:
        print(f"TERMINATE|ERROR|DYNAMICSIMULATION|{message}|")