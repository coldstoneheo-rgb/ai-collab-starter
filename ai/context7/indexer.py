# lightweight indexer for repo documents
import os
from pathlib import Path
import json

IGNORE = {'.git', 'node_modules', 'dist', '__pycache__'}

def scan_repo(base='.'):
    files = []
    for root, dirs, filenames in os.walk(base):
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for f in filenames:
            if f.endswith(('.md', '.txt', '.py', '.ts', '.js', '.json', '.tsx', '.jsx', '.html')):
                p = Path(root) / f
                files.append(str(p))
    return files

def build_index(out_file='ai/context7/index.json'):
    files = scan_repo('.')
    docs = []
    for f in files:
        try:
            content = Path(f).read_text(encoding='utf-8')
        except Exception:
            content = ''
        docs.append({'path': f, 'content': content[:20000]})
    os.makedirs(Path(out_file).parent, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as fw:
        json.dump(docs, fw, ensure_ascii=False, indent=2)
    print(f'Indexed {len(docs)} docs -> {out_file}')
    return out_file

def build_chroma_from_repo(base: str = '.', persist_dir=None):
    """
    Scan repo and build a Chroma vector index.
    No-op if chromadb is not installed.
    """
    from pathlib import Path as _Path
    from ai.context7.chroma_pipeline import build_chroma_index, CHROMA_DIR

    target_dir = persist_dir or CHROMA_DIR
    files = scan_repo(base)
    docs = []
    for f in files:
        try:
            content = _Path(f).read_text(encoding='utf-8')
        except Exception:
            content = ''
        docs.append({'path': f, 'content': content[:20000]})

    count = build_chroma_index(docs, persist_dir=target_dir)
    return count


if __name__ == '__main__':
    import sys
    if '--chroma' in sys.argv:
        n = build_chroma_from_repo()
        print(f'Chroma index: {n} chunks')
    else:
        build_index()
