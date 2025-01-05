import tkinter as tk
from tkinter import ttk
import time
import json
from datetime import datetime, timedelta
import psutil
import win32gui
import win32process
from collections import defaultdict
from tkinter import messagebox
import sv_ttk
import os
from PIL import Image, ImageTk
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import sys
import pystray
from PIL import Image
import threading
import win32ui
import win32con
import win32api
import win32gui_struct
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import numpy as np

class ModernEkranTakip:
    def __init__(self):
        self.pencere = tk.Tk()
        self.pencere.title("Modern Ekran Süresi Takip")
        self.pencere.geometry("1000x800")
        
        # İkon önbelleği
        self.icon_cache = {}
        
        # Tema durumu
        self.tema = "dark"  # Varsayılan tema
        
        # Modern tema uygula
        sv_ttk.set_theme(self.tema)
        
        # Kategori veritabanını yükle veya oluştur
        self.kategori_dosyasi = 'kategoriler.json'
        self.kategoriler = self.kategori_veritabanini_yukle()
        
        # Veriler için sözlük
        self.uygulama_sureleri = defaultdict(float)
        self.uygulama_zaman_araliklari = defaultdict(list)
        self.kategori_sureleri = defaultdict(float)
        self.son_kontrol = time.time()
        self.aktif_uygulama = ""
        self.bugunun_tarihi = datetime.now().strftime('%d.%m.%Y')
        
        # Önceki verileri yükle
        self.onceki_verileri_yukle()
        
        # Sistem tepsisi ikonu için değişkenler
        self.icon = None
        self.icon_kapatiliyor = False
        
        # Notebook (sekmeli arayüz) oluştur
        self.notebook = ttk.Notebook(self.pencere)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ana takip sekmesi
        self.takip_sekmesi = ttk.Frame(self.notebook)
        self.notebook.add(self.takip_sekmesi, text="Anlık Takip")
        
        # İstatistik sekmesi
        self.istatistik_sekmesi = ttk.Frame(self.notebook)
        self.notebook.add(self.istatistik_sekmesi, text="İstatistikler")
        
        # Günlük İstatistik sekmesi
        self.gunluk_istatistik_sekmesi = ttk.Frame(self.notebook)
        self.notebook.add(self.gunluk_istatistik_sekmesi, text="Günlük İstatistik")
        
        self.arayuz_olustur()
        self.istatistik_arayuzu_olustur()
        self.gunluk_istatistik_arayuzu_olustur()
        self.icon_olustur()
        self.takip_baslat()
        
        # Pencere kapatma olayını yakala
        self.pencere.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bildirim göster
        messagebox.showinfo("Bilgi", "Program sistem tepsisinde çalışmaya devam edecek.\nUygulamayı açmak için sistem tepsisindeki ikona tıklayabilirsiniz.")

    def onceki_verileri_yukle(self):
        """CSV dosyasından bugüne ait verileri yükle ve topla"""
        try:
            csv_dosyasi = 'ekran_suresi_takip.csv'
            if os.path.exists(csv_dosyasi):
                df = pd.read_csv(csv_dosyasi)
                bugunun_verileri = df[df['Tarih'] == self.bugunun_tarihi]
                
                if not bugunun_verileri.empty:
                    # Aynı uygulamaların sürelerini topla
                    toplam_sureler = bugunun_verileri.groupby('Uygulama')['Süre (Saat)'].sum()
                    son_kullanımlar = bugunun_verileri.groupby('Uygulama')['Son Kullanım'].last()
                    
                    # Verileri uygulama sürelerine ekle
                    for uygulama, sure in toplam_sureler.items():
                        self.uygulama_sureleri[uygulama] = sure * 3600  # Saati saniyeye çevir
                        son_kullanim = son_kullanımlar[uygulama]
                        if son_kullanim != "-":
                            self.uygulama_zaman_araliklari[uygulama].append(son_kullanim)
                    
                    print(f"Bugüne ait {len(toplam_sureler)} uygulamanın verileri yüklendi.")
                
        except Exception as e:
            print(f"Önceki verileri yükleme hatası: {str(e)}")

    def get_file_icon(self, exe_name):
        """Windows'tan exe dosyasının ikonunu al"""
        if exe_name in self.icon_cache:
            return self.icon_cache[exe_name]
            
        try:
            # Sistem yollarını kontrol et
            system32_path = os.path.join(os.environ['SystemRoot'], 'System32', exe_name)
            program_files = os.path.join(os.environ['ProgramFiles'], exe_name)
            program_files_x86 = os.path.join(os.environ['ProgramFiles(x86)'], exe_name)
            
            possible_paths = [system32_path, program_files, program_files_x86]
            icon_path = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            if icon_path is None:
                icon_path = exe_name
            
            # Büyük ikon indeksi
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            
            large, small = win32gui.ExtractIconEx(icon_path, 0)
            if large:
                win32gui.DestroyIcon(large[0])
            
            if small:
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc = hdc.CreateCompatibleDC()
                
                hdc.SelectObject(hbmp)
                hdc.DrawIcon((0, 0), small[0])
                
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGBA',
                    (ico_x, ico_y),
                    bmpstr, 'raw', 'BGRA', 0, 1
                )
                
                # İkonu 16x16 boyutuna küçült
                img = img.resize((16, 16), Image.Resampling.LANCZOS)
                
                # PhotoImage oluştur
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[exe_name] = icon
                
                # Temizlik
                win32gui.DestroyIcon(small[0])
                hdc.DeleteDC()
                hbmp.DeleteObject()
                
                return icon
        except:
            # Hata durumunda varsayılan ikon
            img = Image.new('RGBA', (16, 16), (128, 128, 128, 255))
            icon = ImageTk.PhotoImage(img)
            self.icon_cache[exe_name] = icon
            return icon
            
        return None

    def arayuz_olustur(self):
        # Ana frame
        self.ana_frame = ttk.Frame(self.takip_sekmesi)
        self.ana_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Üst kontrol paneli
        self.kontrol_panel = ttk.Frame(self.ana_frame)
        self.kontrol_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Üst panel sol kısım (tarih)
        self.ust_sol_panel = ttk.Frame(self.kontrol_panel)
        self.ust_sol_panel.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Üst panel sağ kısım (tema butonu)
        self.ust_sag_panel = ttk.Frame(self.kontrol_panel)
        self.ust_sag_panel.pack(side=tk.RIGHT, padx=5)
        
        # Tema değiştirme butonu
        self.tema_buton = ttk.Button(
            self.ust_sag_panel,
            text="🌙 Dark Mod" if self.tema == "light" else "☀️ Light Mod",
            command=self.tema_degistir,
            style='Accent.TButton'
        )
        self.tema_buton.pack(side=tk.RIGHT)
        
        # Tarih gösterimi
        self.tarih_label = ttk.Label(self.ust_sol_panel, 
                                    text=f"Tarih: {self.bugunun_tarihi}", 
                                    font=('Helvetica', 12, 'bold'))
        self.tarih_label.pack(side=tk.LEFT, pady=(0, 10))
        
        # Kategori paneli
        self.kategori_panel = ttk.Frame(self.ana_frame)
        self.kategori_panel.pack(fill=tk.X, pady=(0, 10))
        
        self.kategori_frameler = {}
        self.kategori_etiketler = {}
        
        # Kategorileri grid ile yerleştir
        for i, kategori in enumerate(list(self.kategoriler.keys()) + ["Diğer"]):
            frame = ttk.LabelFrame(self.kategori_panel, text=kategori)
            frame.grid(row=0, column=i, padx=5, sticky="ew")
            self.kategori_panel.grid_columnconfigure(i, weight=1)
            
            etiket = ttk.Label(frame, text="0.00 saat")
            etiket.pack(pady=5)
            
            self.kategori_frameler[kategori] = frame
            self.kategori_etiketler[kategori] = etiket
        
        # TreeView paneli
        self.tree_panel = ttk.Frame(self.ana_frame)
        self.tree_panel.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(self.tree_panel, 
                                columns=("İkon", "Uygulama", "Kategori", "Süre", "Son Kullanım"), 
                                show="headings")
        self.tree.heading("İkon", text="")
        self.tree.heading("Uygulama", text="Uygulama")
        self.tree.heading("Kategori", text="Kategori")
        self.tree.heading("Süre", text="Süre (saat)")
        self.tree.heading("Son Kullanım", text="Son Kullanım")
        
        self.tree.column("İkon", width=30, anchor="center")
        self.tree.column("Uygulama", width=200)
        self.tree.column("Kategori", width=150)
        self.tree.column("Süre", width=100)
        self.tree.column("Son Kullanım", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # TreeView'e sağ tık olayı ekle
        self.tree.bind("<Button-3>", self.kategori_menu_goster)

    def icon_olustur(self):
        # Basit bir ikon oluştur (16x16 piksel, mavi renk - RGB: 65, 105, 225)
        image = Image.new('RGB', (16, 16), color=(65, 105, 225))
        
        # Sistem tepsisi menüsü
        menu = (
            pystray.MenuItem('Göster', self.show_window),
            pystray.MenuItem('Çıkış', self.quit_window)
        )
        
        self.icon = pystray.Icon("ekran_takip", image, "Ekran Süresi Takip", menu)
        
        # İkonu ayrı bir thread'de başlat
        icon_thread = threading.Thread(target=self.icon.run)
        icon_thread.daemon = True
        icon_thread.start()

    def quit_window(self, icon, item):
        """Programı kapatırken verileri kaydet"""
        self.verileri_kaydet()  # Verileri kaydet
        self.icon_kapatiliyor = True
        icon.stop()
        self.pencere.after(0, self.pencere.destroy)
        
    def show_window(self, icon, item):
        self.pencere.after(0, self._show_window)
        
    def _show_window(self):
        self.pencere.deiconify()
        self.pencere.focus_force()
        
    def on_closing(self):
        """Pencere kapatıldığında çağrılır"""
        if not self.icon_kapatiliyor:
            self.pencere.withdraw()
            return "break"
        
    def takip_baslat(self):
        self.uygulama_takip()
        
    def aktif_pencere_al(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except:
            return "bilinmeyen.exe"

    def uygulama_kategorisi(self, uygulama):
        """Uygulamanın kategorisini bul"""
        for kategori, uygulamalar in self.kategoriler.items():
            if uygulama.lower() in [u.lower() for u in uygulamalar]:
                return kategori
        return "Diğer"

    def uygulama_takip(self):
        simdiki_tarih = datetime.now().strftime('%d.%m.%Y')
        if simdiki_tarih != self.bugunun_tarihi:
            # Gün değişiminde verileri kaydet
            self.verileri_kaydet()
            
            # Yeni gün için sıfırla
            self.verileri_sifirla()
            self.bugunun_tarihi = simdiki_tarih
            self.tarih_label.configure(text=f"Tarih: {self.bugunun_tarihi}")
            
            # Yeni günün önceki verilerini yükle
            self.onceki_verileri_yukle()
        
        aktif_uygulama = self.aktif_pencere_al()
        simdiki_zaman = time.time()
        gecen_sure = simdiki_zaman - self.son_kontrol
        
        if aktif_uygulama != self.aktif_uygulama:
            if self.aktif_uygulama:
                self.uygulama_zaman_araliklari[self.aktif_uygulama].append(
                    datetime.now().strftime('%H:%M')
                )
            self.aktif_uygulama = aktif_uygulama
        
        self.uygulama_sureleri[aktif_uygulama] += gecen_sure
        self.son_kontrol = simdiki_zaman
        
        # Her 5 dakikada bir otomatik kaydet
        if int(simdiki_zaman) % 300 == 0:
            self.verileri_kaydet()
        
        self.verileri_guncelle()
        self.pencere.after(1000, self.uygulama_takip)

    def verileri_guncelle(self):
        """Arayüzdeki verileri güncelle"""
        try:
            # Kategori sürelerini güncelle
            self.kategori_sureleri.clear()
            for uygulama, sure in self.uygulama_sureleri.items():
                kategori = self.uygulama_kategorisi(uygulama)
                self.kategori_sureleri[kategori] += sure
            
            # Kategori etiketlerini güncelle
            for kategori, sure in self.kategori_sureleri.items():
                if kategori in self.kategori_etiketler:
                    self.kategori_etiketler[kategori].configure(text=f"{sure/3600:.2f} saat")
            
            # TreeView'ı temizle
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Uygulamaları süreye göre sırala ve ekle
            for uygulama, sure in sorted(self.uygulama_sureleri.items(), key=lambda x: x[1], reverse=True):
                if sure > 0:  # Sadece aktif kullanımı olan uygulamaları göster
                    kategori = self.uygulama_kategorisi(uygulama)
                    son_kullanim = self.uygulama_zaman_araliklari[uygulama][-1] if self.uygulama_zaman_araliklari[uygulama] else "-"
                    
                    try:
                        # İkonu al
                        icon = self.get_file_icon(uygulama)
                        
                        # TreeView'a ekle
                        if icon:
                            self.tree.insert("", tk.END, values=(
                                "",  # İkon sütunu için boş değer
                                uygulama,
                                kategori,
                                f"{sure/3600:.2f}",
                                son_kullanim
                            ), image=icon)
                        else:
                            # İkon yoksa ikonsuz ekle
                            self.tree.insert("", tk.END, values=(
                                "",
                                uygulama,
                                kategori,
                                f"{sure/3600:.2f}",
                                son_kullanim
                            ))
                    except Exception as e:
                        print(f"Uygulama ekleme hatası ({uygulama}): {str(e)}")
                        # Hata durumunda ikonsuz ekle
                        self.tree.insert("", tk.END, values=(
                            "",
                            uygulama,
                            kategori,
                            f"{sure/3600:.2f}",
                            son_kullanim
                        ))
        
        except Exception as e:
            print(f"Veri güncelleme hatası: {str(e)}")
            # Kritik hata durumunda kullanıcıyı bilgilendir
            messagebox.showerror("Hata", "Veriler güncellenirken bir hata oluştu!")

    def verileri_sifirla(self):
        self.uygulama_sureleri.clear()
        self.uygulama_zaman_araliklari.clear()
        self.kategori_sureleri.clear()
        self.verileri_guncelle()

    def baslat(self):
        try:
            self.pencere.mainloop()
        finally:
            if self.icon:
                self.icon.stop()

    def istatistik_arayuzu_olustur(self):
        # Kontrol paneli
        kontrol_frame = ttk.Frame(self.istatistik_sekmesi)
        kontrol_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Tarih aralığı seçimi
        ttk.Label(kontrol_frame, text="Tarih Aralığı:", 
                 font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        self.tarih_secimi = ttk.Combobox(kontrol_frame, 
                                        values=["Son 7 Gün", "Son 30 Gün", "Tüm Zamanlar"],
                                        state="readonly", width=15)
        self.tarih_secimi.set("Son 7 Gün")
        self.tarih_secimi.pack(side=tk.LEFT, padx=5)
        
        # Yenile butonu
        ttk.Button(kontrol_frame, text="Yenile",
                  command=self.istatistikleri_goster,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # İstatistik özeti için frame
        self.ozet_frame = ttk.Frame(self.istatistik_sekmesi)
        self.ozet_frame.pack(fill=tk.X)
        
        # Grafikler için frame
        self.grafik_frame = ttk.Frame(self.istatistik_sekmesi)
        self.grafik_frame.pack(fill=tk.BOTH, expand=True)

    def istatistikleri_goster(self):
        try:
            # Mevcut grafikleri temizle
            for widget in self.grafik_frame.winfo_children():
                widget.destroy()
            for widget in self.ozet_frame.winfo_children():
                widget.destroy()
            
            # CSV dosyasını oku
            df = pd.read_csv('ekran_suresi_takip.csv')
            print("CSV dosyası okundu:", len(df), "kayıt bulundu")
            
            # Tarihleri datetime'a çevir
            df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y')
            print("Tarihler dönüştürüldü")
            
            # Sadece var olan tarihleri al ve sırala
            mevcut_tarihler = sorted(df['Tarih'].unique())
            
            # Tarih aralığını filtrele
            if self.tarih_secimi.get() == "Son 7 Gün":
                son_tarih = mevcut_tarihler[-1]
                baslangic_tarihi = max(mevcut_tarihler[0], son_tarih - pd.Timedelta(days=6))
                df = df[(df['Tarih'] >= baslangic_tarihi) & (df['Tarih'] <= son_tarih)]
            elif self.tarih_secimi.get() == "Son 30 Gün":
                son_tarih = mevcut_tarihler[-1]
                baslangic_tarihi = max(mevcut_tarihler[0], son_tarih - pd.Timedelta(days=29))
                df = df[(df['Tarih'] >= baslangic_tarihi) & (df['Tarih'] <= son_tarih)]
            
            # Günlük kullanım grafiği için verileri hazırla
            gunluk_kullanim = df.groupby('Tarih')['Süre (Saat)'].sum().reset_index()
            gunluk_kullanim = gunluk_kullanim.sort_values('Tarih')  # Tarihe göre sırala
            
            # Ana figür oluştur
            fig = plt.figure(figsize=(15, 12))
            gs = fig.add_gridspec(3, 2, 
                                height_ratios=[1, 1, 1], 
                                hspace=1.0,
                                wspace=0.4)
            
            # 1. Günlük Toplam Kullanım Grafiği
            ax1 = fig.add_subplot(gs[0, :])
            ax1.plot(range(len(gunluk_kullanim)), gunluk_kullanim['Süre (Saat)'], 
                    color='#2196F3', linewidth=2, marker='o')
            ax1.fill_between(range(len(gunluk_kullanim)), gunluk_kullanim['Süre (Saat)'], 
                           alpha=0.2, color='#2196F3')
            ax1.set_xticks(range(len(gunluk_kullanim)))
            ax1.set_xticklabels([d.strftime('%d.%m.%Y') for d in gunluk_kullanim['Tarih']], 
                               rotation=0)
            ax1.grid(True, alpha=0.3)
            
            # 2. Kategori Pasta Grafiği
            ax2 = fig.add_subplot(gs[1, 0])
            kategori_kullanim = df.groupby('Kategori')['Süre (Saat)'].sum()
            colors = ['#FF9800', '#2196F3', '#4CAF50', '#9C27B0', '#F44336']
            
            # Pasta grafiği çiz
            wedges, texts, autotexts = ax2.pie(kategori_kullanim.values,
                                             labels=[''] * len(kategori_kullanim),
                                             colors=colors[:len(kategori_kullanim)],
                                             autopct='',
                                             startangle=90)
            
            # Etiketleri ve yüzdeleri alt alta ekle
            labels_with_pcts = []
            for label, val in zip(kategori_kullanim.index, kategori_kullanim.values):
                percentage = val/kategori_kullanim.sum()*100
                if percentage >= 1:  # %1'den büyük değerleri göster
                    labels_with_pcts.append(f'{label}\n({percentage:.1f}%)')
                elif percentage > 0:  # %1'den küçük değerleri tek ondalıklı göster
                    labels_with_pcts.append(f'{label}\n({percentage:.1f}%)')
            
            # Legend'ı grafiğin soluna yerleştir ve boyutunu ayarla
            ax2.legend(wedges, labels_with_pcts,
                      title="Kategoriler",
                      loc="center right",
                      bbox_to_anchor=(-0.2, 0.5),
                      fontsize=9,
                      labelspacing=1.2)  # Etiketler arası boşluğu artır
            
            # 3. En Çok Kullanılan Uygulamalar
            ax3 = fig.add_subplot(gs[1, 1])
            uygulama_kullanim = df.groupby('Uygulama')['Süre (Saat)'].sum().sort_values(ascending=True).tail(5)
            bars = ax3.barh(range(len(uygulama_kullanim)), uygulama_kullanim.values,
                          color='#2196F3')
            ax3.set_yticks(range(len(uygulama_kullanim)))
            ax3.set_yticklabels(uygulama_kullanim.index)
            
            for i, v in enumerate(uygulama_kullanim.values):
                ax3.text(v + 0.1, i, f'{v:.1f}s', va='center')
            
            # 4. Gece/Gündüz Kullanım Grafiği
            ax4 = fig.add_subplot(gs[2, :])
            
            # Başlangıç saatlerini işle
            def saat_donustur(x):
                try:
                    if pd.isna(x) or x == '-':
                        return 12
                    return int(x.split(':')[0])
                except:
                    return 12
            
            df['Saat'] = df['Saat'].apply(saat_donustur)
            
            def zaman_dilimi_hesapla(row):
                baslangic = row['Saat']
                sure = row['Süre (Saat)']
                if 0 <= baslangic < 12:
                    return sure, 0
                else:
                    return 0, sure
            
            df[['Gece', 'Gunduz']] = df.apply(zaman_dilimi_hesapla, axis=1, result_type='expand')
            
            # Sadece var olan günleri göster
            gunluk = df.groupby('Tarih').agg({
                'Gece': 'sum',
                'Gunduz': 'sum'
            }).reset_index()
            
            gunluk = gunluk.sort_values('Tarih')  # Tarihe göre sırala
            
            bar_width = 0.35
            x = np.arange(len(gunluk))
            
            gece = ax4.bar(x - bar_width/2, 
                         gunluk['Gece'],
                         bar_width,
                         label='Gece (00:00-11:59)',
                         color='#2196F3',
                         alpha=0.7)
            
            gunduz = ax4.bar(x + bar_width/2, 
                            gunluk['Gunduz'],
                            bar_width,
                            label='Gündüz (12:00-23:59)',
                            color='#FFA726',
                            alpha=0.7)
            
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax4.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.1f}',
                               ha='center', va='bottom',
                               fontsize=10, fontweight='bold')
            
            add_value_labels(gece)
            add_value_labels(gunduz)
            
            ax4.set_xticks(x)
            ax4.set_xticklabels([d.strftime('%d.%m.%Y') for d in gunluk['Tarih']],
                               rotation=0,
                               ha='center',
                               fontsize=10)
            
            ax4.legend(loc='upper right')
            ax4.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            # Grafikleri canvas'a ekle
            canvas = FigureCanvasTkAgg(fig, self.grafik_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            print("Grafikler başarıyla oluşturuldu")
            
        except Exception as e:
            print(f"Grafik oluşturma hatası: {str(e)}")
            import traceback
            print("Hata detayı:")
            print(traceback.format_exc())
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f'Grafik oluşturulamadı\nHata: {str(e)}',
                   horizontalalignment='center',
                   verticalalignment='center')
            
            canvas = FigureCanvasTkAgg(fig, self.grafik_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def ozet_karti_olustur(self, parent, column, baslik, deger, renk):
        """Özet kartı oluştur"""
        kart = ttk.Frame(parent, style='Card.TFrame')
        kart.grid(row=0, column=column, padx=10, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)
        
        # Ba��lık
        ttk.Label(kart, text=baslik, 
                 font=('Helvetica', 10),
                 foreground='gray').pack(pady=(5,0))
        
        # Değer
        ttk.Label(kart, text=deger,
                 font=('Helvetica', 14, 'bold')).pack(pady=(0,5))

    def verileri_kaydet(self):
        """Mevcut verileri CSV dosyasına kaydet"""
        try:
            csv_dosyasi = 'ekran_suresi_takip.csv'
            saat = datetime.now().strftime('%H:%M:%S')
            
            # Verileri hazırla
            veriler = []
            for uygulama, sure in self.uygulama_sureleri.items():
                kategori = self.uygulama_kategorisi(uygulama)
                son_kullanim = self.uygulama_zaman_araliklari[uygulama][-1] if self.uygulama_zaman_araliklari[uygulama] else "-"
                veriler.append({
                    'Tarih': self.bugunun_tarihi,
                    'Saat': saat,
                    'Uygulama': uygulama,
                    'Kategori': kategori,
                    'Süre (Saat)': round(sure/3600, 2),
                    'Son Kullanım': str(son_kullanim)
                })
            
            # Yeni DataFrame oluştur
            yeni_df = pd.DataFrame(veriler)
            
            try:
                # Mevcut CSV dosyasını oku
                mevcut_df = pd.read_csv(csv_dosyasi, encoding='utf-8-sig')
                # Bugünün verilerini sil
                mevcut_df = mevcut_df[mevcut_df['Tarih'] != self.bugunun_tarihi]
            except FileNotFoundError:
                mevcut_df = pd.DataFrame()
            except Exception as e:
                print(f"CSV okuma hatası: {str(e)}")
                mevcut_df = pd.DataFrame()
            
            # Verileri birleştir ve kaydet
            guncel_df = pd.concat([mevcut_df, yeni_df], ignore_index=True)
            guncel_df.to_csv(csv_dosyasi, index=False, encoding='utf-8-sig')
            print(f"{len(veriler)} uygulamanın verileri kaydedildi.")
            
            # Kayıt işlemi başarılı olduysa tarihleri güncelle
            if hasattr(self, 'tarih_combo'):
                self.tarihleri_yukle()
            
        except Exception as e:
            print(f"Veri kaydetme hatası: {str(e)}")

    def kategori_veritabanini_yukle(self):
        """Kategori veritabanını yükle veya varsayılan kategori listesini oluştur"""
        varsayilan_kategoriler = {
            "Sosyal Medya & İletişim": [
                # Web Tarayıcıları
                "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe", "vivaldi.exe",
                # Mesajlaşma ve Görüntülü Görüşme
                "discord.exe", "telegram.exe", "whatsapp.exe", "teams.exe", "slack.exe",
                "zoom.exe", "skype.exe", "signal.exe", "viber.exe", "line.exe",
                # Sosyal Medya Uygulamaları
                "twitter.exe", "instagram.exe", "facebook.exe", "messenger.exe", "wechat.exe"
            ],
            "Oyun & Eğlence": [
                # Oyun Platformlar
                "steam.exe", "epicgameslauncher.exe", "galaxyclient.exe", "origin.exe", "ubisoftconnect.exe",
                "battlenet.exe", "riotclientservices.exe", "playnite.exe",
                # Popüler Oyunlar
                "league of legends.exe", "valorant.exe", "minecraft.exe", "fortnite.exe",
                "gta5.exe", "csgo.exe", "dota2.exe", "overwatch.exe", "apex_legends.exe",
                "rocketleague.exe", "among us.exe", "pubg.exe",
                # Medya Oynatıcılar
                "spotify.exe", "vlc.exe", "wmplayer.exe", "musicbee.exe", "foobar2000.exe",
                "netflix.exe", "disney+.exe", "primevideo.exe"
            ],
            "Üretkenlik & Geliştirme": [
                # Kod Editörleri ve IDE'ler
                "code.exe", "pycharm64.exe", "idea64.exe", "eclipse.exe", "sublime_text.exe",
                "atom.exe", "webstorm64.exe", "androidstudio64.exe", "rider64.exe", "clion64.exe",
                # Ofis Uygulamaları
                "winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe", "onenote.exe",
                "acrobat.exe", "acrord32.exe", "libreoffice.exe", "wps.exe",
                # Not Alma ve Organizasyon
                "notepad.exe", "notepad++.exe", "obsidian.exe", "notion.exe", "evernote.exe",
                # Geliştirici Araçları
                "git.exe", "github.exe", "postman.exe", "docker.exe", "virtualbox.exe",
                "vmware.exe", "filezilla.exe", "putty.exe"
            ],
            "Tasarım & Multimedya": [
                # Adobe Ürünleri
                "photoshop.exe", "illustrator.exe", "indesign.exe", "premiere.exe",
                "aftereffects.exe", "animate.exe", "lightroom.exe", "audition.exe",
                # Diğer Tasarım Araçları
                "figma.exe", "sketch.exe", "xd.exe", "gimp.exe", "inkscape.exe",
                "blender.exe", "maya.exe", "3dsmax.exe", "zbrush.exe",
                # Video ve Ses Düzenleme
                "vegaspro.exe", "resolve.exe", "obs64.exe", "audacity.exe", "reaper.exe",
                "flstudio.exe", "ableton.exe", "cubase.exe"
            ],
            "Sistem & Yardımcı Programlar": [
                # Windows Sistem Araçları
                "explorer.exe", "taskmgr.exe", "cmd.exe", "powershell.exe",
                "control.exe", "mmc.exe", "regedit.exe", "services.exe",
                # Yardımcı Programlar
                "winrar.exe", "7zfm.exe", "ccleaner.exe", "teamviewer.exe", "anydesk.exe",
                "msiafterburner.exe", "cpuz.exe", "gpuz.exe", "hwinfo64.exe",
                # Güvenlik
                "avgui.exe", "mbam.exe", "360safe.exe", "kaspersky.exe", "norton.exe"
            ]
        }
        
        try:
            if os.path.exists(self.kategori_dosyasi):
                with open(self.kategori_dosyasi, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(self.kategori_dosyasi, 'w', encoding='utf-8') as f:
                    json.dump(varsayilan_kategoriler, f, ensure_ascii=False, indent=4)
                return varsayilan_kategoriler
        except:
            return varsayilan_kategoriler

    def kategori_veritabanini_kaydet(self):
        """Kategori veritabanını dosyaya kaydet"""
        try:
            with open(self.kategori_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.kategoriler, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Kategori kaydetme hatası: {str(e)}")

    def kategori_menu_goster(self, event):
        """Sağ tık menüsünü göster"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # Seçili uygulamayı al
            uygulama = self.tree.item(item)['values'][1]  # İkinci sütun uygulama adı
            
            # Menü oluştur
            menu = tk.Menu(self.pencere, tearoff=0)
            
            # Kategori alt menüsü
            kategori_menu = tk.Menu(menu, tearoff=0)
            for kategori in self.kategoriler.keys():
                kategori_menu.add_command(
                    label=kategori,
                    command=lambda k=kategori: self.uygulama_kategorisini_degistir(uygulama, k)
                )
            
            # Yeni kategori ekleme seçeneği
            kategori_menu.add_separator()
            kategori_menu.add_command(
                label="Yeni Kategori Oluştur...",
                command=lambda: self.yeni_kategori_olustur(uygulama)
            )
            
            menu.add_cascade(label="Kategori Değiştir", menu=kategori_menu)
            menu.tk_popup(event.x_root, event.y_root)

    def yeni_kategori_olustur(self, uygulama):
        """Yeni kategori oluşturma penceresi"""
        dialog = tk.Toplevel(self.pencere)
        dialog.title("Yeni Kategori")
        dialog.geometry("300x150")
        dialog.transient(self.pencere)
        dialog.grab_set()
        
        # Kategori adı girişi
        ttk.Label(dialog, text="Kategori Adı:").pack(pady=5)
        entry = ttk.Entry(dialog)
        entry.pack(pady=5)
        
        # Seçili uygulama bilgisi
        ttk.Label(dialog, text=f"Seçili Uygulama: {uygulama}", font=("Helvetica", 9, "italic")).pack(pady=5)
        
        def kaydet():
            yeni_kategori = entry.get().strip()
            if yeni_kategori:
                if yeni_kategori not in self.kategoriler:
                    # Yeni kategoriyi oluştur ve uygulamayı ekle
                    self.kategoriler[yeni_kategori] = [uygulama]
                    
                    # Eski kategoriden kaldır
                    for kategori, uygulamalar in self.kategoriler.items():
                        if kategori != yeni_kategori and uygulama.lower() in [u.lower() for u in uygulamalar]:
                            uygulamalar.remove(uygulama)
                    
                    # Veritabanını güncelle
                    self.kategori_veritabanini_kaydet()
                    
                    # Arayüzü güncelle
                    self.verileri_guncelle()
                    
                    messagebox.showinfo("Başarılı", f"'{yeni_kategori}' kategorisi oluşturuldu ve '{uygulama}' eklendi!")
                    dialog.destroy()
                else:
                    messagebox.showwarning("Uyarı", "Bu kategori zaten mevcut!")
        
        # Kaydet butonu
        ttk.Button(dialog, text="Kaydet", command=kaydet).pack(pady=10)
        
        # Enter tuşu ile kaydetme
        entry.bind('<Return>', lambda e: kaydet())
        
        # Pencereyi ortala
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Odağı entry'e ver
        entry.focus()

    def uygulama_kategorisini_degistir(self, uygulama, yeni_kategori):
        """Uygulamanın kategorisini değiştir"""
        # Eski kategoriden kaldır
        for kategori, uygulamalar in self.kategoriler.items():
            if uygulama.lower() in [u.lower() for u in uygulamalar]:
                uygulamalar.remove(uygulama)
        
        # Yeni kategoriye ekle
        if uygulama not in self.kategoriler[yeni_kategori]:
            self.kategoriler[yeni_kategori].append(uygulama)
        
        # Veritabanını güncelle
        self.kategori_veritabanini_kaydet()
        
        # Arayüzü güncelle
        self.verileri_guncelle()

    def gunluk_istatistik_arayuzu_olustur(self):
        # Kontrol paneli
        kontrol_frame = ttk.Frame(self.gunluk_istatistik_sekmesi)
        kontrol_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Tarih seçimi
        ttk.Label(kontrol_frame, text="Tarih Seçin:", 
                 font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Tarih seçici için ComboBox
        self.tarih_combo = ttk.Combobox(kontrol_frame, state="readonly", width=20)
        self.tarih_combo.pack(side=tk.LEFT, padx=5)
        
        # Mevcut tarihleri yükle
        self.tarihleri_yukle()
        
        # Yenile butonu
        ttk.Button(kontrol_frame, text="Göster",
                  command=self.secili_gun_istatistiklerini_goster,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Grafikler için frame
        self.gunluk_grafik_frame = ttk.Frame(self.gunluk_istatistik_sekmesi)
        self.gunluk_grafik_frame.pack(fill=tk.BOTH, expand=True)
        
    def tarihleri_yukle(self):
        """CSV dosyasından mevcut tarihleri yükle"""
        try:
            df = pd.read_csv('ekran_suresi_takip.csv')
            # Tarihleri datetime'a çevir
            df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y')
            # Tarihleri sırala ve tekrar orijinal formata çevir
            tarihler = sorted(df['Tarih'].unique(), reverse=True)  # En yeni tarihler başta
            tarihler = [tarih.strftime('%d.%m.%Y') for tarih in tarihler]
            
            self.tarih_combo['values'] = tarihler
            if tarihler:
                self.tarih_combo.set(tarihler[0])  # En son tarihi seç
                
            print(f"Toplam {len(tarihler)} tarih yüklendi")
            
        except Exception as e:
            print(f"Tarih yükleme hatası: {str(e)}")
            messagebox.showerror("Hata", "Tarihler yüklenirken bir hata oluştu!")

    def secili_gun_istatistiklerini_goster(self):
        """Seçili günün istatistiklerini göster"""
        try:
            # Mevcut grafikleri temizle
            for widget in self.gunluk_grafik_frame.winfo_children():
                widget.destroy()
            
            secili_tarih = self.tarih_combo.get()
            if not secili_tarih:
                messagebox.showwarning("Uyarı", "Lütfen bir tarih seçin!")
                return
            
            # CSV dosyasını oku ve seçili tarihe göre filtrele
            df = pd.read_csv('ekran_suresi_takip.csv')
            gunluk_veriler = df[df['Tarih'] == secili_tarih]
            
            if gunluk_veriler.empty:
                messagebox.showinfo("Bilgi", "Seçili tarih için veri bulunamadı!")
                return
            
            # Ana figür oluştur
            fig = plt.figure(figsize=(15, 10))
            gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
            
            # 1. Kategori Pasta Grafiği
            ax1 = fig.add_subplot(gs[0, 0])
            kategori_kullanim = gunluk_veriler.groupby('Kategori')['Süre (Saat)'].sum()
            colors = ['#FF9800', '#2196F3', '#4CAF50', '#9C27B0', '#F44336']
            
            wedges, texts, autotexts = ax1.pie(kategori_kullanim.values,
                                             labels=[''] * len(kategori_kullanim),
                                             colors=colors[:len(kategori_kullanim)],
                                             autopct='',
                                             startangle=90)
            
            # Etiketleri ekle
            labels_with_pcts = []
            for label, val in zip(kategori_kullanim.index, kategori_kullanim.values):
                percentage = val/kategori_kullanim.sum()*100
                if percentage >= 1:
                    labels_with_pcts.append(f'{label}\n({percentage:.1f}%)')
                elif percentage > 0:
                    labels_with_pcts.append(f'{label}\n({percentage:.1f}%)')
            
            ax1.legend(wedges, labels_with_pcts,
                      title="Kategoriler",
                      loc="center left",
                      bbox_to_anchor=(-0.1, 0.5),
                      fontsize=9,
                      labelspacing=1.2)
            
            ax1.set_title('Günlük Kategori Dağılımı', pad=20)
            
            # 2. En Çok Kullanılan Uygulamalar
            ax2 = fig.add_subplot(gs[0, 1])
            uygulama_kullanim = gunluk_veriler.groupby('Uygulama')['Süre (Saat)'].sum().sort_values(ascending=True).tail(5)
            bars = ax2.barh(range(len(uygulama_kullanim)), uygulama_kullanim.values,
                          color='#2196F3')
            ax2.set_yticks(range(len(uygulama_kullanim)))
            ax2.set_yticklabels(uygulama_kullanim.index)
            
            for i, v in enumerate(uygulama_kullanim.values):
                ax2.text(v + 0.1, i, f'{v:.1f}s', va='center')
            
            ax2.set_title('En Çok Kullanılan Uygulamalar', pad=20)
            
            # 3. Gece/Gündüz Kullanım Grafiği
            ax3 = fig.add_subplot(gs[1, :])
            
            def saat_donustur(x):
                try:
                    if pd.isna(x) or x == '-':
                        return 12
                    return int(x.split(':')[0])
                except:
                    return 12
            
            gunluk_veriler['Saat'] = gunluk_veriler['Saat'].apply(saat_donustur)
            
            def zaman_dilimi_hesapla(row):
                baslangic = row['Saat']
                sure = row['Süre (Saat)']
                if 0 <= baslangic < 12:
                    return sure, 0
                else:
                    return 0, sure
            
            gunluk_veriler[['Gece', 'Gunduz']] = gunluk_veriler.apply(zaman_dilimi_hesapla, axis=1, result_type='expand')
            
            toplam_gece = gunluk_veriler['Gece'].sum()
            toplam_gunduz = gunluk_veriler['Gunduz'].sum()
            
            zaman_dilimleri = ['Gece\n(00:00-11:59)', 'Gündüz\n(12:00-23:59)']
            degerler = [toplam_gece, toplam_gunduz]
            
            bars = ax3.bar(zaman_dilimleri, degerler,
                         color=['#2196F3', '#FFA726'])
            
            # Değerleri bar üzerine ekle
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}s',
                        ha='center', va='bottom')
            
            ax3.set_title('Gece/Gündüz Kullanım Dağılımı', pad=20)
            ax3.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            # Grafikleri canvas'a ekle
            canvas = FigureCanvasTkAgg(fig, self.gunluk_grafik_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
        except Exception as e:
            print(f"Günlük istatistik gösterme hatası: {str(e)}")
            messagebox.showerror("Hata", "İstatistikler gösterilirken bir hata oluştu!")

    def tema_degistir(self):
        """Temayı dark ve light mod arasında değiştirir"""
        if self.tema == "dark":
            self.tema = "light"
            self.tema_buton.configure(text="🌙 Dark Mod")
        else:
            self.tema = "dark"
            self.tema_buton.configure(text="☀️ Light Mod")
        
        sv_ttk.set_theme(self.tema)
        
        # Grafiklerin temasını güncelle
        self.grafik_temasini_guncelle()
        
        # İstatistik sekmesindeki grafikleri yenile
        if hasattr(self, 'istatistik_sekmesi'):
            self.istatistikleri_goster()
        
        # Günlük istatistik sekmesindeki grafikleri yenile
        if hasattr(self, 'gunluk_istatistik_sekmesi'):
            self.secili_gun_istatistiklerini_goster()

    def grafik_temasini_guncelle(self):
        """Grafiklerin temasını günceller"""
        if self.tema == "dark":
            plt.style.use('dark_background')
            self.grafik_renkleri = ['#FF9800', '#2196F3', '#4CAF50', '#9C27B0', '#F44336']
        else:
            plt.style.use('default')
            self.grafik_renkleri = ['#FF9800', '#2196F3', '#4CAF50', '#9C27B0', '#F44336']

if __name__ == "__main__":
    uygulama = ModernEkranTakip()
    uygulama.baslat()
