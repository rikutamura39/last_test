"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
# ログ出力を行うためのモジュール
import logging
# streamlitアプリの表示を担当するモジュール
import streamlit as st
# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils
# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize import initialize
# （自作）画面表示系の関数が定義されているモジュール
import components as cn
# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct


############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(
    page_title=ct.APP_NAME
)

# ログ出力を行うためのロガーの設定
logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)

############################################################
# 4. 初期表示
############################################################
# ▼ サイドバーに「利用目的」の選択エリアを表示
with st.sidebar:
    cn.display_select_mode()
    cn.display_initial_ai_message2()

# ▼ メインエリアにタイトルを表示
cn.display_app_title()

# ▼ メインエリアにAIメッセージを表示
cn.display_initial_ai_message()

############################################################
# 5. 会話ログの表示
############################################################
try:
    # 会話ログの表示
    cn.display_conversation_log()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()


############################################################
# 6. チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 7-1. ユーザーメッセージの表示
    # ==========================================
    # ユーザーメッセージのログ出力
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})

    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(chat_message)

    # ==========================================
    # 7-2. LLMからの回答取得
    # ==========================================
    # 「st.spinner」でグルグル回っている間、表示の不具合が発生しないよう空のエリアを表示
    res_box = st.empty()
    # LLMによる回答生成（回答生成が完了するまでグルグル回す）
    with st.spinner(ct.SPINNER_TEXT):
        try:
            # 画面読み込み時に作成したRetrieverを使い、Chainを実行
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()
    
    # ==========================================
    # 7-3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant"):
        try:
            # ==========================================
            # モードが「社内文書検索」の場合
            # ==========================================
            if st.session_state.mode == ct.ANSWER_MODE_1:
                # 入力内容と関連性が高い社内文書のありかを表示
                content = cn.display_search_llm_response(llm_response)

            # ==========================================
            # モードが「社内問い合わせ」の場合
            # ==========================================
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                # 入力に対しての回答と、参照した文書のありかを表示
                content = cn.display_contact_llm_response(llm_response)
            
            # AIメッセージのログ出力
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()

    # # ==========================================
    # # 7-3. LLMからの回答表示
    # # ==========================================
    # with st.chat_message("assistant"):
    #     try:
    #         # ==========================================
    #         # モードが「社内文書検索」の場合
    #         # ==========================================
    #         if st.session_state.mode == ct.ANSWER_MODE_1:
    #             # 入力内容と関連性が高い社内文書のありかを表示
    #             content = cn.display_search_llm_response(llm_response)

    #         # ==========================================
    #         # モードが「社内問い合わせ」の場合
    #         # ==========================================
    #         elif st.session_state.mode == ct.ANSWER_MODE_2:
    #             # 入力に対しての回答と、参照した文書のありかを表示
    #             content = cn.display_contact_llm_response(llm_response)

    #         # -----------------------------
    #         # 参照した PDF のページ番号表示
    #         # -----------------------------
    #         from collections import defaultdict
    #         pdf_pages = defaultdict(set)

    #         # llm_response から "参照された Document のリスト" を取り出す
    #         source_docs = None

    #         if isinstance(llm_response, dict):
    #             # RetrievalQA(Return_source_documents=True) などの典型パターン
    #             source_docs = (
    #                 llm_response.get("source_documents")
    #                 or llm_response.get("documents")
    #                 or llm_response.get("context")
    #             )
    #         elif hasattr(llm_response, "source_documents"):
    #             # オブジェクトに source_documents 属性があるパターン
    #             source_docs = getattr(llm_response, "source_documents")
    #         elif isinstance(llm_response, list):
    #             # そもそも Document のリストが返ってきているパターン
    #             source_docs = llm_response

    #         # 実際に PDF のページ情報を集計
    #         if source_docs:
    #             for doc in source_docs:
    #                 # LangChain Document を想定（doc.metadata を持つ）
    #                 metadata = getattr(doc, "metadata", {}) or {}
    #                 source = metadata.get("source") or metadata.get("file_path")
    #                 if not source or not str(source).lower().endswith(".pdf"):
    #                     # PDF 以外はスキップ
    #                     continue

    #                 # ページ情報を複数キーから探す
    #                 page = (
    #                     metadata.get("page")
    #                     or metadata.get("page_number")
    #                     or metadata.get("page_no")
    #                 )
    #                 if page is None:
    #                     continue

    #                 # 多くの Loader（PyMuPDFLoader など）は 0 始まりなので +1
    #                 try:
    #                     page_int = int(page)
    #                     page_no = page_int + 1
    #                 except Exception:
    #                     # 数値にできなければそのまま
    #                     page_no = page

    #                 pdf_pages[source].add(page_no)

    #         # 1つ以上 PDF が参照されている場合のみ表示
    #         if pdf_pages:
    #             st.markdown("**参照したPDFのページ**")
    #             for src, pages in pdf_pages.items():
    #                 sorted_pages = sorted(pages)
    #                 page_labels = "、".join(f"ページNo{p}" for p in sorted_pages)
    #                 st.markdown(f"- `{src}`（{page_labels}）")

    #         # AIメッセージのログ出力
    #         logger.info({"message": content, "application_mode": st.session_state.mode})

    #     except Exception as e:
    #         # エラーログの出力
    #         logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
    #         # エラーメッセージの画面表示
    #         st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    #         # 後続の処理を中断
    #         st.stop()


    # ==========================================
    # 7-4. 会話ログへの追加
    # ==========================================
    # 表示用の会話ログにユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": chat_message})
    # 表示用の会話ログにAIメッセージを追加
    st.session_state.messages.append({"role": "assistant", "content": content})