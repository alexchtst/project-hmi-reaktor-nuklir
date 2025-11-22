# worker_validate.py
import argparse
from module.digsilentpf_module import connectandsetup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--project_name", required=True)
    args = parser.parse_args()

    success, message, cases = connectandsetup(args.digsilent_path, args.project_name)

    if success:
        print(f"FINISH|SUCCESS|{message}|{','.join(cases)}|CONNECTANDSETUP")
    else:
        print(f"FINISH|ERROR|{message}|..|CONNECTANDSETUP")
