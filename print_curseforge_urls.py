import json;

for f in json.load(open("manifest.json", "r"))["files"]:
    if not f["required"]:
        continue
    file_id = f["fileID"]
    project_id = f["projectID"]
    print("https://www.curseforge.com/api/v1/mods/%i/files/%i/download" % (project_id, file_id))

