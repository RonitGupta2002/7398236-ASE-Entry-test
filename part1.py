
import json
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime
from urllib.parse import quote

checked = 0
package_not = 0
version_not = 0
oldest_pinned_versions = []

requirements_file = "/Users/ronit/Desktop/ASE Entry Test/requirements.txt"

with open(requirements_file, encoding="utf-8-sig") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.strip().startswith("#")
    ]

for requirement in requirements:
    if "==" not in requirement:
        continue

    name, version = map(str.strip, requirement.split("==", 1))
    checked += 1

    url = f"https://pypi.org/pypi/{quote(name, safe='')}/json"

    try:
        with urlopen(url, timeout=15) as response:
            data = json.load(response)

    except HTTPError as e:
        if e.code == 404:
            package_not += 1
            continue
        raise

    except (URLError, TimeoutError) as e:
        print(f"Could not check {name}=={version}: {e}")
        continue

    releases = data["releases"]

    if version not in releases or not releases[version]:
        version_not += 1
        continue

    pinned_files = releases[version]
    latest_version = data["info"]["version"]
    latest_files = releases.get(latest_version, [])

    if not pinned_files or not latest_files:
        continue

    try:
        pinned_date = datetime.fromisoformat(
            pinned_files[0]["upload_time"].replace("Z", "+00:00")
        )
        latest_date = datetime.fromisoformat(
            latest_files[0]["upload_time"].replace("Z", "+00:00")
        )
    except (KeyError, ValueError, TypeError):
        continue

    if pinned_date < latest_date:
        oldest_pinned_versions.append(
            f"{name}=={version} ({pinned_date.year})"
        )

print(f"\nDependencies Checked : {checked}")
print(f"Packages not on PyPI : {package_not}")
print(f"Versions not on PyPI : {version_not}")
print(f"Oldest pinned versions : {len(oldest_pinned_versions)}")

for package in oldest_pinned_versions:
    print(package)
