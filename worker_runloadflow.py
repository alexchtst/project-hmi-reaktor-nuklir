import argparse
from module.digsilentpf_module import running_loadflow
import os

def main():
    parser = argparse.ArgumentParser(description="Worker untuk menjalankan loadflow PowerFactory")
    parser.add_argument("--digsilent_path", required=True)
    parser.add_argument("--proj_name", required=True)
    parser.add_argument("--case_name", required=True)
    args = parser.parse_args()
    
    success, message, path = running_loadflow(
        digsilent_path=args.digsilent_path,
        proj_name=args.proj_name,
        case_name=args.case_name,
        output_dir = os.path.join(os.getcwd(), "data")
    )
    
    if success:
        print(f"FINISH|SUCCESS|{message}|{path}|LOADFLOW")
    else:
        print(f"FINISH|ERROR|{message}|..|LOADFLOW")

if __name__ == "__main__":
    main()
    

# python yourscript.py --digsilent_path "C:\Program Files\DIgSILENT\PowerFactory 2022\Python\3.8" --proj_name "NamaProjectAnda" --case_name "NamaStudyCase"
