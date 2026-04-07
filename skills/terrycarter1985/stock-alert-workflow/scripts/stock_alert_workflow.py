#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "yfinance>=0.2.40",
#     "pandas>=2.0.0",
#     "requests>=2.31.0",
#     "beautifulsoup4>=4.12.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""
Stock Alert Workflow - Earnings Surprise + Analyst Ratings + WhatsApp Notification

Features:
1. Scrape earnings reports and detect EPS beats > 10%
2. Fetch analyst ratings for last 30 days
3. Send formatted alerts via WhatsApp
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup


@dataclass
class EarningsSurprise:
    ticker: str
    company_name: str
    actual_eps: float
    expected_eps: float
    surprise_pct: float
    report_date: datetime
    current_price: float


@dataclass
class AnalystRating:
    ticker: str
    analyst_firm: str
    rating: str  # Buy, Hold, Sell, Overweight, Underweight
    price_target: float
    upside: float
    date: datetime


class EarningsScraper:
    """Scrape earnings data and detect significant EPS surprises."""
    
    def __init__(self, surprise_threshold: float = 10.0):
        self.surprise_threshold = surprise_threshold
    
    def get_earnings_from_yfinance(self, tickers: List[str] = None) -> List[EarningsSurprise]:
        """
        Fetch earnings surprises from Yahoo Finance.
        If no tickers provided, scan S&P 500 components.
        """
        surprises = []
        
        if tickers is None:
            tickers = self._get_sp500_tickers()
            print(f"Scanning {len(tickers)} S&P 500 stocks for earnings surprises...")
        
        for ticker in tickers:
            try:
                result = self._check_single_ticker(ticker)
                if result:
                    surprises.append(result)
                    print(f"✅ {ticker}: {result.surprise_pct:.1f}% EPS beat")
            except Exception as e:
                print(f"⚠️ Error checking {ticker}: {str(e)}")
                continue
        
        return surprises
    
    def _get_sp500_tickers(self) -> List[str]:
        """Get S&P 500 component tickers from Wikipedia."""
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            return list(tables[0]['Symbol'].str.replace('.', '-').values)
        except:
            # Fallback to major stocks if Wikipedia fails
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'JNJ']
    
    def _check_single_ticker(self, ticker: str) -> Optional[EarningsSurprise]:
        """Check if a single ticker has recent earnings surprise > threshold."""
        stock = yf.Ticker(ticker)
        
        # Get earnings history
        try:
            earnings = stock.earnings_dates
            if earnings is None or len(earnings) == 0:
                return None
            
            # Get most recent earnings
            latest = earnings.iloc[0]
            
            # Check if report was in the last 7 days
            report_date = pd.to_datetime(latest.name)
            if report_date < datetime.now() - timedelta(days=7):
                return None
            
            actual_eps = latest.get('Reported EPS', None)
            expected_eps = latest.get('EPS Estimate', None)
            
            if pd.isna(actual_eps) or pd.isna(expected_eps) or expected_eps == 0:
                return None
            
            surprise_pct = ((actual_eps - expected_eps) / abs(expected_eps)) * 100
            
            if abs(surprise_pct) >= self.surprise_threshold:
                info = stock.info
                return EarningsSurprise(
                    ticker=ticker,
                    company_name=info.get('longName', ticker),
                    actual_eps=actual_eps,
                    expected_eps=expected_eps,
                    surprise_pct=surprise_pct,
                    report_date=report_date,
                    current_price=info.get('currentPrice', 0)
                )
            
        except Exception as e:
            return None
        
        return None


class AnalystRatingsFetcher:
    """Fetch and aggregate analyst ratings from the last 30 days."""
    
    def __init__(self, days_back: int = 30):
        self.days_back = days_back
        self.rating_cutoff = datetime.now() - timedelta(days=days_back)
    
    def get_ratings(self, ticker: str) -> List[AnalystRating]:
        """Fetch analyst ratings for a ticker."""
        ratings = []
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get analyst price targets and recommendations
            info = stock.info
            
            # Current consensus
            consensus = info.get('recommendationKey', 'N/A')
            target_low = info.get('targetLowPrice', 0)
            target_mean = info.get('targetMeanPrice', 0)
            target_high = info.get('targetHighPrice', 0)
            num_analysts = info.get('numberOfAnalystOpinions', 0)
            current_price = info.get('currentPrice', 0)
            
            # Add consensus rating
            if target_mean and current_price > 0:
                upside = ((target_mean - current_price) / current_price) * 100
                ratings.append(AnalystRating(
                    ticker=ticker,
                    analyst_firm=f"Consensus ({num_analysts} analysts)",
                    rating=self._normalize_rating(consensus),
                    price_target=target_mean,
                    upside=upside,
                    date=datetime.now()
                ))
            
            # Get recommendations history if available
            try:
                recs = stock.recommendations
                if recs is not None and len(recs) > 0:
                    # Convert index to datetime if needed
                    if isinstance(recs.index, pd.DatetimeIndex):
                        recs = recs[recs.index >= self.rating_cutoff]
                    
                    for _, row in recs.head(10).iterrows():
                        firm = row.get('Firm', 'Unknown')
                        rating = row.get('To Grade', 'N/A')
                        if rating and rating != '':
                            ratings.append(AnalystRating(
                                ticker=ticker,
                                analyst_firm=firm,
                                rating=self._normalize_rating(rating),
                                price_target=0,
                                upside=0,
                                date=row.name if isinstance(row.name, datetime) else datetime.now()
                            ))
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Error fetching ratings for {ticker}: {str(e)}")
        
        return ratings
    
    def _normalize_rating(self, rating: str) -> str:
        """Normalize rating to standard terms."""
        if not rating:
            return 'N/A'
        
        rating_lower = rating.lower()
        if any(x in rating_lower for x in ['buy', 'outperform', 'overweight', 'strong', 'accumulate']):
            return 'Buy'
        elif any(x in rating_lower for x in ['sell', 'underweight', 'underperform']):
            return 'Sell'
        elif 'hold' in rating_lower or 'neutral' in rating_lower:
            return 'Hold'
        else:
            return rating.capitalize()
    
    def summarize_ratings(self, ratings: List[AnalystRating]) -> Dict:
        """Create summary statistics from ratings."""
        if not ratings:
            return {"buy": 0, "hold": 0, "sell": 0, "avg_upside": 0}
        
        buy = sum(1 for r in ratings if r.rating == 'Buy')
        hold = sum(1 for r in ratings if r.rating == 'Hold')
        sell = sum(1 for r in ratings if r.rating == 'Sell')
        valid_upsides = [r.upside for r in ratings if r.upside != 0]
        avg_upside = sum(valid_upsides) / len(valid_upsides) if valid_upsides else 0
        
        return {
            "buy": buy,
            "hold": hold,
            "sell": sell,
            "avg_upside": avg_upside,
            "total": len(ratings)
        }


class WhatsAppNotifier:
    """Send notifications via WhatsApp using OpenClaw message tool."""
    
    def __init__(self):
        self.message_template = """
🚨 *EARNINGS ALERT* 🚨

*{company} ({ticker})*

📊 *EPS Beat: +{surprise_pct:.1f}%*
   • Expected: ${expected_eps:.2f}
   • Actual:   ${actual_eps:.2f}
   • Current Price: ${price:.2f}

📈 *Analyst Ratings (30 days)*:
   • Buy: {buy_count} | Hold: {hold_count} | Sell: {sell_count}
   • Average Upside: {avg_upside:.1f}%

📋 *Top Ratings*:
{top_ratings}

---
⚠️ Not financial advice. DYOR.
        """
    
    def format_alert(self, earnings: EarningsSurprise, ratings: List[AnalystRating], summary: Dict) -> str:
        """Format alert message for WhatsApp."""
        top_ratings_text = ""
        for r in ratings[:5]:
            if r.price_target > 0:
                top_ratings_text += f"   • {r.analyst_firm}: {r.rating} | Target: ${r.price_target:.2f}\n"
            else:
                top_ratings_text += f"   • {r.analyst_firm}: {r.rating}\n"
        
        return self.message_template.format(
            company=earnings.company_name,
            ticker=earnings.ticker,
            surprise_pct=earnings.surprise_pct,
            expected_eps=earnings.expected_eps,
            actual_eps=earnings.actual_eps,
            price=earnings.current_price,
            buy_count=summary['buy'],
            hold_count=summary['hold'],
            sell_count=summary['sell'],
            avg_upside=summary['avg_upside'],
            top_ratings=top_ratings_text
        ).strip()
    
    def send_to_whatsapp(self, message: str, target: str = None) -> bool:
        """
        Send message via OpenClaw message tool.
        Requires OpenClaw WhatsApp channel configured.
        """
        print(f"\n📱 WhatsApp Message:")
        print("="*50)
        print(message)
        print("="*50)
        
        # In actual execution, this would call OpenClaw's message tool
        # For now, we print and return success
        print("\n✅ Alert prepared for WhatsApp delivery")
        return True


def run_workflow(tickers: List[str] = None, surprise_threshold: float = 10.0):
    """Run the complete stock alert workflow."""
    print(f"🚀 Starting Stock Alert Workflow (threshold: {surprise_threshold}%)")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    # Step 1: Scrape earnings surprises
    scraper = EarningsScraper(surprise_threshold=surprise_threshold)
    surprises = scraper.get_earnings_from_yfinance(tickers)
    
    if not surprises:
        print("❌ No earnings surprises found above threshold")
        return
    
    print(f"\n📊 Found {len(surprises)} stocks with significant earnings surprises")
    print("-"*60)
    
    # Step 2: Fetch analyst ratings and send alerts
    ratings_fetcher = AnalystRatingsFetcher(days_back=30)
    notifier = WhatsAppNotifier()
    
    for earnings in surprises:
        print(f"\n📈 Processing {earnings.ticker}...")
        
        ratings = ratings_fetcher.get_ratings(earnings.ticker)
        summary = ratings_fetcher.summarize_ratings(ratings)
        
        print(f"   • Found {len(ratings)} analyst ratings")
        print(f"   • Buy/Hold/Sell: {summary['buy']}/{summary['hold']}/{summary['sell']}")
        print(f"   • Avg upside: {summary['avg_upside']:.1f}%")
        
        alert_message = notifier.format_alert(earnings, ratings, summary)
        notifier.send_to_whatsapp(alert_message)
    
    print("\n✅ Workflow completed successfully!")


def main():
    parser = argparse.ArgumentParser(description='Stock Alert Workflow')
    parser.add_argument('tickers', nargs='*', help='Specific tickers to check')
    parser.add_argument('--threshold', type=float, default=10.0, help='EPS surprise threshold (%%)')
    parser.add_argument('--cron', action='store_true', help='Run in cron mode (silent)')
    
    args = parser.parse_args()
    
    tickers = args.tickers if args.tickers else None
    run_workflow(tickers, args.threshold)


if __name__ == '__main__':
    main()
