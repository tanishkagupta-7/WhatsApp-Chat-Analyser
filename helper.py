import re
import emoji
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
from urlextract import URLExtract
import preprocessor


extract = URLExtract()

def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
       df = df[df['user'] == selected_user]


    # Fetch the no. of Messages
    num_messages = df.shape[0]

    # Fetch the total no. of Words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch the no. of Media
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]

    # Fetch the no. of Links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'user': 'Name', 'count': 'Percent'})
    return x,df


def create_wordcloud(selected_user, df):

    with open('stop_words_english.txt', 'r', encoding='utf-8', errors='ignore') as f:
        stopwords = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    def remove_stop_words(message):
        y = []
        for word in message.split():
            if word not in stopwords:
                y.append(word)
        return ' '.join(y)

    wc = WordCloud(width = 500, height = 500, min_font_size = 10, background_color = 'white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    text = temp['message'].str.cat(sep=' ')
    df_wc = wc.generate(text)
    return df_wc


def most_common_words(selected_user, df):


    # with open('stop_hinglish.txt', 'r', encoding='utf-8', errors='ignore') as f:
    with open('stop_words_english.txt', 'r', encoding='utf-8', errors='ignore') as f:
        stopwords = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            word = re.sub(r'[^a-zA-Z]', '', word)
            if word and word not in stopwords:
                words.append(word)

    from collections import Counter
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
       df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
           emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    # Copy to avoid warnings
    data = df.copy()

    # Filter if a specific user is selected
    if selected_user != 'Overall':
        data = data[data['user'] == selected_user]

    # Safety check for required columns
    if 'day_name' not in data.columns or 'period' not in data.columns:
        return pd.DataFrame()  # Return empty DF if something is missing

    # Create pivot table for heatmap
    user_heatmap = (
        data.pivot_table(
            index='day_name',
            columns='period',
            values='message',
            aggfunc='count'
        )
        .fillna(0)
    )

    # Optional: order the days
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    user_heatmap = user_heatmap.reindex(ordered_days).fillna(0)

    return user_heatmap