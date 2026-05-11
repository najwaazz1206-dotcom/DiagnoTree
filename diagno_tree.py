import sys

class Node:
    def __init__(self, text, ya=None, tidak=None, saran=None, confidence=0):
        self.text = text         
        self.ya = ya             
        self.tidak = tidak       
        self.saran = saran      
        self.confidence = confidence # Menampung nilai kepastian dari referensi medis

def build_complex_diagnostic_tree():
    """
    Menyusun struktur pohon keputusan (Decision Tree).
    Nilai confidence ditentukan berdasarkan spesifisitas gejala pada referensi:
    1. Kemenkes RI 2015 (DBD)
    2. WHO 2022 (COVID-19)
    3. UI Edisi VI (Tifoid)
    """
    
    # --- LEVEL 4: DAUN (HASIL DIAGNOSA) ---
    
    # DBD: Confidence 95% jika ada bintik merah (Gejala Patognomonik Kemenkes)
    res_dbd = Node("Positif DBD (Demam Berdarah Dengue)", 
                   saran="Segera cek trombosit ke RS. Perbanyak minum air putih.",
                   confidence=95)
    
    # Suspek DBD/Flu: Confidence 75% karena gejala masih tumpang tindih
    res_dbd_flu = Node("Suspek DBD atau Flu Berat", 
                       saran="Pantau suhu tubuh dan bintik merah. Jika lemas, ke dokter.",
                       confidence=75)
    
    # COVID-19: Confidence 90% jika ada Anosmia (Protokol WHO 2022)
    res_covid = Node("Indikasi Kuat COVID-19", 
                     saran="Lakukan isolasi mandiri dan tes PCR/Antigen. Pantau saturasi.",
                     confidence=90)
    
    # Tifoid: Confidence 85% untuk demam bertahap & pencernaan (Buku Ajar UI)
    res_tipes = Node("Tifoid (Tipes)", 
                     saran="Konsultasi dokter untuk tes Widal/Tubex. Istirahat total.",
                     confidence=85)
    
    # Flu: Confidence 80% untuk gejala pernapasan umum
    res_flu = Node("Flu (Influenza)", 
                   saran="Istirahat cukup, minum air hangat, dan obat flu bebas.",
                   confidence=80)

    # Demam Umum: Confidence 60% karena gejala terlalu umum (Non-spesifik)
    res_demam_umum = Node("Demam Umum", 
                          saran="Istirahat dan pantau gejala lain dalam 24 jam.",
                          confidence=60)

    # --- LEVEL 3: PERTANYAAN SPESIFIK ---
    q_bintik = Node("Apakah muncul bintik merah di kulit atau mimisan?", 
                    ya=res_dbd, tidak=res_dbd_flu)
    
    # --- LEVEL 2: CABANG GEJALA UTAMA ---
    q_pencernaan = Node("Apakah demam meningkat bertahap & ada gangguan pencernaan?", 
                        ya=res_tipes, tidak=res_demam_umum)
    
    q_flu = Node("Apakah disertai pilek, bersin, dan sakit tenggorokan?", 
                 ya=res_flu, tidak=q_pencernaan)
    
    q_anosmia = Node("Apakah Anda kehilangan indra penciuman atau perasa (anosmia)?", 
                     ya=res_covid, tidak=q_flu)

    q_nyeri = Node("Apakah demam mendadak tinggi disertai nyeri sendi/otot hebat?", 
                   ya=q_bintik, tidak=q_anosmia)

    # --- LEVEL 1: ROOT (AKAR) ---
    root = Node("Apakah Anda mengalami demam?")
    root.ya = q_nyeri
    root.tidak = Node("Kondisi Sehat", 
                      saran="Tetap jaga kesehatan dan pola makan.", 
                      confidence=100)
    
    return root

def jalankan_diagnosa(node):
    """Fungsi DFS Rekursif untuk menelusuri pohon hingga ke daun"""
    if node.saran:
        print("\n" + "="*60)
        print(f"HASIL DIAGNOSA : {node.text}")
        print(f"CONFIDENCE     : {node.confidence}% (Berdasarkan Referensi README)")
        print(f"SARAN MEDIS     : {node.saran}")
        print("="*60)
        return

    ans = input(f"{node.text} (y/n): ").lower().strip()
    
    if ans not in ['y', 'n']:
        print("Input tidak valid. Gunakan 'y' atau 'n'.")
        return jalankan_diagnosa(node)

    if ans == 'y':
        if node.ya: jalankan_diagnosa(node.ya)
    else:
        if node.tidak: jalankan_diagnosa(node.tidak)

if __name__ == "__main__":
    print("\n" + " "*10 + "DIAGNOTREE PRO - SISTEM PAKAR DFS")
    print("-" * 55)
    pohon_pakar = build_complex_diagnostic_tree()
    
    while True:
        jalankan_diagnosa(pohon_pakar)
        if input("\nDiagnosa lagi? (y/n): ").lower() != 'y':
            print("Terima kasih telah menggunakan DiagnoTree.")
            break