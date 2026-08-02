
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "knowledge" / "cleaned_knowledge.json"
OUTPUT_FILE = BASE_DIR / "knowledge" / "cleaned_knowledge_v2.json"

START_MARKERS=["###### Description","##### Description","## Description","# Description"]
END_MARKERS=["##### Contact Us","## Contact","About Us","Payment methods","Back to top","Chat with us","All Right Reserved","© 2026 Magic Money Box"]
REMOVE_PATTERNS=[
r"^Open media.*$",r"^\d+\s*/\s*of\s*\d+$",r"^SKU$",r"^Vendor$",r"^Product Type$",r"^Share.*$",r"^Link$",r"^Close share.*$",r"^Buy it now$",r"^Couldn't load pickup.*$",r"^Refresh$",r"^Estimated delivery.*$",r"^View full details$",r"^Mail Phone Both$",r"^Send$",r"^Quantity.*$",r"^Your email address$",r"^\d+Itemssold.*$",r"^\d+\.\d+\s*/\s*\d+\.\d+$",r"^Hurry!.*$",r"^\d+\s*in stock$",r"^Out of stock$",r"^Judge\.me$"]

def normalize(t):
    return re.sub(r"\n{3,}","\n\n",t.replace("\r","")).strip()

def remove_reviews(t):
    m="## Your cart is empty"
    return t[t.find(m):] if m in t else t

def find_start(t):
    pos=None
    for m in START_MARKERS:
        i=t.find(m)
        if i!=-1 and (pos is None or i<pos):
            pos=i
    if pos is not None:
        return pos
    i=t.find("# ")
    return max(i,0)

def find_end(t):
    end=len(t)
    for m in END_MARKERS:
        i=t.find(m)
        if i!=-1:
            end=min(end,i)
    return end

def clean_lines(t):
    out=[];seen=set()
    for line in t.splitlines():
        s=line.strip()
        if not s:
            if out and out[-1]!="": out.append("")
            continue
        if any(re.match(p,s,re.I) for p in REMOVE_PATTERNS):
            continue
        s=re.sub(r"^#{1,6}\s*","",s)
        s=s.replace("&amp;","&")
        k=s.lower()
        if len(s)<80 and k in seen:
            continue
        seen.add(k)
        out.append(s)
    return normalize("\n".join(out))

def process(e):
    t=remove_reviews(e.get("content",""))
    t=t[find_start(t):find_end(t)]
    e["content"]=clean_lines(t)
    return e

def main():
    with open(INPUT_FILE,"r",encoding="utf-8") as f:
        data=json.load(f)
    cleaned=[process(dict(x)) for x in data]
    with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
        json.dump(cleaned,f,ensure_ascii=False,indent=2)
    print("Saved:",OUTPUT_FILE)

if __name__=="__main__":
    main()
