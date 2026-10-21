#!/usr/bin/env python3
"""
Zero-Dependency RFC 6455 Chrome DevTools Protocol (CDP) Navigator & Visual Actuator v2.0
(Clean-Room Customer Edition — Zero Proprietary Auth Dependencies).
Features:
1. Pure-Python RFC 6455 WebSocket Client (`StandaloneCDP`) over standard library `socket`/`struct`
2. Shadow-DOM Piercing Interactive Element Collector (`SHADOW_DOM_COLLECTOR_JS`)
3. React Fiber In-Memory File Upload Bypass (`build_react_fiber_upload_js`)
4. Visual Bounding-Box Overlay Injector (`VISUAL_BBOX_OVERLAY_JS`)
"""

import os
import json
import base64
import shutil
import socket
import sqlite3
import struct
import tempfile
import urllib.request
from typing import Dict, Any, List, Optional


def flush_cookie_wal_before_headless_cdp(
    cookie_db_path: str,
    target_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    AGW-W12-10: SQLite Cookie WAL Checkpoint Flush & Atomic Snapshot Cloner before Headless CDP Launch.
    Copies a live Chromium Cookies SQLite database + `-wal`/`-shm` sidecars into an isolated snapshot
    directory and runs `PRAGMA wal_checkpoint(FULL)` so headless CDP sessions see freshly minted cookies
    without `SQLITE_BUSY` lock contention.
    """
    if not cookie_db_path or not os.path.exists(cookie_db_path):
        return {"flushed": False, "snapshot_db_path": "", "reason": "cookie_db_missing"}
    work_dir = target_dir or tempfile.mkdtemp(prefix="cdp_cookie_snap_")
    os.makedirs(work_dir, exist_ok=True)
    snap_db = os.path.join(work_dir, "Cookies")
    shutil.copy2(cookie_db_path, snap_db)
    for suffix in ("-wal", "-shm"):
        sidecar = cookie_db_path + suffix
        if os.path.exists(sidecar):
            shutil.copy2(sidecar, snap_db + suffix)
    checkpoint_ok = False
    try:
        conn = sqlite3.connect(snap_db, timeout=2.0)
        conn.execute("PRAGMA wal_checkpoint(FULL);")
        conn.commit()
        conn.close()
        checkpoint_ok = True
    except Exception:
        checkpoint_ok = False
    return {
        "flushed": checkpoint_ok,
        "snapshot_db_path": snap_db,
        "work_dir": work_dir,
    }

SHADOW_DOM_COLLECTOR_JS = r"""
(() => {
  const results = [];
  function walk(root) {
    for (const el of root.querySelectorAll('*')) {
      if (el.shadowRoot) walk(el.shadowRoot);
      const tag = el.tagName.toLowerCase();
      if (['button', 'a', 'input', 'select', 'textarea'].includes(tag) || el.getAttribute('role') === 'button') {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) {
          results.append ? results.append(tag) : results.push({
            tag,
            text: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 80),
            x: Math.round(r.x + r.width / 2),
            y: Math.round(r.y + r.height / 2)
          });
        }
      }
    }
  }
  walk(document);
  return results;
})()
"""


def build_react_fiber_upload_js(selector: str, filename: str, mime_type: str, b64_content: str) -> str:
    """Constructs an in-memory File + DataTransfer synthetic React Fiber upload script."""
    return f"""
    (() => {{
      const input = document.querySelector({json.dumps(selector)});
      if (!input) return {{ ok: false, error: 'Selector not found' }};
      const bin = atob({json.dumps(b64_content)});
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const file = new File([bytes], {json.dumps(filename)}, {{ type: {json.dumps(mime_type)} }});
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
      input.dispatchEvent(new Event('change', {{ bubbles: true }}));
      const fk = Object.keys(input).find(k => k.startsWith('__reactProps$') || k.startsWith('__reactEventHandlers$'));
      if (fk && input[fk] && typeof input[fk].onChange === 'function') {{
        input[fk].onChange({{ target: input, currentTarget: input, nativeEvent: new Event('change') }});
      }}
      return {{ ok: true, filename: file.name, size: file.size }};
    }})()
    """


class StandaloneCDP:
    """Minimal RFC 6455 WebSocket client using only Python stdlib."""
    def __init__(self, host: str = "127.0.0.1", port: int = 9222):
        self.host = host
        self.port = port
        self._msg_id = 0

    def list_tabs(self) -> List[Dict[str, Any]]:
        url = f"http://{self.host}:{self.port}/json/list"
        with urllib.request.urlopen(url, timeout=3) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            return json.loads(raw or "[]")
