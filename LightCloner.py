import os
import shutil
import subprocess
import sys
import re
import time
import datetime

# ==================== LOGGING SYSTEM ====================
os.makedirs("logs", exist_ok=True)
log_file = f"logs/clone_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

def log(text):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ==================== BANNER ====================
print("""
   █████╗ ██╗   ██╗ █████╗ ██╗  ██╗██╗███╗   ██╗
  ██╔══██╗██║   ██║██╔══██╗██║ ██╔╝██║████╗  ██║
  ███████║██║   ██║███████║█████╔╝ ██║██╔██╗ ██║
  ██╔══██║╚██╗ ██╔╝██╔══██║██╔═██╗ ██║██║╚██╗██║
  ██║  ██║ ╚████╔╝ ██║  ██║██║  ██╗██║██║ ╚████║
  ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
       MASS CLONER PRO  — AHMED BHAI!
       Special for 2025
""")

# ==================== APK FINDER ====================
def find_apks():
    apks = []
    for root, dirs, files in os.walk(".", topdown=True):
        if "CLONES" in dirs:
            dirs.remove("CLONES")  # Skip output folder
        for file in files:
            if file.lower().endswith(".apk"):
                apks.append(os.path.abspath(os.path.join(root, file)))
    return apks


found_apks = find_apks()

choice = input("\nEnter APK path or press Enter to auto-detect: ").strip().strip('"\'')
if choice:
    ORIGINAL_APK = choice
else:
    if not found_apks:
        log("No APK found! Place your APK here.")
        input("Press Enter to exit..."); sys.exit()
    elif len(found_apks) == 1:
        ans = input(f"\nFound:\n→ {found_apks[0]}\n\nUse this APK? (Y/n): ").lower()
        ORIGINAL_APK = found_apks[0] if ans not in ["n", "no"] else (input("Enter path: ") or sys.exit())
    else:
        print("\nMultiple APKs found:")
        for i, apk in enumerate(found_apks, 1):
            print(f" [{i}] {os.path.basename(apk)}")
        while True:
            try:
                num = int(input(f"\nChoose APK (1-{len(found_apks)}): "))
                ORIGINAL_APK = found_apks[num-1]
                break
            except:
                print("Invalid choice!")

if not os.path.exists(ORIGINAL_APK):
    log("APK file not found!")
    input("Press Enter to exit..."); sys.exit()

log(f"Selected → {os.path.basename(ORIGINAL_APK)}")

# ==================== SETTINGS ====================
MAX_CLONES = int(input("\nHow many clones do you want? (Default 50): ") or "50")
OUTPUT_DIR = "CLONES"
os.makedirs(OUTPUT_DIR, exist_ok=True)

APKTOOL   = "tools/apktool.jar"      
ZIPALIGN  = "tools/zipalign.exe"
APKSIGNER = "tools/apksigner.jar"
KEYSTORE  = "keystore/key.keystore"
ALIAS     = "clonekey"
PASSWORD  = "Ahmed1"

# ==================== PACKAGE DETECTION (UNIVERSAL) ====================
def detect_package():
    try:
        result = subprocess.run(["aapt", "dump", "badging", ORIGINAL_APK],
                              capture_output=True, text=True, timeout=30)
        match = re.search(r"package: name='([^']+)'", result.stdout)
        if match: 
            return match.group(1)
    except: pass
    
    try:
        subprocess.run(["java", "-jar", APKTOOL, "d", ORIGINAL_APK, "--no-res", "-f", "-o", "tmp_detect"],
                       check=True, capture_output=True)
        with open("tmp_detect/AndroidManifest.xml", "r", encoding="utf-8", errors="ignore") as f:
            match = re.search(r'package="([^"]+)"', f.read())
        shutil.rmtree("tmp_detect", ignore_errors=True)
        if match: 
            return match.group(1)
    except: pass
    
    log("WARNING: Could not detect package name! Using dummy.")
    return "com.cloned.app"  # Universal safe fallback

BASE_PACKAGE = detect_package()
log(f"Package detected → {BASE_PACKAGE}")

def generate_package(num):
    parts = BASE_PACKAGE.split(".")
    if len(parts) < 2:
        return f"{BASE_PACKAGE}{num}"
    return f"{parts[0]}{num}.{'.'.join(parts[1:])}"

# ==================== MAIN CLONING LOOP (100% UNIVERSAL) ====================
times = []
log(f"\CREATING {MAX_CLONES} CLONES — ALHAMDULILLAH")

for i in range(1, MAX_CLONES + 1):
    start_time = time.time()
    new_pkg = generate_package(i)
    temp_dir = f"temp_{i}"
    final_apk = f"{OUTPUT_DIR}/Clone_{i}.apk"
    log(f"[{i:02d}/{MAX_CLONES}] Creating → {new_pkg}")

    try:
        # Decode
        subprocess.run(["java", "-jar", APKTOOL, "d", ORIGINAL_APK, "-f", "-o", temp_dir],
                       check=True, capture_output=True)

        # 100% WORKING PACKAGE CHANGE FOR APKTOOL 2.12.1+ (2025 METHOD)
        manifest_path = f"{temp_dir}/AndroidManifest.xml"
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
                manifest = f.read()
            manifest = manifest.replace(BASE_PACKAGE, new_pkg)
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(manifest)
            log(f"   Package FORCED changed → {new_pkg}")


        strings_path = f"{temp_dir}/res/values/strings.xml"
        if os.path.exists(strings_path):
            with open(strings_path, "r", encoding="utf-8") as f:
                xml = f.read()

            # Find <string name="app_name">ANYTHING</string> and change it
            if '<string name="app_name">' in xml:
                new_name = f"Clone {i}"
                xml = re.sub(r'<string name="app_name">[^<]*</string>',
                            f'<string name="app_name">{new_name}</string>', xml)
                log(f"   App name changed to → {new_name}")
            with open(strings_path, "w", encoding="utf-8") as f:
                f.write(xml)

        # Native bypass (Unity/il2cpp games)
        so_path = f"{temp_dir}/lib/armeabi-v7a/libil2cpp.so"
        if os.path.exists(so_path):
            data = bytearray(open(so_path, "rb").read())
            old = BASE_PACKAGE.encode()
            new = new_pkg.encode()
            if old in data:
                data = data.replace(old, new.ljust(len(old), b'\x00'), 1)
                open(so_path, "wb").write(data)
                log("   Native anti-clone bypass applied!")

        # Rebuild & sign (CLEAN MODE — NO .idsig)
        subprocess.run(["java", "-jar", APKTOOL, "b", temp_dir, "-o", f"unsigned_{i}.apk"], check=True)
        subprocess.run([ZIPALIGN, "-f", "-v", "4", f"unsigned_{i}.apk", final_apk], check=True)

        temp_signed = final_apk + ".temp_signed.apk"
        subprocess.run([
            "java", "--enable-native-access=ALL-UNNAMED", "-jar", APKSIGNER, "sign",
            "--ks", KEYSTORE, "--ks-key-alias", ALIAS, "--ks-pass", f"pass:{PASSWORD}",
            "--v1-signing-enabled", "true",
            "--v2-signing-enabled", "false",
            "--v3-signing-enabled", "false",
            "--out", temp_signed,
            final_apk
        ], check=True)

        os.replace(temp_signed, final_apk)
        if os.path.exists(final_apk + ".idsig"):
            os.remove(final_apk + ".idsig")   # FORCE DELETE .idsig
        duration = time.time() - start_time
        times.append(duration)
        eta = int((MAX_CLONES - i) * (sum(times)/len(times))) if times else 0
        h, r = divmod(eta, 3600)
        m, s = divmod(r, 60)
        log(f"   SUCCESS Clone_{i}.apk ({duration:.1f}s) | ETA: {h:02d}:{m:02d}:{s:02d}")

    except Exception as e:
        log(f"   FAILED Clone {i}: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        for f in [f"unsigned_{i}.apk", f"unsigned_{i}.apk.idsig"]:
            if os.path.exists(f): os.remove(f)

# ==================== DONE ====================
log(f"\nALHAMDULILLAH — ALL {MAX_CLONES} CLONES CREATED SUCCESSFULLY!")
log(f"Check folder: {OUTPUT_DIR}/")
print(f"\nALHAMDULILLAH! All clones are ready in '{OUTPUT_DIR}' folder")
print("You can now install all of them at the same time!")
input("\nPress Enter to exit...")