# Motherless Image Scraper

A Python tool for scraping images from galleries on the Motherless website using Selenium. This tool is configurable, supports concurrent downloading, and skips already downloaded images.

## Features

- **Configurable**: Customize settings via `config.json`.
- **Concurrent**: Multithreaded scraping for speed.
- **Duplicate Handling**: Skips images that are already downloaded.

## Setup

### Prerequisites

- **Python 3.x**
- **Google Chrome**
- **pip**

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/motherless-image-scraper.git
    cd motherless-image-scraper
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure**: Edit `config.json`:

    ```json
    {
        "base_url": "https://motherless.com/gi/your_gallery_name_here",
        "start_page": 1,
        "end_page": 10,
        "output_dir": "your_output_directory_here",
        "num_threads": 5
    }
    ```

## Usage

Run the script:

```bash
python scraper.py
Images will be saved in the specified output directory. The script automatically skips already downloaded images.
