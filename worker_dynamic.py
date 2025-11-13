# worker_dynamic.py
import argparse
from module.digsilent_pf import run_dynamic_simulation
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--project_name", required=True)
    parser.add_argument("--start_time", type=float, default=-0.1)
    parser.add_argument("--stop_time", type=float, default=5)
    parser.add_argument("--start_fault", type=float, default=0)
    parser.add_argument("--clear_fault", type=float, default=0.23)
    parser.add_argument("--fault_element_name", default="Line 02 - 03")
    parser.add_argument("--fault_element_type", default="ElmLne")
    parser.add_argument("--fault_type", type=int, default=0)
    args = parser.parse_args()

    success, message, filepath = run_dynamic_simulation(
        digsilent_path=args.digsilent_path,
        proj_name=args.project_name,
        start_time_simulation=args.start_time,
        stop_time_simulation=args.stop_time,
        start_fault=args.start_fault,
        clear_fault=args.clear_fault,
        fault_element_name=args.fault_element_name,
        fault_element_type=args.fault_element_type,
        fault_type=args.fault_type,
        output_dir = os.path.join(os.getcwd(), "data")
    )

    if success:
        print(f"[SUCCESS] {message} | Filepath: {filepath}")
    else:
        print(f"[FAILED] {message}")
