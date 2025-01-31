import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set(style='whitegrid')

# Memuat dataset
df_day = pd.read_csv('data/day.csv')
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_day['year'] = df_day['dteday'].dt.year

# Pengaturan sidebar
st.header('Analisis Dataset Bike Sharing :sparkles:')
st.sidebar.image("https://storage.googleapis.com/kaggle-datasets-images/3556223/6194875/c51f57d9f027c00fc8d573060eef197b/dataset-cover.jpeg", width=300)
min_date = df_day['dteday'].min().date()
max_date = df_day['dteday'].max().date()

# Filter rentang tanggal
start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Mengubah objek tanggal menjadi datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Memfilter data berdasarkan rentang tanggal yang dipilih
filtered_data = df_day[(df_day['dteday'] >= start_date) & (df_day['dteday'] <= end_date)]

# Menghitung jumlah pengguna hari ini dan kemarin
todays_cnt = int(filtered_data['cnt'].iloc[0])
yesterdays_cnt = int(filtered_data['cnt'].iloc[-1])

# Menampilkan metrik di sidebar dengan pemisah ribuan
st.sidebar.metric(
    label="Pertumbuhan Pengguna Harian",
    value=todays_cnt,
    delta=yesterdays_cnt
)

# Pengguna Harian
daily_users_data = filtered_data.groupby('dteday').agg({
    'casual': 'sum',
    'registered': 'sum',
    'cnt': 'sum'
}).reset_index()

st.subheader('Total Pengguna')

col1, col2, col3 = st.columns(3)

def format_number(number):
    return f"{number:,}"

with col1:
    total_casual = daily_users_data.casual.sum()
    st.metric("Total Pengguna Casual", value=format_number(total_casual))

with col2:
    total_registered = daily_users_data.registered.sum()
    st.metric("Total Pengguna Terdaftar", value=format_number(total_registered))

with col3:
    total_cnt = daily_users_data.cnt.sum()
    st.metric("Total Pengguna", value=format_number(total_cnt))

# PLOT 1
user_counts_data = df_day[['casual', 'registered']].sum()

# Membuat plot pie
fig_pie, ax_pie = plt.subplots()
ax_pie.pie(user_counts_data, labels=user_counts_data.index, autopct='%2.1f%%', startangle=90, colors=['#FF6F61', '#6A5ACD'])
ax_pie.axis('equal')
ax_pie.set_title("Persentase Pengguna (Casual vs Terdaftar)")

# Menampilkan plot di Streamlit
st.pyplot(fig_pie)

# PLOT 2
st.subheader('Pengguna Harian')
# menentukan ukuran gambar
fig_fh3, ax_fh3 = plt.subplots(figsize=(16, 8))
# Membuat plot
sns.lineplot(x='dteday', y='casual', data=daily_users_data, ax=ax_fh3, label='Casual', marker='o', color="#FF6F61")
sns.lineplot(x='dteday', y='registered', data=daily_users_data, ax=ax_fh3, label='Registered', marker='o', color="#6A5ACD")
ax_fh3.set_ylabel("Jumlah Pengguna")
ax_fh3.set_xlabel("Tanggal")
ax_fh3.set_title("Jumlah Pengguna Casual dan Terdaftar per Hari")
ax_fh3.tick_params(axis='x', rotation=45)  # Memutar label sumbu x untuk keterbacaan yang lebih baik
ax_fh3.legend(["Casual", "Terdaftar"])

# Menampilkan plot di Streamlit
st.pyplot(fig_fh3)

# PLOT 3
st.subheader('Pengguna vs Temperatur')

# Memetakan nilai musim numerik ke label
season_mapping = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Autumn'}
filtered_data['season'] = filtered_data['season'].map(season_mapping)

# Membuat plot
fig_temp, ax_temp = plt.subplots(figsize=(12, 6))
ax_temp.scatter(filtered_data['casual'], filtered_data['temp'], label='Casual')
ax_temp.scatter(filtered_data['registered'], filtered_data['temp'], label='Terdaftar')
ax_temp.set_xlabel('Jumlah Pengguna')
ax_temp.set_ylabel('Temperatur (normalisasi)')
ax_temp.legend()
ax_temp.set_title('Hubungan antara Pengguna Sepeda dan Temperatur')

# Menampilkan plot di Streamlit
st.pyplot(fig_temp)

# Data agregat
season_data = filtered_data.groupby('season').agg({
    'registered': 'sum',
    'casual': 'sum'
}).reset_index()

# Data agregat untuk plot
plot_data = filtered_data.groupby(['temp', 'atemp']).agg({
    'cnt': 'sum'
}).reset_index()

# subplot 1
fig, ax = plt.subplots()
sns.regplot(x='cnt', y='temp', data=plot_data, ax=ax, label='temp', color="#FF6F61", line_kws={'color': 'red'})
ax.set_ylabel("Jumlah Pengguna")
ax.set_xlabel("Temperatur")
ax.set_title("Total Pengguna vs Temperatur")
ax.legend()

# subplot 2
fig2, ax = plt.subplots()
sns.regplot(x='cnt', y='atemp', data=plot_data, ax=ax, label='atemp', color="#6A5ACD", line_kws={'color': 'red'})
ax.set_ylabel("Jumlah Pengguna")
ax.set_xlabel("Temperatur")
ax.set_title("Total Pengguna vs Temperatur Rasanya")
ax.legend()

# Menampilkan plot di Streamlit
col1, col2 = st.columns(2)
with col1:
    st.pyplot(fig)

with col2:
    st.pyplot(fig2)

# Expander untuk informasi tambahan
with st.expander("Informasi Tambahan"):
    st.write(""" 
    Secara umum, semakin tinggi temperatur udara (temp dan atemp), maka semakin banyak pengguna Bike Sharing.\n
    Ket:\n
    - **casual**: jumlah pengguna casual
    - **registered**: jumlah pengguna terdaftar
    - **temp**: suhu normal dalam Celsius. Nilai-nilai ini diperoleh melalui (t-t_min)/(t_max-t_min), t_min=-8, t_max=+39 (hanya dalam skala per jam)
    - **atemp**: suhu rasa normal dalam Celsius. Nilai-nilai ini diperoleh melalui (t-t_min)/(t_max-t_min), t_min=-16, t_max=+50 (hanya dalam skala per jam)
    """)

# PLOT 4
st.subheader('Pengguna vs Musim')

fig_fh1, ax_fh1 = plt.subplots()
sns.barplot(x='season', y='registered', data=season_data, ax=ax_fh1, label='Terdaftar', color="#6A5ACD")
sns.barplot(x='season', y='casual', data=season_data, ax=ax_fh1, label='Casual', color="#FF6F61")
ax_fh1.set_ylabel("Jumlah")
ax_fh1.set_title(f"Pengguna Casual dan Terdaftar Berdasarkan Musim")
ax_fh1.legend()

# Menampilkan plot di Streamlit
st.pyplot(fig_fh1)

# PLOT 5
st.subheader('Pengguna vs Cuaca')

season_data= df_day.groupby('weathersit').agg({
    'casual':'sum',
    'registered':'sum'
}).reset_index()
fig_fh1, ax_fh1 = plt.subplots()
sns.barplot(x='weathersit', y='registered', data=season_data, ax=ax_fh1, label='Terdaftar', color="#6A5ACD")
sns.barplot(x='weathersit', y='casual', data=season_data, ax=ax_fh1, label='Casual', color="#FF6F61")
ax_fh1.set_ylabel("Jumlah")
ax_fh1.set_title(f"Pengguna Casual dan Terdaftar Berdasarkan Cuaca")
ax_fh1.legend()

# Menampilkan plot di Streamlit
st.pyplot(fig_fh1)

with st.expander("Informasi Tambahan"):
    st.write(""" 
    Angka 1e6 pada plot yang tertampil adalah notasi ilmiah untuk bilangan 1.000.000.\n
    Secara umum, semakin baik cuacanya, semakin banyak pula pengguna Bike Sharing dengan 1 cuaca paling baik dan 3 cuaca paling buruk.\n
    Ket:\n
    - **1**: Clear, Few clouds, Partly cloudy, Partly cloudy
    - **2**:  Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist
    - **3**: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds
    """)