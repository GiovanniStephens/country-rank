"""
Utility Scoring Function for Country Ranking

This module calculates a personalized utility score for each country based on
multiple preference criteria with non-linear transformations.

Author: Created for personalized country ranking
Date: 2025-11-25
"""

import os
import numpy as np
import pandas as pd
import pycountry
from predict_PPP import estimate_PPP_conversion_rate_long_term_change


# ============================================================================
# CONFIGURATION - Adjust these to your preferences
# ============================================================================

# Weights for each factor (will be normalized to sum to 1.0)
WEIGHTS = {
    'temperature_variability': 2.5,  # Climate is most important
    'temperature_optimality': 2.5,   # Climate is most important
    'sunshine_hours': 2.0,           # Climate factor
    'population_density': 1.0,       # Moderate importance
    'safety': 2.0,                   # Extra weight on safety
    'corruption': 1.0,               # Equal weight
    'healthcare': 1.0,               # Equal weight
    'air_purity': 1.0,               # Equal weight
    'freedom': 1.0,                  # Equal weight
    'ppp_change': 1.0,               # Equal weight
    'net_income_proxy': 1.0,         # Equal weight (inverse of cost)
}

# Temperature preferences (in Celsius)
TEMP_PREFERENCES = {
    'ideal_temp': 24,        # Your ideal temperature
    'comfortable_min': 10,   # Below this starts to get uncomfortable
    'comfortable_max': 27,   # Above this starts to get uncomfortable
    'penalty_threshold': 30, # Above this, steep penalty kicks in
    'extreme_penalty': 35,   # Above this should rarely appear in top 20
}

# Sunshine hours preferences (annual hours)
SUNSHINE_PREFERENCES = {
    'ideal': 2400,           # Your ideal sunshine hours
    'acceptable_min': 1800,  # Below this is less desirable
}

# Population density preferences (people per sq km)
DENSITY_PREFERENCES = {
    'very_low': 20,          # Queenstown-like (~58)
    'comfortable': 300,      # Seoul was fine (~500-600)
    'too_high': 1000,        # Bogota/Shanghai level
}


# ============================================================================
# UTILITY FUNCTIONS - Non-linear transformations
# ============================================================================

def score_temperature_variability(max_temp, min_temp):
    """
    Score based on temperature variability. Lower variability is better.

    You like narrow temperature ranges (avoiding -10 winter, +40 summer).
    Ideal: similar temps year-round around 24°C.

    :param max_temp: Maximum average temperature
    :param min_temp: Minimum average temperature
    :return: Score from 0 to 100
    """
    if pd.isna(max_temp) or pd.isna(min_temp):
        return np.nan

    temp_range = max_temp - min_temp

    # Ideal range: ~10 degrees (e.g., 19-29°C)
    # Penalize heavily for large ranges
    if temp_range <= 10:
        score = 100
    elif temp_range <= 15:
        # Mild penalty
        score = 100 - (temp_range - 10) * 8  # Loses 8 points per degree over 10
    elif temp_range <= 25:
        # Moderate penalty
        score = 60 - (temp_range - 15) * 4
    else:
        # Heavy penalty for extreme variability
        score = 20 - (temp_range - 25) * 2

    return max(0, min(100, score))


def score_temperature_optimality(avg_temp, min_temp, max_temp):
    """
    Score based on how close temperatures are to ideal.

    Preferences:
    - Can live over 10°C (acceptable but not ideal)
    - Gets better until 27-28°C (ideal zone)
    - Sharp dropoff at 30°C+
    - Heavy penalty above 35°C

    :param avg_temp: Average annual temperature
    :param min_temp: Minimum average temperature
    :param max_temp: Maximum average temperature
    :return: Score from 0 to 100
    """
    if pd.isna(avg_temp) or pd.isna(min_temp) or pd.isna(max_temp):
        return np.nan

    ideal = TEMP_PREFERENCES['ideal_temp']
    comfortable_min = TEMP_PREFERENCES['comfortable_min']
    comfortable_max = TEMP_PREFERENCES['comfortable_max']
    penalty_threshold = TEMP_PREFERENCES['penalty_threshold']
    extreme_penalty = TEMP_PREFERENCES['extreme_penalty']

    # Check if max temp is dangerously high (steep penalty)
    if max_temp >= extreme_penalty:
        return 5  # Should rarely appear in top 20
    elif max_temp >= penalty_threshold:
        # Steep dropoff: 30°C is ok, 31-34°C increasingly bad
        heat_penalty = (max_temp - penalty_threshold) * 15  # Loses 15 points per degree
    else:
        heat_penalty = 0

    # Check if min temp is too cold
    if min_temp < comfortable_min:
        cold_penalty = (comfortable_min - min_temp) * 3  # Loses 3 points per degree below 10
    else:
        cold_penalty = 0

    # Score based on average temperature proximity to ideal
    temp_diff = abs(avg_temp - ideal)

    if temp_diff <= 3:
        # Within ideal zone (21-27°C)
        base_score = 100
    elif temp_diff <= 7:
        # Close to ideal (17-20°C or 28-31°C)
        base_score = 100 - (temp_diff - 3) * 8
    else:
        # Far from ideal
        base_score = 68 - (temp_diff - 7) * 5

    # Apply penalties
    final_score = base_score - cold_penalty - heat_penalty

    return max(0, min(100, final_score))


def score_sunshine_hours(sunshine_hours):
    """
    Score based on annual sunshine hours.

    Preferences:
    - Ideal: ~2400 hours
    - Acceptable: 1800+ hours
    - Below 1800: increasingly undesirable

    :param sunshine_hours: Annual sunshine hours
    :return: Score from 0 to 100
    """
    if pd.isna(sunshine_hours):
        return np.nan

    ideal = SUNSHINE_PREFERENCES['ideal']
    acceptable_min = SUNSHINE_PREFERENCES['acceptable_min']

    if sunshine_hours >= ideal:
        # At or above ideal
        # Don't penalize too much for having MORE sunshine
        excess = sunshine_hours - ideal
        score = 100 - (excess / 100) * 2  # Gentle penalty for very sunny
    elif sunshine_hours >= acceptable_min:
        # Between acceptable and ideal (1800-2400)
        # Linear interpolation
        score = 70 + ((sunshine_hours - acceptable_min) / (ideal - acceptable_min)) * 30
    elif sunshine_hours >= 1400:
        # Below acceptable but not terrible (1400-1800)
        score = 40 + ((sunshine_hours - 1400) / 400) * 30
    else:
        # Very low sunshine (below 1400)
        score = (sunshine_hours / 1400) * 40

    return max(0, min(100, score))


def score_population_density(density):
    """
    Score based on population density.

    Preferences:
    - Not too sensitive
    - Queenstown NZ (~58) is good
    - Seoul (~600) was fine
    - Bogota/Shanghai (~1000+) might be too much

    :param density: Population density (people per sq km)
    :return: Score from 0 to 100
    """
    if pd.isna(density):
        return np.nan

    very_low = DENSITY_PREFERENCES['very_low']
    comfortable = DENSITY_PREFERENCES['comfortable']
    too_high = DENSITY_PREFERENCES['too_high']

    if density <= very_low:
        # Very rural - might be too isolated
        score = 60 + (density / very_low) * 20
    elif density <= comfortable:
        # Sweet spot: small town to medium city
        score = 80 + ((comfortable - density) / comfortable) * 20
    elif density <= too_high:
        # Getting crowded but still ok
        score = 80 - ((density - comfortable) / (too_high - comfortable)) * 50
    else:
        # Too dense
        excess = density - too_high
        score = 30 - (excess / 1000) * 20  # Loses 20 points per 1000 over threshold

    return max(0, min(100, score))


def score_safety(safety_index):
    """
    Score based on safety index. Linear: safer is better.

    :param safety_index: Safety index (0-100, higher is safer)
    :return: Score from 0 to 100
    """
    if pd.isna(safety_index):
        return np.nan

    # Direct pass-through (already 0-100, higher is better)
    return max(0, min(100, safety_index))


def score_corruption(cpi_score):
    """
    Score based on Corruption Perceptions Index.

    :param cpi_score: CPI score (0-100, higher = less corrupt)
    :return: Score from 0 to 100
    """
    if pd.isna(cpi_score):
        return np.nan

    # Direct pass-through (already 0-100, higher is better)
    return max(0, min(100, cpi_score))


def score_healthcare(healthcare_index):
    """
    Score based on healthcare index. Linear: higher is better.

    :param healthcare_index: Healthcare index (0-100, higher is better)
    :return: Score from 0 to 100
    """
    if pd.isna(healthcare_index):
        return np.nan

    # Direct pass-through (already 0-100, higher is better)
    return max(0, min(100, healthcare_index))


def score_air_purity(pollution_index):
    """
    Score based on air pollution. Lower pollution is better.

    :param pollution_index: Pollution index (0-100, higher = more polluted)
    :return: Score from 0 to 100
    """
    if pd.isna(pollution_index):
        return np.nan

    # Invert: 0 pollution = 100 score, 100 pollution = 0 score
    return 100 - max(0, min(100, pollution_index))


def score_freedom(freedom_score):
    """
    Score based on country freedom index.

    You prefer free countries but not opposed to moderately conservative
    countries like Georgia (score 60).

    :param freedom_score: Freedom score (0-100, higher is more free)
    :return: Score from 0 to 100
    """
    if pd.isna(freedom_score):
        return np.nan

    # Moderate preference: 60+ is acceptable, 80+ is ideal
    if freedom_score >= 80:
        score = 100
    elif freedom_score >= 60:
        # Georgia-like (60) gets decent score
        score = 70 + ((freedom_score - 60) / 20) * 30
    elif freedom_score >= 40:
        # Less free but still livable
        score = 40 + ((freedom_score - 40) / 20) * 30
    else:
        # Too restrictive
        score = (freedom_score / 40) * 40

    return max(0, min(100, score))


def score_ppp_change(country, nz_ppp_change=None):
    """
    Score based on PPP forecast change relative to New Zealand.

    Positive change relative to NZ = good (your money goes further)
    Negative change relative to NZ = bad (your money loses value)

    :param country: Country name
    :param nz_ppp_change: NZ's PPP change rate (calculated once, passed in)
    :return: Score from 0 to 100
    """
    try:
        country_ppp_change = estimate_PPP_conversion_rate_long_term_change(country)

        if nz_ppp_change is None:
            nz_ppp_change = estimate_PPP_conversion_rate_long_term_change('New Zealand')

        # Relative change: positive means better than NZ
        relative_change = country_ppp_change - nz_ppp_change

        # Score based on relative change
        # +3% better than NZ = excellent (100)
        # 0% same as NZ = neutral (50)
        # -3% worse than NZ = poor (0)

        if relative_change >= 0.03:
            score = 100
        elif relative_change >= 0:
            score = 50 + (relative_change / 0.03) * 50
        elif relative_change >= -0.03:
            score = 50 + (relative_change / 0.03) * 50  # Linear from 50 to 0
        else:
            score = max(0, 50 + (relative_change / 0.03) * 50)

        return max(0, min(100, score))

    except Exception as e:
        # If PPP calculation fails, return NaN
        return np.nan


def score_net_income_proxy(cost_of_living):
    """
    Score based on cost of living (inverse proxy for net income).

    For digital nomads: lower cost = effectively higher net income.

    :param cost_of_living: Weekly cost of living
    :return: Score from 0 to 100
    """
    if pd.isna(cost_of_living):
        return np.nan

    # Benchmark: NZ cost (~1250 pw) = baseline
    # Lower cost = higher score
    # Using exponential decay

    nz_cost = 1251.70  # From data: New Zealand's cost

    if cost_of_living <= 300:
        # Very cheap (like Bangladesh ~294)
        score = 100
    elif cost_of_living <= 600:
        # Cheap (like Thailand ~622)
        score = 90 + ((600 - cost_of_living) / 300) * 10
    elif cost_of_living <= nz_cost:
        # Cheaper than NZ
        score = 50 + ((nz_cost - cost_of_living) / (nz_cost - 600)) * 40
    elif cost_of_living <= nz_cost * 1.5:
        # More expensive than NZ but not terrible
        score = 25 + ((nz_cost * 1.5 - cost_of_living) / (nz_cost * 0.5)) * 25
    else:
        # Very expensive
        score = max(0, 25 - ((cost_of_living - nz_cost * 1.5) / 1000) * 10)

    return max(0, min(100, score))


# ============================================================================
# MAIN SCORING FUNCTION
# ============================================================================

def calculate_country_scores(data_file='data/All Data by Country.csv'):
    """
    Calculate utility scores for all countries in the dataset.

    :param data_file: Path to the consolidated country data CSV
    :return: DataFrame with countries and their scores
    """
    # Load data
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    df = pd.read_csv(os.path.join(data_dir, 'All Data by Country.csv'))

    print(f"Loaded data for {len(df)} countries")

    # Calculate NZ PPP change once (for relative comparison)
    print("Calculating New Zealand PPP baseline...")
    nz_ppp_change = estimate_PPP_conversion_rate_long_term_change('New Zealand')
    print(f"NZ PPP change rate: {nz_ppp_change:.4f}")

    # Calculate individual component scores
    print("\nCalculating component scores...")

    df['score_temp_variability'] = df.apply(
        lambda row: score_temperature_variability(row['max temp'], row['min temp']),
        axis=1
    )

    df['score_temp_optimality'] = df.apply(
        lambda row: score_temperature_optimality(
            row['avg temp'], row['min temp'], row['max temp']
        ),
        axis=1
    )

    # Check if sunshine hours column exists
    if 'Sunshine Hours' in df.columns:
        df['score_sunshine'] = df['Sunshine Hours'].apply(score_sunshine_hours)
    else:
        print("WARNING: Sunshine Hours not found in dataset. Setting to NaN.")
        df['score_sunshine'] = np.nan

    df['score_density'] = df['Density'].apply(score_population_density)
    df['score_safety'] = df['Safety Index'].apply(score_safety)
    df['score_corruption'] = df['CPI score 2020'].apply(score_corruption)
    df['score_healthcare'] = df['Health Care Index'].apply(score_healthcare)
    df['score_air_purity'] = df['Pollution Index'].apply(score_air_purity)
    df['score_freedom'] = df['Score'].apply(score_freedom)  # Freedom score column

    print("Calculating PPP scores (this may take a moment)...")
    df['score_ppp'] = df['Country'].apply(
        lambda country: score_ppp_change(country, nz_ppp_change)
    )

    df['score_income_proxy'] = df['Cost of Living pw'].apply(score_net_income_proxy)

    # Calculate weighted composite score
    print("\nCalculating weighted composite scores...")

    # Normalize weights
    active_weights = WEIGHTS.copy()

    # If sunshine hours not available, redistribute its weight
    if 'Sunshine Hours' not in df.columns or df['score_sunshine'].isna().all():
        print("Redistributing sunshine hours weight to other climate factors...")
        sunshine_weight = active_weights.pop('sunshine_hours')
        # Give extra weight to temperature factors
        active_weights['temperature_variability'] += sunshine_weight / 2
        active_weights['temperature_optimality'] += sunshine_weight / 2

    total_weight = sum(active_weights.values())
    normalized_weights = {k: v / total_weight for k, v in active_weights.items()}

    print("\nNormalized weights:")
    for factor, weight in normalized_weights.items():
        print(f"  {factor}: {weight:.3f}")

    # Calculate composite score
    df['utility_score'] = 0

    score_columns = {
        'temperature_variability': 'score_temp_variability',
        'temperature_optimality': 'score_temp_optimality',
        'sunshine_hours': 'score_sunshine',
        'population_density': 'score_density',
        'safety': 'score_safety',
        'corruption': 'score_corruption',
        'healthcare': 'score_healthcare',
        'air_purity': 'score_air_purity',
        'freedom': 'score_freedom',
        'ppp_change': 'score_ppp',
        'net_income_proxy': 'score_income_proxy',
    }

    for factor, col in score_columns.items():
        if factor in normalized_weights and col in df.columns:
            # Only include non-NaN values in weighted sum
            df['utility_score'] += df[col].fillna(0) * normalized_weights[factor]

    # Count how many factors each country has data for
    df['data_completeness'] = df[[col for col in score_columns.values() if col in df.columns]].notna().sum(axis=1)

    # Filter countries with sufficient data (at least 7 out of 11 factors)
    min_factors = 7
    df_complete = df[df['data_completeness'] >= min_factors].copy()

    print(f"\nFiltered to {len(df_complete)} countries with at least {min_factors} data factors")

    # Sort by utility score
    df_complete = df_complete.sort_values('utility_score', ascending=False)

    return df_complete


def print_top_countries(df, n=20):
    """
    Print the top N countries with their scores.

    :param df: DataFrame with scored countries
    :param n: Number of top countries to display
    """
    print(f"\n{'='*80}")
    print(f"TOP {n} COUNTRIES BY UTILITY SCORE")
    print(f"{'='*80}\n")

    columns_to_show = [
        'Country', 'utility_score', 'avg temp', 'max temp',
        'Safety Index', 'CPI score 2020', 'Cost of Living pw',
        'data_completeness'
    ]

    # Add sunshine if available
    if 'Sunshine Hours' in df.columns:
        columns_to_show.insert(4, 'Sunshine Hours')

    top_n = df.head(n)[columns_to_show]

    for idx, row in top_n.iterrows():
        print(f"{row.name + 1}. {row['Country']}")
        print(f"   Utility Score: {row['utility_score']:.1f}/100")
        print(f"   Avg Temp: {row['avg temp']:.1f}°C | Max: {row['max temp']:.1f}°C")
        if 'Sunshine Hours' in row:
            print(f"   Sunshine: {row['Sunshine Hours']:.0f} hrs/year")
        print(f"   Safety: {row['Safety Index']:.1f} | Corruption: {row['CPI score 2020']:.0f}")
        print(f"   Cost of Living: ${row['Cost of Living pw']:.0f}/week")
        print(f"   Data Completeness: {row['data_completeness']:.0f}/11 factors")
        print()


def save_ranked_countries(df, output_file='Ranked Countries by Utility.csv'):
    """
    Save the ranked countries to a CSV file.

    :param df: DataFrame with scored countries
    :param output_file: Output CSV file path
    """
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    output_path = os.path.join(data_dir, output_file)

    df.to_csv(output_path, index=False)
    print(f"Saved ranked countries to: {output_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("="*80)
    print("PERSONALIZED COUNTRY UTILITY SCORING")
    print("="*80)

    # Calculate scores
    df_ranked = calculate_country_scores()

    # Print top 20
    print_top_countries(df_ranked, n=20)

    # Also print your current benchmark countries
    benchmark_countries = ['New Zealand', 'Spain', 'Portugal', 'Georgia', 'Uruguay']
    print(f"\n{'='*80}")
    print("BENCHMARK COUNTRIES")
    print(f"{'='*80}\n")

    for country in benchmark_countries:
        country_data = df_ranked[df_ranked['Country'] == country]
        if len(country_data) > 0:
            rank = country_data.index[0] + 1
            score = country_data['utility_score'].values[0]
            print(f"{country}: Rank #{rank}, Score: {score:.1f}/100")
        else:
            print(f"{country}: Not found in dataset")

    # Save results
    save_ranked_countries(df_ranked)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
