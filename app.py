import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Gemini APIの設定
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    st.error("⚠️ Gemini APIキーが見つかりません。.envファイルを作成し、GEMINI_API_KEYを設定してください。")
    st.stop()

genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    st.error(f"⚠️ Gemini APIの初期化エラー: {str(e)}")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="大喜利童話（さるかに召還合戦）",
    page_icon="🦀"
)

def generate_summon_description(character):
    """召喚描写を生成"""
    try:
        prompt = f"""
        「{character}」が召喚される場面を描写してください。
        以下の制約を守ってください：
        - 日本語で書いてください
        - 小説風の文体で書いてください
        - セリフは一切入れないでください
        - 「！」は使用しないでください
        - 100文字以内で書いてください
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"{character}が召喚された。"

def main():
    """メイン関数"""
    st.title("🦀 大喜利童話（さるかに召還合戦）🐒")
    
    st.markdown("""
    ### 物語の始まり
    
    昔々、海辺の小さな村に親子のカニが住んでいました。
    ある日、悪賢いサルが親カニをだまして殺してしまいました。
    残された子カニは、親から受け継いだ神秘的な貝殻の力を発見します。
    その貝殻には、万物を召喚する不思議な力が宿っていたのです。
    
    子カニは、この力を駆使してサルへの復讐を誓いました。
    しかし、サルもまた強大な召喚術を操る存在でした。
    
    今、伝説の召還合戦が始まろうとしています。
    あなたは、子カニにどんな仲間を召喚させますか？
    """)
    
    companion = st.text_input("戦いの仲間を入力してください", placeholder="例：蜂、栗、臼、牛の糞")
    
    if st.button("物語を始める", type="primary"):
        if companion.strip():
            with st.spinner("🦀召還中…"):
                summon_description = generate_summon_description(companion)
                content = f"子カニは{companion}を召喚した。\n\n{summon_description}"
            
            st.markdown("### 召喚結果")
            st.write(content)
        else:
            st.error("仲間を入力してください。")

if __name__ == "__main__":
    main() 