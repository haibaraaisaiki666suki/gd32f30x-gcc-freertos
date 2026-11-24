#!/usr/bin/env python3
"""Select a GD32F30x device and update the build/debug configuration.

The device database is read from the CMSIS-Pack (PDSC). The script updates:

  Makefile                        C_DEFS, startup file, linker script
  .vscode/launch.json             executable, targetId, svdFile
  .vscode/c_cpp_properties.json   configuration name, density define

TARGET (the output file name) is deliberately left unchanged, so firmware
artifacts stay generic and independent of the selected device.

It also picks the device SVD for the Cortex-Debug peripheral view (written to
launch.json). All SVDs are normally extracted by fetch_pack.py; the selected
one is extracted here only if it is missing from svd/.

The pack is not redistributed with this project. Obtain it first with
`make debug-setup` and keep it outside version control.

Usage:
    python tools/select_device.py GD32F303VC
    python tools/select_device.py --list
    python tools/select_device.py GD32F303VE --dry-run
    python tools/select_device.py GD32F307VC --pack path/to/dfp.pack
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK = ROOT / "packs" / "GigaDevice.GD32F30x_DFP.2.6.0.pack"
LD_DIR = ROOT / "GD32F30x" / "CMSIS" / "GD" / "GD32F30x" / "Source" / "GCC" / "Ld"
STARTUP_DIR = ROOT / "GD32F30x" / "CMSIS" / "GD" / "GD32F30x" / "Source" / "GCC"
MAKEFILE = ROOT / "Makefile"
LAUNCH_JSON = ROOT / ".vscode" / "launch.json"
CPP_JSON = ROOT / ".vscode" / "c_cpp_properties.json"

DEVICE_RE = re.compile(r"^GD32F(\d{3})([A-Z])([A-Z])$")
TARGET_RE = re.compile(r"(?m)^TARGET\s*=\s*(\S+)\s*$")


def load_pdsc(pack_path):
    with zipfile.ZipFile(pack_path) as pack:
        name = next((n for n in pack.namelist() if n.lower().endswith(".pdsc")), None)
        if name is None:
            raise ValueError("pack contains no .pdsc file")
        return ET.fromstring(pack.read(name))


def collect_devices(pdsc):
    return {dev.get("Dname").upper(): dev for dev in pdsc.iter("device")}


def memory_size(dev, memory_id):
    node = dev.find("memory[@id='%s']" % memory_id)
    if node is None or node.get("size") is None:
        return None
    return int(node.get("size"), 0)


def density_define(dev, flash_size):
    compile_node = dev.find("compile")
    if compile_node is not None and compile_node.get("define"):
        return compile_node.get("define"), "PDSC"
    if flash_size is None:
        raise ValueError("PDSC has no compile define and no IROM1 size")
    if flash_size <= 0x10000:          # <= 64 KiB
        return "GD32F30X_CL", "inferred from flash size"
    if flash_size <= 0x80000:          # <= 512 KiB
        return "GD32F30X_HD", "inferred from flash size"
    return "GD32F30X_XD", "inferred from flash size"


def svd_member(dev, define, pack_path):
    debug_node = dev.find("debug")
    if debug_node is not None and debug_node.get("svd"):
        member = debug_node.get("svd")
    else:
        density = define.rsplit("_", 1)[1]
        member = "SVD/GD32F30x_%s.svd" % density
    with zipfile.ZipFile(pack_path) as pack:
        if member not in pack.namelist():
            raise ValueError("SVD %s not found in the pack" % member)
    return member


def find_startup(define):
    density = define.rsplit("_", 1)[1].lower()
    startup = "startup_gd32f30x_%s.S" % density
    if not (STARTUP_DIR / startup).is_file():
        raise ValueError("startup file not found: %s" % startup)
    return startup


def find_linker(device):
    match = DEVICE_RE.match(device)
    if match is None:
        raise ValueError("cannot parse device name: %s" % device)
    series, _package, size_letter = match.groups()
    name = "gd32f%sx%s_flash.ld" % (series, size_letter)
    if not (LD_DIR / name).is_file():
        available = sorted(p.name for p in LD_DIR.glob("gd32f%sx*_flash.ld" % series))
        raise ValueError(
            "linker script not found: %s\navailable for GD32F%s: %s"
            % (name, series, ", ".join(available) or "none")
        )
    return name


def parse_linker_lengths(text):
    lengths = {}
    for key in ("FLASH", "RAM"):
        match = re.search(
            r"%s\s*\([^)]*\)\s*:\s*ORIGIN\s*=\s*[^,]+,\s*LENGTH\s*=\s*(\S+)"
            % key,
            text,
            re.IGNORECASE,
        )
        if match:
            value = match.group(1)
            multiplier = {"K": 1024, "M": 1024 * 1024}.get(value[-1:].upper())
            lengths[key] = int(value[:-1], 0) * multiplier if multiplier else int(value, 0)
    return lengths


def extract_svd(pack_path, member, dest_dir):
    with zipfile.ZipFile(pack_path) as pack:
        data = pack.read(member)
    dest = dest_dir / Path(member).name
    if dest.exists() and dest.read_bytes() == data:
        return dest, False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest, True


def read_target(text):
    match = TARGET_RE.search(text)
    if match is None:
        raise ValueError("could not find the TARGET assignment in the Makefile")
    return match.group(1)


def update_makefile(text, define, startup, linker):
    new_text, count = re.subn(
        r"-DGD32F30X_(?:CL|HD|XD)\b", "-D%s" % define, text
    )
    if count != 1:
        raise ValueError("could not find -DGD32F30X_* in C_DEFS")
    new_text, count = re.subn(
        r"(?m)^LDSCRIPT\s*=.*$",
        "LDSCRIPT = GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/%s" % linker,
        new_text,
    )
    if count != 1:
        raise ValueError("could not find the LDSCRIPT assignment")
    new_text, count = re.subn(
        r"startup_gd32f30x_(?:cl|hd|xd)\.S", startup, new_text
    )
    if count != 1:
        raise ValueError("could not find the startup file in ASM_SOURCES")
    return new_text


def update_launch_json(data, output, target_id, svd_name):
    configurations = data.get("configurations", [])
    config = next(
        (c for c in configurations if c.get("type") == "cortex-debug"), None
    )
    if config is None:
        raise ValueError("no cortex-debug configuration in .vscode/launch.json")
    config["executable"] = "${workspaceFolder}/build/%s.elf" % output
    config["targetId"] = target_id
    config["svdFile"] = "${workspaceFolder}/svd/%s" % svd_name


def update_cpp_json(data, device, define):
    configurations = data.get("configurations", [])
    if not configurations:
        raise ValueError("no configuration in .vscode/c_cpp_properties.json")
    config = configurations[0]
    config["name"] = device
    defines = [d for d in config.get("defines", []) if not d.startswith("GD32F30X_")]
    defines.append(define)
    config["defines"] = defines


def write_text(path, text):
    if path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def dump_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Select a GD32F30x device and update build/debug configuration"
    )
    parser.add_argument("device", nargs="?", help="device name, e.g. GD32F303VC")
    parser.add_argument("--pack", default=str(DEFAULT_PACK), help="path to the DFP pack")
    parser.add_argument("--list", action="store_true", help="list devices in the pack")
    parser.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
    args = parser.parse_args()

    pack_path = Path(args.pack)
    if not pack_path.is_file():
        print(
            "[error] pack not found: %s\n"
            "        run 'make debug-setup' or pass --pack <path>" % pack_path,
            file=sys.stderr,
        )
        return 1

    try:
        pdsc = load_pdsc(pack_path)
        devices = collect_devices(pdsc)

        if args.list:
            print("Devices in %s:\n" % pack_path.name)
            for name in sorted(devices):
                dev = devices[name]
                flash = memory_size(dev, "IROM1")
                try:
                    define, _origin = density_define(dev, flash)
                except Exception:
                    define = "?"
                debug_node = dev.find("debug")
                svd = debug_node.get("svd") if debug_node is not None else "(inferred)"
                print(
                    "  %-11s define=%-12s flash=%-8s svd=%s"
                    % (name, define, "0x%X" % flash if flash else "?", svd)
                )
            return 0

        if not args.device:
            parser.error("a device name is required (or use --list)")

        device = args.device.upper()
        if device not in devices:
            print(
                "[error] device %s not found in the pack; use --list" % device,
                file=sys.stderr,
            )
            return 1

        dev = devices[device]
        flash_size = memory_size(dev, "IROM1")
        ram_size = memory_size(dev, "IRAM1")
        define, origin = density_define(dev, flash_size)
        startup = find_startup(define)
        linker = find_linker(device)
        member = svd_member(dev, define, pack_path)
        svd_name = Path(member).name
        target_id = device.lower()

        linker_path = LD_DIR / linker
        lengths = parse_linker_lengths(linker_path.read_text(encoding="utf-8"))
        warnings = []
        if flash_size and lengths.get("FLASH") and lengths["FLASH"] != flash_size:
            warnings.append(
                "linker FLASH %s != PDSC IROM1 0x%X"
                % ("0x%X" % lengths["FLASH"], flash_size)
            )
        if ram_size and lengths.get("RAM") and lengths["RAM"] != ram_size:
            warnings.append(
                "linker RAM %s != PDSC IRAM1 0x%X"
                % ("0x%X" % lengths["RAM"], ram_size)
            )

        makefile_text = update_makefile(
            MAKEFILE.read_text(encoding="utf-8"), define, startup, linker
        )
        output = read_target(makefile_text)
        launch_data = json.loads(LAUNCH_JSON.read_text(encoding="utf-8"))
        update_launch_json(launch_data, output, target_id, svd_name)
        cpp_data = json.loads(CPP_JSON.read_text(encoding="utf-8"))
        update_cpp_json(cpp_data, device, define)

        print("Device:  %s" % device)
        print("Density: %s (%s)" % (define, origin))
        print("Startup: %s" % startup)
        print("Linker:  %s" % linker)
        print("Output:  build/%s.elf" % output)
        print("pyOCD:   targetId=%s" % target_id)
        print("SVD:     %s -> svd/%s" % (member, svd_name))
        for warning in warnings:
            print("[warn]  %s" % warning)

        if args.dry_run:
            print("\nDry run: no files were changed.")
            return 0

        changed = []
        if write_text(MAKEFILE, makefile_text):
            changed.append("Makefile")
        launch_text = dump_json(launch_data)
        if write_text(LAUNCH_JSON, launch_text):
            changed.append(".vscode/launch.json")
        cpp_text = dump_json(cpp_data)
        if write_text(CPP_JSON, cpp_text):
            changed.append(".vscode/c_cpp_properties.json")

        svd_dest, extracted = extract_svd(pack_path, member, ROOT / "svd")
        if extracted:
            changed.append(str(svd_dest.relative_to(ROOT)))

        if changed:
            print("\nUpdated: %s" % ", ".join(changed))
        else:
            print("\nConfiguration already up to date.")
        print("Next: make clean && make")
        return 0

    except Exception as err:
        print("[error] %s" % err, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
