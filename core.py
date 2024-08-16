import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import exa_py  # Assuming exa_py is installed
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv


def get_tweet_embed(tweet_url):
    """Fetches and returns the HTML embed code for a tweet URL, or None on error."""
    oembed_url = f"https://publish.twitter.com/oembed?url={tweet_url}&hide_thread=true"
    response = requests.get(oembed_url)
    if response.status_code == 200:
        return response.json()['html']
    else:
        print(f"Error fetching tweet embed: {response.status_code}")
        return None


def analyze_sentiment(text):
    """Analyzes the sentiment of the given text."""
    nltk.download('vader_lexicon')  # Download Vader lexicon (if not already downloaded)
    sentiment_analyzer = SentimentIntensityAnalyzer()
    sentiment = sentiment_analyzer.polarity_scores(text)
    return sentiment


def main():
    """Executes the search and displays results."""
    load_dotenv()  # Load environment variables from .env file

    EXA_API_KEY = os.environ.get('SECRET_KEY')  # Assuming API key stored in a variable named EXA_API_KEY
    if not EXA_API_KEY:
        print("Error: Missing Exa API key. Please set the EXA_API_KEY environment variable.")
        return

    query = "here's an exciting breakthrough in artificial intelligence:"
    include_domains = ["twitter.com", "x.com"]
    num_results = 10

    # Calculate the date for one month ago
    one_month_ago = (datetime.now() - timedelta(days=30)).isoformat()

    # Create Exa instance with your API key
    exa = exa_py.Exa(api_key=EXA_API_KEY)

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
    print(f"Found {len(results)} tweets:\n")

    for i, result in enumerate(results, 1):
        print(f"Tweet {i}:")
        print(f"URL: {result.url}")
        print(f"Published Date: {result.published_date}")
        print(f"Score: {result.score}")

        # Sentiment analysis
        tweet_text = result.text
        sentiment = analyze_sentiment(tweet_text)
        print(f"Sentiment: {sentiment}")

        # Get and display tweet embed (if available)
        embed_html = get_tweet_embed(result.url)
        if embed_html:
            print(embed_html)  # Assuming you have a way to display HTML content
        else:
            print("Sorry, unable to load tweet embed.")

        print("\n" + "-" * 50 + "\n")

    print("Thanks!")


if __name__ == "__main__":
    main()
