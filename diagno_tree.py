"""
╔══════════════════════════════════════════════════════════════════╗
║              DIAGNOTREE PRO - SISTEM PAKAR MEDIS                 ║
║         Berbasis Algoritma DFS (Depth-First Search) Tree         ║
╠══════════════════════════════════════════════════════════════════╣
║  Referensi:                                                      ║
║  [1] Kemenkes RI (2015) - Pedoman DBD                            ║
║  [2] WHO (2022) - COVID-19 Clinical Protocol                     ║
║  [3] Buku Ajar IPD UI Edisi VI - Demam Tifoid                    ║
╚══════════════════════════════════════════════════════════════════╝

Deskripsi:
    Program ini mengimplementasikan struktur data Binary Decision Tree
    yang ditelusuri menggunakan algoritma DFS Rekursif untuk
    mendiagnosis penyakit umum berbasis gejala klinis.

    Konsep pohon keputusan diadaptasi dari:
    Kurniawan, et al. (2024) - "Implementasi Decision Tree dan
    K-Fold Cross Validation pada Klasifikasi Penyakit Diabetes",
    Jurnal Informatika (Sinta 3).

Penulis  : DiagnoTree Team
Versi    : 2.0 Professional
Platform : Python 3.x
"""

import sys
import time
import os


# ──────────────────────────────────────────────────────────────────
#  KONFIGURASI WARNA TERMINAL (ANSI Escape Codes)
# ──────────────────────────────────────────────────────────────────

class Color:
    """Kelas utilitas untuk pewarnaan output terminal via ANSI codes."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

    # Background
    BG_RED    = "\033[41m"
    BG_GREEN  = "\033[42m"
    BG_BLUE   = "\033[44m"
    BG_YELLOW = "\033[43m"

    @staticmethod
    def supports_color():
        """Deteksi apakah terminal mendukung ANSI color codes."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


# ──────────────────────────────────────────────────────────────────
#  STRUKTUR DATA: NODE POHON KEPUTUSAN
# ──────────────────────────────────────────────────────────────────

class Node:
    """
    Representasi satu simpul (node) dalam Binary Decision Tree.

    Atribut:
        text       (str)  : Teks pertanyaan atau nama penyakit.
        ya         (Node) : Anak kiri — cabang jawaban 'Ya'.
        tidak      (Node) : Anak kanan — cabang jawaban 'Tidak'.
        saran      (str)  : Saran medis, hanya ada pada node daun (leaf).
        confidence (int)  : Tingkat kepastian diagnosis (0–100%).
        referensi  (str)  : Sumber ilmiah pendukung nilai confidence.
        level      (int)  : Kedalaman node dalam pohon (untuk visualisasi).
        emoji      (str)  : Ikon penyakit untuk tampilan hasil.
    """

    def __init__(self, text, ya=None, tidak=None,
                 saran=None, confidence=0,
                 referensi="", emoji="🔍",
                 urgency="low", level=0):

        self.text       = text
        self.ya         = ya
        self.tidak      = tidak
        self.saran      = saran
        self.confidence = confidence
        self.referensi  = referensi
        self.emoji      = emoji
        self.urgency    = urgency
        self.level      = level


# ──────────────────────────────────────────────────────────────────
#  FUNGSI UTILITAS TAMPILAN
# ──────────────────────────────────────────────────────────────────

def typewriter(text, delay=0.018, color=""):
    """
    Efek mengetik teks karakter per karakter (typewriter effect).

    Args:
        text  (str)   : Teks yang akan ditampilkan.
        delay (float) : Jeda antar karakter dalam detik.
        color (str)   : Kode warna ANSI opsional.
    """
    if color:
        sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if color:
        sys.stdout.write(Color.RESET)
    print()


def loading_bar(label="Memproses", duration=0.8, width=30):
    """
    Menampilkan progress bar animasi di terminal.

    Args:
        label    (str)   : Label yang ditampilkan di sebelah kiri bar.
        duration (float) : Total durasi animasi dalam detik.
        width    (int)   : Lebar bar dalam karakter.
    """
    print()
    for i in range(width + 1):
        filled  = "█" * i
        empty   = "░" * (width - i)
        percent = int((i / width) * 100)
        bar     = f"\r  {Color.CYAN}{label}{Color.RESET}  [{Color.GREEN}{filled}{Color.GRAY}{empty}{Color.RESET}] {Color.YELLOW}{percent:>3}%{Color.RESET}"
        sys.stdout.write(bar)
        sys.stdout.flush()
        time.sleep(duration / width)
    print(f"  {Color.GREEN}✓ Selesai{Color.RESET}\n")


def confidence_bar(value, width=20):
    """
    Menghasilkan string visual confidence bar berdasarkan nilai persentase.

    Args:
        value (int) : Nilai confidence 0–100.
        width (int) : Lebar bar dalam karakter.

    Returns:
        str: String bar yang telah diberi warna.
    """
    filled = int((value / 100) * width)
    empty  = width - filled

    if value >= 85:
        color = Color.RED
    elif value >= 70:
        color = Color.YELLOW
    else:
        color = Color.CYAN

    bar = f"{color}{'▓' * filled}{Color.GRAY}{'░' * empty}{Color.RESET}"
    return bar


def severity_label(urgency):
    """
    Menentukan label urgensi berdasarkan tingkat kegawatan,
    bukan berdasarkan confidence diagnosis.
    """

    if urgency == "high":
        return f"{Color.BG_RED}{Color.WHITE}{Color.BOLD}  ⚠  SEGERA KE DOKTER  {Color.RESET}"

    elif urgency == "medium":
        return f"{Color.BG_YELLOW}{Color.WHITE}{Color.BOLD}  ⚡ PANTAU KONDISI    {Color.RESET}"

    else:
        return f"{Color.BG_GREEN}{Color.WHITE}{Color.BOLD}  ✓  KONDISI STABIL    {Color.RESET}"


def print_separator(char="─", width=62, color=Color.GRAY):
    """Mencetak garis pemisah horizontal."""
    print(f"{color}{char * width}{Color.RESET}")


def clear_screen():
    """Membersihkan layar terminal lintas platform."""
    os.system('cls' if os.name == 'nt' else 'clear')


# ──────────────────────────────────────────────────────────────────
#  TAMPILAN HEADER & FOOTER
# ──────────────────────────────────────────────────────────────────

def print_header():
    """Menampilkan header aplikasi dengan ASCII art dan info versi."""
    clear_screen()
    print()
    print(f"{Color.CYAN}{Color.BOLD}", end="")
    print("  ██████╗ ██╗ █████╗  ██████╗ ███╗  ██╗ ██████╗")
    print("  ██   ██╗██║██   ██╗██╔════╝ ████╗ ██║██╔═══██╗")
    print("  ██   ██║██║███████║██║  ███╗██╔██╗██║██║   ██║")
    print("  ██   ██║██║██   ██║██║   ██║██║╚████║██║   ██║")
    print("  ██████╔╝██║██║  ██║╚██████╔╝██║ ╚███║╚██████╔╝")
    print("  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝ ╚═════╝")
    print(Color.RESET, end="")
    print(f"  {Color.MAGENTA}{Color.BOLD}{'T R E E':<54}{Color.RESET}", end="")
    print(f"{Color.YELLOW}PRO v2.0{Color.RESET}")
    print()
    print_separator("═", 62, Color.CYAN)
    print(f"  {Color.WHITE}{Color.BOLD}SISTEM PAKAR DIAGNOSIS PENYAKIT UMUM{Color.RESET}")
    print(f"  {Color.GRAY}Algoritma : Depth-First Search (DFS) pada Binary Decision Tree{Color.RESET}")
    print(f"  {Color.GRAY}Referensi : Kemenkes RI 2015 · WHO 2022 · Buku Ajar IPD UI VI{Color.RESET}")
    print_separator("═", 62, Color.CYAN)
    print()


def print_footer():
    """Menampilkan pesan penutup saat program selesai."""
    print()
    print_separator("═", 62, Color.CYAN)
    print(f"  {Color.YELLOW}⚕  DiagnoTree Pro  {Color.GRAY}|  Tugas Proyek SDA 2025{Color.RESET}")
    print(f"  {Color.GRAY}⚠  Hasil ini bukan pengganti diagnosis dokter profesional.{Color.RESET}")
    print_separator("═", 62, Color.CYAN)
    print()
    typewriter("  Terima kasih telah menggunakan DiagnoTree Pro.", 0.025, Color.GREEN)
    print()


# ──────────────────────────────────────────────────────────────────
#  TAMPILAN HASIL DIAGNOSA
# ──────────────────────────────────────────────────────────────────

def print_result(node):
    """
    Menampilkan hasil akhir diagnosa dalam format kartu profesional.

    Format mencakup: nama penyakit, confidence bar, saran medis,
    tingkat urgensi, dan sumber referensi ilmiah.

    Args:
        node (Node): Node daun yang berisi hasil diagnosa.
    """
    loading_bar("Menganalisis gejala", duration=1.2)

    print_separator("╔" + "═" * 60 + "╗", 1, "")
    print(f"  {Color.BOLD}{Color.WHITE}HASIL DIAGNOSA{Color.RESET}")
    print_separator("╠" + "═" * 60 + "╣", 1, "")

    # Nama Penyakit
    print(f"\n  {node.emoji}  {Color.YELLOW}{Color.BOLD}{node.text}{Color.RESET}\n")

    # Confidence Bar
    bar     = confidence_bar(node.confidence)
    print(f"  {Color.WHITE}Tingkat Kepastian{Color.RESET}  {bar}  {Color.BOLD}{node.confidence}%{Color.RESET}")
    print(f"  {Color.GRAY}Sumber: {node.referensi}{Color.RESET}\n")

    # Label Urgensi
    print(f"  {severity_label(node.urgency)}\n")

    # Saran Medis
    print_separator(width=60)
    print(f"  {Color.CYAN}{Color.BOLD}📋 SARAN MEDIS:{Color.RESET}")
    # Wrap saran agar tidak melebihi 56 karakter per baris
    words    = node.saran.split()
    line     = "  "
    for word in words:
        if len(line) + len(word) + 1 > 58:
            print(f"{Color.WHITE}{line}{Color.RESET}")
            line = f"  {word} "
        else:
            line += word + " "
    if line.strip():
        print(f"{Color.WHITE}{line}{Color.RESET}")

    print()
    print_separator(width=60)
    print()


# ──────────────────────────────────────────────────────────────────
#  MEMBANGUN POHON KEPUTUSAN (DECISION TREE)
# ──────────────────────────────────────────────────────────────────

def build_decision_tree():
    """
    Membangun struktur Binary Decision Tree untuk diagnosis penyakit.

    Struktur pohon:
                        [Demam?]
                       /        \\
               [Nyeri Sendi?]  [Sehat]
              /              \\
        [Bintik Merah?]   [Anosmia?]
        /       \\          /        \\
      [DBD]  [Suspek]  [COVID-19] [Pilek?]
                                  /      \\
                              [Flu]   [Pencernaan?]
                                      /         \\
                                  [Tifoid]  [Demam Umum]

    Nilai confidence didasarkan pada spesifisitas gejala dalam
    literatur medis yang dirujuk.

    Returns:
        Node: Root node dari pohon keputusan yang telah dibangun.
    """

    # ── LEVEL 4: DAUN (LEAF NODES = HASIL DIAGNOSA) ──────────────

    # DBD: Confidence 95%
    # Petekiae dan perdarahan ringan merupakan tanda kuat yang sering ditemukan pada DBD
    # Sumber: Kemenkes RI (2015), Hal. 12 — Tanda Klinis DBD
    res_dbd = Node(
        text       = "Indikasi Kuat DBD (Demam Berdarah Dengue)",
        saran      = "Segera cek trombosit ke RS terdekat. Perbanyak minum air putih dan cairan elektrolit. Hindari aspirin atau ibuprofen.",
        confidence = 95,
        urgency    = "high",
        referensi  = "Kemenkes RI (2015) — Petekiae sebagai indikator klinis DBD",
        emoji      = "🦟"
    )

    # Suspek DBD/Flu Berat: Confidence 75%
    # Demam tinggi dan nyeri sendi tanpa perdarahan masih dapat tumpang tindih
    # dengan influenza berat atau fase awal DBD
    # Sumber: Kemenkes RI (2015), WHO Dengue Guidelines
    res_dbd_flu = Node(
        text       = "Suspek DBD atau Flu Berat",
        saran      = "Pantau kemunculan bintik merah dan suhu tubuh setiap 6 jam. Jika trombosit turun, muntah terus-menerus, atau tubuh sangat lemas, segera ke IGD.",
        confidence = 75,
        urgency    = "medium",
        referensi  = "Kemenkes RI (2015) — Kriteria suspek DBD tanpa perdarahan",
        emoji      = "⚠️"
    )

    # COVID-19: Confidence 85%
    # Anosmia/ageusia merupakan gejala khas yang sering ditemukan pada COVID-19
    # meskipun tidak cukup untuk diagnosis definitif tanpa tes laboratorium
    # Sumber: WHO (2022) — COVID-19 Clinical Management
    res_covid = Node(
        text       = "Indikasi Kuat COVID-19",
        saran      = "Lakukan isolasi mandiri sementara. Segera lakukan tes Antigen atau PCR. Pantau saturasi oksigen; jika <95% atau sesak napas memburuk, hubungi layanan medis.",
        confidence = 85,
        urgency    = "high",
        referensi  = "WHO (2022) — Anosmia dan ageusia sebagai gejala khas COVID-19",
        emoji      = "🦠"
    )

    # Tifoid: Confidence 85%
    # Demam bertahap (step-ladder) disertai gangguan gastrointestinal
    # merupakan pola klinis yang sering ditemukan pada tifoid
    # Sumber: Buku Ajar IPD UI Edisi VI — Demam Tifoid
    res_tipes = Node(
        text       = "Indikasi Demam Tifoid (Tipes)",
        saran      = "Konsultasi ke dokter untuk pemeriksaan lanjutan seperti Widal atau Tubex TF. Istirahat cukup dan hindari makanan yang sulit dicerna.",
        confidence = 85,
        urgency    = "medium",
        referensi  = "Buku Ajar IPD UI Ed.VI (2014) — Demam step-ladder dan gangguan GI",
        emoji      = "🌡️"
    )

    # Flu: Confidence 80%
    # Gejala pilek, bersin, dan sakit tenggorokan termasuk kategori
    # Influenza-Like Illness (ILI)
    # Sumber: WHO Influenza Surveillance Guidelines (2014)
    res_flu = Node(
        text       = "Flu (Influenza / Common Cold)",
        saran      = "Istirahat cukup, perbanyak minum air hangat, dan konsumsi makanan bergizi. Obat simptomatik seperti paracetamol dapat membantu meredakan keluhan.",
        confidence = 80,
        urgency    = "low",
        referensi  = "WHO ILI Surveillance (2014) — Kriteria Influenza-Like Illness",
        emoji      = "🤧"
    )

    # Demam Umum: Confidence 60%
    # Gejala yang dilaporkan masih bersifat non-spesifik dan belum dapat
    # mengarah kuat pada penyakit tertentu
    res_demam_umum = Node(
        text       = "Demam Non-Spesifik (Demam Umum)",
        saran      = "Istirahat cukup dan pantau perkembangan gejala selama 24–48 jam. Jika demam berlangsung lebih dari 3 hari atau muncul gejala baru, segera konsultasi ke dokter.",
        confidence = 60,
        urgency    = "low",
        referensi  = "Prinsip umum — Gejala demam non-spesifik belum terpola",
        emoji      = "🌡️"
    )

    # Tidak Ada Indikasi Penyakit: Confidence 95%
    # Tidak ditemukan gejala klinis yang mengarah ke penyakit tertentu
    # berdasarkan jawaban pengguna pada sesi ini
    node_sehat = Node(
        text       = "Tidak Ada Indikasi Penyakit",
        saran      = "Kondisi Anda tampak stabil. Tetap jaga pola hidup sehat, tidur cukup, olahraga teratur, dan konsumsi makanan bergizi.",
        confidence = 95,
        urgency    = "low",
        referensi  = "Tidak ditemukan gejala signifikan berdasarkan input pengguna",
        emoji      = "✅"
    )

    # ── LEVEL 3: PERTANYAAN SPESIFIK ─────────────────────────────

    # Pertanyaan: Apakah ada petekiae atau epistaksis?
    # Memisahkan DBD pasti dari suspek berdasarkan tanda perdarahan
    q_bintik = Node(
        text  = "Apakah muncul bintik-bintik merah di kulit (petekiae) atau mimisan (epistaksis)?",
        ya    = res_dbd,
        tidak = res_dbd_flu
    )


    # ── LEVEL 2: PERTANYAAN GEJALA UTAMA ─────────────────────────

    # Pertanyaan: Pola demam step-ladder + gangguan pencernaan?
    q_pencernaan = Node(
        text  = "Apakah demam meningkat bertahap tiap hari disertai mual, muntah, atau diare?",
        ya    = res_tipes,
        tidak = res_demam_umum
    )

    # Pertanyaan: Gejala ISPA ringan (ILI)?
    q_flu = Node(
        text  = "Apakah disertai pilek, bersin-bersin, dan sakit tenggorokan?",
        ya    = res_flu,
        tidak = q_pencernaan
    )

    # Pertanyaan: Anosmia / ageusia (penanda khas COVID-19)?
    q_anosmia = Node(
        text  = "Apakah Anda kehilangan kemampuan mencium bau (anosmia) atau merasakan makanan (ageusia)?",
        ya    = res_covid,
        tidak = q_flu
    )

    # Pertanyaan: Demam mendadak tinggi + artralgia/mialgia berat?
    # Ciri khas fase febrile DBD: suhu ≥ 38.5°C onset mendadak + nyeri hebat
    q_nyeri = Node(
        text  = "Apakah demam datang mendadak tinggi (≥38.5°C) disertai nyeri sendi atau otot yang hebat?",
        ya    = q_bintik,
        tidak = q_anosmia
    )

    # ── LEVEL 1: ROOT (AKAR POHON) ───────────────────────────────

    # Node sehat: leaf tanpa pertanyaan lanjut
    node_sehat = Node(
        text       = "Tidak Ada Indikasi Penyakit",
        saran      = "Kondisi Anda tampak sehat. Pertahankan pola hidup sehat, tidur cukup, dan konsumsi makanan bergizi.",
        confidence = 100,
        referensi  = "Tidak ada gejala yang dilaporkan",
        emoji      = "✅"
    )

    # Root: pertanyaan pertama — apakah ada demam?
    root       = Node(text="Apakah Anda mengalami demam dalam 3 hari terakhir?")
    root.ya    = q_nyeri
    root.tidak = node_sehat

    return root


# ──────────────────────────────────────────────────────────────────
#  ALGORITMA DFS: PENELUSURAN POHON
# ──────────────────────────────────────────────────────────────────

# Menyimpan riwayat pertanyaan untuk ditampilkan di ringkasan
_question_history = []


def run_dfs(node, depth=0):
    """
    Algoritma DFS Rekursif untuk menelusuri pohon keputusan.

    Prinsip DFS: Dari setiap node, langsung telusuri ke anak
    sesuai jawaban pengguna (ya → kiri, tidak → kanan) hingga
    mencapai node daun (leaf) yang berisi hasil diagnosa.

    Kompleksitas Waktu : O(d) — d = kedalaman pohon
    Kompleksitas Ruang : O(d) — stack rekursi sedalam pohon

    Args:
        node  (Node): Node yang sedang diproses.
        depth (int) : Kedalaman saat ini (untuk indentasi visual).
    """
    # BASE CASE: Node daun — tampilkan hasil
    if node.saran:
        print_result(node)
        return

    # TAMPILKAN PERTANYAAN dengan nomor langkah
    step = depth + 1
    print(f"  {Color.GRAY}[Langkah {step}]{Color.RESET}")
    print(f"  {Color.WHITE}{Color.BOLD}❓ {node.text}{Color.RESET}")
    print(f"  {Color.GREEN}  (y){Color.RESET} Ya    {Color.RED}  (n){Color.RESET} Tidak")
    print()

    # BACA INPUT dengan validasi
    while True:
        try:
            ans = input(f"  {Color.CYAN}➤ Jawaban Anda: {Color.RESET}").lower().strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {Color.YELLOW}Program dihentikan.{Color.RESET}\n")
            sys.exit(0)

        if ans in ['y', 'n']:
            break
        print(f"  {Color.RED}✗ Input tidak valid. Ketik 'y' untuk Ya atau 'n' untuk Tidak.{Color.RESET}\n")

    # Simpan ke riwayat
    label_ans = f"{Color.GREEN}Ya{Color.RESET}" if ans == 'y' else f"{Color.RED}Tidak{Color.RESET}"
    _question_history.append((step, node.text, label_ans))

    print()
    print_separator(width=60, color=Color.GRAY)
    print()

    # REKURSIF: Lanjutkan DFS ke cabang yang dipilih
    if ans == 'y':
        if node.ya:
            run_dfs(node.ya, depth + 1)
    else:
        if node.tidak:
            run_dfs(node.tidak, depth + 1)


# ──────────────────────────────────────────────────────────────────
#  RINGKASAN SESI
# ──────────────────────────────────────────────────────────────────

def print_session_summary():
    """
    Menampilkan ringkasan seluruh jawaban yang diberikan pada sesi ini.
    Berguna untuk pasien yang ingin mendokumentasikan gejala mereka.
    """
    if not _question_history:
        return

    print()
    print_separator("─", 62, Color.GRAY)
    print(f"  {Color.BOLD}{Color.WHITE}📝 RINGKASAN SESI{Color.RESET}")
    print_separator("─", 62, Color.GRAY)
    for step, question, answer in _question_history:
        # Potong pertanyaan jika terlalu panjang
        q_short = question if len(question) <= 48 else question[:45] + "..."
        print(f"  {Color.GRAY}{step}.{Color.RESET} {q_short}")
        print(f"     {Color.GRAY}Jawaban:{Color.RESET} {answer}")
    print_separator("─", 62, Color.GRAY)


# ──────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────────

def main():
    """
    Fungsi utama — mengelola siklus sesi diagnosa.

    Alur:
    1. Tampilkan header
    2. Bangun pohon keputusan (sekali)
    3. Loop sesi: jalankan DFS → tampilkan ringkasan → tanya ulang
    4. Tampilkan footer saat keluar
    """
    print_header()

    typewriter("  Selamat datang di DiagnoTree Pro.", 0.025, Color.WHITE)
    typewriter("  Sistem akan mengajukan beberapa pertanyaan seputar", 0.020, Color.GRAY)
    typewriter("  gejala yang Anda rasakan untuk membantu diagnosis awal.", 0.020, Color.GRAY)
    print()
    print(f"  {Color.YELLOW}⚕  Catatan: Hasil ini bersifat indikatif, bukan diagnosis medis resmi.{Color.RESET}")
    print()
    print_separator(width=62)
    print()

    # Bangun pohon sekali di awal
    pohon = build_decision_tree()

    sesi = 1
    while True:
        print(f"  {Color.MAGENTA}{Color.BOLD}━━ SESI DIAGNOSA #{sesi} ━━{Color.RESET}\n")

        # Reset riwayat tiap sesi baru
        _question_history.clear()

        # Jalankan penelusuran DFS
        run_dfs(pohon)

        # Tampilkan ringkasan jawaban
        print_session_summary()

        # Tanya apakah ingin diagnosa ulang
        print()
        try:
            ulang = input(f"  {Color.CYAN}🔄 Lakukan diagnosa baru? (y/n): {Color.RESET}").lower().strip()
        except (EOFError, KeyboardInterrupt):
            ulang = 'n'

        if ulang != 'y':
            break

        sesi += 1
        print()
        print_separator("═", 62, Color.CYAN)
        print()

    print_footer()


if __name__ == "__main__":
    main()