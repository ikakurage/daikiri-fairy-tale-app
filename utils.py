"""
パフォーマンス最適化のためのユーティリティ関数
Streamlit Community Cloudでの動作を最優先に考慮
"""

import streamlit as st
import time
from functools import wraps

def measure_performance(func):
    """関数の実行時間を測定するデコレーター（開発時のみ）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # 開発時のみ実行時間を表示
        if st.secrets.get("DEBUG", False):
            st.sidebar.write(f"{func.__name__}: {end_time - start_time:.2f}秒")
        
        return result
    return wrapper

@st.cache_data(ttl=3600)
def get_optimized_prompt_template():
    """最適化されたプロンプトテンプレートを取得（キャッシュ付き）"""
    return {
        "story_round": """
        さるかに合戦の物語で、子カニが復讐のために{summon}を召喚しました。
        この召喚に対するサルの反応を、面白く、かつ物語として自然な形で書いてください。
        200文字程度で、サルが{summon}に対抗する何かを召喚する展開にしてください。
        """,
        "final_battle": """
        さるかに合戦の最終決戦です。
        これまでの召喚: {summons}
        
        子カニが最後の召喚を行い、サルとの決着がつく場面を書いてください。
        300文字程度で、「めでたしめでたし」で終わる物語にしてください。
        """
    }

def cleanup_session_state():
    """セッション状態をクリーンアップしてメモリを節約"""
    keys_to_remove = []
    for key in st.session_state.keys():
        if key.startswith('temp_') or key.startswith('cache_'):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]

def optimize_memory_usage():
    """メモリ使用量を最適化するための設定"""
    # 不要なセッション状態をクリーンアップ
    cleanup_session_state()
    
    # ガベージコレクションを強制実行（必要に応じて）
    import gc
    gc.collect()

@st.cache_data(ttl=1800)  # 30分キャッシュ
def get_story_settings():
    """物語設定を取得（キャッシュ付き）"""
    return {
        "max_rounds": 5,
        "max_chars_per_response": 300,
        "timeout_seconds": 30
    }
