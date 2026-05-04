import streamlit as st
import pandas as pd
import os
import time
import plotly.express as px
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ============================
# DOSYA YAPILANDIRMASI
# ============================
# Dashboard, Python scripti tarafından yazılan dosyayı doğrudan okur
SOURCE_CSV = "tespiti_log.csv" 

# ============================
# GOOGLE SHEET YÜKLEME FONKSİYONU
# ============================
def upload_csv_as_google_sheet(dataframe, sheet_name="session_log"):
    """Pandas DataFrame'ini doğrudan Google Sheet olarak yükler"""
    # Yükleme için dataframe'i geçici olarak CSV string/dosyasına kaydet
    temp_filename = "temp_upload.csv"
    dataframe.to_csv(temp_filename, index=False)

    gauth = GoogleAuth()
    
    # Kimlik bilgilerini kontrol et
    gauth.LoadCredentialsFile("credentials.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.json")

    drive = GoogleDrive(gauth)

    # CSV'yi Drive'a yükle
    file_csv = drive.CreateFile({"title": sheet_name, "mimeType": "text/csv"})
    file_csv.SetContentFile(temp_filename)
    file_csv.Upload()

    # CSV'yi Google E-Tablosuna dönüştür
    converted = drive.auth.service.files().copy(
        fileId=file_csv['id'],
        body={"mimeType": "application/vnd.google-apps.spreadsheet", "name": sheet_name}
    ).execute()

    return converted["id"]

# ============================
# STREAMLIT KURULUMU
# ============================
st.set_page_config(page_title="YOLOv8 Paneli", layout="wide", page_icon="📊")
st.title("📊 Gerçek Zamanlı YOLOv8 İzleme Paneli")

# --- YAN MENÜ AYARLARI ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=200)

st.sidebar.markdown("## ⚙️ Ayarlar")
threshold = st.sidebar.number_input("⚠️ Ardışık kusur eşiği", 1, 20, 5)
auto_refresh = st.sidebar.checkbox("🔄 Otomatik yenileme (5sn)", value=True)

# ============================
# OTURUM SIFIRLAMA MANTIĞI (ZAMAN FİLTRESİ)
# ============================
# Orijinal CSV dosyasını silmiyoruz. Sadece sıfırlama zamanını kaydediyoruz.
# Sıfırlama zamanından önceki veriler grafikten gizlenecektir.

if 'start_time' not in st.session_state:
    st.session_state['start_time'] = datetime.min # Varsayılan: Tüm verileri göster

if st.sidebar.button("🔄 Oturumu Sıfırla (Baştan Başla)"):
    st.session_state['start_time'] = datetime.now()
    st.toast("Oturum sıfırlandı! Veriler şu andan itibaren görüntüleniyor.", icon="✅")
    time.sleep(0.5)
    st.rerun()

# ============================
# VERİ YÜKLEME (DOĞRUDAN TESPITI_LOG.CSV'DEN)
# ============================
raw_df = pd.DataFrame()
df = pd.DataFrame()

if os.path.exists(SOURCE_CSV):
    try:
        # CSV'yi oku. Dosya yazılırken çökmemesi için on_bad_lines='skip' kullanıyoruz
        raw_df = pd.read_csv(SOURCE_CSV, on_bad_lines='skip')
        
        if not raw_df.empty:
            # 1. Zaman Damgası Dönüştürme
            raw_df["Timestamp"] = pd.to_datetime(raw_df["Timestamp"], errors='coerce')
            
            # 2. Sınıf sütununun string olduğundan emin ol (grafik güvenliği için)
            raw_df["Class"] = raw_df["Class"].astype(str)
            
            # 3. VERİ FİLTRELEME: Sadece reset butonuna basıldıktan SONRAKİ verileri al
            df = raw_df[raw_df["Timestamp"] >= st.session_state['start_time']].copy()
        
    except Exception as e:
        st.error(f"Veritabanı okuma hatası: {e}")
else:
    st.warning(f"'{SOURCE_CSV}' veritabanı dosyası bulunamadı. Önce Python algılama kodunu çalıştırın.")

# ============================
# DASHBOARD GÖRÜNÜMÜ
# ============================

# Sekme Düzeni
tab1, tab2 = st.tabs(["📊 Gerçek Zamanlı İzleme", "📥 Dışa Aktar & Veri"])

with tab1:
    if df.empty:
        st.info("Veri bekleniyor... (Algılama sisteminin çalıştığından emin olun)")
    else:
        # --- METRİKLER ---
        total_deteksi = len(df)
        # Not: "curuk" ve "cok kotu" modelden gelen etiketlerdir, bunları Türkçe diye değiştirmedim.
        df_cacat = df[df["Class"].isin(["curuk", "cok kotu"])] 
        total_cacat = len(df_cacat)
        persen_cacat = (total_cacat / total_deteksi * 100) if total_deteksi > 0 else 0
        
        # Modu (En çok tekrar eden Sınıfı) güvenli bir şekilde bul
        mode_val = df["Class"].mode()
        class_terbanyak = mode_val[0] if not mode_val.empty else "-"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Bu Oturum Toplamı", total_deteksi)
        col2.metric("❌ Kusur Sayısı", total_cacat)
        col3.metric("⚠️ Kusur Yüzdesi", f"%{persen_cacat:.1f}")
        col4.metric("🏆 En Çok Görülen", class_terbanyak)

        # Uyarı Mantığı (Ardışık çok sayıda kusur varsa Toast mesajı)
        last_classes = df["Class"].tail(threshold).tolist()
        if len(last_classes) >= threshold and all(c in ["curuk", "cok kotu"] for c in last_classes):
            st.error(f"🚨 UYARI: Ardışık {threshold} Kusur Tespit Edildi!")

        # --- GRAFİKLER ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Sınıf Dağılımı")
            counts = df["Class"].value_counts().reset_index()
            counts.columns = ["Class", "Count"]
            if not counts.empty:
                fig = px.bar(counts, x="Class", y="Count", color="Class", text="Count")
                st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            st.subheader("Tespit Trendi")
            if not df.empty:
                # Grafik düzgün görünsün diye dakikalık gruplama
                trend = df.set_index("Timestamp").resample('1min')['Class'].count().reset_index()
                fig2 = px.line(trend, x="Timestamp", y="Class", title="Dakika Başına Tespit Sayısı")
                st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("📋 Detaylı Veri (Bu Oturum)")
    
    # Veri tablosunu göster (Oturuma göre filtrelenmiş)
    st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # CSV İndirme
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 CSV İndir (Bu Oturum)",
            data=csv_data,
            file_name=f"Oturum_Raporu_{datetime.now().strftime('%H%M')}.csv",
            mime="text/csv",
            key='download-csv'
        )

    with col_dl2:
        # Google Sheet Yükleme
        if st.button("☁️ Google Sheets'e Yükle"):
            with st.spinner("Google Drive'a yükleniyor..."):
                try:
                    # Zamana dayalı benzersiz sayfa adı
                    sheet_name = f"Log_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    sid = upload_csv_as_google_sheet(df, sheet_name)
                    st.success(f"Başarılı! Kaydedildi: {sheet_name}")
                    st.markdown(f"[Google E-Tablosunu açmak için tıklayın](https://docs.google.com/spreadsheets/d/{sid})")
                except Exception as e:
                    st.error(f"Yükleme başarısız: {e}")

# Otomatik Yenileme Mantığı
if auto_refresh:
    time.sleep(5)
    st.rerun()