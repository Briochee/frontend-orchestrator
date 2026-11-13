"""Optional local-first rendered screenshot capture for visual audit evidence."""

from __future__ import annotations

import importlib.util
from html import escape
import ipaddress
import json
import socket
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit
from typing import Any


VIEWPORTS: dict[str, dict[str, int]] = {
    "large-desktop": {"width": 1920, "height": 1080},
    "desktop": {"width": 1440, "height": 1000},
    "laptop": {"width": 1280, "height": 900},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 390, "height": 844},
    "small-mobile": {"width": 320, "height": 740},
}
DEPTH_VIEWPORTS: dict[str, tuple[str, ...]] = {
    "standard": ("desktop", "mobile"),
    "deep": ("desktop", "tablet", "mobile"),
    "exhaustive": ("large-desktop", "desktop", "laptop", "tablet", "mobile", "small-mobile"),
}


class BrowserUnavailable(RuntimeError):
    """Raised when optional Playwright support is unavailable."""


def playwright_available() -> bool:
    return importlib.util.find_spec("playwright") is not None


def capture_screenshots(
    url: str,
    output_directory: Path,
    *,
    allow_remote: bool = False,
    timeout_ms: int = 15_000,
    route_paths: tuple[str, ...] | list[str] = (),
    viewports: tuple[str, ...] | list[str] | None = None,
) -> list[dict[str, Any]]:
    """Capture explicit same-origin routes and bounded browser diagnostics.

    This adapter navigates only the explicitly supplied same-origin paths and
    never performs non-read-only requests. The director decides which static
    source-discovered candidates or operator-selected paths to pass here.
    """
    if not playwright_available():
        raise BrowserUnavailable("Playwright is not installed. Install the optional `browser` extra and browser binaries after review.")
    selected_viewports = tuple(viewports or ("desktop", "tablet", "mobile"))
    unknown_viewports = set(selected_viewports) - VIEWPORTS.keys()
    if unknown_viewports:
        raise ValueError(f"Unsupported viewport label(s): {', '.join(sorted(unknown_viewports))}.")
    origin = _validate_url(url, allow_remote=allow_remote)
    output_directory.mkdir(parents=True, exist_ok=True, mode=0o700)

    from playwright.sync_api import sync_playwright

    parsed_base = urlsplit(url)
    base_path = parsed_base.path or "/"
    approved_routes = [(base_path, url)]
    seen_paths = {base_path}
    for route_path in route_paths:
        parsed_route = urlsplit(route_path)
        decoded_segments = unquote(parsed_route.path).split("/")
        if parsed_route.scheme or parsed_route.netloc or not parsed_route.path.startswith("/") or ".." in decoded_segments or "\\" in parsed_route.path or parsed_route.query or parsed_route.fragment:
            raise ValueError(f"Route must be an exact same-origin absolute path without query or traversal: {route_path!r}.")
        normalized = parsed_route.path or "/"
        if normalized not in seen_paths:
            approved_routes.append((normalized, urlunsplit((parsed_base.scheme, parsed_base.netloc, normalized, "", ""))))
            seen_paths.add(normalized)

    evidence: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as error:
            raise BrowserUnavailable("Playwright is installed, but its Chromium executable could not be launched. Install the browser through the documented Playwright setup after review.") from error
        try:
            for route_path, target_url in approved_routes:
                route_slug = _route_slug(route_path)
                for label in selected_viewports:
                    viewport = VIEWPORTS[label]
                    context = browser.new_context(viewport=viewport, device_scale_factor=1, service_workers="block")
                    page = context.new_page()
                    page.set_default_navigation_timeout(timeout_ms)
                    console_errors: list[dict[str, str]] = []
                    page_errors: list[str] = []
                    failed_requests: list[dict[str, str]] = []
                    page.on("console", lambda message: _append_bounded(console_errors, {"type": message.type, "message": _safe_message(message.text)}, 40) if message.type == "error" else None)
                    page.on("pageerror", lambda error: _append_bounded(page_errors, _safe_message(str(error)), 40))
                    page.on("requestfailed", lambda request: _append_bounded(failed_requests, {"url": _safe_url(request.url), "method": request.method, "failure": _safe_message(request.failure or "unknown")}, 40))

                    def restrict_request(request_route: Any) -> None:
                        request = request_route.request
                        try:
                            if _same_origin(request.url, origin) and request.method.upper() in {"GET", "HEAD", "OPTIONS"}:
                                request_route.continue_()
                            else:
                                request_route.abort()
                        except Exception:
                            request_route.abort()

                    viewport_name = label if len(approved_routes) == 1 else f"{route_slug}:{label}"
                    try:
                        page.route("**/*", restrict_request)
                        response = page.goto(target_url, wait_until="domcontentloaded")
                        if not _same_origin(page.url, origin):
                            raise ValueError("The page redirected away from the explicitly approved origin.")
                        readiness = _wait_for_readiness(page)
                        browser_observation = _inspect_page(page)
                        suffix = f"-{route_slug}-{label}" if len(approved_routes) > 1 else f"-{label}"
                        screenshot_path = output_directory / f"{suffix.lstrip('-')}.png"
                        page.screenshot(path=str(screenshot_path), full_page=True, animations="disabled")
                        evidence.append({
                            "path": str(screenshot_path.resolve()),
                            "viewport": viewport_name,
                            "viewport_label": label,
                            "route": route_path,
                            "route_slug": route_slug,
                            "width": viewport["width"],
                            "height": viewport["height"],
                            "rendered_url": _safe_url(page.url),
                            "http_status": response.status if response else None,
                            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "evidence_type": "rendered_browser_screenshot",
                            "readiness": readiness,
                            "document": browser_observation["document"],
                            "landmarks": browser_observation["landmarks"],
                            "internal_links": browser_observation["internal_links"],
                            "controls": browser_observation["controls"],
                            "computed_styles": browser_observation["computed_styles"],
                            "navigation_timing": browser_observation["navigation_timing"],
                            "console_errors": console_errors,
                            "page_errors": page_errors,
                            "failed_requests": failed_requests,
                            "requests_blocked": "Cross-origin and non-read-only requests were blocked.",
                        })
                        if label == "desktop":
                            try:
                                page.keyboard.press("Tab")
                                focus_target = _inspect_focus(page)
                                if focus_target and focus_target.get("tag") != "body":
                                    focus_path = output_directory / f"{suffix.lstrip('-')}-focus.png"
                                    page.screenshot(path=str(focus_path), full_page=True, animations="disabled")
                                    evidence.append({
                                        **evidence[-1],
                                        "path": str(focus_path.resolve()),
                                        "viewport": f"{viewport_name}:focus-1",
                                        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                        "interaction_state": "keyboard_focus_after_one_tab",
                                        "focus_target": focus_target,
                                    })
                            except Exception as error:
                                evidence[-1]["focus_capture_error"] = f"{type(error).__name__}: {_safe_message(str(error))}"
                    except Exception as error:
                        evidence.append({
                            "route": route_path,
                            "viewport": viewport_name,
                            "viewport_label": label,
                            "route_slug": route_slug,
                            "width": viewport["width"],
                            "height": viewport["height"],
                            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "evidence_type": "browser_navigation_failure",
                            "error": f"{type(error).__name__}: {_safe_message(str(error))}",
                            "console_errors": console_errors,
                            "page_errors": page_errors,
                            "failed_requests": failed_requests,
                        })
                    finally:
                        context.close()
        finally:
            browser.close()
    (output_directory / "screenshots.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (output_directory / "gallery.html").write_text(_gallery_html(evidence), encoding="utf-8")
    return evidence


def _route_slug(path: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", path.strip("/")).strip("-").lower()
    return value[:48] or "home"


def _safe_url(value: str) -> str:
    parsed = urlsplit(value)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def _safe_message(value: str) -> str:
    value = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/-]+=*", r"\1[REDACTED]", value)
    value = re.sub(r"(?i)(token|secret|password|api[_-]?key)([=: ]+)[^\s,;]+", r"\1\2[REDACTED]", value)
    value = re.sub(r"(https?://[^\s?]+)\?[^\s]+", r"\1?[query removed]", value)
    return value[:400]


def _append_bounded(collection: list[Any], value: Any, limit: int) -> None:
    if len(collection) < limit:
        collection.append(value)


def _wait_for_readiness(page: Any) -> dict[str, Any]:
    result = {"dom_content_loaded": True, "network_idle": False, "fonts_ready": False}
    try:
        page.wait_for_load_state("networkidle", timeout=1_500)
        result["network_idle"] = True
    except Exception:
        pass
    try:
        result["fonts_ready"] = bool(page.evaluate("""() => Promise.race([
          document.fonts.ready.then(() => true),
          new Promise(resolve => setTimeout(() => resolve(false), 1200))
        ])"""))
    except Exception:
        pass
    return result


def _inspect_page(page: Any) -> dict[str, Any]:
    """Collect bounded structural and computed-style evidence without page text or input values."""
    try:
        return page.evaluate("""() => {
          const count = selector => document.querySelectorAll(selector).length;
          const safePath = href => {
            try { const url = new URL(href, location.href); return url.origin === location.origin ? url.pathname : null; }
            catch (_) { return null; }
          };
          const selectors = ['html', 'body', 'header', 'nav', 'main', 'aside', 'h1', 'h2', 'button', 'input', 'a'];
          const computed = {};
          const styleSample = (selector, element) => {
            if (Object.keys(computed).length >= 100) return;
            if (!element) return;
            const style = getComputedStyle(element);
            const rect = element.getBoundingClientRect();
            computed[selector] = {
              color: style.color, backgroundColor: style.backgroundColor,
              fontFamily: style.fontFamily, fontSize: style.fontSize,
              fontWeight: style.fontWeight, lineHeight: style.lineHeight,
              letterSpacing: style.letterSpacing, margin: style.margin,
              padding: style.padding, borderRadius: style.borderRadius,
              borderColor: style.borderColor, boxShadow: style.boxShadow,
              backgroundImage: style.backgroundImage,
              display: style.display, position: style.position,
              overflow: style.overflow, gap: style.gap,
              gridTemplateColumns: style.gridTemplateColumns,
              width: Math.round(rect.width), height: Math.round(rect.height),
              x: Math.round(rect.x), y: Math.round(rect.y),
            };
          };
          for (const selector of selectors) styleSample(selector, document.querySelector(selector));
          const classSamples = {};
          const candidates = [...document.querySelectorAll('header,nav,main,aside,footer,h1,h2,button,input,select,textarea,a,[role],[class]')];
          for (const element of candidates.slice(0, 180)) {
            if (Object.keys(computed).length >= 100) break;
            const tag = element.tagName.toLowerCase();
            const classes = [...(element.classList || [])].filter(Boolean).slice(0, 2).map(name => name.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 32));
            const base = tag + (classes.length ? '.' + classes.join('.') : '');
            const count = (classSamples[base] || 0) + 1;
            classSamples[base] = count;
            if (count <= 3) styleSample(base + (count > 1 ? `#${count}` : ''), element);
          }
          const links = [...document.querySelectorAll('a[href]')].map(a => safePath(a.href)).filter(Boolean);
          const inputs = [...document.querySelectorAll('input,select,textarea')];
          const unlabeledInputs = inputs.filter(element => {
            const id = element.id;
            return !element.labels?.length && !element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby') && !(id && document.querySelector(`label[for="${CSS.escape(id)}"]`));
          }).length;
          const timing = performance.getEntriesByType('navigation')[0];
          return {
            document: { title: document.title, width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight, readyState: document.readyState },
            landmarks: { main: count('main,[role="main"]'), nav: count('nav,[role="navigation"]'), header: count('header,[role="banner"]'), footer: count('footer,[role="contentinfo"]'), aside: count('aside,[role="complementary"]'), h1: count('h1'), dialogs: count('dialog,[role="dialog"]'), forms: count('form') },
            internal_links: [...new Set(links)].slice(0, 100),
            controls: { buttons: count('button,[role="button"]'), links: count('a[href]'), inputs: inputs.length, inputs_without_associated_label: unlabeledInputs, forms: count('form'), selects: count('select'), textareas: count('textarea'), headings: count('h1,h2,h3,h4,h5,h6') },
            computed_styles: computed,
            navigation_timing: timing ? { domContentLoadedMs: Math.round(timing.domContentLoadedEventEnd), loadMs: Math.round(timing.loadEventEnd), responseMs: Math.round(timing.responseEnd - timing.requestStart), transferSizeBytes: timing.transferSize || null } : {},
          };
        }""")
    except Exception as error:
        return {
            "document": {}, "landmarks": {}, "internal_links": [], "controls": {},
            "computed_styles": {}, "navigation_timing": {}, "inspection_error": type(error).__name__,
        }


def _inspect_focus(page: Any) -> dict[str, Any] | None:
    """Describe the active element and visible focus styling without reading its value or text."""
    try:
        return page.evaluate("""() => {
          const element = document.activeElement;
          if (!element) return null;
          const style = getComputedStyle(element);
          const rect = element.getBoundingClientRect();
          return {
            tag: element.tagName.toLowerCase(),
            role: element.getAttribute('role') || '',
            type: element.getAttribute('type') || '',
            classNames: [...(element.classList || [])].slice(0, 2).map(name => name.slice(0, 32)),
            visible: rect.width > 0 && rect.height > 0,
            outlineStyle: style.outlineStyle,
            outlineWidth: style.outlineWidth,
            outlineColor: style.outlineColor,
            boxShadow: style.boxShadow,
          };
        }""")
    except Exception:
        return None


def _gallery_html(evidence: list[dict[str, Any]]) -> str:
    cards = "\n".join(
        f'<figure><img src="{escape(Path(item["path"]).name, quote=True)}" alt="Captured {escape(str(item["route"]), quote=True)} at {escape(str(item["viewport"]), quote=True)}"><figcaption>{escape(str(item["route"]))} · {escape(str(item["viewport"]))} · HTTP {escape(str(item.get("http_status") or "unknown"))}</figcaption></figure>'
        for item in evidence
        if item.get("evidence_type") == "rendered_browser_screenshot"
    )
    return "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\"><title>Frontend evidence gallery</title><style>body{font:16px system-ui;margin:2rem;background:#f4f5f7;color:#17191c}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1rem}figure{margin:0;background:white;padding:.75rem;border:1px solid #ccd0d6;border-radius:.5rem}img{display:block;width:100%;height:auto}figcaption{padding:.5rem .25rem;font-size:.875rem}</style><h1>Frontend evidence gallery</h1><main>" + cards + "</main></html>\n"


def capture_mockup_screenshots(html_path: Path, output_directory: Path, *, timeout_ms: int = 15_000, viewports: tuple[str, ...] | list[str] | None = None) -> list[dict[str, Any]]:
    """Render a local static prototype without JavaScript or requests outside its artifact directory."""
    if not playwright_available():
        raise BrowserUnavailable("Playwright is not installed; the generated mockup remains available as local HTML/CSS.")
    page_path = html_path.resolve(strict=True)
    if not page_path.is_file():
        raise ValueError("Mockup entry point must be a regular HTML file.")
    artifact_root = page_path.parent.resolve()
    output_directory.mkdir(parents=True, exist_ok=True, mode=0o700)

    from playwright.sync_api import sync_playwright

    evidence: list[dict[str, Any]] = []
    selected_viewports = tuple(viewports or ("desktop", "tablet", "mobile"))
    unknown_viewports = set(selected_viewports) - VIEWPORTS.keys()
    if unknown_viewports:
        raise ValueError(f"Unsupported viewport label(s): {', '.join(sorted(unknown_viewports))}.")
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as error:
            raise BrowserUnavailable("Playwright is installed, but its Chromium executable could not be launched.") from error
        try:
            for label in selected_viewports:
                viewport = VIEWPORTS[label]
                context = browser.new_context(viewport=viewport, device_scale_factor=1, java_script_enabled=False)
                page = context.new_page()
                page.set_default_navigation_timeout(timeout_ms)

                def restrict_request(route: Any) -> None:
                    try:
                        parsed = urlsplit(route.request.url)
                        requested_path = Path(unquote(parsed.path)).resolve()
                        if parsed.scheme == "file" and requested_path.is_relative_to(artifact_root):
                            route.continue_()
                        else:
                            route.abort()
                    except Exception:
                        route.abort()

                page.route("**/*", restrict_request)
                page.goto(page_path.as_uri(), wait_until="domcontentloaded")
                screenshot_path = output_directory / f"{label}.png"
                page.screenshot(path=str(screenshot_path), full_page=True, animations="disabled")
                evidence.append({
                    "path": str(screenshot_path.resolve()),
                    "viewport": label,
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "rendered_url": page_path.as_uri(),
                    "evidence_type": "rendered_mockup_screenshot",
                })
                context.close()
        finally:
            browser.close()
    return evidence


def _validate_url(url: str, *, allow_remote: bool) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an http(s) URL without embedded credentials.")
    host = parsed.hostname.casefold()
    local = host in {"localhost", "127.0.0.1", "::1"}
    if not local:
        try:
            local = ipaddress.ip_address(host).is_loopback
        except ValueError:
            try:
                local = all(ipaddress.ip_address(item[4][0]).is_loopback for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM))
            except (OSError, ValueError):
                local = False
    if not local and not allow_remote:
        raise ValueError("Remote browser access is disabled. Pass --allow-remote only when you authorize screenshots of that URL.")
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def _same_origin(url: str, approved_origin: str) -> bool:
    parsed = urlsplit(url)
    expected = urlsplit(approved_origin)
    return (parsed.scheme.casefold(), parsed.netloc.casefold()) == (expected.scheme.casefold(), expected.netloc.casefold())
