

import platform
import requests
import zipfile
import os
import stat

def download_file(url, dst):
    local_filename = dst
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

def download_and_add(url, version, dst_folder):
    dst_bin = download_file(url, f"{dst_folder}/build.{version}.zip")

    with zipfile.ZipFile(dst_bin, 'r') as zip_ref:
        zip_ref.extractall(f"{dst_folder}/build_llvm{version}")

    os.remove(f"{dst_folder}/build.{version}.zip")

    # Set executable permissions

    try:
        st = os.stat(f"{dst_folder}/build_llvm{version}/build/mewe-linker")
        os.chmod(f"{dst_folder}/build_llvm{version}/build/mewe-linker", st.st_mode | stat.S_IEXEC)

        st = os.stat(f"{dst_folder}/build_llvm{version}/build/mewe-fixer")
        os.chmod(f"{dst_folder}/build_llvm{version}/build/mewe-fixer", st.st_mode | stat.S_IEXEC)
    except Exception as e:
        print(e)

    return version, dict(
        mewe_linker = lambda : f"{dst_folder}/build_llvm{version}/build/mewe-linker",
        mewe_fixer = lambda : f"{dst_folder}/build_llvm{version}/build/mewe-fixer"
    )

def download_mewe_binaries():
    print("Downloading mewe binaries")

    dst_folder = os.path.dirname(__file__)
    dst_folder = os.path.join(dst_folder, "bin")

    if not os.path.exists(dst_folder):
        os.mkdir(dst_folder)

    system = platform.system()
    result = {

    }
    if system == 'Darwin': #MACOS
        
        version, bins = download_and_add("https://github.com/Jacarte/MEWE/releases/download/binaries/build.macos.llvm13.zip", 13, dst_folder)
        result[version] = bins

        version, bins = download_and_add("https://github.com/Jacarte/MEWE/releases/download/binaries/build.macos.llvm12.zip", 12, dst_folder)
        result[version] = bins

        # Add the other version here

        return result
    elif system == 'Linux': # Linux
        
        version, bins = download_and_add("https://github.com/Jacarte/MEWE/releases/download/binaries/build.macos.llvm13.zip", 13, dst_folder)
        result[version] = bins

        version, bins = download_and_add("https://github.com/Jacarte/MEWE/releases/download/binaries/build.macos.llvm12.zip", 12, dst_folder)
        result[version] = bins

        # Add the other version here

        return result
    else:
        exit(f"unknown OS {system}")
    
