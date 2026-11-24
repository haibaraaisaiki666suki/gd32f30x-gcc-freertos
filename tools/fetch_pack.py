#!/usr/bin/env python3
"""Download and verify the official GD32F30x DFP (CMSIS-Pack) and extract all SVDs from it.

By default the 2.6.0 pack (released 2025-08-20) is fetched from GigaDevice's
GD32F30x_Addon repository, saved to packs/GigaDevice.GD32F30x_DFP.2.6.0.pack,
and verified with SHA-256. An existing file that passes verification is not
downloaded again.

Once verified, the SVD/*.svd files are extracted from the pack into svd/ so
Cortex-Debug can show peripheral registers. Which SVD a given part uses is
decided by tools/select_device.py (written to svdFile in launch.json). The
SVDs are generated locally, are not tracked by version control, and are not
redistributed.

License: the DFP is licensed under GigaDevice SLA-GD0006-version1.1 (LICENSE
in the root of the Addon repository). It may only be used for development
with GigaDevice chips, and redistribution is not permitted.

Usage:
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
