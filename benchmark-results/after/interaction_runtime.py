"""Collect safe, same-origin runtime evidence from the isolated benchmark app."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE = "http://127.0.0.1:8765"
OUT = Path(__file__).parent
SCREENSHOTS = OUT / "interaction-screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)


def main() -> None:
    results: dict[str, object] = {
        "base_url": BASE,
        "scope": "isolated synthetic fixture; same-origin only; no app files modified",
        "scenarios": {},
        "browser_errors": [],
        "blocked_requests": [],
    }

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("pageerror", lambda error: results["browser_errors"].append(str(error)))

        def same_origin_only(route) -> None:
            if route.request.url.startswith(BASE + "/"):
                route.continue_()
            else:
                results["blocked_requests"].append(route.request.url)
                route.abort()

        page.route("**/*", same_origin_only)

        def visit(path: str) -> None:
            response = page.goto(BASE + path, wait_until="networkidle")
            if response is None or response.status != 200:
                raise RuntimeError(f"Could not load {path}: {None if response is None else response.status}")

        scenarios: dict[str, object] = {}
        results["scenarios"] = scenarios

        visit("/orders/")
        page.locator("#order-search").fill("NS-1042")
        searched = {
            "count_text": page.locator("#results-count").inner_text(),
            "visible_data_rows": page.locator("#orders-body [data-open]:visible").count(),
        }
        page.locator("#status-filter").select_option(label="Failed")
        filtered = {
            "count_text": page.locator("#results-count").inner_text(),
            "visible_data_rows": page.locator("#orders-body [data-open]:visible").count(),
        }
        page.locator("#order-search").fill("")
        failed_only = {
            "count_text": page.locator("#results-count").inner_text(),
            "visible_data_rows": page.locator("#orders-body [data-open]:visible").count(),
        }
        page.locator("#order-search").fill("no-such-order")
        empty = {
            "count_text": page.locator("#results-count").inner_text(),
            "visible_data_rows": page.locator("#orders-body [data-open]:visible").count(),
            "empty_message": page.locator("#orders-body").inner_text(),
        }
        page.locator("#order-search").fill("")
        page.locator("#status-filter").select_option(label="All")
        view_button = page.locator('#orders-body [data-open="NS-1042"]').first
        view_button.focus()
        page.keyboard.press("Enter")
        dialog_open = {
            "visible": page.locator("#order-dialog").is_visible(),
            "active_element": page.evaluate("document.activeElement?.outerHTML || null"),
            "active_element_inside_dialog": page.locator("#order-dialog [role=dialog]").evaluate("el => el.contains(document.activeElement)"),
            "role": page.locator("#order-dialog [role=dialog]").get_attribute("role"),
            "aria_modal": page.locator("#order-dialog [role=dialog]").get_attribute("aria-modal"),
            "dialog_text": page.locator("#order-dialog").inner_text(),
        }
        page.screenshot(path=str(SCREENSHOTS / "orders-dialog.png"), full_page=True)
        page.keyboard.press("Escape")
        dialog_open["visible_after_escape"] = page.locator("#order-dialog").is_visible()
        page.locator("#close-order").click()
        dialog_closed = {
            "visible": page.locator("#order-dialog").is_visible(),
            "active_element": page.evaluate("document.activeElement?.outerHTML || null"),
        }
        scenarios["orders"] = {
            "search": searched,
            "failed_filter_after_search": filtered,
            "failed_filter_alone": failed_only,
            "empty_results": empty,
            "dialog_open": dialog_open,
            "dialog_close": dialog_closed,
            "tested": True,
        }

        visit("/analytics/")
        slider = page.locator("#order-cutoff")
        initial_cutoff = slider.input_value()
        initial_label = page.locator("#cutoff-label").inner_text()
        initial_count = page.locator("#qualified-orders").inner_text()
        slider.focus()
        slider.press("End")
        changed = {
            "value": slider.input_value(),
            "displayed_value": page.locator("#cutoff-label").inner_text(),
            "qualified_orders": page.locator("#qualified-orders").inner_text(),
        }
        scenarios["analytics"] = {
            "initial": {"value": initial_cutoff, "displayed_value": initial_label, "qualified_orders": initial_count},
            "after_change": changed,
            "tested": True,
        }

        visit("/customers/")
        customer_search = page.locator("#customer-search")
        customer_search.fill("Jordan Lee")
        customer_search_result = {
            "visible_cards": page.locator(".customer-card:visible").count(),
            "card_text": page.locator(".customer-card:visible").all_inner_texts(),
        }
        customer_search.fill("no-such-customer")
        customer_empty = {
            "visible_cards": page.locator(".customer-card:visible").count(),
            "empty_state_present": page.get_by_text("No customers found", exact=False).count() > 0,
        }
        scenarios["customers"] = {
            "search": customer_search_result,
            "empty_results": customer_empty,
            "tested": True,
        }

        visit("/settings/")
        theme = page.locator("#theme-switch")
        theme_before = {
            "aria_checked": theme.get_attribute("aria-checked"),
            "background": page.locator("body").evaluate("el => getComputedStyle(el).backgroundColor"),
            "app_shell_background": page.locator(".app-shell").evaluate("el => getComputedStyle(el).backgroundColor"),
        }
        theme.click()
        theme_after = {
            "aria_checked": theme.get_attribute("aria-checked"),
            "background": page.locator("body").evaluate("el => getComputedStyle(el).backgroundColor"),
            "app_shell_background": page.locator(".app-shell").evaluate("el => getComputedStyle(el).backgroundColor"),
            "toast": page.locator("#toast").inner_text(),
        }
        email_switch = page.locator("#email-switch")
        email_before = email_switch.get_attribute("aria-checked")
        email_switch.focus()
        page.keyboard.press("Space")
        email_after_keyboard = email_switch.get_attribute("aria-checked")
        page.locator("#team-name").fill("QA review")
        page.locator("#alert-threshold").fill("81000")
        page.locator('#settings-form button[type="submit"]').click()
        optimistic = {
            "save_status": page.locator("#save-status").inner_text(),
            "toast": page.locator("#toast").inner_text(),
        }
        page.screenshot(path=str(SCREENSHOTS / "settings-immediate-save.png"), full_page=True)
        page.wait_for_timeout(650)
        delayed = {"save_status": page.locator("#save-status").inner_text()}
        page.screenshot(path=str(SCREENSHOTS / "settings-delayed-failure.png"), full_page=True)
        scenarios["settings"] = {
            "theme_switch": {"before": theme_before, "after": theme_after},
            "email_switch_keyboard": {"before": email_before, "after_space": email_after_keyboard},
            "save": {"immediate": optimistic, "after_650ms": delayed},
            "tested": True,
        }

        page.set_viewport_size({"width": 390, "height": 844})
        visit("/")
        page.locator("#menu-toggle").click()
        mobile_nav = {
            "aria_expanded": page.locator("#menu-toggle").get_attribute("aria-expanded"),
            "sidebar_open": page.locator("#sidebar").evaluate("el => el.classList.contains('open')"),
            "backdrop_open": page.locator("#mobile-backdrop").evaluate("el => el.classList.contains('open')"),
        }
        page.screenshot(path=str(SCREENSHOTS / "mobile-navigation-open.png"), full_page=True)
        page.keyboard.press("Escape")
        mobile_nav["after_escape"] = {
            "aria_expanded": page.locator("#menu-toggle").get_attribute("aria-expanded"),
            "sidebar_open": page.locator("#sidebar").evaluate("el => el.classList.contains('open')"),
        }
        page.locator("#notifications").click()
        notification = page.locator("#toast").inner_text()
        scenarios["shared_interface"] = {
            "mobile_navigation": mobile_nav,
            "notification": notification,
            "tested": True,
        }

        browser.close()

    (OUT / "interaction-runtime-evidence.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
