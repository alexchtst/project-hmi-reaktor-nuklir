# worker_connectandsetup.py
import argparse
import json
from module.digsilentpf_module import connectandsetup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--project_name", required=True)
    args = parser.parse_args()

    success, message, cases, events_data = connectandsetup(args.digsilent_path, args.project_name)

    if success:
        events_json = json.dumps(events_data, ensure_ascii=False)
        import base64
        events_encoded = base64.b64encode(events_json.encode('utf-8')).decode('utf-8')
        
        print(f"FINISH|SUCCESS|CONNECTANDSETUP|{message}|{','.join(cases)}|{events_encoded}")
    else:
        print(f"TERMINATE|ERROR|CONNECTANDSETUP|{message}|..|")