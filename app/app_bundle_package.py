#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import zipfile
import tempfile

def build_universal_apk(base_apk, apk_arm, apk_x64, apk_x86, output_universal, keystore, ks_pass, ks_alias):
    print(f"Creating Universal APK based on {base_apk}...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        unzip_base = os.path.join(tmpdir, "base")
        
        # 1. Extract the base APK (arm64)
        with zipfile.ZipFile(base_apk, 'r') as z: 
            z.extractall(unzip_base)
            
        # 2. Extract other APKs and copy their lib/ folders
        apk_map = {
            apk_arm: "armeabi-v7a",
            apk_x64: "x86_64",
            apk_x86: "x86"
        }
        
        for apk_path, abi_name in apk_map.items():
            if not os.path.exists(apk_path):
                print(f"::warning::Missing {apk_path}, skipping {abi_name}")
                continue
                
            print(f"Injecting {abi_name}...")
            unzip_other = os.path.join(tmpdir, abi_name)
            with zipfile.ZipFile(apk_path, 'r') as z:
                z.extractall(unzip_other)
                
            lib_src = os.path.join(unzip_other, "lib", abi_name)
            lib_dest = os.path.join(unzip_base, "lib", abi_name)
            
            if os.path.exists(lib_src):
                if os.path.exists(lib_dest):
                    shutil.rmtree(lib_dest)
                shutil.copytree(lib_src, lib_dest)

        # 3. Repack the folder into a new APK
        print(f"Repacking into {output_universal}...")
        with zipfile.ZipFile(output_universal, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(unzip_base):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, unzip_base)
                    z.write(full_path, rel_path)

        # 4. Align and Sign
        print("Aligning and Signing...")
        aligned_apk = output_universal.replace(".apk", "-aligned.apk")
        
        build_tools = os.environ.get("ANDROID_HOME", "/usr/local/lib/android/sdk") + "/build-tools/35.0.0"
        zipalign = os.path.join(build_tools, "zipalign")
        apksigner = os.path.join(build_tools, "apksigner")
        
        subprocess.run([zipalign, "-p", "-f", "4", output_universal, aligned_apk], check=True)
        subprocess.run([
            apksigner, "sign", "--ks", keystore, 
            "--ks-pass", f"pass:{ks_pass}", "--ks-key-alias", ks_alias, aligned_apk
        ], check=True)
        
        shutil.move(aligned_apk, output_universal)
        print(f"Successfully created {output_universal}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--x64", required=True)
    parser.add_argument("--x86", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--keystore", required=True)
    parser.add_argument("--ks-pass", required=True)
    parser.add_argument("--ks-alias", required=True)
    args = parser.parse_args()
    
    build_universal_apk(args.base, args.arm, args.x64, args.x86, args.out, args.keystore, args.ks_pass, args.ks_alias)
