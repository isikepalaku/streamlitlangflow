import streamlit as st
import requests
import json

# Fungsi untuk memanggil API LangFlow
def call_langflow_api(message):
    url = "https://api.langflow.astra.datastax.com/lf/3841bdcb-9bd3-4015-a4f0-bb2c5ccb6096/api/v1/run/989e6c62-0220-4238-a411-1c7729a871c6?stream=false"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer AstraCS:PmvMMRtFbiKYlsMOgzptvTyB:04c6ec4556ba6ab4f57e88ab2bc91c173671575b48dad43f5e7e3eb09a089913'
    }
    data = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
  "ChatInput-jcIaa": {},
  "ParseData-GvmBA": {},
  "Prompt-J7ot3": {},
  "ChatOutput-Iy1Hv": {},
  "SplitText-X4VWJ": {},
  "File-8o67n": {},
  "OpenAIEmbeddings-g8ZlQ": {},
  "OpenAIEmbeddings-erWOr": {},
  "AnthropicModel-3BSx9": {},
  "Pinecone-SExFp": {},
  "Pinecone-VT036": {}
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Mengambil respons API
    if response.status_code == 200:
        result = response.json()
        try:
            # Ambil teks dari jalur yang tepat
            return result["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]
        except (KeyError, IndexError):
            return "Error: Unexpected response format."
    else:
        return f"Error: {response.status_code} - Unable to fetch response from LangFlow API."

# Judul aplikasi
st.title("Let's start conversation")

# Inisialisasi riwayat percakapan dan history
if "history" not in st.session_state:
    st.session_state.history = []  # Simpan setiap percakapan di history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False  # Status untuk mengecek apakah percakapan baru dimulai
if "selected_history" not in st.session_state:
    st.session_state.selected_history = None  # Menyimpan riwayat yang dipilih

# Fungsi untuk memulai percakapan baru
def new_conversation():
    if st.session_state.messages:
        # Simpan percakapan yang sudah ada ke history
        st.session_state.history.append(st.session_state.messages.copy())
    # Bersihkan percakapan saat ini
    st.session_state.messages = []
    st.session_state.conversation_started = False  # Reset status percakapan

# Sidebar untuk riwayat chat
with st.sidebar:
    st.title("ChatGPT")
    
    if st.button("New Conversation"):
        new_conversation()

    st.markdown("### History")
    
    # Tambahkan tombol untuk history baru di bagian atas
    history_number = len(st.session_state.history) + 1
    if st.button(f"History {history_number} (New)"):
        st.session_state.history.append([])  # Tambah riwayat kosong
        st.session_state.messages = []  # Bersihkan pesan saat ini

    # Tampilkan semua history dari yang terbaru
    for i, hist in enumerate(reversed(st.session_state.history)):
        history_id = len(st.session_state.history) - i
        button_text = f"History {history_id}"
        if st.button(button_text, key=f"history_{history_id}", help="Click to load this history"):
            st.session_state.messages = hist  # Muat percakapan dari history yang dipilih
            st.session_state.selected_history = history_id  # Tandai history yang dipilih
        # Tandai tombol yang aktif
        if st.session_state.selected_history == history_id:
            st.markdown(f'<style>#{button_text} {{ background-color: #f0f0f0; }}</style>', unsafe_allow_html=True)

# CSS untuk memposisikan bubble chat dan avatar
# Membaca file CSS eksternal
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Memanggil fungsi load_css dan mengimpor file CSS
load_css("style.css")

# Menampilkan pesan dari riwayat chat di antarmuka utama
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'''
            <div class="chat-container user-container">
                <div class="bubble user-bubble">{message["content"]}</div>
                <img src="https://via.placeholder.com/40" class="avatar user-avatar" alt="User avatar">
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown(
            f'''
            <div class="chat-container assistant-container">
                <img src="https://via.placeholder.com/40" class="avatar assistant-avatar" alt="Assistant avatar">
                <div class="bubble assistant-bubble">{message["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

# Menerima input pengguna
if prompt := st.chat_input("What is up?"):
    # Cek jika ini adalah pesan pertama dari percakapan baru
    if not st.session_state.conversation_started:
        new_conversation()  # Simpan percakapan sebelumnya dan mulai percakapan baru
        st.session_state.conversation_started = True  # Tandai bahwa percakapan telah dimulai

    # Menambahkan pesan pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Menampilkan pesan pengguna di antarmuka chat
    st.markdown(
        f'''
        <div class="chat-container user-container">
            <div class="bubble user-bubble">{prompt}</div>
            <img src="https://via.placeholder.com/40" class="avatar user-avatar" alt="User avatar">
        </div>
        ''', unsafe_allow_html=True)
    
    # Panggil API LangFlow untuk mendapatkan respons
    response_content = call_langflow_api(prompt)
    
    # Tampilkan respons asisten di antarmuka chat
    st.markdown(
        f'''
        <div class="chat-container assistant-container">
            <img src="https://via.placeholder.com/40" class="avatar assistant-avatar" alt="Assistant avatar">
            <div class="bubble assistant-bubble">{response_content}</div>
        </div>
        ''', unsafe_allow_html=True)

    # Menambahkan respons asisten ke riwayat chat
    st.session_state.messages.append({"role": "assistant", "content": response_content})
