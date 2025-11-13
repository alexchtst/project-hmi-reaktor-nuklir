# worker_validate.py
import argparse
from module.digsilent_pf import connectandsetup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--project_name", required=True)
    args = parser.parse_args()

    success, message, cases = connectandsetup(args.digsilent_path, args.project_name)

    if success:
        print(f"SUCCESS|{message}|{','.join(cases)}")
    else:
        print(f"ERROR|{message}")
