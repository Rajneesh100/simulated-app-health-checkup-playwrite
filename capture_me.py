import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

RECORDER_JS = """
(() => {
  if (window.__recorderInstalled) return;
  window.__recorderInstalled = true;

  function record(type, data) {
    window.record_event({
      type,
      data,
      url: window.location.href,
      time: Date.now()
    });
  }

  // mouse
  document.addEventListener("mousemove", e => {
    record("mousemove", { x: e.clientX, y: e.clientY });
  }, { passive: true });

  document.addEventListener("click", e => {
    record("click", { x: e.clientX, y: e.clientY, button: e.button });
  }, { passive: true });

  // keyboard (capture modifiers too)
  document.addEventListener("keydown", e => {
    record("keydown", {
      key: e.key, code: e.code,
      ctrl: e.ctrlKey, alt: e.altKey, shift: e.shiftKey, meta: e.metaKey
    });
  });

  document.addEventListener("keyup", e => {
    record("keyup", {
      key: e.key, code: e.code,
      ctrl: e.ctrlKey, alt: e.altKey, shift: e.shiftKey, meta: e.metaKey
    });
  });

  // text input snapshots
  document.addEventListener("input", e => {
    const t = e.target;
    if (t && t.value !== undefined) {
      record("input", {
        selector: t.tagName + (t.id ? "#" + t.id : ""),
        value: t.value
      });
    }
  });

  // scroll
  window.addEventListener("scroll", () => {
    record("scroll", { scrollX: window.scrollX, scrollY: window.scrollY });
  }, { passive: true });

  // url changes (SPA + history)
  window.addEventListener("popstate", () => {
    record("urlchange", { url: window.location.href });
  });
  const _pushState = history.pushState;
  history.pushState = function() {
    _pushState.apply(this, arguments);
    record("urlchange", { url: window.location.href });
  };


  // ✅ pinch/zoom detection via visualViewport
  if (window.visualViewport) {
    let lastScale = window.visualViewport.scale;
    window.visualViewport.addEventListener("resize", () => {
      const s = window.visualViewport.scale;
      if (s !== lastScale) {
        record("zoom", { oldScale: lastScale, newScale: s });
        lastScale = s;
      }
    });
  }
})();
"""

async def main(start_url, output_file):
    events = []
    # start_url = "https://www.rfc-editor.org/rfc/rfc6761.html"  # google_document.json
    # start_url = "https://motion.page/features/mouse-movement/" # mouse.json
    # start_url = "https://apple.com/" # apple.json
    # start_url = "https://practicetestautomation.com/practice-test-login/"  # intractive.jaon

    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False, slow_mo=50)
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-features=TranslateUI",
                "--disable-features=GlobalMediaControls",
            ],
        )
        page = await browser.new_page()

        # 1) expose binding BEFORE any navigation so recorder can call it on the first page
        await page.expose_binding("record_event", lambda source, e: events.append(e))

        # 2) install recorder for all future docs
        await page.add_init_script(RECORDER_JS)

        # 3) now navigate to the first page (recorder will be present there)
        await page.goto(start_url)

        # 4) also run once on the current document (safe-guard; no double listeners due to flag)
        await page.evaluate(RECORDER_JS)

        print("👆 Recording events... (browser will auto-close after 40s)")
        await asyncio.sleep(100)

        # convert timestamps → delays
        processed = []
        prev_time = None
        for e in events:
            ts = e.get("time", 0)
            delay = 100 if prev_time is None else max(0, ts - prev_time)
            prev_time = ts
            processed.append({
                "type": e.get("type"),
                "data": e.get("data", {}),
                "url": e.get("url"),
                "delay": delay,
                "time": ts
            })

        with open(output_file, "w") as f:
            json.dump(processed, f, indent=2)

        print(f"✅ Saved {len(processed)} events to {output_file}")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python capture_me.py <start_url> <output_file>")
        print("Example: python capture_me.py https://foreai.co/ foreai.json")
        sys.exit(1)
    
    start_url = sys.argv[1]
    output_file = sys.argv[2]
    asyncio.run(main(start_url, output_file))
