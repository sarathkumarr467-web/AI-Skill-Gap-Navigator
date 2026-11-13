import urllib.request
import json
import ssl

ctx = ssl.create_default_context()

def check_hf(repo_id):
    url = f"https://huggingface.co/api/datasets/{repo_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "SkillBridgeAI/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            siblings = [s.get("rfilename") for s in data.get("siblings", []) if not s.get("rfilename", "").startswith(".")]
            tags = data.get("tags", [])
            print(f"HF [{repo_id}]: STATUS 200 OK")
            print(f"  Description: {data.get('description', '')[:120]}")
            print(f"  Files: {siblings[:12]}")
            print(f"  Tags: {tags[:6]}")
            return siblings
    except Exception as e:
        print(f"HF [{repo_id}]: ERROR {e}")
        return None

def check_url(name, url):
    req = urllib.request.Request(url, headers={"User-Agent": "SkillBridgeAI/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            print(f"URL [{name}] ({url}): STATUS {resp.status} OK")
            sample = resp.read(300).decode("utf-8", errors="ignore")
            print(f"  Sample snippet: {sample[:150]}")
            return True
    except Exception as e:
        print(f"URL [{name}] ({url}): ERROR {e}")
        return False

if __name__ == "__main__":
    print("=== PROBING 6 DATASET SOURCES ===")
    check_hf("C0ldSmi1e/resume-dataset")
    check_hf("med2425/resume-job-fit-merged-v1")
    check_hf("keerthanshetty/resume-skill-extractor-dataset")
    check_hf("nonameee12233/job-resume-matching")
    check_url("MBPP raw jsonl", "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl")
    check_url("O*NET Center Web", "https://www.onetcenter.org/database.html")
    # Also check direct O*NET downloadable files or onet resource URLs
    check_url("O*NET Skills Resource", "https://www.onetcenter.org/dl_files/database/db_28_0_text/Skills.txt")
    check_url("O*NET Occupations Resource", "https://www.onetcenter.org/dl_files/database/db_29_0_text/Occupation%20Data.txt")
