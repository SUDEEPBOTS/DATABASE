import streamlit as st
import pymongo
import pandas as pd
import json
from bson import ObjectId

# 🎨 Page Config (Tab Title & Icon)
st.set_page_config(page_title="Sudeep DB Manager", page_icon="🗂️", layout="wide")

# 🔐 HEADER & LOGIN
st.title("🗂️ Sudeep Database Manager")
st.markdown("---")

# Sidebar mein Login
with st.sidebar:
    st.header("🔑 Login Panel")
    mongo_url = st.text_input("Enter MongoDB URL", type="password", placeholder="mongodb+srv://...")
    connect_btn = st.button("Connect 🚀")

# Session State to store Connection
if "client" not in st.session_state:
    st.session_state.client = None

# Connection Logic
if connect_btn and mongo_url:
    try:
        client = pymongo.MongoClient(mongo_url)
        # Test Connection
        client.server_info()
        st.session_state.client = client
        st.sidebar.success("✅ Connected Successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Connection Failed: {e}")

# 📂 MAIN FILE MANAGER UI
if st.session_state.client:
    client = st.session_state.client
    
    # 1. Select Database
    all_dbs = client.list_database_names()
    selected_db_name = st.selectbox("💽 Select Database", all_dbs)
    
    if selected_db_name:
        db = client[selected_db_name]
        
        # 2. Select Collection (Folder)
        all_collections = db.list_collection_names()
        selected_col_name = st.selectbox("📂 Select Collection", all_collections)
        
        if selected_col_name:
            collection = db[selected_col_name]
            
            # 3. Data Visualization (Table View)
            st.markdown(f"### 📄 Viewing: `{selected_col_name}`")
            
            # Fetch Data
            data = list(collection.find().limit(100)) # Last 100 entries only for speed
            
            if data:
                # Convert ObjectId to String for display
                for doc in data:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                
                # Show as DataFrame (Table)
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # 🗑️ DELETE SECTION
                st.markdown("---")
                st.subheader("🗑️ Delete Zone")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    # User will paste ID to delete
                    id_to_delete = st.text_input("Paste '_id' to Delete Document")
                with col2:
                    st.write("") # Spacing
                    st.write("") 
                    if st.button("❌ Delete Now", type="primary"):
                        if id_to_delete:
                            try:
                                result = collection.delete_one({"_id": ObjectId(id_to_delete)})
                                if result.deleted_count > 0:
                                    st.success(f"✅ Document {id_to_delete} Deleted!")
                                    st.rerun() # Page Refresh
                                else:
                                    st.error("⚠️ ID not found!")
                            except:
                                st.error("❌ Invalid ID Format")
            else:
                st.info("📂 This collection is empty.")

else:
    st.info("👈 Please enter your MongoDB URL in the sidebar to start.")
  
