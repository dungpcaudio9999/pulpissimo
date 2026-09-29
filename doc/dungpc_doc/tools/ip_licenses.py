#!/usr/bin/env python3
"""List every Bender package with version, commit, source and detected license.

Run from the root of a PULPissimo checkout (needs Bender.lock and utils/bin/bender):
    python3 doc/dungpc_doc/tools/ip_licenses.py
Output: name|version|commit|source|license|license source|license files|path
UNKNOWN means no LICENSE file and no recognizable header: check by hand.
"""
import yaml, subprocess, os, re, glob, sys
root = os.getcwd()
lock = yaml.safe_load(open("Bender.lock"))["packages"]
def detect(path):
    files = [f for f in glob.glob(os.path.join(path, "*")) if re.match(r"(LICEN[CS]E|COPYING)", os.path.basename(f), re.I)]
    text = ""
    for f in files:
        if os.path.isfile(f): text += open(f, errors="ignore").read(4000)
    src = "file"
    if not text:
        # fallback: SPDX / header in sources
        hits = subprocess.run(["grep","-rhoE","SPDX-License-Identifier: *[A-Za-z0-9.+-]+|Solderpad Hardware License,? Version [0-9.]+|Apache License,? Version 2.0",path,"--include=*.sv","--include=*.v","--include=*.vhd"],capture_output=True,text=True).stdout
        text = hits; src = "headers"
    t = text
    if re.search(r"Solderpad Hardware License.{0,20}(Version|v)\s*2\.1|SHL-2\.1", t, re.I|re.S): lic="SHL-2.1"
    elif re.search(r"Solderpad Hardware License.{0,20}(Version|v)\s*0\.51|SHL-0\.51", t, re.I|re.S): lic="SHL-0.51"
    elif re.search(r"Solderpad", t, re.I): lic="Solderpad (version n/a)"
    elif re.search(r"Apache License.{0,20}2\.0|Apache-2\.0", t, re.I|re.S): lic="Apache-2.0"
    elif re.search(r"GNU LESSER GENERAL PUBLIC LICENSE|LGPL", t): lic="LGPL"
    elif re.search(r"BSD", t): lic="BSD"
    elif re.search(r"MIT License|Permission is hereby granted, free of charge", t): lic="MIT"
    else: lic="UNKNOWN"
    return lic, src, [os.path.relpath(f, path) for f in files]
rows=[]
for name, p in lock.items():
    path = subprocess.run(["utils/bin/bender","path",name],capture_output=True,text=True).stdout.strip()
    lic, src, files = detect(path)
    s = p["source"]; url = s.get("Git") or s.get("Path") or str(s)
    rows.append((name, p.get("version") or "-", (p.get("revision") or "-")[:8], url, lic, src, ",".join(files) or "-", os.path.relpath(path, root)))
for r in rows: print("|".join(map(str,r)))
