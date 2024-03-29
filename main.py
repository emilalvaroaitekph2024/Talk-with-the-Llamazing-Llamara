import streamlit
import replicate
import os

# App title
streamlit.set_page_config(page_title="🦙💬Talk with the Llamazing Llamara")

# Replicate Credentials
with streamlit.sidebar:
    streamlit.title("🦙💬Talk with the Llamazing Llamara")
    if 'REPLICATE_API_TOKEN' in streamlit.secrets:
        streamlit.success('API key already provided!', icon='✅')
        replicate_api = streamlit.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = streamlit.text_input("Enter Replicate API token:", type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
            streamlit.warning('Please enter your credentials!', icon='⚠️')
        else:
            streamlit.success('Chat with Llamazing Llamara!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    streamlit.subheader('Models and parameters')
    selected_model = streamlit.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'],
                                                 key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = streamlit.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = streamlit.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = streamlit.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    # streamlit.markdown(
    #     '📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in streamlit.session_state.keys():
    streamlit.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in streamlit.session_state.messages:
    with streamlit.chat_message(message["role"]):
        streamlit.write(message["content"])


def clear_chat_history():
    streamlit.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


streamlit.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# Function for generating LLaMA2 response
# Refactor from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = ("You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only "
                       "respond once as 'Assistant'.")
    for dict_message in streamlit.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(
        'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5',
        input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
               "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1})
    return output


# User-provided prompt
if prompt := streamlit.chat_input(disabled=not replicate_api):
    streamlit.session_state.messages.append({"role": "user", "content": prompt})
    with streamlit.chat_message("user"):
        streamlit.write(prompt)

# Generate a new response if last message is not from assistant
if streamlit.session_state.messages[-1]["role"] != "assistant":
    with streamlit.chat_message("assistant"):
        with streamlit.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = streamlit.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    streamlit.session_state.messages.append(message)
