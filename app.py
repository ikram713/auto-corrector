import streamlit as st
import language_tool_python
from difflib import Differ

# ✅ This must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Multilingual Autocorrect")

# Only include languages supported by LanguageTool
LANGUAGE_CONFIG = {
    "English": {"code": "en", "speller": True},
    "French": {"code": "fr", "speller": False},
    "Spanish": {"code": "es", "speller": False},
    "Portuguese": {"code": "pt", "speller": False},
    "Italian": {"code": "it", "speller": False},
    "Russian": {"code": "ru", "speller": False},
    "Arabic": {"code": "ar", "speller": False}
}

@st.cache_resource
def get_language_tool():
    return language_tool_python.LanguageTool('en')

tool = get_language_tool()

def highlight_differences(original, corrected):
    d = Differ()
    diff = list(d.compare(original.split(), corrected.split()))
    result = []
    for word in diff:
        if word.startswith('+ '):
            result.append(f"<span style='background-color:#ddffdd'>{word[2:]}</span>")
        elif word.startswith('- '):
            result.append(f"<span style='background-color:#ffdddd'>{word[2:]}</span>")
        else:
            result.append(word[2:])
    return " ".join(result)

def correct_text(text, language):
    if not text.strip():
        return text

    lang_config = LANGUAGE_CONFIG[language]

    # Only apply autocorrect for English, import inside function
    if lang_config["speller"]:
        try:
            from autocorrect import Speller
            speller = Speller(lang='en')
            text = speller(text)
        except Exception as e:
            st.warning(f"Spellcheck error: {str(e)}")

    try:
        tool.language = lang_config["code"]
        matches = tool.check(text)
        return language_tool_python.utils.correct(text, matches)
    except Exception as e:
        st.error(f"Grammar check failed: {str(e)}")
        return text

def main():
    st.title("🌍 Advanced Multilingual Autocorrect")

    with st.sidebar:
        st.header("Settings")
        real_time = st.checkbox("Enable real-time correction", True)
        show_diff = st.checkbox("Show differences", True)
        selected_lang = st.selectbox("Select Language", list(LANGUAGE_CONFIG.keys()))
        
        if selected_lang == "Arabic":
            st.warning("Arabic support is limited to grammar checks only.")

    col1, col2 = st.columns(2)

    with col1:
        user_input = st.text_area("Input Text", 
                                  height=300, 
                                  placeholder="Type or paste your text here...",
                                  key="input_text")

    with col2:
        st.markdown("### Corrected Text")
        if user_input:
            if real_time or st.button("Correct Text"):
                with st.spinner("Analyzing text..."):
                    try:
                        corrected = correct_text(user_input, selected_lang)

                        if show_diff:
                            st.markdown(highlight_differences(user_input, corrected), 
                                        unsafe_allow_html=True)
                        else:
                            st.write(corrected)

                        tool.language = LANGUAGE_CONFIG[selected_lang]["code"]
                        error_count = len(tool.check(user_input))
                        st.caption(f"Detected {error_count} potential issues")

                        st.download_button(
                            "📥 Download Corrected Text",
                            corrected,
                            file_name=f"corrected_{selected_lang}.txt"
                        )

                        if corrected == user_input:
                            st.info("No corrections were needed.")

                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
        else:
            st.info("Enter text to see corrections")

if __name__ == "__main__":
    main()

