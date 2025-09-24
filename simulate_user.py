# ---------------------- #VERSION 3 with zomm --------------

import asyncio
import json
import sys
from playwright.async_api import async_playwright

async def simulate(input_file):
    with open(input_file, "r") as f:
        events = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(events[0]["url"])

        for e in events:
            delay = e.get("delay", 200) / 1000
            await asyncio.sleep(delay)

            etype = e["type"]
            data = e["data"]

            if etype == "click":
                await page.mouse.click(data["x"], data["y"], button=["left","middle","right"][data.get("button",0)])

            elif etype == "scroll":
                await page.evaluate(f"window.scrollTo({data['scrollX']}, {data['scrollY']})")

            elif etype == "keydown":
                await page.keyboard.down(data["key"])

            elif etype == "keyup":
                await page.keyboard.up(data["key"])

            elif etype == "input":
                selector = data.get("selector")
                if selector:
                    try:
                        await page.fill(selector, data.get("value",""))
                    except:
                        pass
            
            if etype == "mousemove":
                await page.mouse.move(data["x"], data["y"])

            elif etype == "urlchange":
                if data.get("url"):
                    await page.goto(data["url"])

            elif etype == "zoom":
                old_scale = data.get("oldScale", 1.0)
                new_scale = data.get("newScale", 1.0)
                zoom_x = data.get("x", 0)   # pointer X when zooming
                zoom_y = data.get("y", 0)   # pointer Y when zooming
                # Apply zoom using CSS transform
                await page.evaluate(
                """([oldScale, newScale, zoomX, zoomY]) => {
                    const body = document.body;
                    const prev = oldScale;
                    const next = newScale;

                    // Current scroll offsets
                    const scrollX = window.scrollX;
                    const scrollY = window.scrollY;

                    // Position relative to content
                    const cx = (scrollX + zoomX) / prev;
                    const cy = (scrollY + zoomY) / prev;

                    // Apply zoom
                    body.style.transformOrigin = "0 0";
                    body.style.transform = `scale(${next})`;

                    window.scrollTo(cx * next - zoomX, cy * next - zoomY);
                }""",
                [old_scale, new_scale, zoom_x, zoom_y]
            )
            print(f"✅ Replayed {etype} after {delay*1000:.0f}ms")


        print("Replay finished, browser stays open for inspection")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(simulate(sys.argv[1]))
