import matplotlib.pyplot as plt
import random
import time
# ---------------------------------------------------------
#  YARDIMCI FONKSİYONLAR
# ---------------------------------------------------------

def generate_points(n, min_val=0, max_val=100):
    """
    Belirtilen aralıkta rastgele n adet (x, y) noktası üretir.
    Karmaşıklık: O(N)
    """
    points = []
    for _ in range(n):
        points.append((random.randint(min_val, max_val), random.randint(min_val, max_val)))
    return points

def cross_product(o, a, b):
    """
    Vektörel Çarpım (Cross Product) hesabı.
    (a - o) ve (b - o) vektörlerinin çarpımı.
    
    Sonuç > 0 : b noktası, oa vektörünün solunda (saat yönü tersi)
    Sonuç < 0 : b noktası, oa vektörünün sağında (saat yönü)
    Sonuç = 0 : Doğrusal
    
    Formül: (x2 - x1)(y3 - y1) - (y2 - y1)(x3 - x1)
    Karmaşıklık: O(1)
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

# ---------------------------------------------------------
#  KABA KUVVET (BRUTE FORCE) ALGORİTMASI
# ---------------------------------------------------------

def brute_force_convex_hull(points):
    """
    Kaba Kuvvet Algoritması.
    Her nokta çiftini kontrol eder.
    
    Teorik Karmaşıklık: O(N^3)
    Neden? 
    - İki nokta seçmek için 2 döngü (N * N)
    - Diğer tüm noktaları kontrol etmek için 1 döngü (N)
    """
    n = len(points)
    hull_edges = [] # Çevrimi oluşturan kenarları (nokta çiftlerini) tutacağız

    if n < 3:
        return []

    # 1. Döngü: İlk nokta (i)
    for i in range(n):
        # 2. Döngü: İkinci nokta (j)
        for j in range(n):
            if i == j:
                continue
            
            p1 = points[i]
            p2 = points[j]
            
            on_right_side = True
            
            # 3. Döngü: Diğer tüm noktaları (k) kontrol et
            for k in range(n):
                if k == i or k == j:
                    continue
                
                p3 = points[k]
                
                # p1-p2 doğrusuna göre p3 nerede?
                # Eğer p3 doğrusunun solundaysa (veya sağındaysa, yöne göre değişir),
                # bu kenar dış sınır olamaz diyebiliriz. 
                # Tutarlılık için tüm noktaların sağ tarafta (veya çizgi üstünde) olması gerekir.
                cp = cross_product(p1, p2, p3)
                
                if cp > 0: # Sol tarafta nokta varsa, bu kenar dış sınır değildir.
                    on_right_side = False
                    break 
            
            if on_right_side:
                hull_edges.append((p1, p2))

    return hull_edges

# ---------------------------------------------------------
#  GÖRSELLEŞTİRME
# ---------------------------------------------------------

def plot_hull(points, hull_edges, title="Convex Hull"):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]

    plt.figure(figsize=(8, 6))
    
    # Tüm noktaları çiz
    plt.scatter(x_coords, y_coords, color='blue', label='Noktalar')
    
    # Bulunan kenarları çiz
    for edge in hull_edges:
        p1, p2 = edge
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', linewidth=2) # Kırmızı çizgiler

    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend(["Kenarlar", "Noktalar"])
    plt.grid(True)
    plt.show()

import math  # Açı hesapları için gerekli

# ---------------------------------------------------------
#  GRAHAM SCAN ALGORİTMASI
# ---------------------------------------------------------

def polar_angle(p0, p1):
    """
    p0 noktasına göre p1'in kutupsal açısını hesaplar.
    Karmaşıklık: O(1)
    """
    y_span = p1[1] - p0[1]
    x_span = p1[0] - p0[0]
    return math.atan2(y_span, x_span)

def distance(p0, p1):
    """
    İki nokta arası karesel mesafe (karekök almaya gerek yok, performans için).
    Karmaşıklık: O(1)
    """
    return (p1[0] - p0[0])**2 + (p1[1] - p0[1])**2

def graham_scan(points):
    """
    Graham Scan Algoritması ile Convex Hull bulma.
    Teorik Karmaşıklık: O(N log N)
    """
    n = len(points)
    if n < 3:
        return []

    # Başlangıç noktasını bul (En alt, en sol)
    # Karmaşıklık: O(N)
    start_point = min(points, key=lambda p: (p[1], p[0]))

    # Noktaları start_point'e göre açısına göre sırala
    # Aynı açıda olanlar varsa, uzak olanı seçmek gerekir ama
    # basitlik için Python'un sort'u istikrarlıdır.
    # Karmaşıklık: O(N log N) -> Algoritmanın baskın kısmı burasıdır.
    sorted_points = sorted(points, key=lambda p: (polar_angle(start_point, p), distance(start_point, p)))

    # Başlangıç noktası sıralamada çiftlenmesin diye temizlik yapılabilir
    # ama yığın (stack) mantığı bunu halleder.

    # Stack oluştur ve ilk 3 noktayı ekle
    # Karmaşıklık: O(1)
    stack = [sorted_points[0], sorted_points[1], sorted_points[2]]

    # Kalan noktaları gez
    # Her nokta stack'e en fazla 1 kez girer ve 1 kez çıkar.
    # Karmaşıklık: O(N)
    for i in range(3, n):
        while len(stack) > 1 and cross_product(stack[-2], stack[-1], sorted_points[i]) <= 0:
            # Eğer sola dönüş yoksa (sağa dönüş veya düz ise),
            # stack'in tepesindeki nokta convex hull'ın parçası olamaz. Çıkar.
            stack.pop()
        stack.append(sorted_points[i])

    # Stack'te kalan noktalar Convex Hull'ı oluşturur.
    # Çizim fonksiyonumuz (p1, p2) şeklinde kenar listesi istediği için dönüştürelim:
    hull_edges = []
    for i in range(len(stack)):
        p1 = stack[i]
        p2 = stack[(i + 1) % len(stack)] # Son noktayı ilk noktaya bağla
        hull_edges.append((p1, p2))

    return hull_edges

# ---------------------------------------------------------
# 5. PERFORMANS TESTİ VE GRAFİK (SON ADIM)
# ---------------------------------------------------------

def run_performance_test():
    """
    Farklı N değerleri için algoritmaları yarıştırır ve grafiğini çizer.
    PDF Referans: "Performans Testi ve Grafiksel Karşılaştırma"
    """
    # Test edilecek N değerleri
    # Kaba Kuvvet çok yavaşlayacağı için onda daha az nokta deneyeceğiz.
    n_values = [100, 300, 500, 750, 1000, 2000, 5000, 10000, 20000]
    
    bf_times = []      # Kaba Kuvvet süreleri
    bf_n_values = []   # Kaba Kuvvetin çalıştığı N'ler
    
    gs_times = []      # Graham Scan süreleri
    gs_n_values = []   # Graham Scanin çalıştığı N'ler

    # Kaba Kuvvet için sabır sınırı (N bu değeri geçerse çalıştırma)
    BRUTE_FORCE_LIMIT = 1000 

    print("\n--- PERFORMANS TESTİ BAŞLIYOR ---")
    print(f"{'N':<10} {'Brute Force (sn)':<20} {'Graham Scan (sn)':<20}")
    print("-" * 50)

    for n in n_values:
        points = generate_points(n, 0, 10000) # Geniş bir alana yayalım
        
        # --- Kaba Kuvvet Testi ---
        if n <= BRUTE_FORCE_LIMIT:
            start = time.time()
            brute_force_convex_hull(points)
            end = time.time()
            duration = end - start
            bf_times.append(duration)
            bf_n_values.append(n)
            bf_str = f"{duration:.6f}"
        else:
            bf_str = "Çok Yavaş (Atlandı)"
            # Grafikte kopukluk olmaması için buraya değer eklemiyoruz 
            # veya None ekleyip çizdirirken filtreliyoruz.

        # --- Graham Scan Testi ---
        start = time.time()
        graham_scan(points)
        end = time.time()
        duration = end - start
        gs_times.append(duration)
        gs_n_values.append(n)
        
        print(f"{n:<10} {bf_str:<20} {duration:.6f}")

    # --- GRAFİK ÇİZİMİ ---
    plt.figure(figsize=(10, 6))
    
    # Kaba Kuvvet Çizgisi (Mavi)
    plt.plot(bf_n_values, bf_times, marker='o', linestyle='-', color='blue', label='Kaba Kuvvet (Brute Force)')
    
    # Graham Scan Çizgisi (Turuncu)
    plt.plot(gs_n_values, gs_times, marker='s', linestyle='-', color='orange', label='Graham Scan')

    plt.title('Algoritma Performans Karşılaştırması')
    plt.xlabel('N (Nokta Sayısı)')
    plt.ylabel('Süre (Saniye)')
    plt.legend()
    plt.grid(True)
    
    # Kaba Kuvvetin limitini grafikte belirt
    plt.axvline(x=BRUTE_FORCE_LIMIT, color='red', linestyle='--', alpha=0.5)
    plt.text(BRUTE_FORCE_LIMIT + 50, max(gs_times)/2, 'Brute Force Limiti', color='red', rotation=90)
    
    plt.show()

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    while True:
        try:
            # Kullanıcıdan nokta sayısı al
            print("\n" + "="*40)
            giris = input("Örnek gösterim için Nokta Sayısı (N) giriniz (Çıkış için 'q'): ")
            if giris.lower() == 'q':
                break
            
            N = int(giris)
            print(f"\n{N} adet rastgele nokta üretiliyor...")
            noktalar = generate_points(N)

            # --- KABA KUVVET (BRUTE FORCE) GÖSTERİMİ ---
            # Çok yüksek sayılarda bilgisayar donmasın diye uyarı
            if N > 1000:
                print("UYARI: N > 1000 için Kaba Kuvvet çok uzun sürebilir! Yine de çalıştırılıyor...")

            print("1. Kaba Kuvvet hesaplanıyor...")
            bf_start = time.time()
            bf_edges = brute_force_convex_hull(noktalar)
            bf_end = time.time()
            bf_sure = bf_end - bf_start
            print(f"   -> Tamamlandı! Süre: {bf_sure:.6f} saniye")
            
            # Çizim 
            plot_title = f"Kaba Kuvvet (N={N}) - Süre: {bf_sure:.6f} sn"
            plot_hull(noktalar, bf_edges, title=plot_title)
            print("   (Devam etmek için açılan grafik penceresini kapatın...)")

            # --- GRAHAM SCAN GÖSTERİMİ ---
            print("2. Graham Scan hesaplanıyor...")
            gs_start = time.time()
            gs_edges = graham_scan(noktalar)
            gs_end = time.time()
            gs_sure = gs_end - gs_start
            print(f"   -> Tamamlandı! Süre: {gs_sure:.6f} saniye")

            # Çizim
            plot_title = f"Graham Scan (N={N}) - Süre: {gs_sure:.6f} sn"
            plot_hull(noktalar, gs_edges, title=plot_title)
            print("   (Grafik penceresi kapatıldı.)")

            # --- PERFORMANS TESTİNE GEÇİŞ ---
            print("-" * 40)
            soru = input("Büyük Performans Testi (Grafik) yapılsın mı? (e/h): ")
            if soru.lower() == 'e':
                run_performance_test()
                break # Testten sonra programdan çık
            else:
                print("Yeni bir N değeri girebilirsiniz.")
                
        except ValueError:
            print("Lütfen geçerli bir tam sayı giriniz!")