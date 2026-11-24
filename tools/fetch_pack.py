#!/usr/bin/env python3
"""下载并校验 GD32F30x 官方 DFP（CMSIS-Pack），并解出包内全部 SVD。

默认从 GigaDevice 的 GD32F30x_Addon 仓库获取 2.6.0（2025-08-20 发布），
保存到 packs/GigaDevice.GD32F30x_DFP.2.6.0.pack，并用 SHA-256 校验。
已存在且校验通过时不重复下载。

校验通过后从包内解出 SVD/*.svd 到 svd/，供 Cortex-Debug 显示外设寄存器。
具体型号使用哪个 SVD 由 tools/select_device.py 决定（写入 launch.json 的
svdFile）。SVD 在本地生成，不纳入版本控制，也不再分发。

许可：该 DFP 按 GigaDevice SLA-GD0006-version1.1 授权（Addon 仓库根
目录的 LICENSE），仅允许配合兆易芯片用于开发，禁止再分发。

用法:
    python tools/fetch_pack.py
    python tools/fetch_pack.py --force
    python tools/fetch_pack.py --url https://mirror/... --dest packs/dfp.pack
    python tools/fetch_pack.py --no-svd
"""

import argparse
import hashlib
import os
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

PACK_NAME = "GigaDevice.GD32F30x_DFP.2.6.0.pack"
DEFAULT_URL = (
    "https://raw.githubusercontent.com/GigaDevice-GD32-MCU/GD32F30x_Addon/"
    "main/Keil/Keil5/" + PACK_NAME
)
PACK_SHA256 = "ef90301be96d0607cf3ed46742d9b08a68ad7e4b07b2259b5f9062d45feabe78"
SVD_PREFIX = "svd/"
SVD_SUFFIX = ".svd"
DEFAULT_SVD_DIR = Path("svd")
LICENSE_URL = (
    "https://github.com/GigaDevice-GD32-MCU/GD32F30x_Addon/blob/main/LICENSE"
)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path):
    actual = sha256_of(path)
    if actual.lower() != PACK_SHA256:
        raise ValueError(f"SHA-256 mismatch (expected {PACK_SHA256}, got {actual})")
    with zipfile.ZipFile(path) as pack:
        bad = pack.testzip()
        if bad is not None:
            raise ValueError(f"corrupt zip entry: {bad}")
        pdsc = next((n for n in pack.namelist() if n.lower().endswith(".pdsc")), None)
        if pdsc is None:
            raise ValueError("pack contains no .pdsc file")
        if 'version="2.6.0"' not in pack.read(pdsc).decode("utf-8", "replace"):
            raise ValueError("pack does not declare version 2.6.0")


def extract_svds(pack_path, svd_dir):
    with zipfile.ZipFile(pack_path) as pack:
        members = sorted(
            name
            for name in pack.namelist()
            if name.lower().startswith(SVD_PREFIX) and name.lower().endswith(SVD_SUFFIX)
        )
        if not members:
            raise ValueError("pack contains no SVD/*.svd file")
        extracted = 0
        for member in members:
            data = pack.read(member)
            dest = svd_dir / Path(member).name
            if dest.exists() and dest.read_bytes() == data:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            extracted += 1
    if extracted:
        print(f"Extracted {extracted} SVD file(s) to {svd_dir}")
    else:
        print(f"SVD already extracted: {svd_dir}")


def download(url, dest):
    print(f"Downloading {url}")
    request = urllib.request.Request(
        url, headers={"User-Agent": "gd32f303-gcc-baseline"}
    )
    with urllib.request.urlopen(request, timeout=60) as response, open(dest, "wb") as out:
        shutil.copyfileobj(response, out)


def main():
    parser = argparse.ArgumentParser(
        description="Download and verify the GD32F30x DFP 2.6.0 pack"
    )
    parser.add_argument(
        "--dest",
        default=str(Path("packs") / PACK_NAME),
        help="destination .pack path (default: packs/<pack name>)",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="download URL")
    parser.add_argument("--force", action="store_true", help="replace an existing file")
    parser.add_argument(
        "--svd-dir",
        default=str(DEFAULT_SVD_DIR),
        help="directory for extracted SVD files (default: svd/)",
    )
    parser.add_argument(
        "--no-svd", action="store_true", help="only fetch the pack, do not extract SVDs"
    )
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        try:
            verify(dest)
        except Exception as err:
            if not args.force:
                print(
                    f"[error] existing file is not the expected pack: {dest}\n"
                    f"        {err}\n"
                    "        re-run with --force to download it again",
                    file=sys.stderr,
                )
                return 1
            print(f"Existing file failed verification, replacing it: {err}")
        else:
            print(f"Already downloaded and verified: {dest}")
            if not args.no_svd:
                extract_svds(dest, Path(args.svd_dir))
            return 0

    fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), suffix=".pack.part")
    os.close(fd)
    try:
        download(args.url, tmp_name)
        verify(tmp_name)
        if dest.exists() and not os.access(dest, os.W_OK):
            os.chmod(dest, stat.S_IWRITE | stat.S_IREAD)
        os.replace(tmp_name, dest)
    except Exception as err:
        print(f"[error] failed to fetch the pack: {err}", file=sys.stderr)
        return 1
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

    print(f"Saved and verified: {dest}")
    print(f"SHA-256: {PACK_SHA256}")
    print(
        "License: GigaDevice SLA-GD0006-version1.1; use is limited to\n"
        "         development with GigaDevice devices, and redistribution\n"
        f"         of the pack is not permitted. {LICENSE_URL}"
    )
    if not args.no_svd:
        extract_svds(dest, Path(args.svd_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
