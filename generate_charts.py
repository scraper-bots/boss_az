#!/usr/bin/env python3
"""
Boss.az Job Market Analysis - Business Intelligence Dashboard
Generates comprehensive business insights and visualizations from job seeker data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import re
from collections import Counter
import numpy as np

warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Configure matplotlib for better looking charts
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

class JobMarketAnalyzer:
    def __init__(self, data_path):
        """Load and prepare the resume data for analysis"""
        print("Loading job market data...")
        self.df = pd.read_csv(data_path)
        print(f"Loaded {len(self.df):,} resume records")
        self.prepare_data()

    def prepare_data(self):
        """Clean and prepare data for analysis"""
        print("Preparing data for analysis...")

        # Clean salary data - extract numeric values
        self.df['salary_clean'] = self.df['salary'].apply(self._extract_salary)

        # Clean experience data
        self.df['experience_years'] = self.df['experience'].apply(self._extract_experience_years)

        # Clean age
        self.df['age_clean'] = pd.to_numeric(self.df['age'].str.extract(r'(\d+)')[0], errors='coerce')

        # Clean view count
        self.df['view_count_clean'] = pd.to_numeric(self.df['view_count'], errors='coerce')

        # Clean city names
        self.df['city_clean'] = self.df['city'].fillna('Unknown').str.strip()

        # Extract job categories from titles
        self.df['job_category'] = self.df['title'].apply(self._categorize_job)

        print("Data preparation complete!")

    def _extract_salary(self, salary_str):
        """Extract numeric salary value from string"""
        if pd.isna(salary_str):
            return None
        # Extract numbers from salary string
        numbers = re.findall(r'\d+', str(salary_str))
        if numbers:
            return int(numbers[0])
        return None

    def _extract_experience_years(self, exp_str):
        """Convert experience categories to numeric years (midpoint)"""
        if pd.isna(exp_str):
            return None
        exp_str = str(exp_str).lower()

        if 'təcrübəsiz' in exp_str or 'без опыта' in exp_str or 'no experience' in exp_str:
            return 0
        elif '1 ildən az' in exp_str or 'менее года' in exp_str:
            return 0.5
        elif '1 ildən 3' in exp_str:
            return 2
        elif '3 ildən 5' in exp_str:
            return 4
        elif '5 ildən artıq' in exp_str or 'более 5' in exp_str:
            return 6
        return None

    def _categorize_job(self, title):
        """Categorize jobs into major categories"""
        if pd.isna(title):
            return 'Other'

        title_lower = str(title).lower()

        # Define category keywords
        categories = {
            'IT & Technology': ['proqramçı', 'developer', 'programmer', 'it', 'sistem', 'designer', 'dizayner'],
            'Finance & Accounting': ['mühasib', 'maliyyə', 'accountant', 'finance', 'bank'],
            'Sales & Marketing': ['satış', 'marketing', 'sales', 'reklam', 'menecer'],
            'HR & Administration': ['kadr', 'hr', 'human resource', 'insan resurs', 'ofis'],
            'Engineering': ['mühəndis', 'engineer', 'texniki'],
            'Healthcare': ['həkim', 'tibb', 'medical', 'doctor', 'nurse'],
            'Education': ['müəllim', 'teacher', 'təhsil', 'education'],
            'Logistics': ['logistika', 'logistics', 'driver', 'sürücü'],
            'Customer Service': ['müştəri', 'customer', 'operator', 'call center']
        }

        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category

        return 'Other'

    def generate_all_charts(self):
        """Generate all business intelligence charts"""
        print("\nGenerating business intelligence charts...")

        self.chart_1_salary_by_experience()
        self.chart_2_top_job_categories()
        self.chart_3_education_distribution()
        self.chart_4_gender_distribution()
        self.chart_5_age_distribution()
        self.chart_6_city_distribution()
        self.chart_7_experience_distribution()
        self.chart_8_salary_distribution()
        self.chart_9_view_count_analysis()
        self.chart_10_salary_by_category()
        self.chart_11_experience_by_category()
        self.chart_12_monthly_activity_trends()

        print("\nAll charts generated successfully in charts/ directory!")

    def chart_1_salary_by_experience(self):
        """Salary expectations vs experience level"""
        plt.figure(figsize=(12, 6))

        # Filter data with valid salary and experience
        data = self.df[self.df['salary_clean'].notna() & self.df['experience_years'].notna()]

        if len(data) > 0:
            # Group by experience and calculate average salary
            exp_salary = data.groupby('experience_years')['salary_clean'].agg(['mean', 'median', 'count'])
            exp_salary = exp_salary[exp_salary['count'] >= 10]  # At least 10 samples

            # Create bar chart
            x = np.arange(len(exp_salary))
            width = 0.35

            fig, ax = plt.subplots(figsize=(12, 6))
            bars1 = ax.bar(x - width/2, exp_salary['mean'], width, label='Average Salary', alpha=0.8)
            bars2 = ax.bar(x + width/2, exp_salary['median'], width, label='Median Salary', alpha=0.8)

            ax.set_xlabel('Years of Experience', fontweight='bold')
            ax.set_ylabel('Salary Expectation (AZN)', fontweight='bold')
            ax.set_title('Salary Expectations by Experience Level', fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels([f'{int(yr)} years' if yr > 0 else 'No exp.' for yr in exp_salary.index])
            ax.legend()
            ax.grid(axis='y', alpha=0.3)

            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=9)

            plt.tight_layout()
            plt.savefig('charts/01_salary_by_experience.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✓ Generated: Salary by Experience chart")

    def chart_2_top_job_categories(self):
        """Most in-demand job categories"""
        plt.figure(figsize=(12, 7))

        # Count job categories
        category_counts = self.df['job_category'].value_counts().head(12)

        # Create horizontal bar chart
        colors = sns.color_palette("husl", len(category_counts))
        bars = plt.barh(range(len(category_counts)), category_counts.values, color=colors, alpha=0.8)

        plt.yticks(range(len(category_counts)), category_counts.index)
        plt.xlabel('Number of Job Seekers', fontweight='bold')
        plt.title('Top Job Categories in the Market', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, category_counts.values)):
            plt.text(value, i, f' {value:,}', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig('charts/02_top_job_categories.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Top Job Categories chart")

    def chart_3_education_distribution(self):
        """Education level distribution"""
        plt.figure(figsize=(10, 6))

        # Count education levels
        edu_counts = self.df['education'].value_counts().head(8)

        # Create bar chart
        colors = sns.color_palette("Set2", len(edu_counts))
        bars = plt.bar(range(len(edu_counts)), edu_counts.values, color=colors, alpha=0.8)

        plt.xticks(range(len(edu_counts)), edu_counts.index, rotation=45, ha='right')
        plt.ylabel('Number of Candidates', fontweight='bold')
        plt.title('Education Level Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig('charts/03_education_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Education Distribution chart")

    def chart_4_gender_distribution(self):
        """Gender distribution in job market"""
        plt.figure(figsize=(10, 6))

        # Count gender distribution
        gender_counts = self.df['gender'].value_counts()

        # Create bar chart
        colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
        bars = plt.bar(range(len(gender_counts)), gender_counts.values,
                       color=colors[:len(gender_counts)], alpha=0.8, width=0.6)

        plt.xticks(range(len(gender_counts)), gender_counts.index)
        plt.ylabel('Number of Job Seekers', fontweight='bold')
        plt.title('Gender Distribution in Job Market', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)

        # Add value labels and percentages
        total = gender_counts.sum()
        for bar, value in zip(bars, gender_counts.values):
            height = bar.get_height()
            percentage = (value / total) * 100
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value):,}\n({percentage:.1f}%)',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        plt.tight_layout()
        plt.savefig('charts/04_gender_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Gender Distribution chart")

    def chart_5_age_distribution(self):
        """Age distribution of job seekers"""
        plt.figure(figsize=(12, 6))

        # Filter valid ages
        ages = self.df['age_clean'].dropna()
        ages = ages[(ages >= 18) & (ages <= 65)]

        # Create histogram
        plt.hist(ages, bins=15, color='#3498db', alpha=0.7, edgecolor='black')
        plt.xlabel('Age', fontweight='bold')
        plt.ylabel('Number of Candidates', fontweight='bold')
        plt.title('Age Distribution of Job Seekers', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)

        # Add median line
        median_age = ages.median()
        plt.axvline(median_age, color='red', linestyle='--', linewidth=2,
                   label=f'Median Age: {median_age:.0f}')
        plt.legend()

        plt.tight_layout()
        plt.savefig('charts/05_age_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Age Distribution chart")

    def chart_6_city_distribution(self):
        """Geographic distribution of candidates"""
        plt.figure(figsize=(12, 7))

        # Count top cities
        city_counts = self.df['city_clean'].value_counts().head(15)

        # Create horizontal bar chart
        colors = sns.color_palette("coolwarm", len(city_counts))
        bars = plt.barh(range(len(city_counts)), city_counts.values, color=colors, alpha=0.8)

        plt.yticks(range(len(city_counts)), city_counts.index)
        plt.xlabel('Number of Candidates', fontweight='bold')
        plt.title('Geographic Distribution - Top Cities', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, city_counts.values)):
            plt.text(value, i, f' {value:,}', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig('charts/06_city_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: City Distribution chart")

    def chart_7_experience_distribution(self):
        """Experience level distribution"""
        plt.figure(figsize=(10, 6))

        # Count experience levels
        exp_counts = self.df['experience'].value_counts()

        # Create bar chart
        colors = sns.color_palette("viridis", len(exp_counts))
        bars = plt.bar(range(len(exp_counts)), exp_counts.values, color=colors, alpha=0.8)

        plt.xticks(range(len(exp_counts)), exp_counts.index, rotation=45, ha='right')
        plt.ylabel('Number of Candidates', fontweight='bold')
        plt.title('Experience Level Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)

        # Add value labels and percentages
        total = exp_counts.sum()
        for bar, value in zip(bars, exp_counts.values):
            height = bar.get_height()
            percentage = (value / total) * 100
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value):,}\n({percentage:.1f}%)',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig('charts/07_experience_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Experience Distribution chart")

    def chart_8_salary_distribution(self):
        """Salary expectation distribution"""
        plt.figure(figsize=(12, 6))

        # Filter valid salaries (remove outliers)
        salaries = self.df['salary_clean'].dropna()
        salaries = salaries[(salaries >= 200) & (salaries <= 5000)]

        # Create histogram
        plt.hist(salaries, bins=30, color='#2ecc71', alpha=0.7, edgecolor='black')
        plt.xlabel('Salary Expectation (AZN)', fontweight='bold')
        plt.ylabel('Number of Candidates', fontweight='bold')
        plt.title('Salary Expectation Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)

        # Add statistical lines
        median_salary = salaries.median()
        mean_salary = salaries.mean()
        plt.axvline(median_salary, color='red', linestyle='--', linewidth=2,
                   label=f'Median: {median_salary:.0f} AZN')
        plt.axvline(mean_salary, color='orange', linestyle='--', linewidth=2,
                   label=f'Average: {mean_salary:.0f} AZN')
        plt.legend()

        plt.tight_layout()
        plt.savefig('charts/08_salary_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Salary Distribution chart")

    def chart_9_view_count_analysis(self):
        """Resume visibility analysis"""
        plt.figure(figsize=(12, 6))

        # Filter valid view counts
        views = self.df['view_count_clean'].dropna()
        views = views[views <= views.quantile(0.95)]  # Remove top 5% outliers

        # Create histogram
        plt.hist(views, bins=30, color='#e74c3c', alpha=0.7, edgecolor='black')
        plt.xlabel('Number of Views', fontweight='bold')
        plt.ylabel('Number of Resumes', fontweight='bold')
        plt.title('Resume Visibility Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)

        # Add statistical lines
        median_views = views.median()
        mean_views = views.mean()
        plt.axvline(median_views, color='blue', linestyle='--', linewidth=2,
                   label=f'Median: {median_views:.0f} views')
        plt.axvline(mean_views, color='green', linestyle='--', linewidth=2,
                   label=f'Average: {mean_views:.0f} views')
        plt.legend()

        plt.tight_layout()
        plt.savefig('charts/09_view_count_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: View Count Analysis chart")

    def chart_10_salary_by_category(self):
        """Average salary by job category"""
        plt.figure(figsize=(12, 7))

        # Calculate average salary by category
        data = self.df[self.df['salary_clean'].notna()]
        salary_by_cat = data.groupby('job_category')['salary_clean'].agg(['mean', 'count'])
        salary_by_cat = salary_by_cat[salary_by_cat['count'] >= 20]  # At least 20 samples
        salary_by_cat = salary_by_cat.sort_values('mean', ascending=True)

        # Create horizontal bar chart
        colors = sns.color_palette("rocket", len(salary_by_cat))
        bars = plt.barh(range(len(salary_by_cat)), salary_by_cat['mean'], color=colors, alpha=0.8)

        plt.yticks(range(len(salary_by_cat)), salary_by_cat.index)
        plt.xlabel('Average Salary Expectation (AZN)', fontweight='bold')
        plt.title('Average Salary Expectations by Job Category', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, salary_by_cat['mean'])):
            plt.text(value, i, f' {int(value)} AZN', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig('charts/10_salary_by_category.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Salary by Category chart")

    def chart_11_experience_by_category(self):
        """Experience distribution across job categories"""
        plt.figure(figsize=(14, 8))

        # Get top categories
        top_cats = self.df['job_category'].value_counts().head(8).index

        # Prepare data for stacked bar chart
        exp_data = []
        exp_levels = self.df['experience'].value_counts().index[:5]

        for cat in top_cats:
            cat_data = self.df[self.df['job_category'] == cat]
            exp_dist = cat_data['experience'].value_counts()
            exp_data.append([exp_dist.get(level, 0) for level in exp_levels])

        # Create stacked bar chart
        exp_data = np.array(exp_data).T
        x = np.arange(len(top_cats))
        colors = sns.color_palette("Set3", len(exp_levels))

        fig, ax = plt.subplots(figsize=(14, 8))
        bottom = np.zeros(len(top_cats))

        for i, (exp_level, color) in enumerate(zip(exp_levels, colors)):
            ax.bar(x, exp_data[i], bottom=bottom, label=exp_level, color=color, alpha=0.8)
            bottom += exp_data[i]

        ax.set_xlabel('Job Category', fontweight='bold')
        ax.set_ylabel('Number of Candidates', fontweight='bold')
        ax.set_title('Experience Distribution by Job Category', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(top_cats, rotation=45, ha='right')
        ax.legend(title='Experience Level', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig('charts/11_experience_by_category.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated: Experience by Category chart")

    def chart_12_monthly_activity_trends(self):
        """Monthly activity trends"""
        plt.figure(figsize=(14, 6))

        # Extract month from approval_date
        self.df['approval_month'] = pd.to_datetime(self.df['approval_date'],
                                                    format='%B %d, %Y',
                                                    errors='coerce').dt.to_period('M')

        # Count by month
        monthly_counts = self.df['approval_month'].value_counts().sort_index()
        monthly_counts = monthly_counts.tail(12)  # Last 12 months

        if len(monthly_counts) > 0:
            # Create line chart
            plt.plot(range(len(monthly_counts)), monthly_counts.values,
                    marker='o', linewidth=2, markersize=8, color='#9b59b6')
            plt.fill_between(range(len(monthly_counts)), monthly_counts.values, alpha=0.3, color='#9b59b6')

            plt.xticks(range(len(monthly_counts)),
                      [str(m) for m in monthly_counts.index],
                      rotation=45, ha='right')
            plt.ylabel('Number of New Resumes', fontweight='bold')
            plt.xlabel('Month', fontweight='bold')
            plt.title('Monthly Job Seeker Activity Trends', fontsize=16, fontweight='bold', pad=20)
            plt.grid(alpha=0.3)

            # Add value labels
            for i, value in enumerate(monthly_counts.values):
                plt.text(i, value, f'{value:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

            plt.tight_layout()
            plt.savefig('charts/12_monthly_activity_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✓ Generated: Monthly Activity Trends chart")

    def print_key_insights(self):
        """Print key business insights"""
        print("\n" + "="*70)
        print("KEY BUSINESS INSIGHTS")
        print("="*70)

        total_resumes = len(self.df)
        print(f"\n📊 Total Active Resumes: {total_resumes:,}")

        # Gender insights
        gender_dist = self.df['gender'].value_counts()
        print(f"\n👥 Gender Distribution:")
        for gender, count in gender_dist.items():
            pct = (count / total_resumes) * 100
            print(f"   {gender}: {count:,} ({pct:.1f}%)")

        # Top job categories
        print(f"\n💼 Top 5 Job Categories:")
        for i, (cat, count) in enumerate(self.df['job_category'].value_counts().head(5).items(), 1):
            pct = (count / total_resumes) * 100
            print(f"   {i}. {cat}: {count:,} ({pct:.1f}%)")

        # Salary insights
        salaries = self.df['salary_clean'].dropna()
        if len(salaries) > 0:
            print(f"\n💰 Salary Expectations:")
            print(f"   Average: {salaries.mean():.0f} AZN")
            print(f"   Median: {salaries.median():.0f} AZN")
            print(f"   Range: {salaries.min():.0f} - {salaries.max():.0f} AZN")

        # Experience insights
        print(f"\n📈 Experience Distribution:")
        for exp, count in self.df['experience'].value_counts().head(5).items():
            pct = (count / total_resumes) * 100
            print(f"   {exp}: {count:,} ({pct:.1f}%)")

        # Age insights
        ages = self.df['age_clean'].dropna()
        if len(ages) > 0:
            print(f"\n🎂 Age Demographics:")
            print(f"   Average Age: {ages.mean():.0f} years")
            print(f"   Median Age: {ages.median():.0f} years")
            print(f"   Age Range: {ages.min():.0f} - {ages.max():.0f} years")

        # Top cities
        print(f"\n🌍 Top 5 Cities:")
        for i, (city, count) in enumerate(self.df['city_clean'].value_counts().head(5).items(), 1):
            pct = (count / total_resumes) * 100
            print(f"   {i}. {city}: {count:,} ({pct:.1f}%)")

        print("\n" + "="*70)


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("BOSS.AZ JOB MARKET ANALYSIS")
    print("Business Intelligence Dashboard Generator")
    print("="*70 + "\n")

    # Load and analyze data
    analyzer = JobMarketAnalyzer('resume_scraper/resumes.csv')

    # Print key insights
    analyzer.print_key_insights()

    # Generate all charts
    analyzer.generate_all_charts()

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print("\nAll business intelligence charts have been generated.")
    print("Check the 'charts/' directory for visual insights.")
    print("\n")


if __name__ == "__main__":
    main()
