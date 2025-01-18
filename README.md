# Google Maps Review Scraper

A Python script to scrape Google Maps reviews using Selenium. This script extracts reviews, ratings, timestamps, user details, and more from Google Maps review pages. It supports exporting data to CSV or JSON formats.

## Features

- Scrapes reviews from Google Maps with detailed metadata.
- Supports headless browser operation for efficiency.
- Saves data as CSV or JSON.
- Logs actions for debugging and analysis.
- Allows customization through command-line arguments.

## Prerequisites

1. **Python 3.7 or later**: Ensure Python is installed.
2. **Google Chrome**: The script uses Chrome as the browser.
3. **ChromeDriver**: Download the ChromeDriver matching your Chrome version from [ChromeDriver Downloads](https://sites.google.com/a/chromium.org/chromedriver/).

## Installation

1. Clone this repository or download the script:

   ```bash
   git clone https://github.com/yourusername/google-maps-review-scraper.git
   ```

2. Navigate to the project directory:

```bash
cd google-maps-review-scraper
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Usage
Run the script with the following command-line arguments:

```bash
python scraper.py --driver <PATH_TO_CHROMEDRIVER> --url <GOOGLE_MAPS_REVIEW_URL>
```

## Command-Line Arguments

| Argument         | Type    | Default   | Description                                                              |
| ---------------- | ------- | --------- | ------------------------------------------------------------------------ |
| `--driver`       | string  | `Driver/chromedriver.exe`      | Path to the ChromeDriver executable (required).                          |
| `--url`          | string  | None      | Google Maps reviews URL to scrape (required).                            |
| `--headless`     | boolean | `True`    | Run the browser in headless mode (default: `True`).                      |
| `--verbose`      | boolean | `False`   | Enable verbose logging (default: `False`).                               |
| `--timeout`        | int     | `5`      | Delay for WebDriver actions in seconds (default: `10`).                  |
| `--original`     | boolean | `True`    | Include the original language comment (default: `True`).                 |
| `--language`     | string  | `en`      | Language for reviews (default: English).                                 |
| `--concat_extra` | boolean | `False`   | Combine extra review attributes into a single column (default: `False`). |
| `--path`         | string  | `data`    | Directory to save scraped data (default: `data`).                        |
| `--name`         | string  | `reviews` | File name prefix for saved data (default: `reviews`).                    |
| `--timestamp`    | boolean | `True`    | Append a timestamp to the file name (default: `True`).                   |
| `--log_file`     | string  | `None`    | File name for logging (default: logs displayed in the console).          |

## Code Usage Example

```python
from app import GoogleMapsReviewScraper
url_1 = "url_example_1" # Google Maps location while reviews are visible
DriverLocation = "./Driver/chromedriver.exe"
# open browser 
scrapper = GoogleMapsReviewScraper(driver_path=DriverLocation, headless=False, verbose=True, delay=5, original=True, language="en", concat_extra=True)
# scrap data from url_1
data = scrapper.scrap(url_1)
# save in data/google_maps_reviews.csv
scrapper.save_data(data= data, name="google_maps_reviews") 
# close browser
scrapper.exit(force=True)
```

## Output

The scraper produces two types of output files, depending on the `concat_extra` argument:

1. **CSV File** (if `concat_extra` is set to `True`):
2. **JSON File** (if `concat_extra` is set to `False`):

The output files are saved in the directory specified by the `--path` argument. The file name will be a combination of the provided `--name` and the timestamp (if `--timestamp` is enabled).

## Troubleshooting

ChromeDriver not found: Ensure the `--driver` path is correct and points to the ChromeDriver executable.
Google Maps URL issues: Verify the URL points to a valid Google Maps review page.
Slow scraping: Adjust the `--delay` parameter to optimize performance.
License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contribution

Feel free to open issues or submit pull requests to improve the script!

## Acknowledgements

Selenium for browser automation.
Google Maps for the review data.

## Disclaimer

This script is intended for educational purposes only. Scraping data from websites may violate their terms of service. Use this tool responsibly.
