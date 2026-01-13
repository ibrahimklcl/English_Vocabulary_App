import customtkinter as ctk
import random
import os

# CustomTkinter ayarları
ctk.set_appearance_mode("Dark")  # [GÜNCELLENDİ] Başlangıç modu Koyu olarak ayarlandı
ctk.set_default_color_theme("blue")

# Dosya yolları
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
WORDS_FILE = os.path.join(BASE_PATH, "words.txt")
PROGRESS_FILE = os.path.join(BASE_PATH, "progress.txt")

# Kelimeleri oku
def kelimeleri_yukle(dosya=WORDS_FILE):
    kelimeler = {}
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    ing, tr = line.strip().split("=")
                    kelimeler[ing.strip()] = tr.strip()
    except FileNotFoundError:
        print(f"Uyarı: {dosya} bulunamadı.")
        # Demo kelimeler, dosya yoksa programın çalışması için
        return {"hello": "merhaba", "world": "dünya", "code": "kod"}
    return kelimeler

# İlerlemeden verileri oku
def ilerleme_yukle():
    if not os.path.exists(PROGRESS_FILE):
        return {"dogru": 0, "yanlis": 0, "yanlislar": []}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    data = {"dogru": 0, "yanlis": 0, "yanlislar": []}
    for line in lines:
        if line.startswith("dogru="):
            try: data["dogru"] = int(line.split("=")[1])
            except: data["dogru"] = 0
        elif line.startswith("yanlis="):
            try: data["yanlis"] = int(line.split("=")[1])
            except: data["yanlis"] = 0
        elif line.startswith("yanlislar="):
            raw = line.split("=")[1]
            data["yanlislar"] = raw.split(",") if raw else []
    return data

# İlerlemeyi kaydet
def ilerleme_kaydet(dogru, yanlis, yanlislar):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(f"dogru={dogru}\n")
        f.write(f"yanlis={yanlis}\n")
        f.write(f"yanlislar={','.join(yanlislar)}\n")

class KelimeUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Kelime Öğrenme Uygulaması")
        self.root.geometry("600x680") 
        self.root.resizable(False, False)

        # Kelimeleri ve ilerlemeyi yükle
        self.kelimeler = kelimeleri_yukle()
        prog = ilerleme_yukle()
        self.yanlislar = prog["yanlislar"].copy()
        self.pending_yanlis = self.yanlislar.copy()
        self.dogru_sayisi = prog["dogru"]
        self.yanlis_sayisi = prog["yanlis"]
        self.current_word = ""

        # Karıştırılmış kelimeler listesi
        self.sorulacak_kelimeler = list(self.kelimeler.keys())
        random.shuffle(self.sorulacak_kelimeler)
        self.sorulan_kelimeler = set()

        # --- Arayüzü Grid (ızgara) ile düzenle ---
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=2) # Soru alanı
        self.root.grid_rowconfigure(1, weight=1) # Giriş alanı
        self.root.grid_rowconfigure(2, weight=1) # Bildirim alanı
        self.root.grid_rowconfigure(3, weight=1) # İlerleme çubuğu alanı
        self.root.grid_rowconfigure(4, weight=1) # Ana Buton alanı
        self.root.grid_rowconfigure(5, weight=1) # Diğer Buton alanı
        self.root.grid_rowconfigure(6, weight=2) # Dinamik geri bildirim alanı

        # 1. Soru Alanı
        self.label_soru = ctk.CTkLabel(root, text="Başlamak için 'Yeni Kelime' butonuna bas",
                                       font=("Segoe UI", 26, "bold")) 
        self.label_soru.grid(row=0, column=0, sticky="nsew", pady=(20, 10))

        # 2. Giriş Alanı
        self.entry_cevap = ctk.CTkEntry(root, 
                                        font=("Segoe UI", 20),
                                        width=400,
                                        height=50,
                                        placeholder_text="Cevabınızı buraya yazın...")
        self.entry_cevap.grid(row=1, column=0, sticky="n", pady=10)
        self.entry_cevap.bind("<Return>", lambda event: self.kontrol_et())

        # 3. Bildirim Alanı
        self.label_notify = ctk.CTkLabel(root, text="", font=("Segoe UI", 16, "bold"))
        self.label_notify.grid(row=2, column=0, sticky="n", pady=5)

        # 4. İlerleme Alanı
        self.progress_bar = ctk.CTkProgressBar(root, 
                                               width=400,
                                               height=12)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=3, column=0, sticky="n", pady=15)
        
        self.label_skor = ctk.CTkLabel(root, 
                                       text=f"Doğru: {self.dogru_sayisi} | Yanlış: {self.yanlis_sayisi}",
                                       font=("Segoe UI", 15, "bold"))
        self.label_skor.grid(row=3, column=0, sticky="n", pady=(35, 0))

        # 5. Ana Buton Alanı
        self.frame_main_buttons = ctk.CTkFrame(root, fg_color="transparent")
        self.frame_main_buttons.grid(row=4, column=0, pady=(15, 5))

        self.button_kontrol = ctk.CTkButton(self.frame_main_buttons, 
                                            text="Kontrol Et", 
                                            width=150, height=45,
                                            font=("Segoe UI", 15, "bold")) 
        self.button_kontrol.grid(row=0, column=0, padx=7, pady=5)
        self.button_kontrol.configure(command=self.kontrol_et)

        self.button_goster = ctk.CTkButton(self.frame_main_buttons, 
                                           text="Cevabı Göster 💡", 
                                           width=150, height=45,
                                           font=("Segoe UI", 15, "bold"),
                                           fg_color="#FFA000", hover_color="#FF8F00")
        self.button_goster.grid(row=0, column=1, padx=7, pady=5)
        self.button_goster.configure(command=self.cevabi_goster)

        self.button_yeni = ctk.CTkButton(self.frame_main_buttons, 
                                         text="Yeni Kelime 🔄", 
                                         width=150, height=45,
                                         font=("Segoe UI", 15, "bold"))
        self.button_yeni.grid(row=0, column=2, padx=7, pady=5)
        self.button_yeni.configure(command=self.yeni_kelime)
        
        # 6. Diğer Butonlar Alanı
        self.frame_util_buttons = ctk.CTkFrame(root, fg_color="transparent")
        self.frame_util_buttons.grid(row=5, column=0, pady=(0, 15))

        self.button_yanlislar = ctk.CTkButton(self.frame_util_buttons, text="Yanlışlar ❌", 
                                              width=120, height=38, font=("Segoe UI", 12),
                                              fg_color="#D32F2F", hover_color="#B71C1C")
        self.button_yanlislar.grid(row=0, column=0, padx=5, pady=5)
        self.button_yanlislar.configure(command=self.yanlis_popup)
        
        self.button_liste = ctk.CTkButton(self.frame_util_buttons, text="Tüm Liste 📚", 
                                          width=120, height=38, font=("Segoe UI", 12))
        self.button_liste.grid(row=0, column=1, padx=5, pady=5)
        self.button_liste.configure(command=self.kelime_listesi_popup)
        
        self.button_yenile = ctk.CTkButton(self.frame_util_buttons, text="Yenile 🔃", 
                                           width=120, height=38, font=("Segoe UI", 12))
        self.button_yenile.grid(row=0, column=2, padx=5, pady=5)
        self.button_yenile.configure(command=self.kelimeleri_yeniden_yukle)
        
        self.button_sifirla = ctk.CTkButton(self.frame_util_buttons, text="Sıfırla 🗑️", 
                                          width=120, height=38, font=("Segoe UI", 12),
                                          fg_color="#757575", hover_color="#424242")
        self.button_sifirla.grid(row=0, column=3, padx=5, pady=5)
        self.button_sifirla.configure(command=self.sifirla)
        
        # [GÜNCELLENDİ] Anahtarın varsayılan metni "Açık Mod" oldu
        self.theme_switch = ctk.CTkSwitch(self.frame_util_buttons, text="Açık Mod", 
                                          command=self.toggle_theme, font=("Segoe UI", 12))
        self.theme_switch.grid(row=0, column=4, padx=10, pady=5)
        
        # 7. Dinamik Geri Bildirim Çerçevesi
        self.feedback_frame = ctk.CTkFrame(self.root, height=100, corner_radius=0)
        self.feedback_frame.grid(row=6, column=0, sticky="nsew", padx=0, pady=0)
        self.feedback_frame.grid_columnconfigure(0, weight=1)
        self.feedback_frame.grid_rowconfigure(0, weight=1)
        
        self.feedback_label = ctk.CTkLabel(self.feedback_frame, text="", font=("Segoe UI", 22, "bold"), text_color="white")
        self.feedback_label.grid(row=0, column=0, sticky="nsew")
        
        self.feedback_frame.grid_remove() 
        # ------------------- Arayüz Bitişi -------------------

    # Yeni kelime
    def yeni_kelime(self):
        kalan = [w for w in self.sorulacak_kelimeler if w not in self.sorulan_kelimeler]
        if not kalan and not self.pending_yanlis:
            self.tum_kelimeler_bitti()
            return
            
        if kalan:
            self.current_word = kalan[0]
            self.sorulan_kelimeler.add(self.current_word)
        elif self.pending_yanlis:
            self.current_word = self.pending_yanlis.pop(0)
            
        self.label_soru.configure(text=f"Bu kelimenin Türkçesi nedir? ➡ {self.current_word}")
        self.entry_cevap.delete(0, ctk.END)
        self.label_notify.configure(text="") # Bildirimi temizle

        # Progress bar'ı güncelle
        toplam_kelime = len(self.kelimeler)
        sorulan_sayisi = len([w for w in self.sorulan_kelimeler if w in self.kelimeler])
        
        if toplam_kelime > 0:
            ilerleme = sorulan_sayisi / toplam_kelime
            self.progress_bar.set(ilerleme)
        else:
            self.progress_bar.set(0)

    # Cevap kontrolü
    def kontrol_et(self):
        if not self.current_word:
            self.label_notify.configure(text="Önce yeni kelime seçin!", text_color="orange")
            return
            
        cevap = self.entry_cevap.get().strip().lower()
        
        # Cevap girilmemişse kontrol etme
        if not cevap:
            self.label_notify.configure(text="Lütfen bir cevap girin.", text_color="orange")
            return

        dogru = self.kelimeler[self.current_word].lower()
        
        if cevap == dogru:
            self.dogru_sayisi += 1
            if self.current_word in self.yanlislar:
                self.yanlislar.remove(self.current_word)
            if self.current_word in self.pending_yanlis:
                 self.pending_yanlis.remove(self.current_word)
            
            self.label_skor.configure(text=f"Doğru: {self.dogru_sayisi} | Yanlış: {self.yanlis_sayisi}")
            ilerleme_kaydet(self.dogru_sayisi, self.yanlis_sayisi, self.yanlislar)
            
            self.goster_geri_bildirim("dogru")

        else:
            self.yanlis_sayisi += 1
            if self.current_word not in self.yanlislar:
                self.yanlislar.append(self.current_word)
            if self.current_word not in self.pending_yanlis:
                self.pending_yanlis.append(self.current_word)

            self.label_skor.configure(text=f"Doğru: {self.dogru_sayisi} | Yanlış: {self.yanlis_sayisi}")
            ilerleme_kaydet(self.dogru_sayisi, self.yanlis_sayisi, self.yanlislar)

            self.goster_geri_bildirim("yanlis", dogru)

    # Cevabı Göster Fonksiyonu
    def cevabi_goster(self):
        if not self.current_word:
            self.label_notify.configure(text="Önce yeni kelime seçin!", text_color="orange")
            return
            
        dogru = self.kelimeler[self.current_word].lower()
        
        self.yanlis_sayisi += 1
        if self.current_word not in self.yanlislar:
            self.yanlislar.append(self.current_word)
        if self.current_word not in self.pending_yanlis:
            self.pending_yanlis.append(self.current_word)

        self.label_skor.configure(text=f"Doğru: {self.dogru_sayisi} | Yanlış: {self.yanlis_sayisi}")
        ilerleme_kaydet(self.dogru_sayisi, self.yanlis_sayisi, self.yanlislar)
        
        self.goster_geri_bildirim("ipucu", dogru)

    # Dinamik Geri Bildirim Yöneticisi
    def goster_geri_bildirim(self, tip, dogru_cevap=None):
        # Kontrolleri gizle
        self.frame_main_buttons.grid_remove()
        self.frame_util_buttons.grid_remove()
        self.entry_cevap.grid_remove()
        
        if tip == "dogru":
            self.feedback_frame.configure(fg_color="#2E7D32") # Koyu Yeşil
            self.feedback_label.configure(text="✅ Doğru!")
        elif tip == "yanlis":
            self.feedback_frame.configure(fg_color="#C62828") # Koyu Kırmızı
            self.feedback_label.configure(text=f"❌ Yanlış!\nDoğru: {dogru_cevap}")
        elif tip == "ipucu":
            self.feedback_frame.configure(fg_color="#FFA000") # Turuncu
            self.feedback_label.configure(text=f"💡 Doğru Cevap: {dogru_cevap}")
            
        self.feedback_frame.grid()
        
        self.root.after(1500, self.siradaki_soru_hazirla)

    # Arayüzü sıradaki soru için hazırlayan fonksiyon
    def siradaki_soru_hazirla(self):
        self.feedback_frame.grid_remove()
        
        self.entry_cevap.grid()
        self.entry_cevap.focus_set() 
        self.frame_main_buttons.grid()
        self.frame_util_buttons.grid()
        
        self.yeni_kelime()

    # Tüm kelimeler bittiğinde
    def tum_kelimeler_bitti(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("Tebrikler!")
        popup.geometry("400x250")
        popup.transient(self.root); popup.grab_set()

        label = ctk.CTkLabel(popup, text="🎉 Tüm kelimeleri tamamladın!", font=("Segoe UI", 16, "bold"))
        label.pack(pady=15)
        
        if self.yanlislar:
            info_text = f"{len(self.yanlislar)} yanlış kelimen var. 'Yanlışlar ❌' butonundan görebilirsin."
        else:
            info_text = "Tebrikler, yanlış kelime yok! 🎯"
        ctk.CTkLabel(popup, text=info_text, font=("Segoe UI", 12)).pack(pady=5)

        def yeniden_baslat():
            popup.destroy()
            self.sorulan_kelimeler.clear()
            random.shuffle(self.sorulacak_kelimeler)
            self.pending_yanlis = self.yanlislar.copy()
            self.label_notify.configure(text="Liste sıfırlandı, tekrar başlıyoruz!", text_color="blue")
            self.progress_bar.set(0)
            self.root.after(500, self.yeni_kelime)

        ctk.CTkButton(popup, text="Yeniden Başlat", command=yeniden_baslat, width=140).pack(pady=8)
        ctk.CTkButton(popup, text="Kapat", command=popup.destroy, width=140).pack(pady=4)

    # Yanlış popup
    def yanlis_popup(self):
        if not self.yanlislar:
            self.label_notify.configure(text="Şu anda yanlış kelime yok.", text_color="orange")
            return
            
        popup = ctk.CTkToplevel(self.root)
        popup.title("Yanlış Kelimeler"); popup.geometry("420x340")
        popup.transient(self.root); popup.grab_set()

        scroll_frame = ctk.CTkScrollableFrame(popup, width=400, height=300)
        scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        for kelime in self.yanlislar:
            ctk.CTkLabel(scroll_frame, text=f"{kelime} = {self.kelimeler.get(kelime, '')}",
                         font=("Segoe UI", 13), text_color="red").pack(anchor="w", padx=16, pady=2)

    # Scroll destekli kelime listesi
    def kelime_listesi_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("Kelime Listesi"); popup.geometry("400x500")
        popup.transient(self.root); popup.grab_set()

        label = ctk.CTkLabel(popup, text="Kelime Durumları", font=("Segoe UI", 16, "bold"))
        label.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(popup, width=380, height=420)
        scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        for kelime in self.kelimeler.keys():
            renk = "gray" 
            if kelime in self.yanlislar: renk = "red"
            elif kelime in self.sorulan_kelimeler: renk = "green"
            ctk.CTkLabel(scroll_frame, text=f"{kelime} = {self.kelimeler[kelime]}",
                         font=("Segoe UI", 13), text_color=renk).pack(anchor="w", padx=5, pady=2)

    # Sıfırla
    def sifirla(self):
        self.dogru_sayisi = 0; self.yanlis_sayisi = 0
        self.yanlislar = []; self.pending_yanlis = []
        self.sorulan_kelimeler.clear()
        random.shuffle(self.sorulacak_kelimeler)
        self.label_skor.configure(text=f"Doğru: {self.dogru_sayisi} | Yanlış: {self.yanlis_sayisi}")
        self.label_notify.configure(text="İlerleme sıfırlandı!", text_color="orange")
        self.progress_bar.set(0)
        ilerleme_kaydet(self.dogru_sayisi, self.yanlis_sayisi, self.yanlislar)

    # Kelimeleri yeniden yükle
    def kelimeleri_yeniden_yukle(self):
        self.kelimeler = kelimeleri_yukle()
        self.sorulacak_kelimeler = list(self.kelimeler.keys())
        random.shuffle(self.sorulacak_kelimeler)
        self.sorulan_kelimeler.clear()
        self.pending_yanlis = self.yanlislar.copy()
        self.label_notify.configure(
            text=f"Kelimeler yenilendi, toplam {len(self.kelimeler)} kelime mevcut.", text_color="green"
        )
        self.label_soru.configure(text="Yeni kelimeleri görebilmek için 'Yeni Kelime' butonuna basın.")
        self.progress_bar.set(0)

    # Tema değiştirme fonksiyonu
    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        if mode == "Light":
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="Açık Mod")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="Koyu Mod")

# Çalıştır
if __name__ == "__main__":
    root = ctk.CTk()
    app = KelimeUygulamasi(root)
    root.mainloop()