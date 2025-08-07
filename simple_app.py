import streamlit as st

# ページ設定
st.set_page_config(
    page_title="大喜利童話（さるかに召還合戦）",
    page_icon="🦀"
)

# メイン関数
def main():
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
    
    # シンプルな入力
    companion = st.text_input("戦いの仲間を入力してください", placeholder="例：蜂、栗、臼、牛の糞")
    
    if st.button("物語を始める", type="primary"):
        if companion.strip():
            st.success(f"子カニは{companion}を召喚しました！")
            st.write(f"**{companion}**が現れ、サルに向かって立ち向かいました。")
        else:
            st.error("仲間を入力してください。")

if __name__ == "__main__":
    main()
