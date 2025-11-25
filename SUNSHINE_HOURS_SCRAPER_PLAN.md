# Sunshine Hours Scraper Implementation Plan

## Objective
Scrape annual sunshine hours data from Wikipedia and integrate it into the country ranking dataset.

---

## Data Source
**URL:** https://en.wikipedia.org/wiki/List_of_cities_by_sunshine_duration

**Data Type:** City-level annual sunshine hours (from WMO 1961-1990 averages)

**Challenge:** Wikipedia blocks automated scraping (403 errors), so we'll need to use alternative approaches.

---

## Implementation Strategy

### Approach 1: Use Wikipedia API (RECOMMENDED)
Instead of scraping HTML directly, use Wikipedia's official API to get the page content.

**Advantages:**
- No 403 blocking
- Official API endpoint
- More reliable than HTML parsing
- Returns clean structured data

**API Endpoint:**
```
https://en.wikipedia.org/w/api.php?action=parse&page=List_of_cities_by_sunshine_duration&format=json
```

### Approach 2: Manual Export + Python Processing
If API doesn't work:
1. Manually open the Wikipedia page in browser
2. Export tables to CSV using browser developer tools or copy-paste
3. Save as `data/raw_sunshine_hours_cities.csv`
4. Use Python script to aggregate city → country level

---

## Data Structure Overview

Wikipedia page contains multiple tables organized by region:
- **Africa**
- **Asia**
- **Europe**
- **North America**
- **South America**
- **Oceania**

Each table has columns like:
- City
- Country
- Annual sunshine hours
- Jan, Feb, Mar, ... (monthly breakdown)

---

## Step-by-Step Implementation Plan

### Step 1: Create Scraper Script
**File:** `scrape_sunshine_hours.py`

**Tasks:**
1. Fetch Wikipedia page content using API or requests with proper headers
2. Parse HTML tables using BeautifulSoup
3. Extract city name, country, and annual sunshine hours
4. Handle data cleaning:
   - Remove footnote references (e.g., "[1]", "[2]")
   - Convert string numbers to floats
   - Handle missing/incomplete data

**Sample Code Structure:**
```python
import requests
import pandas as pd
from bs4 import BeautifulSoup
import pycountry
import scrape_urls  # Reuse existing utility functions

# Wikipedia API approach
def fetch_wikipedia_api(page_title):
    """Fetch Wikipedia page content via API"""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "format": "json",
        "prop": "text"
    }
    response = requests.get(url, params=params)
    return response.json()

# Alternative: Direct HTML with custom headers
def fetch_with_headers(url):
    """Fetch with browser-like headers to avoid 403"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    response = requests.get(url, headers=headers)
    return response.text

def parse_sunshine_tables(html_content):
    """Parse all regional tables from Wikipedia page"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all tables with class 'wikitable' or 'sortable'
    tables = soup.find_all('table', class_='wikitable')

    all_data = []
    for table in tables:
        # Extract headers
        headers = [th.text.strip() for th in table.find_all('th')]

        # Extract rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = [td.text.strip() for td in row.find_all('td')]
            if len(cells) >= 3:  # Ensure we have city, country, hours
                all_data.append(cells)

    return all_data

def clean_sunshine_data(raw_data):
    """Clean and structure the scraped data"""
    cleaned = []
    for row in raw_data:
        # Remove footnote markers like [1], [2]
        city = row[0].split('[')[0].strip()
        country = row[1].split('[')[0].strip()

        # Extract annual hours (usually in 'Year' or 'Annual' column)
        annual_hours = extract_annual_hours(row)

        cleaned.append({
            'city': city,
            'country': country,
            'annual_sunshine_hours': annual_hours
        })

    return pd.DataFrame(cleaned)

def extract_annual_hours(row):
    """Extract annual sunshine hours from row data"""
    # Logic to find the 'Annual' or 'Year' column value
    # Handle commas in numbers (e.g., "3,200" → 3200)
    # Handle missing data
    pass
```

---

### Step 2: Aggregate City Data to Country Level
**File:** `scrape_sunshine_hours.py` (continued)

**Strategy:**
- Multiple cities per country → compute **average** or **median**
- Consider using major cities only (capital + largest cities)
- Weight by city population if available (optional enhancement)

**Code:**
```python
def aggregate_to_country_level(df):
    """
    Aggregate city-level data to country-level.

    Options:
    1. Mean of all cities in a country
    2. Median (more robust to outliers)
    3. Weighted average by city population (if available)
    """
    country_avg = df.groupby('country')['annual_sunshine_hours'].mean()
    country_median = df.groupby('country')['annual_sunshine_hours'].median()
    country_count = df.groupby('country').size()

    result = pd.DataFrame({
        'Country': country_avg.index,
        'Avg Sunshine Hours': country_avg.values,
        'Median Sunshine Hours': country_median.values,
        'Number of Cities': country_count.values
    })

    # Use median if country has many cities (more robust)
    # Otherwise use mean
    result['Sunshine Hours'] = result.apply(
        lambda row: row['Median Sunshine Hours'] if row['Number of Cities'] >= 3
                    else row['Avg Sunshine Hours'],
        axis=1
    )

    return result[['Country', 'Sunshine Hours']]
```

---

### Step 3: Standardize Country Names
**File:** `scrape_sunshine_hours.py` (continued)

**Approach:** Use same pattern as existing scripts (`predict_PPP.py`, `get_data.py`)

**Code:**
```python
def standardize_country_names(df):
    """
    Standardize country names using pycountry library.
    Same pattern as predict_PPP.py lines 14-23.
    """
    std_country_names = []

    for country in df['Country']:
        try:
            # Try fuzzy matching
            std_name = pycountry.countries.search_fuzzy(country)[0].name
            std_country_names.append(std_name)
        except:
            # Keep original if no match found
            std_country_names.append(country)
            print(f"Warning: Could not standardize '{country}'")

    df['Country'] = std_country_names
    return df

def manual_country_mapping():
    """
    Handle special cases that pycountry might miss.
    """
    return {
        'U.S.A.': 'United States',
        'USA': 'United States',
        'UK': 'United Kingdom',
        'UAE': 'United Arab Emirates',
        'South Korea': 'Korea, Republic of',
        'North Korea': 'Korea, Democratic People\'s Republic of',
        # Add more as needed
    }
```

---

### Step 4: Save to CSV
**File:** `scrape_sunshine_hours.py` (continued)

**Output:** `data/Sunshine Hours by Country.csv`

**Format:**
```
Country,Sunshine Hours
Afghanistan,3200
Albania,2500
...
```

**Code:**
```python
def main():
    """Main execution flow"""
    # 1. Fetch Wikipedia page
    print("Fetching Wikipedia page...")
    page_title = "List_of_cities_by_sunshine_duration"
    html_content = fetch_wikipedia_api(page_title)
    # OR: html_content = fetch_with_headers(url)

    # 2. Parse tables
    print("Parsing sunshine tables...")
    raw_data = parse_sunshine_tables(html_content)

    # 3. Clean data
    print("Cleaning data...")
    df_cities = clean_sunshine_data(raw_data)

    # 4. Aggregate to country level
    print("Aggregating to country level...")
    df_countries = aggregate_to_country_level(df_cities)

    # 5. Standardize country names
    print("Standardizing country names...")
    df_countries = standardize_country_names(df_countries)

    # 6. Save to CSV
    output_path = 'data/Sunshine Hours by Country.csv'
    df_countries.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

    # 7. Print summary statistics
    print(f"\nTotal countries: {len(df_countries)}")
    print(f"Average sunshine hours: {df_countries['Sunshine Hours'].mean():.0f}")
    print(f"Range: {df_countries['Sunshine Hours'].min():.0f} - {df_countries['Sunshine Hours'].max():.0f}")

if __name__ == '__main__':
    main()
```

---

### Step 5: Integrate into Main Dataset
**File:** `get_data.py`

**Modification Required:** Add sunshine hours to the data joining process

**Code Changes:**
```python
# Add this import near the top of get_data.py
sunshine_hours = pd.read_csv(os.path.join(data_dir, 'Sunshine Hours by Country.csv'))

# Add to the merge operations (find the section where other CSVs are merged)
all_data = all_data.merge(
    sunshine_hours,
    left_on='Country',
    right_on='Country',
    how='left'  # Left join to keep all countries even if no sunshine data
)
```

**Expected Column in `All Data by Country.csv`:**
- New column: `Sunshine Hours`

---

## Data Validation & Quality Checks

### After Scraping
1. **Check for missing countries:**
   - Compare scraped country list vs. existing dataset
   - Identify countries with no sunshine data

2. **Sanity checks:**
   - Sunshine hours should be between 1,000 - 4,500 hours/year
   - Tropical countries: ~2,000-3,000 hours
   - Sunny deserts: 3,500-4,000 hours
   - Northern Europe: 1,500-2,000 hours

3. **Manual review:**
   - Spot-check known countries (e.g., Spain ~2,700, Egypt ~3,500, UK ~1,500)

### Code for Validation:
```python
def validate_sunshine_data(df):
    """Validate scraped sunshine hours data"""

    # Check range
    invalid_range = df[(df['Sunshine Hours'] < 1000) | (df['Sunshine Hours'] > 4500)]
    if len(invalid_range) > 0:
        print("WARNING: Countries with unusual sunshine hours:")
        print(invalid_range)

    # Check for NaN/missing
    missing = df[df['Sunshine Hours'].isna()]
    if len(missing) > 0:
        print(f"WARNING: {len(missing)} countries with missing sunshine data")

    # Print summary
    print(f"\nData summary:")
    print(df['Sunshine Hours'].describe())
```

---

## Handling Edge Cases

### Common Issues & Solutions

1. **Wikipedia table structure changes**
   - Solution: Add flexibility to column detection (search for keywords like "Annual", "Year", "Total")

2. **Multiple cities with same name**
   - Example: "Paris, France" vs "Paris, Texas"
   - Solution: Use both city and country columns for disambiguation

3. **Countries with no data**
   - Solution: Use `how='left'` in merge to preserve countries, fill NaN later with regional averages

4. **Special territories**
   - Example: Puerto Rico, Hong Kong, Greenland
   - Solution: Map to parent country OR keep as separate entry (match existing dataset approach)

5. **Country name mismatches**
   - Example: "Czech Republic" vs "Czechia"
   - Solution: Manual mapping dictionary + pycountry fuzzy matching

---

## Alternative Fallback Plan

If Wikipedia scraping fails completely:

### Manual Data Entry Process
1. Open Wikipedia page in browser
2. For each regional table:
   - Select all → Copy
   - Paste into Google Sheets or Excel
3. Clean in spreadsheet:
   - Remove footnotes
   - Add "Country" column header
   - Extract annual column
4. Export to CSV
5. Run Python script to aggregate and standardize country names

**Estimated Time:** 30-45 minutes of manual work

---

## Testing Strategy

### Unit Tests
Create `test_sunshine_scraper.py`:

```python
import pytest
import pandas as pd
from scrape_sunshine_hours import (
    clean_sunshine_data,
    aggregate_to_country_level,
    standardize_country_names
)

def test_clean_sunshine_data():
    """Test data cleaning function"""
    raw_data = [
        ['Paris[1]', 'France[2]', '1,662', '...'],
        ['London', 'United Kingdom', '1,633', '...']
    ]
    result = clean_sunshine_data(raw_data)
    assert result.loc[0, 'city'] == 'Paris'
    assert result.loc[0, 'country'] == 'France'

def test_aggregate_to_country_level():
    """Test country-level aggregation"""
    df = pd.DataFrame({
        'country': ['France', 'France', 'Germany'],
        'annual_sunshine_hours': [2500, 2600, 1800]
    })
    result = aggregate_to_country_level(df)
    assert result.loc[result['Country'] == 'France', 'Sunshine Hours'].values[0] == 2550

def test_country_name_standardization():
    """Test country name standardization"""
    df = pd.DataFrame({'Country': ['USA', 'UK', 'France']})
    result = standardize_country_names(df)
    assert 'United States' in result['Country'].values
```

---

## Expected Deliverables

1. **Script:** `scrape_sunshine_hours.py` (new file)
2. **Data:** `data/Sunshine Hours by Country.csv` (new file)
3. **Integration:** Modified `get_data.py` to include sunshine hours
4. **Updated Dataset:** `data/All Data by Country.csv` with new column

---

## Timeline Estimate

- **Setup & Initial Scraper:** 1-2 hours
- **Data Cleaning & Aggregation:** 1 hour
- **Country Name Mapping:** 30 minutes
- **Testing & Validation:** 30 minutes
- **Integration into get_data.py:** 15 minutes

**Total:** ~3-4 hours

---

## Next Steps After Sunshine Data is Ready

1. Verify sunshine hours column exists in `All Data by Country.csv`
2. Proceed with creating the utility scoring function
3. Incorporate sunshine hours with your preference: "~2400 ideal, acceptable 1800+"

---

## Dependencies

**Python Packages (already in requirements.txt):**
- `requests`
- `beautifulsoup4`
- `pandas`
- `pycountry`

**New Dependencies (if needed):**
```bash
# None - all required packages already installed
```

---

## Useful Resources

- **Wikipedia API Documentation:** https://www.mediawiki.org/wiki/API:Main_page
- **BeautifulSoup Docs:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **pycountry GitHub:** https://github.com/flyingcircusio/pycountry

---

## Notes

- Wikipedia data is from 1961-1990 WMO averages (historical but still relevant for long-term climate patterns)
- Some countries may only have 1-2 cities listed → less reliable average
- Consider weighting by city size in future enhancement
- This plan reuses existing patterns from your codebase (scrape_urls.py, pycountry standardization)
