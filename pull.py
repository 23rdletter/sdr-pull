#!/usr/bin/env python3
"""Daily SDR/BDR pull. Runs on GitHub Actions, which has unrestricted egress.

Stage 1: resolve each candidate company to its live ATS board (cached in
         ats_universe.json, so this only costs anything on the first run).
Stage 2: pull every posting from those boards, plus Adzuna.
Stage 3: filter to SDR/BDR + UK, dedupe against seen.json, write outputs.

Outputs, all committed back to the repo so Claude can read them with one fetch:
  data/jobs_latest.json  every live matching role
  data/new_today.json    only roles never seen before
  data/seen.json         the dedupe ledger
"""
import json, os, re, sys, time, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests
from companies import company_list, slug_variants

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (compatible; personal-job-alert/1.0)"}
TIMEOUT = 12

# North West employers advertise SDR work as "Business Development Executive".
# Searching only for SDR/BDR misses most of the local market, so both vocabularies
# are matched here. Verified against Indeed Manchester, 27 July 2026.
TITLE_RE = re.compile(
    r"\b(sdr|bdr|sales development|business development representative|"
    r"business development executive|business development consultant|"
    r"new business sales|outbound sales|inside sales|sales development rep|"
    r"business development rep)\b", re.I)
UK_RE = re.compile(
    r"\b(uk|u\.k\.|united kingdom|england|scotland|wales|northern ireland|london|"
    r"manchester|liverpool|leeds|birmingham|bristol|edinburgh|glasgow|cardiff|"
    r"belfast|sheffield|newcastle|nottingham|reading|cambridge|oxford|brighton|"
    r"emea|remote)\b", re.I)

ATS = [
    ("greenhouse",      "https://boards-api.greenhouse.io/v1/boards/{s}/jobs"),
    ("lever",           "https://api.lever.co/v0/postings/{s}?mode=json"),
    ("ashby",           "https://api.ashbyhq.com/posting-api/job-board/{s}"),
    ("workable",        "https://apply.workable.com/api/v1/widget/accounts/{s}?details=true"),
    ("smartrecruiters", "https://api.smartrecruiters.com/v1/companies/{s}/postings?limit=100"),
    ("recruitee",       "https://{s}.recruitee.com/api/offers/"),
]


def get(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=UA)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------- stage 1
def normalise(ats, data, company, slug):
    out = []
    def add(title, loc, url):
        if title and TITLE_RE.search(title) and UK_RE.search(f"{loc} {title}"):
            out.append({"title": title.strip(), "company": company,
                        "location": (loc or "").strip(), "url": url,
                        "source": f"ATS/{ats}", "slug": slug})
    try:
        if ats == "greenhouse":
            for j in data.get("jobs", []):
                add(j.get("title"), (j.get("location") or {}).get("name", ""), j.get("absolute_url"))
        elif ats == "lever":
            for j in data:
                c = j.get("categories") or {}
                add(j.get("text"), c.get("location", ""), j.get("hostedUrl"))
        elif ats == "ashby":
            for j in data.get("jobs", []):
                add(j.get("title"), j.get("location", ""), j.get("jobUrl"))
        elif ats == "workable":
            for j in data.get("jobs", []):
                loc = ", ".join(filter(None, [j.get("city"), j.get("country")]))
                add(j.get("title"), loc, j.get("url"))
        elif ats == "smartrecruiters":
            for j in data.get("content", []):
                loc = (j.get("location") or {})
                add(j.get("name"), f"{loc.get('city','')}, {loc.get('country','')}",
                    f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}")
        elif ats == "recruitee":
            for j in data.get("offers", []):
                add(j.get("title"), j.get("location", ""), j.get("careers_url"))
    except Exception as e:
        print(f"  parse error {company}/{ats}: {e}", file=sys.stderr)
    return out


def resolve(item):
    name, sector = item
    for slug in slug_variants(name):
        for ats, tmpl in ATS:
            data = get(tmpl.format(s=slug))
            if not data:
                continue
            n = (len(data) if isinstance(data, list)
                 else len(data.get("jobs", data.get("offers", data.get("content", [])))))
            if n:
                return {"company": name, "sector": sector, "ats": ats, "slug": slug}
    return None


def build_universe():
    path = os.path.join(DATA, "ats_universe.json")
    if os.path.exists(path):
        u = json.load(open(path))
        print(f"universe loaded from cache: {len(u)} boards")
        return u
    cands = company_list()
    print(f"first run: probing {len(cands)} companies...")
    with ThreadPoolExecutor(max_workers=32) as ex:
        u = [r for r in ex.map(resolve, cands) if r]
    json.dump(u, open(path, "w"), indent=1)
    print(f"universe built: {len(u)}/{len(cands)} companies resolved")
    return u


# ---------------------------------------------------------------- stage 2
def pull_ats(universe):
    tmpl = dict(ATS)
    def one(entry):
        data = get(tmpl[entry["ats"]].format(s=entry["slug"]))
        if not data:
            return []
        rows = normalise(entry["ats"], data, entry["company"], entry["slug"])
        for r in rows:
            r["sector"] = entry["sector"]
        return rows
    with ThreadPoolExecutor(max_workers=32) as ex:
        return [r for batch in ex.map(one, universe) for r in batch]


# Adzuna's default `what` matches the whole advert body, which is why a plain
# "sales development representative" search returns 23,000 results topped by estate
# agents. `title_only=1` restricts the match to the job title, which is the API
# equivalent of the site's adv=1&qtl= advanced search. Verified 27 July 2026.
ADZUNA_QUERIES = [
    # Remote-first: the active search
    {"what": "development representative", "title_only": 1},
    {"what": "sales development", "title_only": 1},
    {"what": "business development representative", "title_only": 1},
    # North West local vocabulary, parked but still collected
    {"what": "business development executive", "title_only": 1,
     "where": "manchester", "distance": 50},
    {"what": "development representative", "title_only": 1,
     "where": "manchester", "distance": 50},
    {"what": "business development executive", "title_only": 1,
     "where": "liverpool", "distance": 40},
]


def pull_adzuna():
    app_id, app_key = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        print("adzuna: no credentials, skipping")
        return []
    rows = []
    for q in ADZUNA_QUERIES:
        for page in (1, 2):
            params = {"app_id": app_id, "app_key": app_key, "results_per_page": 50,
                      "content-type": "application/json", **q}
            url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
            try:
                r = requests.get(url, params=params, timeout=TIMEOUT, headers=UA)
                if r.status_code != 200:
                    print(f"adzuna {q['what']} p{page}: HTTP {r.status_code}")
                    break
                for j in r.json().get("results", []):
                    # Adzuna wraps matched terms in <strong> tags inside the title,
                    # e.g. "Sales <strong>Development</strong> Representative". Strip
                    # them BEFORE the regex test or the word boundaries never match
                    # and every Adzuna result is silently discarded.
                    title = re.sub(r"<[^>]+>", "", j.get("title", "")).strip()
                    if not TITLE_RE.search(title):
                        continue
                    lo, hi = j.get("salary_min"), j.get("salary_max")
                    rows.append({
                        "title": title,
                        "company": (j.get("company") or {}).get("display_name", "Unknown"),
                        "location": (j.get("location") or {}).get("display_name", ""),
                        "url": j.get("redirect_url"),
                        "salary": f"£{int(lo):,} - £{int(hi):,}" if lo and hi else "",
                        "source": "Adzuna", "sector": "unknown",
                        "posted": j.get("created", "")[:10],
                    })
            except Exception as e:
                print(f"adzuna error: {e}", file=sys.stderr)
            time.sleep(0.4)
    print(f"adzuna: {len(rows)} matching roles")
    return rows


# ---------------------------------------------------------------- stage 3
def key(r):
    return re.sub(r"[^a-z0-9]+", "",
                  f"{r['company'].lower()}{r['title'].lower()}")[:80]


def main():
    today = dt.date.today().isoformat()
    universe = build_universe()
    ats_rows = pull_ats(universe)
    print(f"ATS: {len(ats_rows)} matching roles from {len(universe)} boards")
    rows = ats_rows + pull_adzuna()

    merged, seen_now = {}, set()
    for r in rows:
        k = key(r)
        if k not in merged:
            r.setdefault("salary", "")
            merged[k] = r
            seen_now.add(k)

    seen_path = os.path.join(DATA, "seen.json")
    seen_before = json.load(open(seen_path)) if os.path.exists(seen_path) else {}
    new = [v for k, v in merged.items() if k not in seen_before]
    for k in seen_now:
        seen_before.setdefault(k, today)

    json.dump(list(merged.values()), open(os.path.join(DATA, "jobs_latest.json"), "w"), indent=1)
    json.dump(new, open(os.path.join(DATA, "new_today.json"), "w"), indent=1)
    json.dump(seen_before, open(seen_path, "w"), indent=1)
    json.dump({"run_date": today, "total_live": len(merged), "new_today": len(new),
               "boards_polled": len(universe)},
              open(os.path.join(DATA, "status.json"), "w"), indent=1)
    print(f"\n{len(merged)} live matching roles, {len(new)} new today")


if __name__ == "__main__":
    main()
