import sys, os, glob
from playwright.sync_api import sync_playwright
os.environ["ZK_STILL"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figs_push
exe = sorted(glob.glob(os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell')))[-1]
name, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    pg = b.new_page(viewport={"width": 960, "height": 700}, device_scale_factor=2, java_script_enabled=False)
    pg.set_content(f"<!doctype html><html><head><meta charset=utf-8></head><body style='margin:0;background:#000'>{getattr(figs_push, name)()}</body></html>")
    pg.wait_for_timeout(300)
    pg.locator("body>div").first.screenshot(path=out)
    b.close()
print(out)
