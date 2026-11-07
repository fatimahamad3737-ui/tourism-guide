import os
import tempfile

import streamlit as st
from PIL import Image

# ---------------------------------------------------------------
# إعداد الصفحة
# ---------------------------------------------------------------
st.set_page_config(page_title="Smart Tourism Guide", layout="centered")

# دعم الاتجاه من اليمين لليسار
st.markdown(
    """
    <style>
    .block-container { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏛️ المرشد السياحي الذكي - موقع الحجر (قصر الفريد)")
st.caption("نظام التوثيق والرصد البصري المدعوم بالذكاء الاصطناعي والاستدعاءات الفعلية للخدمات")
st.markdown("---")


# ---------------------------------------------------------------
# قراءة الإعدادات (Secrets أو متغيرات البيئة)
# ---------------------------------------------------------------
def get_secret(name: str, default: str = "") -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    return os.environ.get(name, default).strip()


ROBOFLOW_API_KEY = get_secret("ROBOFLOW_API_KEY")
ROBOFLOW_WORKSPACE = get_secret("ROBOFLOW_WORKSPACE")   # اختياري
ROBOFLOW_PROJECT = get_secret("ROBOFLOW_PROJECT")       # مثال: alfareed-landmarks
ROBOFLOW_VERSION = int(get_secret("ROBOFLOW_VERSION", "1") or 1)

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
GEMINI_MODEL = get_secret("GEMINI_MODEL", "gemini-2.5-flash")

ELEVENLABS_API_KEY = get_secret("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = get_secret("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

HF_TOKEN = get_secret("HF_TOKEN")
HF_MODEL = get_secret("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")


def require(value: str, name: str) -> bool:
    """يوقف التنفيذ بوضوح إذا كان المفتاح غير موجود بدل استدعاء بمفتاح وهمي."""
    if not value:
        st.error(f"المفتاح أو الإعداد `{name}` غير موجود. أضفه في `.streamlit/secrets.toml`.")
        return False
    return True


# ---------------------------------------------------------------
# 1. Roboflow
# ---------------------------------------------------------------
st.subheader("1. التعرف البصري (Roboflow Inference)")
uploaded_file = st.file_uploader("قم برفع صورة المعلم الأثري...", type=["jpg", "jpeg", "png"])

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")  # تحويل لـ RGB لتجنب أخطاء PNG الشفاف
    st.image(image, caption="الصورة المدخلة للنظام", use_container_width=True)

    if st.button("تشغيل التحليل البصري بـ Roboflow"):
        if require(ROBOFLOW_API_KEY, "ROBOFLOW_API_KEY") and require(ROBOFLOW_PROJECT, "ROBOFLOW_PROJECT"):
            with st.spinner("جاري التواصل مع نموذج Roboflow وتحليل المعالم..."):
                tmp_in = tmp_out = None
                try:
                    from roboflow import Roboflow

                    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
                    ws = rf.workspace(ROBOFLOW_WORKSPACE) if ROBOFLOW_WORKSPACE else rf.workspace()
                    model = ws.project(ROBOFLOW_PROJECT).version(ROBOFLOW_VERSION).model

                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                        tmp_in = f.name
                    image.save(tmp_in, format="JPEG")

                    result = model.predict(tmp_in, confidence=40, overlap=30)
                    data = result.json()

                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                        tmp_out = f.name
                    result.save(tmp_out)  # صورة عليها مربعات الاكتشاف

                    st.success("تم التحليل بنجاح بواسطة Roboflow!")
                    st.image(tmp_out, caption="نتيجة الاكتشاف", use_container_width=True)

                    preds = data.get("predictions", [])
                    if preds:
                        for p in preds:
                            st.write(f"• **{p.get('class')}** — الثقة: {p.get('confidence', 0):.0%}")
                    else:
                        st.info("لم يتم اكتشاف أي معلم. جرّب صورة أوضح أو خفّض نسبة الثقة.")
                    with st.expander("الاستجابة الكاملة (JSON)"):
                        st.json(data)
                except Exception as e:
                    st.error(f"فشل الاتصال بـ Roboflow: {e}")
                finally:
                    for p in (tmp_in, tmp_out):
                        if p and os.path.exists(p):
                            os.remove(p)

st.markdown("---")

# ---------------------------------------------------------------
# 2. Gemini
# ---------------------------------------------------------------
st.subheader("2. المرشد السياحي الذكي (Google Gemini AI)")
user_query = st.text_input(
    "اسأل المرشد السياحي عن قصر الفريد أو تاريخ الموقع:",
    "اكتب نبذة تاريخية مختصرة عن قصر الفريد في مدائن صالح.",
)
use_image = st.checkbox("أرفق الصورة المرفوعة مع السؤال", value=False, disabled=image is None)

if st.button("توليد الإجابة بواسطة Gemini"):
    if require(GEMINI_API_KEY, "GEMINI_API_KEY"):
        with st.spinner("جاري التوليد والاستدلال الذكي..."):
            try:
                from google import genai

                client = genai.Client(api_key=GEMINI_API_KEY)
                contents = [image, user_query] if (use_image and image is not None) else user_query
                response = client.models.generate_content(model=GEMINI_MODEL, contents=contents)
                st.markdown("### رد المرشد الذكي:")
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ أثناء استدعاء نموذج Gemini: {e}")

st.markdown("---")

# ---------------------------------------------------------------
# 3. ElevenLabs
# ---------------------------------------------------------------
st.subheader("3. التوليد الصوتي الذكي (ElevenLabs Text-to-Speech)")
text_to_speak = st.text_area(
    "أدخل النص المراد تحويله إلى صوت سياحي:",
    "مرحباً بك في موقع قصر الفريد الأثري.",
)

if st.button("تحويل النص إلى صوت"):
    if require(ELEVENLABS_API_KEY, "ELEVENLABS_API_KEY"):
        with st.spinner("جاري توليد الملف الصوتي عبر ElevenLabs..."):
            try:
                from elevenlabs.client import ElevenLabs

                client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                audio_stream = client.text_to_speech.convert(
                    voice_id=ELEVENLABS_VOICE_ID,
                    text=text_to_speak,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                )
                audio_bytes = b"".join(audio_stream)
                st.audio(audio_bytes, format="audio/mp3")
                st.success("تم توليد الصوت بنجاح!")
            except Exception as e:
                st.error(f"خطأ في توليد الصوت عبر ElevenLabs: {e}")

st.markdown("---")

# ---------------------------------------------------------------
# 4. Hugging Face
# ---------------------------------------------------------------
st.subheader("4. معالجة النصوص المتقدمة (Hugging Face Inference API)")
hf_text = st.text_area(
    "أدخل نصاً للتحليل اللغوي أو التلخيص:",
    "قصر الفريد هو أحد أبرز المعالم الأثرية في الحجر.",
)

if st.button("تحليل النص عبر Hugging Face"):
    if require(HF_TOKEN, "HF_TOKEN"):
        with st.spinner("جاري إرسال الطلب لنموذج Hugging Face..."):
            try:
                from huggingface_hub import InferenceClient

                hf_client = InferenceClient(token=HF_TOKEN)
                # نموذج bart-large-cnn إنجليزي فقط، لذلك نستخدم نموذج محادثة متعدد اللغات
                response = hf_client.chat_completion(
                    model=HF_MODEL,
                    messages=[
                        {"role": "system", "content": "أنت مساعد لغوي. لخّص النص التالي بالعربية في جملتين."},
                        {"role": "user", "content": hf_text},
                    ],
                    max_tokens=300,
                )
                st.info(response.choices[0].message.content)
            except Exception as e:
                st.error(f"خطأ في الاتصال بـ Hugging Face: {e}")
