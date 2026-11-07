import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from roboflow import Roboflow
from elevenlabs.client import ElevenLabs
from huggingface_hub import InferenceClient

# إعداد الصفحة
st.set_page_config(page_title="Smart Tourism Guide", layout="centered")

st.setTitle("🏛️ المرشد السياحي الذكي - موقع الحجر (قصر الفريد)")
st.caption("نظام التوثيق والرصد البصري المدعوم بالذكاء الاصطناعي والاستدعاءات الفعلية للخدمات")
st.markdown("---")

# استدعاء مفاتيح الأمان من Streamlit Secrets
ROBOFLOW_API_KEY = st.secrets.get("ROBOFLOW_API_KEY", "YOUR_ROBOFLOW_KEY")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
ELEVENLABS_API_KEY = st.secrets.get("ELEVENLABS_API_KEY", "YOUR_ELEVENLABS_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN", "YOUR_HF_TOKEN")

# تهيئة الخدمات برمجياً
if GEMINI_API_KEY != "YOUR_GEMINI_KEY":
    genai.configure(api_key=GEMINI_API_KEY)

# 1. قسم Roboflow (اكتشاف الكائنات والمعالم)
st.subheader("1. التعرف البصري (Roboflow Inference)")
uploaded_file = st.file_uploader("قم بررفع صورة المعلم الأثري...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة المدخلة للنظام", use_column_width=True)
    
    if st.button("تشغيل التحليل البصري بـ Roboflow"):
        with st.spinner("جاري التواصل مع نموذج Roboflow وتحليل المعالم..."):
            try:
                # استدعاء حقيقي لنموذج Roboflow (يتم تعديل اسم المشروع ورقم النسخة حسب مشروعك)
                rf = Roboflow(api_key=ROBOFLOW_API_KEY)
                project = rf.workspace().project("your-project-id")
                model = project.version("1").model
                
                # حفظ الصورة مؤقتًا للتحليل
                temp_path = "temp_img.jpg"
                image.save(temp_path)
                
                prediction = model.predict(temp_path, confidence=40, overlap=30).json()
                st.success("تم التحليل بنجاح بواسطة Roboflow!")
                st.json(prediction)
            except Exception as e:
                st.error(f"فشل الاتصال بـ Roboflow: تأكد من صحة المفتاح وإعدادات النموذج. الخطأ: {e}")

st.markdown("---")

# 2. قسم Gemini (التوليد والتحليل السياحي)
st.subheader("2. المرشد السياحي الذكي (Google Gemini AI)")
user_query = st.text_input("اسأل المرشد السياحي عن قصر الفريد أو تاريخ الموقع:", "اكتب نبذة تاريخية مختصرة عن قصر الفريد في مدائن صالح.")

if st.button("توليد الإجابة بواسطة Gemini"):
    with st.spinner("جاري التوليد والاستدلال الذكي..."):
        try:
            model_gemini = genai.GenerativeModel('gemini-1.5-pro')
            response = model_gemini.generate_content(user_query)
            st.markdown("### رد المرشد الذكي:")
            st.write(response.text)
        except Exception as e:
            st.error(f"حدث خطأ أثناء استدعاء نموذج Gemini: {e}")

st.markdown("---")

# 3. قسم ElevenLabs (التحويل الصوتي)
st.subheader("3. التوليد الصوتي الذكي (ElevenLabs Text-to-Speech)")
text_to_speak = st.text_area("أدخل النص المراد تحويله إلى صوت سياحي:", "مرحباً بك في موقع قصر الفريد الأثري.")

if st.button("تحويل النص إلى صوت"):
    with st.spinner("جاري توليد الملف الصوتي عبر ElevenLabs..."):
        try:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            audio = client.generate(
                text=text_to_speak,
                voice="21m00Tcm4TlvDq8ikWAM",  # صوت افتراضي أو معرّف صوت خاص بك
                model="eleven_multilingual_v2"
            )
            audio_path = "output_audio.mp3"
            with open(audio_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            st.audio(audio_path, format="audio/mp3")
            st.success("تم توليد الصوت بنجاح!")
        except Exception as e:
            st.error(f"خطأ في توليد الصوت عبر ElevenLabs: {e}")

st.markdown("---")

# 4. قسم Hugging Face (التحليل اللغوي المساعد)
st.subheader("4. معالجة النصوص المتقدمة (Hugging Face Inference API)")
hf_text = st.text_input("أدخل نصاً للتحليل اللغوي أو التلخيص:", "قصر الفريد هو أحد أبرز المعالم الأثرية في الحجر.")

if st.button("تحليل النص عبر Hugging Face"):
    with st.spinner("جاري إرسال الطلب لنموذج Hugging Face..."):
        try:
            hf_client = InferenceClient(token=HF_TOKEN)
            # مثال على استخدام نموذج تلخيص أو تحليل
            response = hf_client.summarization(
                text=hf_text,
                model="facebook/bart-large-cnn"
            )
            st.info(response.summary_text)
        except Exception as e:
            st.error(f"خطأ في الاتصال بـ Hugging Face: {e}")
