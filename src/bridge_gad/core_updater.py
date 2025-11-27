import os, sys, requests, tempfile, shutil
from tkinter import messagebox

GITHUB_RELEASES = "https://api.github.com/repos/CRAJKUMARSINGH/Bridge_GAD_Yogendra_Borse/releases/latest"

def check_core_update(current_version: str):
    try:
        r = requests.get(GITHUB_RELEASES, timeout=5)
        r.raise_for_status()
        latest = r.json()
        latest_tag = latest["tag_name"].lstrip("v")

        if latest_tag != current_version:
            if messagebox.askyesno("Bridge_GAD Update",
                                   f"A new version ({latest_tag}) is available.\n"
                                   f"Do you want to update now?"):
                asset = next((a for a in latest["assets"] if a["name"].endswith(".exe")), None)
                if asset:
                    _download_and_install(asset["browser_download_url"])
                else:
                    messagebox.showinfo("Update", "Installer not found in release assets.")
    except Exception as e:
        print("Core update check failed:", e)

def _download_and_install(url):
    try:
        temp_dir = tempfile.mkdtemp()
        local_file = os.path.join(temp_dir, "Bridge_GAD_Update.exe")
        with requests.get(url, stream=True, timeout=20) as r:
            with open(local_file, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        messagebox.showinfo("Update", "Bridge_GAD will now restart to apply the update.")
        os.startfile(local_file)
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Update Failed", f"Update failed:\n{e}")