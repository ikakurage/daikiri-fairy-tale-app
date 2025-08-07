import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import time

# 環境変数の読み込み
load_dotenv()

# Gemini APIの設定
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    st.error("""
    ⚠️ **Gemini APIキーが見つかりません**
    
    `.env`ファイルを作成し、以下の内容を記入してください：
    
    ```
    GEMINI_API_KEY=your_actual_api_key_here
    ```
    
    APIキーは[Google AI Studio](https://makersuite.google.com/app/apikey)から取得できます。
    """)
    st.stop()

genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    st.error(f"""
    ⚠️ **Gemini APIの初期化エラー**
    
    エラー: {str(e)}
    
    モデル名を変更して再試行します...
    """)
    try:
        model = genai.GenerativeModel('gemini-1.0-pro')
    except Exception as e2:
        st.error(f"""
        ⚠️ **Gemini APIの初期化に失敗しました**
        
        エラー: {str(e2)}
        
        利用可能なモデルを確認してください。
        """)
        st.stop()

# ページ設定（エラーを防ぐため最小限の設定）
st.set_page_config(
    page_title="大喜利童話（さるかに召還合戦）",
    page_icon="��",
    layout="wide"
)

# セッション状態の安全な初期化（エラーを防ぐため）
def initialize_session_state():
    """セッション状態を安全に初期化する"""
    if 'story_history' not in st.session_state:
        st.session_state.story_history = []
    if 'crab_wins' not in st.session_state:
        st.session_state.crab_wins = 0
    if 'monkey_wins' not in st.session_state:
        st.session_state.monkey_wins = 0
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'start'
    if 'crab_character' not in st.session_state:
        st.session_state.crab_character = ""
    if 'monkey_character' not in st.session_state:
        st.session_state.monkey_character = ""

# セッション状態を初期化
initialize_session_state()

def generate_story_response(prompt, context=""):
    """Gemini APIを使用してストーリーを生成"""
    try:
        full_prompt = f"""
        あなたは「さるかに合戦」をベースにした物語の作者です。
        以下の指示に従って、物語を続けてください：
        
        {context}
        
        指示：{prompt}
        
        以下の制約を守ってください：
        - 物語は日本語で書いてください
        - 小説風の文体で書いてください
        - セリフは一切入れないでください
        - 「！」は使用しないでください
        - いきなりバトルに突入する形で書いてください
        - 子カニは読者が指定したキャラクターのみを召喚し、それ以外のキャラクターは召喚しません
        - 子カニは傍観者として、読者が指定したキャラクターを召喚するだけです
        - 子カニが新しいキャラクターを勝手に召喚することは絶対にありません
        - 子カニは召喚したキャラクター以外の新しいキャラクターを登場させることはありません
        - 召喚したキャラクターが特別な行動をする描写は避けてください
        - 召喚したキャラクターが他のキャラクターを召喚することはありません
        - 召喚したキャラクターが新しいキャラクターを登場させることはありません
        - メタ的な文章（読者への問いかけ、説明など）は一切入れないでください
        - 純粋に物語の内容のみを書いてください
        - 絶対に新しいキャラクターを登場させないでください
        """
        
        response = model.generate_content(full_prompt)
        # 「。」で改行を追加
        text = response.text.replace('。', '。\n')
        return text
    except Exception as e:
        st.error(f"""
        ⚠️ **Gemini APIエラー**
        
        エラー: {str(e)}
        
        モデル名を確認し、APIキーが正しく設定されているか確認してください。
        """)
        return f"エラーが発生しました: {str(e)}"

def generate_counter_attack_response(user_attack):
    """サルの反撃を生成"""
    try:
        import random
        
        # サルが召喚するキャラクターをランダムに決定
        counter_characters = [
            "悪魔", "雷神", "氷の精", "火の精", "影武者", 
            "メカゴジラ", "フェニックス", "竜王", "魔神", "死神",
            "巨大ロボット", "魔法使い", "戦士", "忍者", "騎士"
        ]
        counter_character = random.choice(counter_characters)
        
        counter_prompt = f"""
        サルが{counter_character}を召喚してカニの召喚したキャラクターとバトルする場面を書いてください。
        必ず「サルは{counter_character}を召喚した。」で始めてください。
        
        以下の制約を守ってください：
        - 物語は日本語で書いてください
        - 小説風の文体で書いてください
        - セリフは一切入れないでください
        - 「！」は使用しないでください
        - 「サルは○○を召喚した」で始まり、「○○は○○してカニの召喚したキャラクターと戦った」など、1対1のバトルを描写してください（倒す表現は禁止）
        - カニが召喚したキャラクター以外の新しいキャラクターを登場させないでください
        - メタ的な文章（読者への問いかけ、説明など）は一切入れないでください
        - 純粋に物語の内容のみを書いてください
        """
        response = model.generate_content(counter_prompt)
        # 「。」で改行を追加
        text = response.text.replace('。', '。\n')
        return text
    except Exception as e:
        st.error(f"""
        ⚠️ **Gemini APIエラー**
        
        エラー: {str(e)}
        
        モデル名を確認し、APIキーが正しく設定されているか確認してください。
        """)
        return f"エラーが発生しました: {str(e)}"

def generate_battle_description():
    """1対1の一騎打ちバトル描写を生成"""
    try:
        import random
        crab_char = st.session_state.crab_character
        monkey_char = st.session_state.monkey_character
        
        if not crab_char or not monkey_char:
            return ""
        
        # ランダムに勝敗を決定（50%の確率でカニ勝利、50%の確率でサル勝利）
        winner = random.choice([crab_char, monkey_char])
        
        battle_prompt = f"""
        {crab_char}と{monkey_char}の一騎打ちを描写してください。
        
        以下の制約を守ってください：
        - 物語は日本語で書いてください
        - 小説風の文体で書いてください
        - セリフは一切入れないでください
        - 「！」は使用しないでください
        - 1対1の一騎打ちを描写してください
        - 必ず「{winner}が勝利した。」で終えてください
        - 勝敗を明確にしてください
        - メタ的な文章（読者への問いかけ、説明など）は一切入れないでください
        - 純粋に物語の内容のみを書いてください
        - 最後に必ず「{winner}が勝利した。」で終えてください
        """
        
        response = model.generate_content(battle_prompt)
        # 「。」で改行を追加
        text = response.text.replace('。', '。\n')
        return text
    except Exception as e:
        st.error(f"""
        ⚠️ **Gemini APIエラー**
        
        エラー: {str(e)}
        
        モデル名を確認し、APIキーが正しく設定されているか確認してください。
        """)
        return f"エラーが発生しました: {str(e)}"

def generate_summon_description(crab_char):
    """カニの召喚描写を生成"""
    try:
        # マルフーシャとスネジンカの場合は特別な処理
        if crab_char in ["マルフーシャ", "スネジンカ"]:
            base_description = f"灰色の戦闘服を身にまとい、電熱砲の銃器を構えた栗毛の少女だった。"
            
            # サルの召還儀式の描写を追加
            summon_prompt = f"""
            {crab_char}が召喚された後の、サルが怖気づいて負けじと召還の儀式を始めるシーンを描写してください。
            
            以下の制約を守ってください：
            - 物語は日本語で書いてください
            - 小説風の文体で書いてください
            - セリフは一切入れないでください
            - 「！」は使用しないでください
            - メタ的な文章（読者への問いかけ、説明など）は一切入れないでください
            - 純粋に物語の内容のみを書いてください
            - {crab_char}の外見描写は既に済んでいるので、サルの反応と召還儀式のみを描写してください
            - 子カニとサルは1対1の対決なので、「サルたち」「他のサル」などの複数形表現は使用しないでください
            - サルは1匹のみ存在し、子カニも1匹のみ存在します
            """
            
            response = model.generate_content(summon_prompt)
            # 「。」で改行を追加
            additional_text = response.text.replace('。', '。\n')
            
            return f"{base_description}\n\n{additional_text}"
        
        summon_prompt = f"""
        {crab_char}の召喚シーンを描写してください。
        
        以下の要素を含めてください：
        1. {crab_char}の外見的特徴（姿、形、色、大きさなど）
        2. {crab_char}がサルに対して敵意を向けている描写
        3. サルが怖気づいて、負けじと召還の儀式を始めるシーン
        
        以下の制約を守ってください：
        - 物語は日本語で書いてください
        - 小説風の文体で書いてください
        - セリフは一切入れないでください
        - 「！」は使用しないでください
        - メタ的な文章（読者への問いかけ、説明など）は一切入れないでください
        - 純粋に物語の内容のみを書いてください
        - 子カニとサルは1対1の対決なので、「サルたち」「他のサル」などの複数形表現は使用しないでください
        - サルは1匹のみ存在し、子カニも1匹のみ存在します
        """
        
        response = model.generate_content(summon_prompt)
        # 「。」で改行を追加
        text = response.text.replace('。', '。\n')
        return text
    except Exception as e:
        st.error(f"""
        ⚠️ **Gemini APIエラー**
        
        エラー: {str(e)}
        
        モデル名を確認し、APIキーが正しく設定されているか確認してください。
        """)
        return f"エラーが発生しました: {str(e)}"

def analyze_battle_result(battle_text):
    """バトル結果を分析して勝敗を判定"""
    try:
        # バトルテキストから最後の勝敗文を直接判定
        crab_char = st.session_state.crab_character
        monkey_char = st.session_state.monkey_character
        
        # 最後の勝敗文を直接判定
        if f"{crab_char}が勝利した。" in battle_text:
            return "crab_win"
        elif f"{monkey_char}が勝利した。" in battle_text:
            return "monkey_win"
        else:
            # 明確な勝敗文がない場合は、AIに判定を依頼
            analysis_prompt = f"""
            以下のバトル描写を分析して、どちらが勝ったかを判定してください：
            
            {battle_text}
            
            以下の形式で回答してください：
            - カニ側が勝った場合：「カニ勝利」
            - サル側が勝った場合：「サル勝利」
            - 引き分けの場合：「引き分け」
            
            勝敗が明確でない場合は、より強い印象を与えた方を勝者としてください。
            
            重要：回答は必ず「カニ勝利」「サル勝利」「引き分け」のいずれかで始めてください。
            """
            
            response = model.generate_content(analysis_prompt)
            result = response.text.strip()
            
            # より詳細な判定ロジック
            result_lower = result.lower()
            
            # カニの勝利条件を明確に判定
            if ("カニ勝利" in result or 
                result.startswith("カニ勝利") or
                ("カニ" in result and "勝" in result) or
                "crab" in result_lower or
                ("かに" in result_lower and "勝" in result)):
                return "crab_win"
            elif ("サル勝利" in result or 
                  result.startswith("サル勝利") or
                  ("サル" in result and "勝" in result) or
                  "monkey" in result_lower or
                  ("さる" in result_lower and "勝" in result)):
                return "monkey_win"
            else:
                # デフォルトでサルが勝ったと判定
                return "monkey_win"
    except Exception as e:
        # エラーの場合はデフォルトでサルが勝ったと判定
        return "monkey_win"

def display_story():
    """物語を表示"""
    st.markdown('<div class="story-container">', unsafe_allow_html=True)
    
    # 冒頭文を常に表示
    st.markdown("""
    <h3>物語の始まり</h3>
    
    昔々、海辺の小さな村に親子のカニが住んでいました。
    ある日、悪賢いサルが親カニをだまして殺してしまいました。
    残された子カニは、親から受け継いだ神秘的な貝殻の力を発見します。
    その貝殻には、万物を召喚する不思議な力が宿っていたのです。
    
    子カニは、この力を駆使してサルへの復讐を誓いました。
    しかし、サルもまた強大な召喚術を操る存在でした。
    
    今、伝説の召還合戦が始まろうとしています。
    あなたは、子カニにどんな仲間を召喚させますか？
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    for i, entry in enumerate(st.session_state.story_history):
        if entry['type'] == 'story':
            st.markdown(entry['content'])
        elif entry['type'] == 'battle':
            # 召喚パートを表示
            if entry['content'] and not entry['content'].strip() == "":
                st.markdown(f"<div class='battle-section'>{entry['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='battle-section'>{entry['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(entry['content'])
        
        if i < len(st.session_state.story_history) - 1:
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_start():
    """ゲーム開始画面の処理"""
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
    
    st.write("⚔️ **第1ラウンド**")
    st.write(f"🦀 **{st.session_state.crab_wins}勝** | 🐒 **{st.session_state.monkey_wins}勝**")
    st.write("**あなたの選択：**")
    companion = st.text_input("戦いの仲間を入力してください", 
                              placeholder="例：蜂、栗、臼、牛の糞")
    
    if st.button("物語を始める", type="primary"):
        if companion.strip():
            # 入力された文字列をカンマで分割してすべてのキャラクターを取得
            companions = [c.strip() for c in companion.split(',') if c.strip()]
            
            # カニのキャラクターを記録（複数の場合は最初の1つをメインとして使用）
            st.session_state.crab_character = companions[0]
            
            # 複数キャラクターの召喚を表示
            if len(companions) == 1:
                fixed_content = f"子カニは{companions[0]}を召喚した。"
            else:
                # 複数キャラクターの場合
                characters_text = "、".join(companions)
                fixed_content = f"子カニは{characters_text}を召喚した。"
            
            # 召喚描写を生成
            with st.spinner("🦀召還中…"):
                summon_description = generate_summon_description(companions[0])  # 最初のキャラクターで描写生成
                full_content = f"{fixed_content}\n\n{summon_description}"
            
            st.session_state.story_history.append({
                'type': 'battle',
                'content': full_content
            })
            
            # ゲーム状態を更新
            st.session_state.game_state = 'playing'
            st.session_state.current_round = 1
            st.rerun()
        else:
            st.error("仲間を入力してください。")

def handle_playing():
    """ゲームプレイ中の処理"""
    st.markdown("""
    ### ゲームプレイ中
    
    あなたは、子カニにどんな仲間を召喚させますか？
    """)
    
    st.write("⚔️ **第1ラウンド**")
    st.write(f"🦀 **{st.session_state.crab_wins}勝** | 🐒 **{st.session_state.monkey_wins}勝**")
    st.write("**あなたの選択：**")
    companion = st.text_input("戦いの仲間を入力してください", 
                              placeholder="例：蜂、栗、臼、牛の糞")
    
    if st.button("物語を始める", type="primary"):
        if companion.strip():
            # 入力された文字列をカンマで分割してすべてのキャラクターを取得
            companions = [c.strip() for c in companion.split(',') if c.strip()]
            
            # カニのキャラクターを記録（複数の場合は最初の1つをメインとして使用）
            st.session_state.crab_character = companions[0]
            
            # 複数キャラクターの召喚を表示
            if len(companions) == 1:
                fixed_content = f"子カニは{companions[0]}を召喚した。"
            else:
                # 複数キャラクターの場合
                characters_text = "、".join(companions)
                fixed_content = f"子カニは{characters_text}を召喚した。"
            
            # 召喚描写を生成
            with st.spinner("🦀召還中…"):
                summon_description = generate_summon_description(companions[0])  # 最初のキャラクターで描写生成
                full_content = f"{fixed_content}\n\n{summon_description}"
            
            st.session_state.story_history.append({
                'type': 'battle',
                'content': full_content
            })
            
            # ゲーム状態を更新
            st.session_state.game_state = 'playing'
            st.session_state.current_round = 1
            st.rerun()
        else:
            st.error("仲間を入力してください。")

def handle_ended():
    """ゲーム終了画面の処理"""
    st.markdown("""
    ### ゲーム終了
    
    あなたは、子カニにどんな仲間を召喚させますか？
    """)
    
    st.write("⚔️ **第1ラウンド**")
    st.write(f"🦀 **{st.session_state.crab_wins}勝** | 🐒 **{st.session_state.monkey_wins}勝**")
    st.write("**あなたの選択：**")
    companion = st.text_input("戦いの仲間を入力してください", 
                              placeholder="例：蜂、栗、臼、牛の糞")
    
    if st.button("物語を始める", type="primary"):
        if companion.strip():
            # 入力された文字列をカンマで分割してすべてのキャラクターを取得
            companions = [c.strip() for c in companion.split(',') if c.strip()]
            
            # カニのキャラクターを記録（複数の場合は最初の1つをメインとして使用）
            st.session_state.crab_character = companions[0]
            
            # 複数キャラクターの召喚を表示
            if len(companions) == 1:
                fixed_content = f"子カニは{companions[0]}を召喚した。"
            else:
                # 複数キャラクターの場合
                characters_text = "、".join(companions)
                fixed_content = f"子カニは{characters_text}を召喚した。"
            
            # 召喚描写を生成
            with st.spinner("🦀召還中…"):
                summon_description = generate_summon_description(companions[0])  # 最初のキャラクターで描写生成
                full_content = f"{fixed_content}\n\n{summon_description}"
            
            st.session_state.story_history.append({
                'type': 'battle',
                'content': full_content
            })
            
            # ゲーム状態を更新
            st.session_state.game_state = 'playing'
            st.session_state.current_round = 1
            st.rerun()
        else:
            st.error("仲間を入力してください。")

def main():
    """メイン関数（エラーを防ぐため安全に実装）"""
    # セッション状態を初期化
    initialize_session_state()
    
    # タイトル
    st.title("🦀 大喜利童話（さるかに召還合戦）🐒")
    
    # ゲーム状態に応じて処理を分岐
    if st.session_state.game_state == 'start':
        handle_start()
    elif st.session_state.game_state == 'playing':
        handle_playing()
    elif st.session_state.game_state == 'ended':
        handle_ended()
    else:
        st.error("不明なゲーム状態です。ゲームをリセットします。")
        st.session_state.game_state = 'start'
        st.rerun()

if __name__ == "__main__":
    main() 