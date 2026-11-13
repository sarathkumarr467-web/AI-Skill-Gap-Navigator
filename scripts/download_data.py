"""
SkillBridge AI - Robust Dataset Acquisition Script
Downloads and caches the 6 core datasets:
1. HuggingFace: C0ldSmi1e/resume-dataset (Resume text classification)
2. HuggingFace: med2425/resume-job-fit-merged-v1 (Resume-Job Fit pairs)
3. HuggingFace: keerthanshetty/resume-skill-extractor-dataset (Skill Extraction)
4. Official O*NET Database (db_28_0_text: Occupations, Skills, Technology Skills)
5. Google Research MBPP: Python Programming Challenges (Question bank & code execution)
6. HuggingFace: nonameee12233/job-resume-matching (Resume-Job Matching)
"""

import os
import sys
import json
import time
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SkillBridgeAI-Pipeline/1.0"
}

def stream_download(url: str, dest_path: Path, max_retries: int = 3, timeout: int = 60) -> bool:
    """Download a file with streaming chunks and live progress reporting."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        print(f"  [CACHE] File exists: {dest_path.name} ({dest_path.stat().st_size / (1024*1024):.2f} MB)", flush=True)
        return True

    print(f"  [CONNECTING] {url}", flush=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")
    
    for attempt in range(1, max_retries + 1):
        try:
            with requests.get(url, headers=HEADERS, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                start_time = time.time()
                
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=131072): # 128KB chunks
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0 and downloaded % (1024 * 1024 * 4) < 131072:
                                pct = (downloaded / total_size) * 100
                                mb = downloaded / (1024 * 1024)
                                total_mb = total_size / (1024 * 1024)
                                print(f"    -> {dest_path.name}: {mb:.1f}MB / {total_mb:.1f}MB ({pct:.1f}%)", flush=True)
                
                # Rename temp to destination
                if temp_path.exists():
                    if dest_path.exists():
                        dest_path.unlink()
                    temp_path.rename(dest_path)
                
                duration = time.time() - start_time
                mb = dest_path.stat().st_size / (1024 * 1024)
                print(f"  [SUCCESS] {dest_path.name} downloaded ({mb:.2f} MB in {duration:.1f}s)", flush=True)
                return True
        except Exception as e:
            print(f"  [ATTEMPT {attempt}/{max_retries} FAILED] {e}", flush=True)
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            time.sleep(2)
            
    return False

def acquire_c0ldsmi1e_resume():
    """1. C0ldSmi1e/resume-dataset"""
    print("\n--- [1/6] HuggingFace: C0ldSmi1e/resume-dataset ---", flush=True)
    target_dir = RAW_DATA_DIR / "c0ldsmi1e_resume"
    files = ["train.csv", "eval.csv"]
    results = []
    for f in files:
        url = f"https://huggingface.co/datasets/C0ldSmi1e/resume-dataset/resolve/main/{f}"
        results.append(stream_download(url, target_dir / f))
    return all(results)

def acquire_med2425_job_fit():
    """2. med2425/resume-job-fit-merged-v1"""
    print("\n--- [2/6] HuggingFace: med2425/resume-job-fit-merged-v1 ---", flush=True)
    target_dir = RAW_DATA_DIR / "med2425_job_fit"
    url = "https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1/resolve/main/data/train-00000-of-00002.parquet"
    return stream_download(url, target_dir / "train-00000.parquet")

def acquire_keerthanshetty_skills():
    """3. keerthanshetty/resume-skill-extractor-dataset"""
    print("\n--- [3/6] HuggingFace: keerthanshetty/resume-skill-extractor-dataset ---", flush=True)
    target_dir = RAW_DATA_DIR / "keerthanshetty_skills"
    url = "https://huggingface.co/datasets/keerthanshetty/resume-skill-extractor-dataset/resolve/main/data/train-00000-of-00001.parquet"
    return stream_download(url, target_dir / "train-00000.parquet")

def acquire_onet_database():
    """4. Official O*NET Database (db_28_0_text)"""
    print("\n--- [4/6] Official O*NET Database ---", flush=True)
    target_dir = RAW_DATA_DIR / "onet_database"
    files = [
        ("Occupation Data.txt", "https://www.onetcenter.org/dl_files/database/db_28_0_text/Occupation%20Data.txt"),
        ("Skills.txt", "https://www.onetcenter.org/dl_files/database/db_28_0_text/Skills.txt"),
        ("Technology Skills.txt", "https://www.onetcenter.org/dl_files/database/db_28_0_text/Technology%20Skills.txt"),
        ("Knowledge.txt", "https://www.onetcenter.org/dl_files/database/db_28_0_text/Knowledge.txt")
    ]
    results = []
    for fname, url in files:
        results.append(stream_download(url, target_dir / fname, timeout=45))
    return all(results)

def acquire_mbpp_problems():
    """5. Google Research MBPP Python Programming Problems"""
    print("\n--- [5/6] Google Research MBPP Python Problems ---", flush=True)
    target_dir = RAW_DATA_DIR / "mbpp_problems"
    url = "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl"
    return stream_download(url, target_dir / "mbpp.jsonl")

def acquire_nonameee_matching():
    """6. nonameee12233/job-resume-matching"""
    print("\n--- [6/6] HuggingFace: nonameee12233/job-resume-matching ---", flush=True)
    target_dir = RAW_DATA_DIR / "nonameee_matching"
    # Download job.csv and matches.csv first
    files = ["matches.csv", "job.csv", "cv.csv"]
    results = []
    for f in files:
        url = f"https://huggingface.co/datasets/nonameee12233/job-resume-matching/resolve/main/{f}"
        results.append(stream_download(url, target_dir / f, timeout=60))
    return any(results)

def main():
    print("=" * 65, flush=True)
    print("  SkillBridge AI: Streaming Dataset Acquisition Pipeline", flush=True)
    print("=" * 65, flush=True)
    
    status = {
        "c0ldsmi1e_resume": acquire_c0ldsmi1e_resume(),
        "med2425_job_fit": acquire_med2425_job_fit(),
        "keerthanshetty_skills": acquire_keerthanshetty_skills(),
        "onet_database": acquire_onet_database(),
        "mbpp_problems": acquire_mbpp_problems(),
        "nonameee_matching": acquire_nonameee_matching()
    }
    
    print("\n" + "=" * 65, flush=True)
    print("Dataset Acquisition Status:", flush=True)
    all_ok = True
    for name, ok in status.items():
        res = "SUCCESS (CACHED/VERIFIED)" if ok else "PARTIAL/FAILED"
        print(f"  * {name:25s}: {res}", flush=True)
        if not ok:
            all_ok = False
    print("=" * 65, flush=True)
    
    manifest_path = RAW_DATA_DIR / "download_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(status, f, indent=2)
    print(f"Manifest written to {manifest_path}", flush=True)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
