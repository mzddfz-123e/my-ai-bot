import os
import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="المساعد الذكي الشامل",
    page_icon="🤖",
    layout="centered"
)

# تخصيص اتجاه النص ليدعم اللغة العربية
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    stChatMessage { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 المساعد الذكي الشامل")
st.caption("ذكاء اصطناعي مخصص للإجابة عن أسئلتك والبحث في الإنترنت عند الحاجة")

# --- القائمة الجانبية للإعدادات ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    st.markdown("---")
    
    if st.button("مسح السجل / محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- إدارة سجل المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- استقبال سؤال المستخدم وتوليد الإجابة ---
user_input = st.chat_input("اكتب سؤالك هنا...")

if user_input:
    if not api_key:
        st.error("الرجاء إدخل مفتاح Gemini API في الشريط الجانبي للبدء.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        os.environ["GOOGLE_API_KEY"] = api_key
        
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
            
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير وتوليد الإجابة..."):
                    # إذا طلب المستخدم بحث مباشر في النت
                    if "بحث" in user_input or "ابحث" in user_input:
                        search = DuckDuckGoSearchRun()
                        search_results = search.run(user_input)
                        prompt = f"بناءً على نتائج البحث التالية: {search_results}\n\nأجب عن السؤال التالي باللغة العربية: {user_input}"
                        response = llm.invoke(prompt)
                    else:
                        response = llm.invoke(user_input)
                    
                    answer = response.content
                    st.markdown(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
