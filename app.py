import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

# 環境変数の読み込み（キャッシュ付き）
@st.cache_resource
def load_environment():
    """環境変数を読み込み、Gemini APIを初期化する（キャッシュ付き）"""
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# Gemini APIの初期化（キャッシュ付き）
@st.cache_resource
def initialize_gemini():
    """Geminiモデルを初期化する（キャッシュ付き）"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        st.error(f"Gemini APIの初期化に失敗しました: {e}")
        return None

# 物語データの読み込み（キャッシュ付き）
@st.cache_data
def load_story_data():
    """物語の基本データを読み込む（キャッシュ付き）"""
    return {
        "title": "大喜利童話（さるかに召還合戦）",
        "intro": """
        昔々、海辺の小さな村に親子のカニが住んでいました。
        ある日、悪賢いサルが親カニをだまして殺してしまいました。
        残された子カニは、親から受け継いだ神秘的な貝殻の力を発見します。
        その貝殻には、万物を召喚する不思議な力が宿っていたのです。
        
        子カニは、この力を駆使してサルへの復讐を誓いました。
        しかし、サルもまた強大な召喚術を操る存在でした。
        
        今、伝説の召還合戦が始まろうとしています。
        あなたは、子カニにどんな仲間を召喚させますか？
        """,
        "max_rounds": 5
    }

# 物語生成（キャッシュ付き、ただし入力に応じて動的に）
@st.cache_data(ttl=3600)  # 1時間キャッシュ
def generate_story_round(_model, round_num, crab_summon, monkey_response=None):
    """物語の1ラウンドを生成する（キャッシュ付き）"""
    if not _model:
        return "エラー: Gemini APIが利用できません。"
    
    try:
        if round_num == 1:
            prompt = f"""
            さるかに合戦の物語で、子カニが復讐のために{crab_summon}を召喚しました。
            この召喚に対するサルの反応を、面白く、かつ物語として自然な形で書いてください。
            200文字程度で、サルが{crab_summon}に対抗する何かを召喚する展開にしてください。
            """
        else:
            prompt = f"""
            さるかに合戦の物語の続きです。
            これまでの展開：
            - 子カニが{crab_summon}を召喚
            - サルが{monkey_response}で対抗
            
            この状況での次の展開を、面白く、かつ物語として自然な形で書いてください。
            200文字程度で、子カニが新たな召喚を行う展開にしてください。
            """
        
        response = _model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return f"物語生成中にエラーが発生しました: {e}"

# 最終決戦の生成（キャッシュ付き）
@st.cache_data(ttl=3600)
def generate_final_battle(_model, all_summons):
    """最終決戦を生成する（キャッシュ付き）"""
    if not _model:
        return "エラー: Gemini APIが利用できません。"
    
    try:
        prompt = f"""
        さるかに合戦の最終決戦です。
        これまでの召喚: {', '.join(all_summons)}
        
        子カニが最後の召喚を行い、サルとの決着がつく場面を書いてください。
        300文字程度で、「めでたしめでたし」で終わる物語にしてください。
        """
        
        response = _model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return f"最終決戦の生成中にエラーが発生しました: {e}"

# ページ設定
st.set_page_config(
    page_title="大喜利童話（さるかに召還合戦）",
    page_icon="🦀",
    layout="wide"
)

# カスタムCSS（メモリ効率のため最小限）
st.markdown("""
<style>
    .main {
        background-color: #ffe6e6;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 環境変数とGeminiの初期化
    if not load_environment():
        st.error("環境変数の読み込みに失敗しました。.envファイルを確認してください。")
        return
    
    model = initialize_gemini()
    if not model:
        st.error("Gemini APIの初期化に失敗しました。")
        return
    
    # 物語データの読み込み
    story_data = load_story_data()
    
    st.title(f"🦀 {story_data['title']} 🐒")
    
    # セッション状態の初期化
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 0
    if 'story_history' not in st.session_state:
        st.session_state.story_history = []
    if 'all_summons' not in st.session_state:
        st.session_state.all_summons = []
    
    # イントロ表示
    st.markdown(story_data['intro'])
    
    # 物語の進行
    if st.session_state.current_round < story_data['max_rounds']:
        with st.form("story_form"):
            companion = st.text_input(
                f"第{st.session_state.current_round + 1}ラウンド: 戦いの仲間を入力してください", 
                placeholder="例：蜂、栗、臼、牛の糞"
            )
            
            if st.form_submit_button("召喚する", type="primary"):
                if companion.strip():
                    # 進捗表示
                    with st.spinner("物語を生成中..."):
                        # 物語生成
                        story_text = generate_story_round(
                            model, 
                            st.session_state.current_round + 1, 
                            companion
                        )
                        
                        # 履歴に追加
                        st.session_state.story_history.append({
                            'round': st.session_state.current_round + 1,
                            'summon': companion,
                            'story': story_text
                        })
                        st.session_state.all_summons.append(companion)
                        st.session_state.current_round += 1
                    
                    st.success(f"子カニは{companion}を召喚しました！")
                    st.rerun()
                else:
                    st.error("仲間を入力してください。")
    
    # 物語履歴の表示
    if st.session_state.story_history:
        st.markdown("### 物語の進行")
        for entry in st.session_state.story_history:
            with st.expander(f"第{entry['round']}ラウンド: {entry['summon']}の召喚"):
                st.write(entry['story'])
    
    # 最終決戦
    if st.session_state.current_round >= story_data['max_rounds'] and st.session_state.all_summons:
        st.markdown("### 🎯 最終決戦")
        
        if 'final_battle' not in st.session_state:
            with st.spinner("最終決戦を生成中..."):
                final_story = generate_final_battle(model, st.session_state.all_summons)
                st.session_state.final_battle = final_story
        
        st.write(st.session_state.final_battle)
        
        # リセットボタン
        if st.button("新しい物語を始める"):
            st.session_state.current_round = 0
            st.session_state.story_history = []
            st.session_state.all_summons = []
            if 'final_battle' in st.session_state:
                del st.session_state.final_battle
            st.rerun()

if __name__ == "__main__":
    main() 