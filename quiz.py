from manim import *
import random
import requests
import os
from mutagen.mp3 import MP3

class Quran(Scene):
    def construct(self):
        # 💡 إعدادات التحكم: رقم السورة ومعرّف القارئ
        SURAH_NUMBER = 62
        RECITER = "ar.abdulsamad" # يمكنك تغييره إلى "" أو أي قارئ آخر
        
        # إنشاء مجلد مؤقت لحفظ ملفات الصوت إذا لم يكن موجوداً
        if not os.path.exists("audio_temp"):
            os.makedirs("audio_temp")

        # 1. جلب بيانات السورة والصوت من الـ API
        print("\n" + "="*50)
        print(f"[*] جاري الاتصال بالـ API وسحب بيانات السورة رقم {SURAH_NUMBER}...")
        print("="*50 + "\n")
        
        surah_data = self.fetch_surah_data(SURAH_NUMBER, RECITER)
        
        if not surah_data:
            print("[!] فشل جلب البيانات. تأكد من اتصالك بالإنترنت.")
            return

        surah_name = surah_data["name"]
        ayahs_list = surah_data["ayahs"]

        # 2. بناء المشهد (الخلفية المضيئة والفقاعات المتحركة)
        bg = Rectangle(width=config.frame_width, height=config.frame_height, stroke_width=0)
        bg.set_color_by_gradient("#f2fff7", "#ffffff")
        self.add(bg)

        bubbles = VGroup()
        for _ in range(65):  
            radius = random.uniform(0.2, 0.55)
            bubble = Circle(
                radius=radius, color="#43a047", 
                fill_opacity=random.uniform(0.15, 0.35),
                stroke_color="#2e7d32", stroke_opacity=0.15, stroke_width=1
            )
            bubble.move_to([
                random.uniform(-config.frame_width/2, config.frame_width/2), 
                random.uniform(-config.frame_height/2, config.frame_height/2), 0
            ])
            bubble.vx = random.uniform(-0.25, 0.25)
            bubble.vy = random.uniform(-0.25, 0.25)
            bubbles.add(bubble)
        self.add(bubbles)

        def update_bubbles(mob, dt):
            limit_x = config.frame_width / 2
            limit_y = config.frame_height / 2
            for b in mob:
                b.shift([b.vx * dt, b.vy * dt, 0])
                if abs(b.get_x()) > limit_x: b.vx *= -1
                if abs(b.get_y()) > limit_y: b.vy *= -1
        bubbles.add_updater(update_bubbles)

        # 3. بناء صندوق العرض الزجاجي
        box = RoundedRectangle(
            corner_radius=0.4, width=10.5, height=3.5,
            fill_color="#ffffff", fill_opacity=0.7,  
            stroke_color="#2e7d32", stroke_opacity=0.4, stroke_width=2
        )
        self.play(FadeIn(box, scale=0.95), run_time=1.2, rate_func=smooth)

        # 4. استعراض الآيات ومزامنتهما مع الصوت ديناميكياً
        for index, ayah in enumerate(ayahs_list):
            text_str = ayah["text"]
            ayah_num = ayah["numberInSurah"]
            audio_url = ayah["audio"]

            # تحميل ملف الصوت للآية الحالية
            audio_path = f"audio_temp/ayah_{ayah_num}.mp3"
            self.download_audio(audio_url, audio_path)
            
            # حساب مدة الصوت الحقيقية
            audio_duration = MP3(audio_path).info.length

            # --- التعديل الجوهري للتعامل مع البسملة المدمجة في الآية الأولى ---
            if index == 0 and SURAH_NUMBER not in [1, 9] and text_str.startswith("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"):
                # نقتطع نص الآية بدون البسملة للمرحلة الثانية
                clean_ayah_text = text_str.replace("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "").strip()
                
                # تشغيل ملف الصوت (الذي يبدأ بالبسملة طبيعياً بصوت الشيخ المختار)
                self.add_sound(audio_path)
                
                # أولاً: عرض نص البسملة فقط
                bismillah_text = MarkupText('<span foreground="#1b5e20">« بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ »</span>', font="Amiri", font_size=34, weight=BOLD)
                info_text = MarkupText(f'<span foreground="#555555">📖 سورة {surah_name}</span>', font="Arial", font_size=16)
                
                bismillah_text.move_to(box.get_center() + UP * 0.25)
                info_text.next_to(bismillah_text, DOWN, buff=0.4)
                
                self.play(FadeIn(bismillah_text, shift=UP * 0.1), FadeIn(info_text, shift=UP * 0.1), run_time=0.8)
                
                # وقت انتظار مخصص لنطق البسملة (حوالي 2.3 ثانية لغالبية القراء كالـحُصري)
                self.wait(2.3)
                
                # الانتقال من نص البسملة إلى نص الآية الأولى
                self.play(FadeOut(bismillah_text), FadeOut(info_text), run_time=0.4)
                
                # ثانياً: تجهيز نص الآية الأولى الفعلي وعرضه
                quran_text = MarkupText(f'<span foreground="#1b5e20">« {clean_ayah_text} »</span>', font="Amiri", font_size=34, weight=BOLD)
                info_text = MarkupText(f'<span foreground="#555555">📖 سورة {surah_name} - آية {ayah_num}</span>', font="Arial", font_size=16)
                
                if quran_text.width > box.width - 1.0:
                    quran_text.scale((box.width - 1.2) / quran_text.width)
                
                quran_text.move_to(box.get_center() + UP * 0.25)
                info_text.next_to(quran_text, DOWN, buff=0.4)
                
                self.play(FadeIn(quran_text, shift=UP * 0.1), FadeIn(info_text, shift=UP * 0.1), run_time=0.6)
                
                # نخصم وقت البسملة المستهلك من إجمالي مدة ملف الصوت
                display_wait = max(0.5, audio_duration - 3.7)
                self.wait(display_wait)
                
            else:
                # المعالجة الطبيعية لباقي الآيات (أو للفاتحة والتوبة)
                quran_text = MarkupText(f'<span foreground="#1b5e20">« {text_str} »</span>', font="Amiri", font_size=34, weight=BOLD)
                info_text = MarkupText(f'<span foreground="#555555">📖 سورة {surah_name} - آية {ayah_num}</span>', font="Arial", font_size=16)

                if quran_text.width > box.width - 1.0:
                    quran_text.scale((box.width - 1.2) / quran_text.width)

                quran_text.move_to(box.get_center() + UP * 0.25)
                info_text.next_to(quran_text, DOWN, buff=0.4)

                self.add_sound(audio_path)
                
                self.play(
                    FadeIn(quran_text, shift=UP * 0.1),
                    FadeIn(info_text, shift=UP * 0.1),
                    run_time=1.0
                )
                
                display_wait = max(0.5, audio_duration - 1.5)
                self.wait(display_wait)

            # الانتقال السلس للآية التالية
            if index < len(ayahs_list) - 1:
                self.play(FadeOut(quran_text), FadeOut(info_text), run_time=0.5)
        
        self.wait(2)

    def fetch_surah_data(self, surah_number, reciter):
        url = f"https://api.alquran.cloud/v1/surah/{surah_number}/{reciter}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()["data"]
        except Exception as e:
            print(f"حدث خطأ أثناء جلب البيانات: {e}")
        return None

    def download_audio(self, url, save_path):
        if not os.path.exists(save_path):
            r = requests.get(url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
