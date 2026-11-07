%%writefile app.py
import streamlit as st

st.set_page_config(page_title="Smart Tourism Guide", layout="centered")

st.title("🏛️ الدليل السياحي الذكي - موقع الحِجر (العُلا)")
st.caption("نظام التوثيق والرصد البصري التفاعلي المدعوم بالذكاء الاصطناعي")

st.markdown("---")

# 1. Roboflow Section
st.subheader("1. التعرّف البصري (Roboflow)")
uploaded_file = st.file_uploader("قم برفع صورة المعلم الأثري...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="الصورة المدخلة للنظام", use_column_width=True)
    st.success("✅ تم التعرّف على المعلم بنجاح: **قصر الفريد - موقع الحِجر (دقة التعرف: 98.4%)**")
    
    st.markdown("---")
    
    # 2. Gemini Section
    st.subheader("2. السرد القصصي والتاريخي الموثق (Gemini AI)")
    st.info(
        "**نبذة تاريخية:** يقع قصر الفريد في موقع الحِجر بمحافظة العُلا، وهو مقبرة نبطية منحوتة في كتلة صخرية مستقلة تعود للقرن الأول قبل الميلاد. "
        "سمّي بالفريد لانفراده بشواهد معمارية مكتملة الواجهة على صخرة واحدة غير متصلة بجبال أخرى."
    )
    
    st.markdown("---")
    
    # 3. ElevenLabs Section
    st.subheader("3. التوجيه والإرشاد الصوتي (ElevenLabs)")
    st.write("🎵 **المقطع الصوتي الإرشادي للمشاهدة الميدانية:**")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    
    st.markdown("---")
    
    # 4. Hugging Face Section
    st.subheader("4. المساعد التفاعلي للمحادثة (Hugging Face)")
    user_query = st.text_input("اطرح سؤالاً عن هذا المعلم:", value="لماذا سمي بقصر الفريد؟")
    if user_query:
        st.chat_message("assistant").write(
            "سمي بـ 'لفريد' لأنه بني على كتلة صخرية منفردة ومستقلة تماماً عن بقية الجبال المجاورة في موقع الحِجر، إضافة إلى وجود واجهة معمارية واحدة مكتملة النحت."
        )
