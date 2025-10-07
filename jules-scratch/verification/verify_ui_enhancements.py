from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Increase timeout to give the app more time to load
        page.goto("http://127.0.0.1:8050", timeout=30000)

        # Take an initial screenshot for debugging
        page.screenshot(path="jules-scratch/verification/initial_view.png")

        # Wait for the main heading to ensure the page is loaded
        expect(page.get_by_role("heading", name="Caliper v2 – Dash/Plotly Wrapper")).to_be_visible()

        # 1. Verify Prompt Library
        # Wait for the dropdown by its ID, which is more reliable than text
        prompt_dropdown = page.locator("#prompt-library")
        expect(prompt_dropdown).to_be_visible()
        expect(page.get_by_text("Prompt Library")).to_be_visible()

        prompt_dropdown.click()
        expect(page.get_by_text("Population Forecast QA")).to_be_visible()

        # 2. Verify Artifact Health Indicators
        expect(page.get_by_text("Artifact Health:")).to_be_visible()
        expect(page.locator("#health-retrieval")).to_be_visible()
        expect(page.locator("#health-enhanced")).to_be_visible()
        expect(page.locator("#health-draft")).to_be_visible()
        expect(page.locator("#health-review")).to_be_visible()

        # 3. Verify Evidence Explorer modal is present but hidden
        expect(page.locator("#modal-evidence-explorer")).to_be_hidden()

        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

if __name__ == "__main__":
    run_verification()