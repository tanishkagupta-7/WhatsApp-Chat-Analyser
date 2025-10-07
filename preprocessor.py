# preprocessor.py
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def preprocess(data: str) -> pd.DataFrame:

    ts_pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*(?:am|pm)'
    matches = list(re.finditer(ts_pattern, data, flags=re.IGNORECASE))

    dates = []
    raw_messages = []

    # if no matches, return empty df
    if not matches:
        return pd.DataFrame(columns=['date', 'user_message', 'user', 'message'])

    for i, m in enumerate(matches):
        ts = m.group(0)
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(data)
        message_text = data[start:end].strip()
        dates.append(ts)
        raw_messages.append(message_text)

    # Now raw_messages typically start with " - User: message" or " - Messages and calls ..."
    # Clean the leading separator and split user and message.
    users = []
    messages = []
    for rm in raw_messages:
        # Remove leading '-' or ':' left by slicing (some exports include " - ")
        rm_clean = re.sub(r'^\s*-\s*', '', rm)
        # Try to split "Name: message" -> name may contain spaces and unicode
        # Use regex that looks for the first occurrence of "Name: "
        entry = re.split(r'([^:]{1,200}):\s', rm_clean, maxsplit=1)
        # re.split returns: ['', <name>, <message>] if pattern matched at beginning,
        # or [rm_clean] if no match.
        if len(entry) >= 3 and entry[1].strip():
            user = entry[1].strip()
            msg = entry[2].strip()
        else:
            # group notification or system message (no user)
            user = 'group_notification'
            msg = rm_clean.strip()
        users.append(user)
        messages.append(msg)

    # Convert dates -> datetime (adjust format if your export uses different ordering)
    df = pd.DataFrame({
        'date_str': dates,
        'user_message': raw_messages,
        'user': users,
        'message': messages
    })

    df['date_str'] = df['date_str'].str.replace('\u202f', ' ', regex=False).str.strip()
    df['date'] = pd.to_datetime(df['date_str'], format='%d/%m/%Y, %I:%M %p', dayfirst=True, errors='coerce')
    # If some are NaT (maybe two-digit year), try alternative:
    if df['date'].isna().any():
        df.loc[df['date'].isna(), 'date'] = pd.to_datetime(
            df.loc[df['date'].isna(), 'date_str'],
            format='%d/%m/%y, %I:%M %p', dayfirst=True, errors='coerce'
        )

    # Add time breakdown columns (only for rows with parsable dates)
    df['year']   = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month']  = df['date'].dt.month_name()
    df['day']    = df['date'].dt.day
    df['only_date'] = df['date'].dt.date
    df['hour']   = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['day_name'] = df['date'].dt.day_name()

    df = df[['date', 'user', 'message', 'year', 'month_num', 'month', 'day', 'only_date', 'hour', 'minute', 'day_name']]

    # Create time period column
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df








