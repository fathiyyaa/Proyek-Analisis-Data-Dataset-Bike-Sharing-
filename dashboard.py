import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
 
# Setup tema seaborn
sns.set(style='dark')

st.set_page_config(layout="wide")  # Mengatur tampilan dashboard jadi lebar

st.markdown(
    "<h1 style='text-align: center;'>Dashboard Bike Sharing 🚴🏻‍♀️</h1>",
    unsafe_allow_html=True
)

# ================= Layout 2 grafik pertama (atas) ================= #
col1, col2 = st.columns(2)

# Load dataset
@st.cache_data
def load_data():
    df_bike_day = pd.read_csv("https://raw.githubusercontent.com/fathiyyaa/proyek_dicoding/main/Bike/day.csv")
    df_bike_hour = pd.read_csv("https://raw.githubusercontent.com/fathiyyaa/proyek_dicoding/main/Bike/hour.csv")
    return df_bike_day,df_bike_hour

df_bike_day, df_bike_hour = load_data()

df_bike_day['dteday'] = pd.to_datetime(df_bike_day['dteday'])
df_bike_hour['dteday'] = pd.to_datetime(df_bike_hour['dteday'])


def create_df_total(df_bike_day):
    df_total = pd.DataFrame({
        "Total Working Days": [df_bike_day['workingday'].sum()],
        "Total Holidays": [df_bike_day['holiday'].sum()]
    })
    return df_total

def create_weekday_counts(df_bike_day):
    weekday_counts = df_bike_day.groupby('weekday')['cnt'].sum()
    return weekday_counts

def create_year_2011(df_bike_day):
    year_2011_day = df_bike_day[df_bike_day['yr'] == 0]
    return year_2011_day

def create_year_2012(df_bike_day):
    year_2012_day = df_bike_day[df_bike_day['yr'] == 1]
    return year_2012_day

def create_waktu(df_bike_hour):
    df_bike_hour['time_of_day'] = np.where(
    df_bike_hour['hr'].between(6, 11), 'Pagi',
    np.where(df_bike_hour['hr'].between(12, 17), 'Siang', 'Malam')
)
    return df_bike_hour

def create_total_time(df_bike_hour):
    df_total_time = pd.DataFrame.from_dict({
    "Total Pagi": [df_bike_hour['time_of_day'].value_counts().get('Pagi', 0)],
    "Total Siang": [df_bike_hour['time_of_day'].value_counts().get('Siang', 0)],
    "Total Malam": [df_bike_hour['time_of_day'].value_counts().get('Malam', 0)]
})
    return df_total_time

# Pilih rentang tanggal
st.sidebar.subheader("Tanggal 📅")
start_date = st.sidebar.date_input("Pilih Tanggal Mulai", df_bike_day["dteday"].min())
end_date = st.sidebar.date_input("Pilih Tanggal Akhir", df_bike_day["dteday"].max())

# Konversi ke datetime agar bisa difilter
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

st.sidebar.write(f"📌 Data ditampilkan dari {start_date.date()} hingga {end_date.date()}, pilih rentang tanggal minimal 1 minggu")

# Filter dataset berdasarkan tanggal yang dipilih
df_bike_day_filtered = df_bike_day[(df_bike_day["dteday"] >= start_date) & (df_bike_day["dteday"] <= end_date)]
df_bike_hour_filtered = df_bike_hour[(df_bike_hour["dteday"] >= start_date) & (df_bike_hour["dteday"] <= end_date)]

# Menyiapkan data frame
df_bike_hour = create_waktu(df_bike_hour_filtered) 
df_total = create_df_total(df_bike_day_filtered)
weekday_counts = create_weekday_counts(df_bike_day_filtered)
year_2011_day = create_year_2011(df_bike_day_filtered)
year_2012_day = create_year_2012(df_bike_day_filtered)
df_total_time = create_total_time(df_bike_hour_filtered)

with col1:
# Buat figure dan axis
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(["Working Days", "Holidays"], df_total.iloc[0], color=["#72BCD4", "#D3D3D3"])

# Tambahkan judul dan label
    plt.title('Total Bike Sharing per Working Days and Holidays')
    plt.xticks(rotation=0)

# Tampilkan plot di Streamlit
    st.pyplot(fig)

    max_value = weekday_counts.max()

    # Buat warna: merah untuk nilai maksimum, biru untuk lainnya
    colors = ["#72BCD4" if value == max_value else "#D3D3D3" for value in weekday_counts.values]

    # Buat figure dan axis
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(weekday_counts.index, weekday_counts.values, color=colors)

with col2:
    ax.set_title('Total Bike Sharing per Weekday')

    # Pastikan label weekday tampil dengan benar
    ax.set_xticks(ticks=weekday_counts.index)
    ax.set_xticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])

    # Tampilkan di Streamlit
    st.pyplot(fig)

# Pilih waktu (Dropdown) dengan key unik
time_selection = st.selectbox("Pilih Waktu:", ["Pagi", "Siang", "Malam"], key="waktu")

# Filter data berdasarkan pilihan waktu
hourly_data = df_bike_hour[df_bike_hour["time_of_day"] == time_selection]

# Group by jam dan jumlah total rental
hourly_counts = hourly_data.groupby("hr")["cnt"].sum()

# --- Visualisasi: Total Bike Rentals per Hour (Pagi, Siang, Malam) ---
st.subheader(f"Total Bike Rentals per Hour ({time_selection})")

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(hourly_counts.index, hourly_counts.values, color="#72BCD4")
ax.set_title(f"Total Bike Rentals per Hour ({time_selection})")
ax.set_xlabel("Hour")
ax.set_ylabel("Total Rentals")
ax.set_xticks(hourly_counts.index)
st.pyplot(fig)


# --- Visualisasi: Perbandingan Total Bike Sharing per Bulan (2011 vs 2012) ---
import streamlit as st
import matplotlib.pyplot as plt

st.subheader("Perbandingan Total Bike Sharing per Bulan (2011 vs 2012)")

# Mengelompokkan data berdasarkan bulan
rentals_2011 = year_2011_day.groupby(year_2011_day['dteday'].dt.month)['cnt'].sum()
rentals_2012 = year_2012_day.groupby(year_2012_day['dteday'].dt.month)['cnt'].sum()

# Pilihan tahun untuk ditampilkan
year_selection = st.selectbox("Pilih Tahun:", [2011, 2012, "Keduanya"], key="tahun")

# Plot line chart sesuai pilihan
fig, ax = plt.subplots(figsize=(10, 6))

if year_selection == 2011:
    ax.plot(rentals_2011.index, rentals_2011.values, marker='o', linestyle='-', color='#FFDB58', label='2011')
elif year_selection == 2012:
    ax.plot(rentals_2012.index, rentals_2012.values, marker='s', linestyle='-', color='#9ACD32', label='2012')
else:  # Jika "Keduanya" dipilih
    ax.plot(rentals_2011.index, rentals_2011.values, marker='o', linestyle='-', color='#FFDB58', label='2011')
    ax.plot(rentals_2012.index, rentals_2012.values, marker='s', linestyle='-', color='#9ACD32', label='2012')

ax.set_xticks(range(1, 13))
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax.set_title("Perbandingan Total Bike Sharing per Bulan")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)

# Menampilkan plot
st.pyplot(fig)

st.markdown("""
**📌kesimpulan**
- Waktu terbaik untuk menambah stok sepeda adalah pada jam 4 sore saat hari kerja, karena puncak peminjaman akan terjadi pada jam 5-6 sore. Hal ini menunjukkan bahwa banyak pengguna memanfaatkan sepeda setelah jam kerja, kemungkinan untuk pulang ke rumah atau aktivitas lainnya. Oleh karena itu, pengelola sistem peminjaman sepeda dapat mempertimbangkan untuk meningkatkan jumlah unit yang tersedia pada sore hari untuk menghindari kekurangan stok.
- Tren per bulan pada 2011 dan 2012 sedikit berbeda, tetapi memiliki pola serupa dengan peningkatan peminjaman pada bulan Januari–Mei dan penurunan pada Oktober–Desember. Hal ini mungkin disebabkan oleh faktor cuaca, musim liburan, atau perubahan kebiasaan pengguna. Perlu dilakukan analisis lebih lanjut mengenai faktor apa saja yang berpengaruh, dapat dilakukan dengan regresi atau metode lainnya. Strategi promosi dapat difokuskan pada akhir tahun untuk meningkatkan minat pengguna, misalnya dengan memberikan diskon atau program loyalitas pada bulan Oktober–Desember
""")