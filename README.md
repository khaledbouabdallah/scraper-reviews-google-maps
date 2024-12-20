# Scraper Reviews Google Maps

This project is a web scraper designed to extract reviews from Google Maps. It can be used to gather customer feedback for businesses listed on Google Maps.

## Features

- Extract reviews from Google Maps
- Save reviews to a CSV file
- Handle pagination to get all reviews
- Configurable to scrape reviews for different businesses

## Requirements

- Python 3.x
- BeautifulSoup
- Requests
- Pandas

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/scraper-reviews-google-maps.git
    ```
2. Navigate to the project directory:
    ```bash
    cd scraper-reviews-google-maps
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Open the `config.py` file and set the `GOOGLE_MAPS_URL` to the URL of the business you want to scrape reviews for.
2. Run the scraper:
    ```bash
    python scraper.py
    ```
3. The reviews will be saved to a `reviews.csv` file in the project directory.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact [yourname@example.com](mailto:yourname@example.com).
