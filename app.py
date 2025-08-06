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

# ページ設定
st.set_page_config(
    page_title="大喜利童話（さるかに召還合戦）",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カスタムCSS（エラーを防ぐため安全なCSSのみ）
st.markdown("""
<style>
    .main {
        background-color: #ffe6e6;
    }
    .story-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        font-family: 'Noto Sans JP', sans-serif;
        line-height: 1.8;
        font-size: 16px;
    }
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        color: #d32f2f;
    }
    .input-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .battle-section {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    /* エラーを防ぐための安全なスタイル */
    .stApp {
        background-color: #ffe6e6;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の安全な初期化
try:
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
    if 'current_story' not in st.session_state:
        st.session_state.current_story = ""
    if 'crab_character' not in st.session_state:
        st.session_state.crab_character = ""
    if 'monkey_character' not in st.session_state:
        st.session_state.monkey_character = ""
    if 'battle_result' not in st.session_state:
        st.session_state.battle_result = ""
    if 'special_event_triggered' not in st.session_state:
        st.session_state.special_event_triggered = False
except Exception as e:
    st.error(f"セッション状態の初期化エラー: {str(e)}")
    # セッション状態をリセット
    for key in ['story_history', 'crab_wins', 'monkey_wins', 'current_round', 'game_state', 'current_story', 'crab_character', 'monkey_character', 'battle_result', 'special_event_triggered']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.story_history = []
    st.session_state.crab_wins = 0
    st.session_state.monkey_wins = 0
    st.session_state.current_round = 1
    st.session_state.game_state = 'start'
    st.session_state.current_story = ""
    st.session_state.crab_character = ""
    st.session_state.monkey_character = ""
    st.session_state.battle_result = ""
    st.session_state.special_event_triggered = False

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
        crab_char = st.session_state.current_crab_char
        monkey_char = st.session_state.current_monkey_char
        
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
        crab_char = st.session_state.current_crab_char
        monkey_char = st.session_state.current_monkey_char
        
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

def main():
    try:
        # タイトル
        st.markdown('<h1 class="title">🦀 大喜利童話（さるかに召還合戦）🐒</h1>', unsafe_allow_html=True)
        
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
            
    except Exception as e:
        st.error(f"アプリケーションエラーが発生しました: {str(e)}")
        st.info("ページを再読み込みしてください。")
        if st.button("ゲームをリセット"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def handle_start():
    """ゲーム開始時の処理"""
    st.markdown("""
    <div class="story-container">
    <h3>物語の始まり</h3>
    
    昔々、海辺の小さな村に親子のカニが住んでいました。
    ある日、悪賢いサルが親カニをだまして殺してしまいました。
    残された子カニは、親から受け継いだ神秘的な貝殻の力を発見します。
    その貝殻には、万物を召喚する不思議な力が宿っていたのです。
    
    子カニは、この力を駆使してサルへの復讐を誓いました。
    しかし、サルもまた強大な召喚術を操る存在でした。
    
    今、伝説の召還合戦が始まろうとしています。
    あなたは、子カニにどんな仲間を召喚させますか？
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
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
            st.session_state.current_crab_char = companions[0]
            
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
            
            # サルが新しいキャラクターを召喚する必要がある場合
            st.session_state.waiting_for_counter = True
            st.session_state.counter_start_time = time.time()
            st.session_state.battle_phase = "monkey_summon"
            
            st.session_state.last_attack = companion
            st.session_state.game_state = 'playing'
            st.session_state.monkey_summoned_characters = []  # ゲーム開始時にサルの召喚履歴を初期化
            st.session_state.current_input = ""  # ゲーム開始時に入力欄を初期化
            st.rerun()
        else:
            st.error("仲間を入力してください。")
    st.markdown('</div>', unsafe_allow_html=True)

def handle_playing():
    """ゲームプレイ中の処理"""
    display_story()
    
    # サルの反撃待機中の場合
    if st.session_state.waiting_for_counter:
        current_time = time.time()
        elapsed_time = current_time - st.session_state.counter_start_time
        
        if elapsed_time < 5:  # 2秒から5秒に延長
            # 5秒未満の場合、「🐒召還中…」を表示
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.info("🐒召還中…")
            st.markdown('</div>', unsafe_allow_html=True)
            time.sleep(0.1)  # 少し待機してから再描画
            st.rerun()
        else:
            # 2秒経過した場合、サルの反撃を生成
            with st.spinner("🐒召還中…"):
                # サルが新しいキャラクターを召喚（ラウンドごとに新しく召喚）
                counter_character = select_monkey_character(st.session_state.current_crab_char)
                st.session_state.current_monkey_char = counter_character
                
                # 召喚履歴に追加
                if counter_character not in st.session_state.monkey_summoned_characters:
                    st.session_state.monkey_summoned_characters.append(counter_character)
                
                # マルフーシャとスネジンカの特殊演出をチェック
                is_special_event, crab_sister, monkey_sister = check_special_sisters_summon(
                    st.session_state.current_crab_char, counter_character
                )
                
                if is_special_event:
                    # 特殊演出を生成
                    special_event = generate_sisters_special_event(crab_sister, monkey_sister)
                    
                    # サルの召喚を表示
                    summon_content = f"サルは{counter_character}を召喚した。"
                    
                    # 特殊演出を結合
                    full_response = f"{summon_content}\n\n{special_event}"
                    
                    st.session_state.story_history.append({
                        'type': 'battle',
                        'content': full_response
                    })
                    
                    # 引き分けとして処理
                    st.session_state.battle_result = "draw"
                else:
                    # 通常のバトル処理
                    # サルの召喚を表示
                    summon_content = f"サルは{counter_character}を召喚した。"
                    
                    # バトル描写を生成
                    battle_description = generate_battle_description()
                    
                    # バトル結果を分析
                    battle_result = analyze_battle_result(battle_description)
                    st.session_state.battle_result = battle_result
                    
                    # サルの召喚とバトル描写を結合
                    full_response = f"{summon_content}\n\n{battle_description}"
                    
                    st.session_state.story_history.append({
                        'type': 'battle',
                        'content': full_response
                    })
                
            st.session_state.waiting_for_counter = False
            st.session_state.battle_phase = "battle"
            st.rerun()
    else:
        # 通常の入力処理
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # バトル結果を確認
        if st.session_state.battle_phase == "battle":
            # バトル結果に応じて次のアクションを決定
            if st.session_state.battle_result == "crab_win":
                # カニが勝った場合
                st.session_state.crab_wins += 1
                if st.session_state.crab_wins >= 3:
                    # カニが3回勝利した場合、カニの勝利
                    st.session_state.game_state = 'ended'
                    st.session_state.battle_result = "crab_victory"
                else:
                    # 次のラウンドへ
                    st.session_state.current_round += 1
                    st.session_state.battle_phase = "crab_summon"
                    # サルのキャラクターをリセット（次のラウンドで新しく召喚）
                    st.session_state.current_monkey_char = ""
                    # 入力欄をリセット
                    st.session_state.current_input = ""
                st.rerun()
            elif st.session_state.battle_result == "monkey_win":
                # サルが勝った場合
                st.session_state.monkey_wins += 1
                if st.session_state.monkey_wins >= 3:
                    # サルが3回勝利した場合、サルの勝利
                    st.session_state.game_state = 'ended'
                    st.session_state.battle_result = "monkey_victory"
                else:
                    # 次のラウンドへ
                    st.session_state.current_round += 1
                    st.session_state.battle_phase = "crab_summon"
                    # サルのキャラクターをリセット（次のラウンドで新しく召喚）
                    st.session_state.current_monkey_char = ""
                    # 入力欄をリセット
                    st.session_state.current_input = ""
                st.rerun()
            elif st.session_state.battle_result == "draw":
                # 引き分けの場合（マルフーシャとスネジンカの特殊演出）
                # 勝利数はカウントされない
                # 次のラウンドへ
                st.session_state.current_round += 1
                st.session_state.battle_phase = "crab_summon"
                # サルのキャラクターをリセット（次のラウンドで新しく召喚）
                st.session_state.current_monkey_char = ""
                # 入力欄をリセット
                st.session_state.current_input = ""
                st.rerun()

        
        # ラウンド表示と勝利回数表示
        st.write(f"⚔️ **第{st.session_state.current_round}ラウンド**")
        st.write(f"🦀 **{st.session_state.crab_wins}勝** | 🐒 **{st.session_state.monkey_wins}勝**")
        
        if st.session_state.crab_wins < 3 and st.session_state.monkey_wins < 3:
            user_input = st.text_input("カニが召喚するものを入力してください", 
                                       value=st.session_state.current_input,
                                       placeholder="例：巨大な岩、雷、竜巻など",
                                       key=f"input_round_{st.session_state.current_round}")
            
            # 入力が変更された場合、セッション状態を更新
            if user_input != st.session_state.current_input:
                st.session_state.current_input = user_input
            
            if st.button("戦いを続ける", type="primary"):
                if user_input.strip():
                    # 入力された文字列をカンマで分割してすべてのキャラクターを取得
                    inputs = [i.strip() for i in user_input.split(',') if i.strip()]
                    
                    # カニのキャラクターを記録（複数の場合は最初の1つをメインとして使用）
                    st.session_state.current_crab_char = inputs[0]
                    
                    # 複数キャラクターの召喚を表示
                    if len(inputs) == 1:
                        fixed_content = f"子カニは{inputs[0]}を召喚した。"
                    else:
                        # 複数キャラクターの場合
                        characters_text = "、".join(inputs)
                        fixed_content = f"子カニは{characters_text}を召喚した。"
                    
                    # 召喚描写を生成
                    with st.spinner("🦀召還中…"):
                        summon_description = generate_summon_description(inputs[0])  # 最初のキャラクターで描写生成
                        full_content = f"{fixed_content}\n\n{summon_description}"
                    
                    st.session_state.story_history.append({
                        'type': 'battle',
                        'content': full_content
                    })
                    
                    # サルが新しいキャラクターを召喚する必要がある場合
                    st.session_state.waiting_for_counter = True
                    st.session_state.counter_start_time = time.time()
                    st.session_state.battle_phase = "monkey_summon"
                    
                    st.session_state.last_attack = user_input
                    # 入力欄をクリア
                    st.session_state.current_input = ""
                    st.rerun()
                else:
                    st.error("召喚するものを入力してください。")
        st.markdown('</div>', unsafe_allow_html=True)

def get_related_character(crab_char):
    """カニのキャラクターに関連するキャラクターを取得"""
    try:
        # 関連キャラクターを判定するプロンプト
        related_prompt = f"""
        以下のキャラクター「{crab_char}」に関連するキャラクターを1つ選んでください。
        
        以下のルールに従ってください：
        1. 同じジャンル、分野、作品、時代、または関連性のあるキャラクターを選んでください
        2. 具体的な名前を1つだけ回答してください
        3. 関連性が不明な場合は「不明」と回答してください
        
        例：
        - ジョン・ウィック → シュワルツェネッガー（アクション映画）
        - イーサン・ハント → ジョン・マクレーン（アクション映画）
        - 太宰治 → 川端康成（文学）
        - 夏目漱石 → 芥川龍之介（文学）
        - スパイダーマン → バットマン（スーパーヒーロー）
        - ドラえもん → ポケモン（アニメ）
        
        回答は必ず1つのキャラクター名のみで、説明は不要です。
        """
        
        response = model.generate_content(related_prompt)
        result = response.text.strip()
        
        # 結果をクリーンアップ
        result = result.replace('。', '').replace('、', '').replace('（', '').replace('）', '').strip()
        
        # 「不明」や空の場合はNoneを返す
        if result.lower() in ['不明', 'unknown', 'none', ''] or len(result) < 2:
            return None
        
        return result
        
    except Exception as e:
        # エラーの場合はNoneを返す
        return None

def select_monkey_character(crab_char):
    """サルのキャラクターを選択（関連キャラクター優先、重複除外）"""
    try:
        # マルフーシャとスネジンカの特殊処理
        if crab_char == "マルフーシャ":
            return "スネジンカ"
        elif crab_char == "スネジンカ":
            return "マルフーシャ"
        
        # 既に召喚したキャラクターのリストを取得
        summoned_characters = st.session_state.monkey_summoned_characters.copy()
        
        # まず関連キャラクターを試す
        related_char = get_related_character(crab_char)
        
        if related_char and related_char not in summoned_characters:
            # 関連キャラクターが見つかり、かつまだ召喚していない場合
            return related_char
        else:
            # 関連キャラクターが見つからないか、既に召喚済みの場合、デフォルトリストから選択
            import random
            default_characters = [
                "悪魔", "雷神", "氷の精", "火の精", "影武者", 
                "メカゴジラ", "フェニックス", "竜王", "魔神", "死神",
                "巨大ロボット", "魔法使い", "戦士", "忍者", "騎士"
            ]
            
            # 既に召喚したキャラクターを除外
            available_characters = [char for char in default_characters if char not in summoned_characters]
            
            # 利用可能なキャラクターがない場合は、すべてのキャラクターから選択（重複を許容）
            if not available_characters:
                available_characters = default_characters
            
            return random.choice(available_characters)
            
    except Exception as e:
        # エラーの場合、デフォルトリストから選択
        import random
        default_characters = [
            "悪魔", "雷神", "氷の精", "火の精", "影武者", 
            "メカゴジラ", "フェニックス", "竜王", "魔神", "死神",
            "巨大ロボット", "魔法使い", "戦士", "忍者", "騎士"
        ]
        return random.choice(default_characters)

def check_special_sisters_summon(crab_char, monkey_char):
    """マルフーシャとスネジンカの特殊演出をチェック"""
    sisters = ["マルフーシャ", "スネジンカ"]
    
    # カニがマルフーシャまたはスネジンカを召喚したかチェック
    if crab_char in sisters:
        # サルが対応する姉妹を召喚する必要がある
        if crab_char == "マルフーシャ":
            expected_monkey_char = "スネジンカ"
        else:  # crab_char == "スネジンカ"
            expected_monkey_char = "マルフーシャ"
        
        # サルが期待される姉妹を召喚したかチェック
        if monkey_char == expected_monkey_char:
            return True, crab_char, monkey_char
    
    return False, None, None

def generate_sisters_special_event(crab_char, monkey_char):
    """マルフーシャとスネジンカの特殊演出を生成"""
    # マルフーシャは姉、スネジンカは妹（常に固定）
    elder_sister = "マルフーシャ"
    younger_sister = "スネジンカ"
    
    special_event = f"""
灰色の戦闘服を身にまとい、電熱砲の銃器を構えた栗毛の少女が召喚された。

{elder_sister}「{younger_sister}…。なぜ、こんなところにいる。」

{younger_sister}「姉さん！」

{elder_sister}「時間がない。力づくでも連れ戻す。」

硝煙と土埃が入り混じった空気が、肺を焼く。電熱砲が放つ轟音が耳朶を叩き、ライフルの連射音が木霊する。二人は互いの存在を抹消するため、数多の銃器を駆使して戦場を駆け抜けていた。

{younger_sister}は、跳弾の嵐を紙一重でかわし、爆炎の熱を肌で感じながらトリガーを引く。ライフルから放たれた弾丸は、相手の肩を掠め、鮮血が舞い散った。だが、相手も怯むことなくハンドガンを構え、正確無比な三連射を放つ。{younger_sister}は咄嗟に身を翻し、弾丸は彼女の頬をかすめていった。熱い痛みが走る。

息つく暇もない攻防が続く中、{younger_sister}はふと、その手を止めた。無数の銃弾と爆炎が渦巻く戦場で、彼女はただ静かに立ち尽くしている。相手は、その隙を見逃すまいと銃口を向けたが、引き金を引くことはできなかった。{younger_sister}の瞳には、殺意ではなく、深い悲しみが宿っていたからだ。

{younger_sister}「やだよ…姉さんと、戦いたくないよ…」

{elder_sister}「{younger_sister}…」

{younger_sister}「私…姉さんと、パン屋をやりたいよ…！」

{elder_sister}「…私もだ」

そういって、{elder_sister}と{younger_sister}は抱きしめあった。

その様子を見ていた子カニとサルは涙を流して拍手した。

そして和解したために、判定は「引き分け」となり、どちらの勝利数もカウントされなかった。
"""
    
    return special_event


def handle_ended():
    """ゲーム終了時の処理"""
    display_story()
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    if st.session_state.battle_result == "crab_victory":
        if st.session_state.crab_wins == 3 and st.session_state.monkey_wins == 0:
            st.success("🦀 **勝利！！** 3連勝おめでとう！！")
        else:
            st.success("🦀 **勝利！！**")
        st.write("子カニは見事にサルを倒し、親の仇を討ちました。めでたしめでたし。")
    elif st.session_state.battle_result == "monkey_victory":
        st.error("🦀 **敗北…**")
        st.write("子カニはサルに敗れ、親の仇を討つことができませんでした。")
    elif st.session_state.battle_result == "draw":
        st.info("🦀 **引き分け！！** どちらも勝利数にカウントされませんでした。")
    
    if st.button("新しい物語を始める", type="primary"):
        st.session_state.story_history = []
        st.session_state.crab_wins = 0
        st.session_state.monkey_wins = 0
        st.session_state.current_round = 1
        st.session_state.game_state = 'start'
        st.session_state.current_crab_char = ""
        st.session_state.current_monkey_char = ""
        st.session_state.battle_phase = "crab_summon"
        st.session_state.battle_result = ""
        st.session_state.monkey_summoned_characters = []  # サルの召喚履歴もリセット
        st.session_state.current_input = ""  # ゲーム終了時に入力欄をリセット
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 