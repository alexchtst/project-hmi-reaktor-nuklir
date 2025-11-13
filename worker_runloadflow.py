import argparse
from module.digsilent_pf import running_loadflow
import os

def main():
    parser = argparse.ArgumentParser(description="Worker untuk menjalankan loadflow PowerFactory")
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--proj_name", required=True)
    parser.add_argument("--case_name", required=True)
    args = parser.parse_args()
    
    success, data = running_loadflow(
        digsilent_path=args.digsilent_path,
        proj_name=args.proj_name,
        case_name=args.case_name,
        output_dir = os.path.join(os.getcwd(), "data")
    )
    
    if success:
        print("SUCCESS")
        print(data)
    else:
        print("FAILED")
        print(data)

if __name__ == "__main__":
    main()
