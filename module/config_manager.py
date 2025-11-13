def newConfig(content):
    import os
    import json
    from datetime import datetime
    CONFIGPATH = "../config"
    
    try:
        required_fields = ['name', 'projectname',
                           'digsilentpath', 'fileresults']
        for field in required_fields:
            if field not in content or not content[field]:
                raise ValueError(f"invalid configuration: missing '{field}'")

        if isinstance(content['fileresults'], list):
            raise ValueError(
                "invalid configuration: 'fileresults' should not be a list")

        now = datetime.now()
        formatted_date_time = now.strftime("%Y%m%d_%H%M%S")

        data = {
            "name": f"{content['name']}-{formatted_date_time}",
            "projectname": content["projectname"],
            "digsilentpath": content["digsilentpath"],
            "fileresults": content["fileresults"],
        }

        os.makedirs(CONFIGPATH, exist_ok=True)

        filename = os.path.join(
            CONFIGPATH, f"{content['name']}-{formatted_date_time}.json")
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=4)

        return f"Success: new config saved to {filename}"

    except Exception as e:
        return f"Error happened: {str(e)}"


def loadConfig(path):
    import os
    import json
    from datetime import datetime
    CONFIGPATH = "../config"
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
            return config_data
    except Exception as e:
        return f"Error happened while loading: {str(e)}"


def syncConfig(path, newResults):
    import os
    import json
    from datetime import datetime
    
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as file:
            config = json.load(file)

        if isinstance(newResults, str):
            new_results_list = [newResults]
        elif isinstance(newResults, list):
            new_results_list = newResults
        else:
            raise ValueError("newResults must be a string or list of strings")

        if "fileresults" not in config or not config["fileresults"]:
            config["fileresults"] = []
        elif isinstance(config["fileresults"], str):
            config["fileresults"] = [config["fileresults"]]

        for result in new_results_list:
            if result not in config["fileresults"]:
                config["fileresults"].append(result)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)

        return f"Synced config: added {len(new_results_list)} new file(s) to {path}"

    except Exception as e:
        return f"Error happened while syncing: {str(e)}"


def loadSanitizeSavedConfig(configpath = "../config"):
    import os
    CONFIGPATH = configpath
    
    try:
        os.makedirs(CONFIGPATH, exist_ok=True)
        
        files = [f for f in os.listdir(CONFIGPATH) if f.endswith(".json")]
        
        configs = {}
        for f in files:
            name = os.path.splitext(f)[0]
            abs_path = os.path.abspath(os.path.join(CONFIGPATH, f))
            configs[name] = abs_path

        return configs

    except Exception as e:
        return f"Error happened while loading configs: {str(e)}"
