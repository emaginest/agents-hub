"""
Playwright-based web scraping tool for the Agents Hub framework.

This module provides a tool for advanced web scraping using Playwright,
which can handle JavaScript-heavy websites and implement anti-detection techniques.
"""

import asyncio
import json
import logging
import os
import random
import re
from typing import Dict, List, Any, Optional, Union, Tuple

from bs4 import BeautifulSoup
from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    BrowserContext,
    Response,
)
from agents_hub.tools.base import BaseTool

# Initialize logger
logger = logging.getLogger(__name__)


class PlaywrightScraperTool(BaseTool):
    """
    Tool for advanced web scraping using Playwright.

    This tool provides methods for scraping JavaScript-heavy websites,
    handling dynamic content, and implementing anti-detection techniques.
    """

    def __init__(self):
        """Initialize the Playwright scraper tool."""
        super().__init__(
            name="playwright_scraper",
            description="Scrape content from JavaScript-heavy websites using Playwright",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape",
                    },
                    "extract_type": {
                        "type": "string",
                        "enum": ["text", "html", "metadata", "all"],
                        "description": "Type of content to extract",
                        "default": "text",
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector to extract specific content",
                    },
                    "wait_for_selector": {
                        "type": "string",
                        "description": "CSS selector to wait for before extracting content",
                    },
                    "wait_time": {
                        "type": "integer",
                        "description": "Time to wait in milliseconds after page load",
                        "default": 0,
                    },
                    "include_images": {
                        "type": "boolean",
                        "description": "Whether to include image URLs in the result",
                        "default": False,
                    },
                    "block_resources": {
                        "type": "boolean",
                        "description": "Whether to block non-essential resources (images, fonts, etc.)",
                        "default": True,
                    },
                    "browser_type": {
                        "type": "string",
                        "enum": ["chromium", "firefox", "webkit"],
                        "description": "Browser type to use",
                        "default": "chromium",
                    },
                    "stealth_mode": {
                        "type": "boolean",
                        "description": "Whether to use stealth mode to avoid detection",
                        "default": True,
                    },
                    "scroll_to_bottom": {
                        "type": "boolean",
                        "description": "Whether to scroll to the bottom of the page to load lazy content",
                        "default": False,
                    },
                    "js_scenario": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of JavaScript actions to perform (click, type, etc.)",
                    },
                    "headers": {
                        "type": "object",
                        "description": "Custom headers to use for the request",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds",
                        "default": 60000,
                    },
                },
                "required": ["url"],
            },
        )

    async def run(
        self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Run the Playwright scraper tool.

        Args:
            parameters: Parameters for the tool
            context: Optional context information

        Returns:
            Scraped content
        """
        url = parameters.get("url")
        extract_type = parameters.get("extract_type", "text")
        selector = parameters.get("selector")
        wait_for_selector = parameters.get("wait_for_selector")
        wait_time = parameters.get("wait_time", 0)
        include_images = parameters.get("include_images", False)
        block_resources = parameters.get("block_resources", True)
        browser_type = parameters.get("browser_type", "chromium")
        stealth_mode = parameters.get("stealth_mode", True)
        scroll_to_bottom = parameters.get("scroll_to_bottom", False)
        js_scenario = parameters.get("js_scenario", [])
        headers = parameters.get("headers", {})
        timeout = parameters.get("timeout", 60000)

        logger.info(f"Scraping URL: {url}")

        try:
            async with async_playwright() as playwright:
                # Select browser type
                browser_instance = getattr(playwright, browser_type)

                # Launch browser with additional options
                browser = await browser_instance.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"],
                )

                # Create a browser context with custom viewport
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent=self._get_user_agent(),
                    extra_http_headers=headers,
                )

                # Apply stealth mode if enabled
                if stealth_mode:
                    await self._apply_stealth_mode(context)

                # Create a new page
                page = await context.new_page()

                # Set up resource blocking if enabled
                if block_resources:
                    await self._setup_resource_blocking(page)

                # Set up response interception for metadata
                responses = []
                page.on("response", lambda response: responses.append(response))

                # Navigate to the URL with timeout
                await page.goto(url, timeout=timeout, wait_until="networkidle")

                # Wait for specific selector if provided
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=timeout)

                # Wait additional time if specified
                if wait_time > 0:
                    await asyncio.sleep(wait_time / 1000)  # Convert to seconds

                # Execute JavaScript scenario if provided
                if js_scenario:
                    await self._execute_js_scenario(page, js_scenario)

                # Scroll to bottom if enabled
                if scroll_to_bottom:
                    await self._scroll_to_bottom(page)

                # Extract content based on extract_type
                if extract_type == "html":
                    content = await page.content()
                    result = {"html": content, "url": url}
                else:
                    # Get page content for parsing
                    page_content = await page.content()

                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(page_content, "lxml")

                    # Apply selector if provided
                    if selector:
                        elements = soup.select(selector)
                        if not elements:
                            await browser.close()
                            return {
                                "error": f"No elements found matching selector: {selector}",
                                "url": url,
                            }

                        # Extract text content
                        text_content = "\n".join(
                            el.get_text(strip=True) for el in elements
                        )

                        # Extract images if requested
                        images = []
                        if include_images:
                            for el in elements:
                                images.extend(
                                    [
                                        img.get("src")
                                        for img in el.find_all("img")
                                        if img.get("src")
                                    ]
                                )

                        result = {
                            "text": text_content,
                            "images": images if include_images else None,
                            "url": url,
                        }
                    else:
                        # Extract all text content
                        text_content = soup.get_text(separator="\n", strip=True)

                        # Extract all images if requested
                        images = []
                        if include_images:
                            images = [
                                img.get("src")
                                for img in soup.find_all("img")
                                if img.get("src")
                            ]

                        result = {
                            "text": text_content,
                            "images": images if include_images else None,
                            "url": url,
                        }

                    # Add metadata if requested
                    if extract_type == "metadata" or extract_type == "all":
                        metadata = self._extract_metadata(soup, responses)
                        result["metadata"] = metadata

                # Take screenshot if requested
                if parameters.get("screenshot"):
                    screenshot = await page.screenshot()
                    result["screenshot"] = screenshot

                # Close browser
                await browser.close()

                return result

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error scraping URL {url}: {error_message}")

            # Provide more helpful error messages for common issues
            if "Timeout" in error_message:
                error_message = f"Timeout error: The page took too long to load. Consider increasing the timeout value. Original error: {error_message}"
            elif "Target closed" in error_message:
                error_message = f"Target closed: The browser was closed unexpectedly. This might be due to a crash or resource limitation. Original error: {error_message}"
            elif "Protocol error" in error_message:
                error_message = f"Protocol error: There was an issue communicating with the browser. Try again or use a different browser type. Original error: {error_message}"
            elif "browser has disconnected" in error_message:
                error_message = f"Browser disconnected: The browser connection was lost. This might be due to a crash or resource limitation. Original error: {error_message}"

            return {"error": error_message, "url": url, "status": "error"}

    async def _apply_stealth_mode(self, context: BrowserContext) -> None:
        """
        Apply stealth mode to avoid detection.

        Args:
            context: Browser context
        """
        # Add scripts to avoid detection
        await context.add_init_script(
            """
            // Override the webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });

            // Override Chrome automation property
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };

            // Override the plugins and mimeTypes
            if (navigator.plugins) {
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return [
                            {
                                0: {
                                    type: "application/x-google-chrome-pdf",
                                    suffixes: "pdf",
                                    description: "Portable Document Format",
                                    enabledPlugin: Plugin,
                                },
                                description: "Chrome PDF Plugin",
                                filename: "internal-pdf-viewer",
                                name: "Chrome PDF Plugin",
                                length: 1,
                            },
                            {
                                0: {
                                    type: "application/pdf",
                                    suffixes: "pdf",
                                    description: "Portable Document Format",
                                    enabledPlugin: Plugin,
                                },
                                description: "Chrome PDF Viewer",
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                name: "Chrome PDF Viewer",
                                length: 1,
                            },
                            {
                                0: {
                                    type: "application/x-nacl",
                                    suffixes: "",
                                    description: "Native Client Executable",
                                    enabledPlugin: Plugin,
                                },
                                1: {
                                    type: "application/x-pnacl",
                                    suffixes: "",
                                    description: "Portable Native Client Executable",
                                    enabledPlugin: Plugin,
                                },
                                description: "Native Client",
                                filename: "internal-nacl-plugin",
                                name: "Native Client",
                                length: 2,
                            },
                        ];
                    },
                });
            }

            // Override the languages property
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Override the permissions
            if (navigator.permissions) {
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = (parameters) => {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({ state: Notification.permission });
                    }
                    return originalQuery(parameters);
                };
            }
        """
        )

    async def _setup_resource_blocking(self, page: Page) -> None:
        """
        Set up resource blocking to improve performance.

        Args:
            page: Page object
        """
        # Block resource types that are not needed for scraping
        await page.route("**/*", self._handle_route)

    async def _handle_route(self, route):
        """
        Handle route for resource blocking.

        Args:
            route: Route object
        """
        # List of resource types to block
        block_resource_types = [
            "image",
            "media",
            "font",
            "stylesheet",
        ]

        # List of resource names to block (e.g., analytics, ads)
        block_resource_names = [
            "google-analytics",
            "googletagmanager",
            "doubleclick",
            "facebook",
            "twitter",
            "linkedin",
            "analytics",
            "tracking",
            "advertisement",
            "ads",
        ]

        # Get request details
        request = route.request
        resource_type = request.resource_type
        url = request.url

        # Check if resource should be blocked
        if resource_type in block_resource_types:
            await route.abort()
            return

        if any(name in url.lower() for name in block_resource_names):
            await route.abort()
            return

        # Continue with the request if not blocked
        await route.continue_()

    async def _scroll_to_bottom(self, page: Page) -> None:
        """
        Scroll to the bottom of the page to load lazy content.

        Args:
            page: Page object
        """
        # Get the page height
        height = await page.evaluate("document.body.scrollHeight")

        # Scroll in steps
        for i in range(0, height, 100):
            await page.evaluate(f"window.scrollTo(0, {i})")
            await asyncio.sleep(0.1)  # Small delay between scrolls

        # Final scroll to the bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)  # Wait for any lazy-loaded content

    async def _execute_js_scenario(
        self, page: Page, scenario: List[Dict[str, Any]]
    ) -> None:
        """
        Execute a JavaScript scenario (sequence of actions).

        Args:
            page: Page object
            scenario: List of actions to perform
        """
        for action in scenario:
            action_type = list(action.keys())[0]
            action_params = action[action_type]

            if action_type == "click":
                await page.click(action_params["selector"])

            elif action_type == "fill":
                await page.fill(action_params["selector"], action_params["value"])

            elif action_type == "type":
                await page.type(action_params["selector"], action_params["value"])

            elif action_type == "press":
                await page.press(action_params["selector"], action_params["key"])

            elif action_type == "wait_for_selector":
                await page.wait_for_selector(action_params["selector"])

            elif action_type == "wait_for_navigation":
                await page.wait_for_navigation()

            elif action_type == "wait_for_timeout":
                await asyncio.sleep(
                    action_params["timeout"] / 1000
                )  # Convert to seconds

            elif action_type == "evaluate":
                await page.evaluate(action_params["script"])

            elif action_type == "select_option":
                await page.select_option(
                    action_params["selector"], action_params["value"]
                )

            elif action_type == "check":
                await page.check(action_params["selector"])

            elif action_type == "uncheck":
                await page.uncheck(action_params["selector"])

    def _extract_metadata(
        self, soup: BeautifulSoup, responses: List[Response]
    ) -> Dict[str, Any]:
        """
        Extract metadata from the page.

        Args:
            soup: BeautifulSoup object
            responses: List of responses

        Returns:
            Metadata dictionary
        """
        metadata = {}

        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                meta_tags[name] = content

        metadata["meta_tags"] = meta_tags

        # Extract title
        title = soup.find("title")
        if title:
            metadata["title"] = title.text

        # Extract links
        links = []
        for link in soup.find_all("a", href=True):
            links.append(
                {
                    "text": link.text.strip(),
                    "href": link["href"],
                }
            )

        metadata["links"] = links

        # Extract response headers from main document
        main_response = next(
            (
                r
                for r in responses
                if r.url.split("?")[0] == r.request.url.split("?")[0]
            ),
            None,
        )
        if main_response:
            try:
                metadata["headers"] = dict(main_response.headers)
                metadata["status"] = main_response.status
            except Exception:
                pass

        return metadata

    def _get_user_agent(self) -> str:
        """
        Get a random user agent string.

        Returns:
            User agent string
        """
        user_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            # Firefox on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        ]

        return random.choice(user_agents)
