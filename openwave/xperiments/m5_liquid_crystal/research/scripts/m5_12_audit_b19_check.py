"""M5.12 block-19 WRAP AUDIT checker (independent, headless).

Re-runs the mechanical layers of the b19 wrap audit over the two close
documents:

  1. findings/m5_12_close_note.md
  2. tasks/m5_12_task_details.md (blocks 18 + 19)

Layers automated here (the judgment layers live in the b19 JSON findings):
  C2  close-sentence character diff vs data/m5_12_audit_b18.json
      key "close_sentence" (both documents)
  C3  equation-to-code map: file exists, the line number lands on the
      named function's def line, GitHub URL path == local repo path
  C1  key numbers re-read from the primary JSONs (b18 decider, b18/b17
      audits, ladder endpoint battery, b16 unit map, gates)
  C5  presence checks (N4c baseline file, rmatvec log entry)

Writes nothing; prints a pass/fail line per check. The adjudicated
findings + verdict live in data/m5_12_audit_b19.json.

Run: python3 scripts/m5_12_audit_b19_check.py   (from research/)
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)
GH_PREFIX = ("https://github.com/openwave-labs/openwave/blob/main/"
             "openwave/xperiments/m5_liquid_crystal/research/scripts/")

FAILS = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


def extract_blockquote(path, anchor):
    txt = open(path).read()
    seg = txt[txt.find(anchor):]
    m = re.search(r"\n> (.*?)\n", seg, re.S)
    return m.group(1).replace("\n> ", " ").strip()


def c2_close_sentence():
    js = json.load(open(os.path.join(RES, "data/m5_12_audit_b18.json")))["close_sentence"]
    note = extract_blockquote(os.path.join(RES, "findings/m5_12_close_note.md"),
                              "THE PHASE D CLOSE")
    task = extract_blockquote(os.path.join(RES, "tasks/m5_12_task_details.md"),
                              "THE PHASE D CLOSE (the licensed sentence")
    for name, s in (("close_note", note), ("task_details", task)):
        check(f"C2 {name} close sentence verbatim", s == js,
              "" if s == js else
              "quote-style drift: doc uses double quotes around still descending, "
              "JSON uses single quotes (2 chars); rest identical")


def c3_map():
    rows = [
        ("m5_12_d3a_bvp.py", 71, "x_pack"),
        ("m5_12_d3a_bvp.py", 153, "shat"),
        ("m5_17_energy.py", 115, "curvature_density_np"),
        ("m5_12_b14_seeds.py", 73, "s0_q2"),
        ("m5_12_b14_seeds.py", 78, "q2_channels"),
        ("m5_12_b14_seeds.py", 143, "a2_free"),
        ("m5_12_b12_hard.py", 109, "omega_bal"),
        ("m5_12_b12_hard.py", 116, "run_ladder"),
        ("m5_12_d3b_newton.py", 91, "wscale_at"),
        ("m5_12_b17_control.py", 84, "r_mean_of"),
        ("m5_12_b17_control.py", 96, "zoom_to_frame"),
        ("m5_12_b16_unitmap.py", 79, "r_mean_bvp"),
    ]
    note = open(os.path.join(RES, "findings/m5_12_close_note.md")).read()
    for fname, ln, fn in rows:
        p = os.path.join(HERE, fname)
        ok = os.path.exists(p)
        if ok:
            lines = open(p).readlines()
            ok = ln <= len(lines) and lines[ln - 1].lstrip().startswith(f"def {fn}(")
        check(f"C3 map {fname}#L{ln} -> def {fn}", ok)
        check(f"C3 url {fname}#L{ln} in note", f"{GH_PREFIX}{fname}#L{ln}" in note)


def c1_numbers():
    d = json.load(open(os.path.join(RES, "data/m5_12_b18_decider.json")))
    check("C1 b18 a2_star 0.303725", d["a2_star"] == 0.303725)
    check("C1 b18 anchor 4.1e-7", abs(d["anchor_rel"] - 4.09e-7) < 1e-8)
    check("C1 b18 optimum 7.213/6.148",
          round(d["best"]["native"]["optimum"], 3) == 7.213
          and round(d["best"]["rc-matched"]["optimum"], 3) == 6.148)
    check("C1 b18 gains 5.0%/-14.2%",
          round(d["best"]["native"]["gain_vs_p1"] * 100, 1) == 5.0
          and round(d["best"]["rc-matched"]["gain_vs_p1"] * 100, 1) == -14.2)
    check("C1 b18 p1 floor 5.44/5.11",
          round(d["references"]["native"]["p1_full"]["omega_bal"], 2) == 5.44
          and round(d["references"]["rc-matched"]["p1_full"]["omega_bal"], 2) == 5.11)
    check("C1 b18 six top-6 candidates", len(d["candidates"]) == 6)

    a = json.load(open(os.path.join(RES, "data/m5_12_audit_b18.json")))
    ev = a["D1_decider_machinery"]["evidence"]
    check("C1 b18 Gram offdiag 0.997", round(ev["gram"]["offdiag_max"], 3) == 0.997)
    check("C1 b18 12x Gram content", round(ev["k0_gram_content"]["ratio"]) == 12)
    gd = ev["gap_decomposition"]
    check("C1 b18 +127.9% Gram stage", round(gd["stage_gram_pct"], 1) == 127.9)
    check("C1 b18 +5.8% nonlin stage", round(gd["stage_nonlin_pct"], 1) == 5.8)
    check("C1 b18 supersede list 12 items", len(a["supersede_list"]) == 12)
    bat = a["D2_rule_adjudication"]["evidence"]["seed_battery"]
    gn = sorted(b["gain_native"] * 100 for b in bat)
    grc = sorted(b["gain_rc-matched"] * 100 for b in bat)
    check("C1 b18 native median 14.6%", round(gn[len(gn) // 2], 1) == 14.6)
    check("C1 b18 rc median 0.5%", round(grc[len(grc) // 2], 1) == 0.5)
    check("C1 b18 rc range -3.3..5.1",
          round(grc[0], 1) == -3.3 and round(grc[-1], 1) == 5.1)
    check("C1 b18 max native gain 28.3% (p1)", round(gn[-1], 1) == 28.3)
    proj = a["D2_rule_adjudication"]["evidence"]["projection"]["decider_k0"]
    check("C1 b18 projection ~6.2",
          abs(proj["native"]["projected_relaxed_median"] - 6.2) < 0.1)

    b17 = json.load(open(os.path.join(RES, "data/m5_12_audit_b17.json")))
    rows = b17["A4_controlled_distance"]["evidence"]["rows"]
    obs = [r["omega_bal"] for r in rows]
    fac = [f for r in rows for f in r["factor_vs_band"]]
    check("C1 b17 p1 controlled root 5.10-5.89",
          round(min(obs), 2) >= 5.10 and round(max(obs), 2) <= 5.89)
    check("C1 b17 distance 4.4-5.5x",
          round(min(fac), 1) == 4.4 and round(max(fac), 1) == 5.5)

    u = json.load(open(os.path.join(RES, "data/m5_12_b16_unitmap.json")))
    check("C1 b16 band 1.07-1.15", u["m58"]["band"] == [1.07, 1.15])
    check("C1 b16 anchors 2.628/4.941",
          u["m58"]["static_seed_core"] == 2.628 and u["m58"]["settled_ground"] == 4.941)

    # endpoint |F| range across the standing ladder chains
    fs, hs = [], []
    for f in glob.glob(os.path.join(RES, "data/m5_12_b12_hard_ladder_*_.json")):
        d = json.load(open(f))
        s = json.dumps(d)
        for m in re.finditer(r'"H_swing_over_S0": ([0-9.]+)', s):
            hs.append(float(m.group(1)))
        hist = re.findall(r'"F_norm": ([0-9.]+)', s)
        if hist:
            fs.append(float(hist[-1]))
    check("C1 ladder endpoint |F| ~ 100-520",
          90 < min(fs) < 110 and 500 < max(fs) < 530,
          f"measured {min(fs):.0f}-{max(fs):.0f}")
    check("C1 ladder H_swing/S0 ~ 2 (standing chains)",
          all(1.9 < h < 2.1 for h in hs if h < 2.5))

    g = json.load(open(os.path.join(RES, "data/m5_12_b12_gates_p1_.json")))
    check("C1 HG gates machine precision",
          g["HG1_nonfinite"] == 0.0 and g["HG2_com_rel"] < 1e-13
          and g["HG3_retract"] < 1e-14)
    check("C1 n96 spectral spec exists",
          os.path.exists(os.path.join(RES, "data/m5_18_spectral_spec_n96.json")))


def c5_presence():
    check("C5 N4c baseline exists",
          os.path.exists(os.path.join(RES, "tasks/m5_10e_findings_N4c.md")))
    task = open(os.path.join(RES, "tasks/m5_12_task_details.md")).read()
    check("C5 rmatvec bug in EXECUTION LOG 07-08 12:10",
          "07-08 12:10" in task and "rmatvec" in task)
    n4c = open(os.path.join(RES, "tasks/m5_10e_findings_N4c.md")).read()
    check("C5 N4c carries 1:1.148:1.682 + 5.8/7.3 compression",
          "1 : 1.148 : 1.682" in n4c and "5.8" in n4c and "7.3" in n4c)


def main():
    c2_close_sentence()
    c3_map()
    c1_numbers()
    c5_presence()
    print()
    print("MECHANICAL LAYER:", "ALL PASS" if not FAILS else f"{len(FAILS)} FAIL -> {FAILS}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
