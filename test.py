import speedtest

def run_speedtest():
    # Buat objek Speedtest
    st = speedtest.Speedtest()
    
    # Ambil server terdekat
    st.get_best_server()
    
    # Lakukan speedtest
    st.download()
    st.upload()
    
    # Ambil hasil speedtest
    download_speed = st.results.download / 1_000_000
    upload_speed = st.results.upload / 1_000_000
    ping_time = st.results.ping
    share_link = st.results.share()
    if share_link and share_link.startswith("http://"):
        share_link = f"https://{share_link[7:]}"
    
    # Tampilkan hasil speedtest
    print("Speed Test Result")
    print("•━••━••━••━••━•")
    print(f"ꑭ Ping: {ping_time} ms")
    print(f"ꑭ Download Speed: {download_speed:.2f} Mbps")
    print(f"ꑭ Upload Speed: {upload_speed:.2f} Mbps")
    print(f"ꑭ Link: {share_link}")
    print("•━••━••━••━••━•")

# Panggil fungsi run_speedtest
run_speedtest()
