import requests
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Ch-Ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

def is_similar(target, text, threshold=0.8):
    target_len = len(target)
    max_similarity = 0

    for i in range(len(text) - target_len + 1):
        window = text[i:i + target_len]
        match_count = sum(1 for t, w in zip(target, window) if t == w)
        similarity = match_count / target_len
        max_similarity = max(max_similarity, similarity)

    return max_similarity >= threshold


url = "https://www.amazon.com/Canon-EOS-Mark-RF24-105mm-F4-7-1/dp/B0BL7X3KLV/ref=sr_1_2?crid=JSV9ZU07ABQ5&dib=eyJ2IjoiMSJ9.dERRBb4kqmUcZyXJ4z8BIyzv357NfDBMWPvREbElTYGcaMousI8i6RJnHSE4Tm-1MUPj9C-Qq1T1-jbkEWJAykiDr7icV6MlF8vaVe6vaits8j0eDOjWZuJP6Us2nASynnyCS_EkLJ00oC7bUMxR8m9-7aVibUQ9Nl_W7-aNcUCH0BejIKAev1YaH2mVVcYYx5uOkCplCgx1pNGbTHi4WwdJfV3nMjdqPH8wPXm7_FM.1aVsZqTDoauhXFhS2b5tWBOTx6H00QrOqwaNB-XJz_w&dib_tag=se&keywords=canon+camera&qid=1757870227&sprefix=canon+camer%2Caps%2C301&sr=8-2"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    html = response.text
    pattern = re.compile(r'''
        <span\s+class="a-profile-name">(.+?)</span>
        .*?
        <span\s+data-hook="review-date".*?>(.*?)</span>
        .*?
        <span\s+data-hook="review-body".*?>(.*?)</span>
    ''', re.VERBOSE | re.DOTALL)

    matches = pattern.findall(html)

    if matches:
        for match in matches:
            reviewer_name = match[0].strip()
            review_date_location = match[1].strip()
            review_body = re.sub(r'<.*?>', '', match[2])

            if is_similar("Reviewed in the United States", review_date_location):
                review_date = re.search(r'on (.+)', review_date_location).group(1).strip()
                sentiment_scores = sid.polarity_scores(review_body)
                compound_score = sentiment_scores['compound']

                if compound_score >= 0.75:
                    stars = 5
                elif compound_score >= 0.5:
                    stars = 4
                elif compound_score >= 0.25:
                    stars = 3
                elif compound_score >= 0.0:
                    stars = 2
                else:
                    stars = 1

                filled_stars = " ★ " * stars
                empty_stars = "☆" * (5 - stars)
                star_rating = filled_stars + empty_stars

                print(f"Reviewer Name: {reviewer_name}")
                print(f"Review Date: {review_date}")
                print(f"Review Body:\n{review_body}")
                print(f"Sentiment: {sentiment_scores}")
                print(f"Star Rating: {star_rating} ({stars}/5)")
                print("\n" + "-" * 100 + "\n")
    else:
        print("No reviews found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")