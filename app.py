import os
import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="المساعد الذكي الشامل",
    page_icon="🤖",
    layout="centered"
)

# تخصيص الاتجاه والمظهر بالـ CSS ليدعم اللغة العربية
st.markdown("""
    <style>
    .main {
        direction: rtl;
        text-align: right;
    }
    stChatMessage {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 المساعد الذكي الشامل")
st.caption("ذكاء اصطناعي مخصص للإجابة عن جميع أسئلتك والبحث في الإنترنت عند الحاجة")

# --- القائمة الجانبية للإعدادات ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    st.markdown("---")
    st.markdown("💡 يمكنك الحصول على مفتاح API مجاني من Google AI Studio.")
    
    if st.button("مسح السجل / محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- إدارة سجل المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- استقبال سؤال المستخدم وتوليد الإجابة ---
user_input = st.chat_input("اكتب سؤالك هنا...")

if user_input:
    if not api_key:
        st.error("الرجاء إدخال مفتاح Gemini API في الشريط الجانبي للبدء.")
    else:
        # 1. عرض سؤال المستخدم
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. إعداد النموذج والأدوات
        os.environ["GOOGLE_API_KEY"] = api_key
        
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
            search_tool = DuckDuckGoSearchRun()
            tools = [search_tool]

            template = """أنت مساعد ذكي شامل ومصمم للإجابة عن كل الأسئلة بدقة باللغة العربية.
تستطيع استخدام أداة البحث في الإنترنت إذا كان السؤال يتطلب معلومات حديثة أو تفاصيل لا تعرفها.

لديك الوصول إلى الأدوات التالية:
{tools}

استخدم النمط التالي للوصول للإجابة:
Question: السؤال الذي يجب الإجابة عليه
Thought: التفكير فيما يجب فعله
Action: اسم الأداة المراد استخدامها، يجب أن تكون واحدة من [{tool_names}]
Action Input: مدخلات الأداة
Observation: نتيجة استخدام الأداة
... (يمكن تكرار Thought/Action/Action Input/Observation عند الحاجة)
Thought: الآن أعرف الإجابة النهائية
Final Answer: الإجابة النهائية والمفصلة باللغة العربية.

Question: {input}
Thought:{agent_scratchpad}"""

            prompt = PromptTemplate.from_template(template)
            agent = create_react_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

            # 3. عرض مؤشر الانتظار وإنشاء الإجابة
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير والبحث عن أفضل إجابة..."):
                    response = agent_executor.invoke({"input": user_input})
                    answer = response["output"]
                    st.markdown(answer)

            # 4. حفظ إجابة الذكاء الاصطناعي في السجل
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
