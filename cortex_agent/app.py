import json
import streamlit as st
import pandas as pd
import requests
import snowflake.connector

HOST = "EQCNGGW-UUB67242.snowflakecomputing.com"
API_ENDPOINT = "/api/v2/cortex/agent:run"
API_TIMEOUT = 50000  # in milliseconds

CORTEX_SEARCH_SERVICES = "DASH_DB.DASH_SCHEMA.VEHICLES_INFO"
SEMANTIC_MODELS_SUPPLY_CHAIN = "@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS/supply_chain_semantic_model.yaml"
SEMANTIC_MODELS_SUPPORT_TICKETS = "@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS/support_tickets_semantic_model.yaml"


if 'CONN' not in st.session_state or st.session_state.CONN is None:
    st.session_state.CONN = snowflake.connector.connect(
    user="ANGELCORTEX2025",
    password="angelrehCortex1997",
    account="EQCNGGW",
    host=HOST,
    port=443,
    warehouse="COMPUTE_WH",
    role="ACCOUNTADMIN",
)


def run_snowflake_query(query):
    try:
        df = pd.read_sql(query.replace(';',''), st.session_state.CONN)
        
        return df

    except Exception as e:
        st.error(f"Error executing SQL: {str(e)}")
        return None, None

def snowflake_api_call(query: str, limit: int = 10):
    
    payload = {
        "model": "llama3.1-70b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ],
        "tools": [
            { "tool_spec": { "type": "cortex_analyst_text_to_sql", "name": "supply_chain" } },
            { "tool_spec": { "type": "cortex_analyst_text_to_sql", "name": "support" } },
            { "tool_spec": { "type": "cortex_search", "name": "vehicles_info_search" } }
        ],
        "tool_resources": {
            "supply_chain": {"semantic_model_file": SEMANTIC_MODELS_SUPPLY_CHAIN},
            "support": {"semantic_model_file": SEMANTIC_MODELS_SUPPORT_TICKETS},
            "vehicles_info_search": {
                "name": CORTEX_SEARCH_SERVICES,
                "max_results": limit,
                "title_column": "title",
                "id_column": "relative_path"
            }
        }
    }
    
    try:
        resp = requests.post(
            url=f"https://{HOST}/{API_ENDPOINT}",
            json=payload,
            headers={
                "Authorization": f'Snowflake Token="{st.session_state.CONN.rest.token}"',
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
            
        if resp.status_code != 200:
            st.error(f"❌ HTTP Error: {resp.status_code} - {resp.reason}")
            st.error(f"Response details: {resp.text}")
            return None
        
        return resp
            
    except Exception as e:
        st.error(f"Error making request: {str(e)}")
        return None

def parse_response_to_events(response):
    """Parse raw SSE response into a list of events"""
    events = []
        
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            
            if decoded.startswith("data: "):
                content = decoded.replace("data: ", "")
                if content == "[DONE]":
                    break

                parsed = json.loads(content)
                events.append(parsed)

    return events

def process_sse_response(response):
    """Process SSE response"""
    text = ""
    sql = ""
    citations = []
    
    if not response:
        return text, sql, citations
    if isinstance(response, str):
        return text, sql, citations
    try:
        for event in response:
            if event.get('object') == "message.delta":
                delta = event.get('delta', {})
                
                for content_item in delta.get('content', []):
                    content_type = content_item.get('type')
                    if content_type == "tool_results":
                        tool_results = content_item.get('tool_results', {})
                        if 'content' in tool_results:
                            for result in tool_results['content']:
                                if result.get('type') == 'json':
                                    text += result.get('json', {}).get('text', '')
                                    search_results = result.get('json', {}).get('searchResults', [])
                                    for search_result in search_results:
                                        citations.append({'source_id':search_result.get('source_id',''), 'doc_id':search_result.get('doc_id', ''), 'text':search_result.get('text', '')})
                                    sql = result.get('json', {}).get('sql', '')
                    if content_type == 'text':
                        text += content_item.get('text', '')
                            
    except json.JSONDecodeError as e:
        print(f"Error processing events: {str(e)}")
                
    except Exception as e:
        print(f"Error processing events: {str(e)}")
        
    return text, sql, citations

def main():
    st.title("Cortex Agent POC")

    # Sidebar for new chat
    with st.sidebar:
        if st.button("New Conversation", key="new_chat"):
            st.session_state.messages = []
            st.rerun()

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'].replace("•", "\n\n"))

    if query := st.chat_input("Would you like to learn?"):
        # Add user message to chat
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Get response from API
        with st.spinner("Processing your request..."):
            response = snowflake_api_call(query, limit=1)
            events = parse_response_to_events(response)
            text, sql, citations = process_sse_response(events)
            
            # Add assistant response to chat
            if text:
                text = text.replace("【†", "[")
                text = text.replace("†】", "]")
                st.session_state.messages.append({"role": "assistant", "content": text})
                
                with st.chat_message("assistant"):
                    st.markdown(text.replace("•", "\n\n"))
                    if citations:
                        st.write("Citations:")
                        for citation in citations:
                            doc_id = citation.get("doc_id", "")
                            transcript_text = citation.get("text", "")
                            if doc_id:
                                with st.expander(f"[{citation.get('source_id', '')}] ({doc_id})"):
                                    st.write(transcript_text)

            # Display SQL if present
            if sql:
                # st.markdown("### Generated SQL")
                with st.expander("### Generated SQL"):
                    st.code(sql, language="sql")
                df_results = run_snowflake_query(sql)
                if not df_results.empty:
                    # st.write("### Results")
                    st.dataframe(df_results)

if __name__ == "__main__":
    main()