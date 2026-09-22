import json, statistics

def load(fn):
    raw = json.load(open(fn))
    return {sub: {(int(k) if k.isdigit() else k): v for k,v in d.items()} for sub, d in raw.items()}

BEDS = [2,3,4,5]

def compute_ratios(*raws):
    ratios = {(2,3):[], (3,4):[], (4,5):[]}
    for raw in raws:
        for sub, d in raw.items():
            for a,b in ratios:
                if d.get(a) and d.get(b):
                    ratios[(a,b)].append(d[b]/d[a])
    return {k: statistics.mean(v) for k,v in ratios.items() if v}

def compute_hu_ratio(*raws):
    vals = []
    for raw in raws:
        for sub, d in raw.items():
            if d.get(3) and d.get("unit3"):
                vals.append(d[3]/d["unit3"])
    return statistics.mean(vals) if vals else 1.232

def fill_curve(known3, avg_ratio):
    c = {3: known3}
    c[2] = known3 / avg_ratio[(2,3)]
    c[4] = known3 * avg_ratio[(3,4)]
    c[5] = c[4] * avg_ratio[(4,5)]
    return c

def anchor_from_known(known, avg_ratio):
    nearest_bed = min(known.keys())
    val = known[nearest_bed]
    anchor3 = val
    b = nearest_bed
    while b > 3:
        anchor3 = anchor3 / avg_ratio[(b-1,b)]
        b -= 1
    while b < 3:
        anchor3 = anchor3 * avg_ratio[(b,b+1)]
        b += 1
    return anchor3

def process(raw, avg_ratio, avg_hu_ratio, neighbor_fallback, all_final_ref):
    final = {}
    notes = {}
    for sub, d in raw.items():
        if sub in neighbor_fallback:
            continue
        known = {b: d[b] for b in BEDS if d.get(b)}
        if 3 in known:
            filled = fill_curve(known[3], avg_ratio)
            filled.update(known)
            final[sub] = filled
            notes[sub] = "real Domain data" + ("" if len(known)==4 else f"; interpolated missing tiers from own {sorted(known.keys())} via avg growth ratios")
        elif known:
            anchor3 = anchor_from_known(known, avg_ratio)
            filled = fill_curve(anchor3, avg_ratio)
            filled.update(known)
            final[sub] = filled
            notes[sub] = f"no 3bd sample; anchored from own {min(known.keys())}bd real data via avg growth ratios"
        elif d.get("unit3"):
            anchor3 = d["unit3"] * avg_hu_ratio
            final[sub] = fill_curve(anchor3, avg_ratio)
            notes[sub] = f"no house sales data; anchored from unit 3bd median ({d['unit3']:,.0f}) x avg house/unit premium {avg_hu_ratio:.3f}"
        else:
            final[sub] = None
            notes[sub] = "PENDING neighbor fallback"

    for sub, neighbors in neighbor_fallback.items():
        vals = {b: [] for b in BEDS}
        for n in neighbors:
            src = final.get(n) or all_final_ref.get(n)
            if src:
                for b in BEDS:
                    if src.get(b):
                        vals[b].append(src[b])
        curve = {b: statistics.mean(v) for b,v in vals.items() if v}
        if curve:
            final[sub] = curve
            notes[sub] = f"no usable sales signal; averaged from neighboring suburbs {neighbors}"
        else:
            final[sub] = None
            notes[sub] = f"SKIPPED: neighbors also lacked data"

    return final, notes

# ---- Eastern Suburbs batch 2 (combine with batch1 for ratio robustness) ----
raw_east1 = load("raw_east.json")
raw_east2 = load("raw_east2.json")
avg_ratio_east = compute_ratios(raw_east1, raw_east2)
avg_hu_east = compute_hu_ratio(raw_east1, raw_east2)
print("Eastern Suburbs avg ratios:", {f"{a}->{b}": round(r,3) for (a,b),r in avg_ratio_east.items()})
print("Eastern Suburbs house/unit ratio:", round(avg_hu_east,3))

east1_final = json.load(open("curves_east_final.json"))
NEIGHBOR_FALLBACK_EAST2 = {
    "Potts Point": ["Darlinghurst", "Woolloomooloo", "Elizabeth Bay"],
    "Daceyville": ["Kingsford", "Pagewood"],
    "Phillip Bay": ["Chifley", "Matraville", "Little Bay"],
}
east2_final, east2_notes = process(raw_east2, avg_ratio_east, avg_hu_east, NEIGHBOR_FALLBACK_EAST2, east1_final)

json.dump(east2_final, open("curves_east2_final.json","w"), indent=2)
json.dump(east2_notes, open("curves_east2_notes.json","w"), indent=2)
print("\n--- Eastern Suburbs batch 2 results ---")
for sub, c in east2_final.items():
    print(sub, {b: round(v) for b,v in c.items()} if c else None, "|", east2_notes.get(sub))

# ---- Inner West (new region, self-contained ratios) ----
raw_iw = load("raw_innerwest.json")
avg_ratio_iw = compute_ratios(raw_iw)
avg_hu_iw = compute_hu_ratio(raw_iw)
print("\nInner West avg ratios:", {f"{a}->{b}": round(r,3) for (a,b),r in avg_ratio_iw.items()})
print("Inner West house/unit ratio:", round(avg_hu_iw,3))

iw_final, iw_notes = process(raw_iw, avg_ratio_iw, avg_hu_iw, {}, {})
json.dump(iw_final, open("curves_innerwest_final.json","w"), indent=2)
json.dump(iw_notes, open("curves_innerwest_notes.json","w"), indent=2)
print("\n--- Inner West results ---")
for sub, c in iw_final.items():
    print(sub, {b: round(v) for b,v in c.items()} if c else None, "|", iw_notes.get(sub))
