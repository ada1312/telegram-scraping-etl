from telethon import TelegramClient
import asyncio
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from config import load_config

config = load_config()

# Replace these with your own values
api_id = config.api_id
api_hash = config.api_hash
chat_username = config.chat_username
sample_size = 1000

async def all_chats(chat_username, sample_size):
    async with TelegramClient('session', api_id, api_hash) as client:
        chat_info = await client.get_entity(chat_username)
        messages = await client.get_messages(entity=chat_info, limit=sample_size)
        return {"messages": messages, "channel": chat_info}

async def main_test():
    results = await all_chats(chat_username, sample_size)
    print("Keys in results:", results.keys())
    print("Channel info:", results["channel"].to_dict())
    print("Number of messages:", len(results["messages"]))

    # Convert messages to DataFrame
    df = pd.DataFrame([
        {
            'date': m.date,
            'text': m.text if m.text else '',  # Handle potential None values
            'from_user': m.from_id.user_id if m.from_id else None
        } for m in results["messages"]
    ])

    # Save to JSON
    df.to_json('telegram_sample.json', orient='records', date_format='iso')

    # Date analysis
    df["just_date"] = pd.to_datetime(df.date).dt.date
    print(f"Date range: {df.just_date.min()} - {df.just_date.max()}")

    # Daily frequency of messages
    daily_count = df.groupby("just_date").size().reset_index(name="freq")
    print("Daily message count:")
    print(daily_count.head())

    # Plot frequency of messages
    plt.figure(figsize=(20, 10))
    daily_count.plot(x="just_date", y="freq", xlabel="Date")
    plt.title("Daily Message Frequency")
    plt.savefig("message_frequency.png")
    plt.close()

    print(f"Average daily messages: {daily_count.freq.mean():.2f}")

    # Text analysis
    vectorizer = TfidfVectorizer(stop_words='english')
    dtm = vectorizer.fit_transform(df['text'])
    vocab = vectorizer.get_feature_names_out()

    # Top 30 words
    sum_words = dtm.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in zip(vocab, range(len(vocab)))]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    print("Top 30 words:")
    print(words_freq[:30])

    # Topic modeling
    K = 10
    kmeans = KMeans(n_clusters=K)
    kmeans.fit(dtm)
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    
    print("\nTop terms per cluster:")
    for i in range(K):
        print(f"Cluster {i}:")
        print(', '.join([vocab[ind] for ind in order_centroids[i, :10]]))

# Run the main function
asyncio.run(main_test())