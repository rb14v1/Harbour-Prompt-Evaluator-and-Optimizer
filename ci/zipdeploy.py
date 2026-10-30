import base64
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

ZIP_DEPLOY_TIMEOUT = 900


def main():
    var_name, zip_path = sys.argv[1], sys.argv[2]
    profile = ET.fromstring(base64.b64decode(os.environ[var_name]))
    method = next(p for p in profile.iter("publishProfile") if p.get("publishMethod") == "MSDeploy")
    host = method.get("publishUrl").split(":")[0]
    token = base64.b64encode(f"{method.get('userName')}:{method.get('userPWD')}".encode()).decode()

    with open(zip_path, "rb") as f:
        body = f.read()

    request = urllib.request.Request(
        f"https://{host}/api/zipdeploy",
        data=body,
        method="POST",
        headers={"Authorization": f"Basic {token}", "Content-Type": "application/zip"},
    )
    with urllib.request.urlopen(request, timeout=ZIP_DEPLOY_TIMEOUT) as response:
        print(f"Zip deploy to {host} returned HTTP {response.status}")


if __name__ == "__main__":
    main()
