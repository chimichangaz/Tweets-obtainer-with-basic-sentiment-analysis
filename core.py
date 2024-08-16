from flask import Flask, render_template, request
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import exa_py  # Ensure you have the Exa API library installed

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Sentiment analysis function
def analyze_sentiment(text):
    nltk.download('vader_lexicon')  # Ensure VADER lexicon is downloaded
    sentiment_analyzer = SentimentIntensityAnalyzer()
    sentiment = sentiment_analyzer.polarity_scores(text)
    return sentiment

# Fetch tweet embed function
def get_tweet_embed(tweet_url):
    oembed_url = f"https://publish.twitter.com/oembed?url={tweet_url}&hide_thread=true"
    response = requests.get(oembed_url)
    if response.status_code == 200:
        return response.json()['html']
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
        num_results = 10
        include_domains = ["twitter.com", "x.com"]
        one_month_ago = (datetime.now() - timedelta(days=30)).isoformat()

        # Fetch API key from environment variables
        EXA_API_KEY = os.environ.get('SECRET_KEY')
        if not EXA_API_KEY:
            return "Error: Missing API key."

        # Create Exa instance with your API key
        exa = exa_py.Exa(api_key=EXA_API_KEY)
        try:
            # Execute the search
            search_response = exa.search_and_contents(
                query,
                include_domains=include_domains,
                num_results=num_results,
                use_autoprompt=True,
                text=True,
                start_published_date=one_month_ago
            )
            results = search_response.results

            # Process results
            analyzed_results = []
            for result in results:
                sentiment = analyze_sentiment(result.text)
                embed_html = get_tweet_embed(result.url)
                analyzed_results.append({
                    'url': result.url,
                    'published_date': result.published_date,
                    'sentiment': sentiment,
                    'embed_html': embed_html
                })
            return render_template('results.html', results=analyzed_results)
        except Exception as e:
            return f"An error occurred: {e}"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
