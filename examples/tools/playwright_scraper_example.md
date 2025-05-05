# Playwright Scraper Tool Example

This example demonstrates how to use the `PlaywrightScraperTool` for advanced web scraping with the Agents Hub framework.

## Important Note

When running this example, you may encounter timeouts or other issues with certain websites that have strong anti-scraping measures. The example has been updated to use more reliable websites and includes error handling to provide helpful messages when issues occur.

## Features

The Playwright Scraper Tool provides the following features:

- **JavaScript Rendering**: Scrape JavaScript-heavy websites that require a full browser to render
- **Anti-Detection**: Avoid being blocked by websites with stealth mode
- **Dynamic Interaction**: Execute JavaScript scenarios to interact with websites (click, type, etc.)
- **Resource Blocking**: Improve performance by blocking unnecessary resources
- **Infinite Scroll Handling**: Automatically scroll to load lazy-loaded content
- **Flexible Content Extraction**: Extract text, HTML, or metadata from websites

## Prerequisites

Before running this example, make sure you have installed the required dependencies:

```bash
# Install agents-hub in development mode
pip install -e ../../

# Install Playwright
pip install playwright

# Install Playwright browsers
playwright install chromium firefox
```

## Usage

### Basic Usage

```python
from agents_hub.tools.standard import PlaywrightScraperTool

# Initialize the tool
playwright_scraper = PlaywrightScraperTool()

# Use the tool
result = await playwright_scraper.run({
    "url": "https://example.com",
    "extract_type": "text",
})

print(result["text"])
```

### Advanced Usage

```python
# Scrape with a specific selector and stealth mode
result = await playwright_scraper.run({
    "url": "https://example.com",
    "extract_type": "text",
    "selector": ".main-content",
    "stealth_mode": True,
    "wait_for_selector": ".loaded-indicator",
})

# Execute a JavaScript scenario
result = await playwright_scraper.run({
    "url": "https://example.com",
    "extract_type": "text",
    "js_scenario": [
        {"click": {"selector": "#login-button"}},
        {"fill": {"selector": "#username", "value": "testuser"}},
        {"fill": {"selector": "#password", "value": "password123"}},
        {"click": {"selector": "#submit-button"}},
        {"wait_for_navigation": {"timeout": 2000}},
    ],
})
```

### Using with an Agent

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import PlaywrightScraperTool

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Initialize the Playwright scraper tool
playwright_scraper = PlaywrightScraperTool()

# Create an agent with the Playwright scraper tool
agent = Agent(
    name="web_researcher",
    llm=llm,
    tools=[playwright_scraper],
    system_prompt="You are a web researcher that can scrape and analyze web content from JavaScript-heavy websites."
)

# Use the agent to scrape a JavaScript-heavy website
response = await agent.run("Scrape and summarize the content from https://example.com")
print(response)
```

## Running the Example

To run the example:

```bash
# Navigate to the examples directory
cd examples/tools

# Run the example
python playwright_scraper_example.py
```

## Parameters

The `PlaywrightScraperTool` accepts the following parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `url` | string | URL to scrape | (required) |
| `extract_type` | string | Type of content to extract (`text`, `html`, `metadata`, `all`) | `text` |
| `selector` | string | CSS selector to extract specific content | (optional) |
| `wait_for_selector` | string | CSS selector to wait for before extracting content | (optional) |
| `wait_time` | integer | Time to wait in milliseconds after page load | 0 |
| `include_images` | boolean | Whether to include image URLs in the result | `false` |
| `block_resources` | boolean | Whether to block non-essential resources | `true` |
| `browser_type` | string | Browser type to use (`chromium`, `firefox`, `webkit`) | `chromium` |
| `stealth_mode` | boolean | Whether to use stealth mode to avoid detection | `true` |
| `scroll_to_bottom` | boolean | Whether to scroll to the bottom of the page | `false` |
| `js_scenario` | array | List of JavaScript actions to perform | (optional) |
| `headers` | object | Custom headers to use for the request | (optional) |
| `timeout` | integer | Timeout in milliseconds | 30000 |

## Anti-Detection Techniques

The `PlaywrightScraperTool` implements several anti-detection techniques to avoid being blocked by websites:

1. **User Agent Randomization**: Randomly selects a user agent from a list of common browsers
2. **WebDriver Property Patching**: Hides the WebDriver property that automation tools expose
3. **Plugin and MIME Type Emulation**: Emulates browser plugins and MIME types
4. **Language Preferences**: Sets realistic language preferences
5. **Permissions Handling**: Properly handles permission requests

These techniques help to make the automated browser appear more like a real user's browser, reducing the likelihood of being detected and blocked.

## Resource Blocking

To improve performance, the `PlaywrightScraperTool` can block unnecessary resources like images, stylesheets, fonts, and tracking scripts. This significantly reduces bandwidth usage and speeds up the scraping process.

Resource blocking is enabled by default but can be disabled by setting `block_resources` to `false`.

## JavaScript Scenarios

The `js_scenario` parameter allows you to define a sequence of actions to perform on the page. Each action is an object with a single key representing the action type and a value containing the parameters for that action.

Supported actions include:

- `click`: Click on an element
- `fill`: Fill a form field
- `type`: Type text into an element
- `press`: Press a key
- `wait_for_selector`: Wait for an element to appear
- `wait_for_navigation`: Wait for navigation to complete
- `wait_for_timeout`: Wait for a specified time
- `evaluate`: Evaluate JavaScript code
- `select_option`: Select an option from a dropdown
- `check`: Check a checkbox
- `uncheck`: Uncheck a checkbox

Example:

```python
"js_scenario": [
    {"click": {"selector": "#login-button"}},
    {"fill": {"selector": "#username", "value": "testuser"}},
    {"fill": {"selector": "#password", "value": "password123"}},
    {"click": {"selector": "#submit-button"}},
    {"wait_for_navigation": {"timeout": 2000}},
]
```

## Troubleshooting

If you encounter issues with the Playwright Scraper Tool, try the following:

1. **Install Playwright Browsers**: Make sure you have installed the required browsers:
   ```bash
   playwright install chromium firefox
   ```

2. **Increase Timeout**: Some websites take longer to load. Try increasing the `timeout` parameter:
   ```python
   result = await playwright_scraper.run({
       "url": "https://example.com",
       "timeout": 120000,  # 2 minutes
   })
   ```

3. **Try Different Websites**: Some websites have strong anti-scraping measures. Try with a different website that is less likely to block scrapers.

4. **Change Browser Type**: Some websites work better with different browsers. Try changing the `browser_type` parameter:
   ```python
   result = await playwright_scraper.run({
       "url": "https://example.com",
       "browser_type": "firefox",  # Try Firefox instead of Chrome
   })
   ```

5. **Adjust Stealth Settings**: In some cases, you might need to customize the stealth settings:
   ```python
   # Disable stealth mode
   result = await playwright_scraper.run({
       "url": "https://example.com",
       "stealth_mode": False,
   })
   ```

6. **Check for Captchas**: Some websites might show captchas that need to be solved manually.

7. **Use Proper Error Handling**: Always check for errors in the result:
   ```python
   result = await playwright_scraper.run({
       "url": "https://example.com",
   })

   if "error" in result:
       print(f"Error: {result['error']}")
   else:
       print(f"Success! Content: {result['text'][:100]}...")
   ```

## License

This example is part of the Agents Hub framework and is licensed under the MIT License.
