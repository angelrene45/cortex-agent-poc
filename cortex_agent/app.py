import json
import streamlit as st
import pandas as pd
import requests
import snowflake.connector

HOST = "FRHSAXD-CFB18747.snowflakecomputing.com"
API_ENDPOINT = "/api/v2/cortex/agent:run"
API_TIMEOUT = 50000  # in milliseconds

CORTEX_SEARCH_SERVICES = "sales_intelligence.data.sales_conversation_search"
SEMANTIC_MODELS = "@sales_intelligence.data.models/sales_metrics_model.yaml"

if 'CONN' not in st.session_state or st.session_state.CONN is None:
    st.session_state.CONN = snowflake.connector.connect(
        user="ANGELCORTEX2025",
        password="angelrehCortex1997",
        account="XIB99769",
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
            {
                "tool_spec": {
                    "type": "cortex_analyst_text_to_sql",
                    "name": "analyst1"
                }
            },
            {
                "tool_spec": {
                    "type": "cortex_search",
                    "name": "search1"
                }
            }
        ],
        "tool_resources": {
            "analyst1": {"semantic_model_file": SEMANTIC_MODELS},
            "search1": {
                "name": CORTEX_SEARCH_SERVICES,
                "max_results": limit,
                "id_column": "conversation_id"
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
        
        import pprint
        pprint.pprint(resp.content.decode("utf-8"))
        
        try:
            response_content = resp.json()
        except json.JSONDecodeError:
            st.error("❌ Failed to parse API response. The server may have returned an invalid JSON format.")
            st.error(f"Raw response: {resp.content[:200]}...")
            return None
            
        return response_content
            
    except Exception as e:
        st.error(f"Error making request: {str(e)}")
        return None

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
            if event.get('event') == "message.delta":
                data = event.get('data', {})
                delta = data.get('delta', {})
                
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
                                        citations.append({'source_id':search_result.get('source_id',''), 'doc_id':search_result.get('doc_id', '')})
                                    sql = result.get('json', {}).get('sql', '')
                    if content_type == 'text':
                        text += content_item.get('text', '')
                            
    except json.JSONDecodeError as e:
        st.error(f"Error processing events: {str(e)}")
                
    except Exception as e:
        st.error(f"Error processing events: {str(e)}")
        
    return text, sql, citations

def main():
    st.title("Intelligent Sales Assistant")

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
            response = snowflake_api_call(query, 1)
            text, sql, citations = process_sse_response(response)
            
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
                            if doc_id:
                                query = f"SELECT transcript_text FROM sales_conversations WHERE conversation_id = '{doc_id}'"
                                result = run_snowflake_query(query)
                                result_df = result.to_pandas()
                                if not result_df.empty:
                                    transcript_text = result_df.iloc[0, 0]
                                else:
                                    transcript_text = "No transcript available"
                    
                                with st.expander(f"[{citation.get('source_id', '')}]"):
                                    st.write(transcript_text)

            # Display SQL if present
            if sql:
                st.markdown("### Generated SQL")
                st.code(sql, language="sql")
                sales_results = run_snowflake_query(sql)
                if sales_results:
                    st.write("### Sales Metrics Report")
                    st.dataframe(sales_results)

if __name__ == "__main__":
    main()