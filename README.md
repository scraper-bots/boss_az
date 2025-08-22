# Boss.az Resume Scraper

A Python web scraper for collecting job seeker resume data from boss.az, Azerbaijan's leading job portal.

## Features

- **Complete Resume Data Extraction**: Scrapes comprehensive information from job seeker profiles including personal details, contact information, skills, education, and work experience
- **Automatic Pagination**: Handles pagination to scrape all available resume listings across multiple pages
- **Two-Phase Scraping**: First collects all resume URLs from listing pages, then scrapes detailed information from individual resume pages
- **Respectful Scraping**: Built-in delays and proper headers to avoid overwhelming the server
- **CSV Export**: Saves all collected data in a structured CSV format for easy analysis
- **Error Handling**: Robust error handling with comprehensive logging
- **Configurable**: Easy to configure page limits, delays, and output settings

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- lxml

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python boss_scraper.py
```

This will:
- Scrape the first 5 pages of resumes
- Save data to `boss_az_resumes.csv`
- Use a 2-second delay between requests

### Configuration

You can modify the configuration in the `main()` function of `boss_scraper.py`:

```python
# Configuration options
START_URL = "https://boss.az/resumes?action=index&controller=resumes&only_path=true&page=1&type=resumes"
MAX_PAGES = 5  # Set to None to scrape all pages
OUTPUT_FILE = "boss_az_resumes.csv"
DELAY = 2  # Delay between requests in seconds
```

### Advanced Usage

You can also use the scraper programmatically:

```python
from boss_scraper import BossAzScraper

# Create scraper instance with custom delay
scraper = BossAzScraper(delay=3)

# Run scraper with custom parameters
scraper.run_scraper(
    start_url="https://boss.az/resumes?action=index&controller=resumes&only_path=true&page=1&type=resumes",
    max_pages=10,  # Scrape 10 pages
    output_file="custom_output.csv"
)
```

## Data Fields

The scraper extracts the following information for each resume:

### Basic Information
- `url`: Direct link to the resume
- `title`: Job title/position sought
- `seeker_name`: Name of the job seeker
- `salary`: Expected salary
- `full_name`: Complete name

### Contact Information
- `phone`: Phone number
- `email`: Email address

### Personal Details
- `city`: City/location
- `age`: Age
- `gender`: Gender
- `approval_date`: Date when resume was approved/posted
- `expiry_date`: Resume expiration date

### Professional Information
- `skills`: Detailed skills and competencies
- `education`: Education level
- `education_info`: Detailed educational background
- `experience`: Work experience level
- `experience_info`: Detailed work experience
- `personal_info`: Additional personal information

### Metadata
- `listing_number`: Unique listing ID
- `view_count`: Number of times the resume has been viewed

## Output

The scraper saves data to a CSV file with UTF-8 encoding, making it easy to:
- Import into Excel or Google Sheets
- Analyze with Python pandas
- Process with other data analysis tools

## Best Practices

- **Respect Rate Limits**: The default 2-second delay is recommended. Increase if you encounter issues
- **Monitor Usage**: Keep an eye on the logs to ensure successful scraping
- **Test First**: Run with a small `MAX_PAGES` value first to test the setup
- **Handle Large Datasets**: For scraping all pages, consider running in batches

## Logging

The scraper provides detailed logging information including:
- Progress updates for each page and resume
- Error messages for failed requests
- Summary statistics

Log messages are displayed in the console with timestamps and severity levels.

## Error Handling

The scraper includes robust error handling for:
- Network connection issues
- Missing page elements
- Invalid URLs
- Server errors

Failed requests are logged but don't stop the overall scraping process.

## Legal and Ethical Considerations

- This scraper is for educational and research purposes
- Respect the website's robots.txt and terms of service
- Use reasonable delays between requests
- Don't overload the server with too many concurrent requests
- Consider the privacy of the scraped data

## Troubleshooting

### Common Issues

1. **Network Errors**: Check your internet connection and try increasing the delay
2. **Empty Results**: Verify the start URL is accessible and contains resume listings
3. **Missing Dependencies**: Ensure all packages from requirements.txt are installed

### Getting Help

If you encounter issues:
1. Check the log output for error messages
2. Verify the website structure hasn't changed
3. Test with a smaller page limit first

## License

This project is provided as-is for educational purposes. Please use responsibly and in accordance with applicable laws and website terms of service.