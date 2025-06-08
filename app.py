from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from scipy import stats

app = Flask(__name__)

def calculate_correlation(uk_returns, china_returns):
    """Calculate correlation between UK and Chinese returns"""
    if len(uk_returns) != len(china_returns):
        min_len = min(len(uk_returns), len(china_returns))
        uk_returns = uk_returns[-min_len:]
        china_returns = china_returns[-min_len:]
    
    correlation = np.corrcoef(uk_returns, china_returns)[0, 1]
    return correlation

def calculate_hedge_ratio(uk_volatility, china_volatility, correlation):
    """Calculate optimal hedge ratio using variance minimization"""
    hedge_ratio = (uk_volatility / china_volatility) * correlation
    return hedge_ratio

def fetch_stock_data(ticker, period='6mo'):
    """Fetch historical stock data"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        if data.empty:
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_returns(price_data):
    """Calculate daily returns from price data"""
    returns = price_data['Close'].pct_change().dropna()
    return returns

def calculate_china_exposure(uk_ticker):
    """Estimate China exposure based on sector and company profile"""
    # This is a simplified estimation - in reality, you'd use more sophisticated methods
    china_exposed_sectors = {
        'Technology': 0.3,
        'Basic Materials': 0.4,
        'Consumer Cyclical': 0.25,
        'Industrials': 0.35,
        'Energy': 0.2,
        'Financial Services': 0.15,
        'Healthcare': 0.1,
        'Consumer Defensive': 0.1,
        'Utilities': 0.05,
        'Real Estate': 0.1,
        'Communication Services': 0.2
    }
    
    try:
        stock = yf.Ticker(uk_ticker)
        info = stock.info
        sector = info.get('sector', 'Unknown')
        
        # Base exposure from sector
        base_exposure = china_exposed_sectors.get(sector, 0.15)
        
        # Adjust based on market cap (larger companies often have more global exposure)
        market_cap = info.get('marketCap', 0)
        if market_cap > 100e9:  # > 100B
            base_exposure *= 1.3
        elif market_cap > 10e9:  # > 10B
            base_exposure *= 1.1
            
        return min(base_exposure, 0.5)  # Cap at 50% exposure
    except:
        return 0.15  # Default exposure

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_hedge', methods=['POST'])
def calculate_hedge():
    try:
        data = request.json
        uk_shares = data.get('uk_shares', [])
        china_hedges = data.get('china_hedges', [])
        position_values = data.get('position_values', {})
        
        results = {
            'uk_portfolio': [],
            'hedge_recommendations': [],
            'total_china_exposure': 0,
            'errors': []
        }
        
        # Analyze UK portfolio
        total_portfolio_value = 0
        weighted_china_exposure = 0
        
        for share in uk_shares:
            ticker = share['ticker']
            value = float(position_values.get(ticker, 0))
            
            # Fetch data
            uk_data = fetch_stock_data(ticker)
            if uk_data is None:
                results['errors'].append(f"Could not fetch data for {ticker}")
                continue
                
            # Calculate returns and volatility
            returns = calculate_returns(uk_data)
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            # Estimate China exposure
            china_exposure = calculate_china_exposure(ticker)
            china_exposed_value = value * china_exposure
            
            results['uk_portfolio'].append({
                'ticker': ticker,
                'value': value,
                'volatility': round(volatility * 100, 2),
                'china_exposure': round(china_exposure * 100, 2),
                'china_exposed_value': round(china_exposed_value, 2)
            })
            
            total_portfolio_value += value
            weighted_china_exposure += china_exposed_value
        
        results['total_china_exposure'] = round(weighted_china_exposure, 2)
        
        # Calculate hedge recommendations for each Chinese instrument
        for hedge in china_hedges:
            hedge_ticker = hedge['ticker']
            
            # Fetch Chinese stock data
            china_data = fetch_stock_data(hedge_ticker)
            if china_data is None:
                results['errors'].append(f"Could not fetch data for {hedge_ticker}")
                continue
            
            china_returns = calculate_returns(china_data)
            china_volatility = china_returns.std() * np.sqrt(252)
            
            # Calculate average correlation with UK portfolio
            correlations = []
            for uk_share in results['uk_portfolio']:
                uk_ticker = uk_share['ticker']
                uk_data = fetch_stock_data(uk_ticker)
                if uk_data is not None:
                    uk_returns = calculate_returns(uk_data)
                    corr = calculate_correlation(uk_returns.values, china_returns.values)
                    if not np.isnan(corr):
                        correlations.append(corr)
            
            avg_correlation = np.mean(correlations) if correlations else 0
            
            # Calculate hedge ratio
            portfolio_volatility = np.mean([share['volatility']/100 for share in results['uk_portfolio']])
            hedge_ratio = calculate_hedge_ratio(portfolio_volatility, china_volatility, avg_correlation)
            
            # Calculate hedge size
            hedge_notional = weighted_china_exposure * abs(hedge_ratio)
            
            # Determine hedge effectiveness
            effectiveness = abs(avg_correlation) * 100
            
            results['hedge_recommendations'].append({
                'ticker': hedge_ticker,
                'correlation': round(avg_correlation, 3),
                'volatility': round(china_volatility * 100, 2),
                'hedge_ratio': round(hedge_ratio, 3),
                'hedge_notional': round(hedge_notional, 2),
                'effectiveness': round(effectiveness, 2),
                'direction': 'SHORT' if hedge_ratio > 0 else 'LONG'
            })
        
        # Sort recommendations by effectiveness
        results['hedge_recommendations'].sort(key=lambda x: x['effectiveness'], reverse=True)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='192.168.2.244', port=1850, debug=True)