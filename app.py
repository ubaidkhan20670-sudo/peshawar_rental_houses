import streamlit as st
import pandas as pd
from datetime import date
import os

# ---------- Page Setup ----------
st.set_page_config(page_title="Peshawar House Rental Finder", page_icon="🏠", layout="wide")

DATA_PATH = os.path.join("data", "houses.csv")

# ---------- Load Data ----------
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        cols = ["house_id", "village_area", "full_address", "rent", "rooms",
                "bathrooms", "house_type", "area_size", "furnished",
                "owner_contact", "description", "date_added"]
        return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

if "houses_df" not in st.session_state:
    st.session_state.houses_df = load_data()

df = st.session_state.houses_df

# ---------- Header ----------
st.title("🏠 Peshawar House Rental Finder")
st.caption("Search rental houses across Peshawar by area, rent, and rooms.")

tab_browse, tab_add = st.tabs(["🔍 Browse Houses", "➕ Add New House"])

# ============================================================
# TAB 1: BROWSE / SEARCH
# ============================================================
with tab_browse:
    st.sidebar.header("Filter Houses")

    if df.empty:
        st.info("No listings yet. Add your first house from the 'Add New House' tab.")
    else:
        # --- Filters ---
        areas = sorted(df["village_area"].dropna().unique().tolist())
        selected_area = st.sidebar.selectbox("Village / Area", ["All"] + areas)

        min_rent, max_rent = int(df["rent"].min()), int(df["rent"].max())
        rent_range = st.sidebar.slider(
            "Rent Range (PKR/month)", min_value=min_rent, max_value=max_rent,
            value=(min_rent, max_rent), step=1000
        )

        room_options = sorted(df["rooms"].dropna().unique().tolist())
        selected_rooms = st.sidebar.multiselect("Rooms (Bedrooms)", room_options, default=room_options)

        house_types = sorted(df["house_type"].dropna().unique().tolist())
        selected_type = st.sidebar.multiselect("House Type", house_types, default=house_types)

        sort_option = st.sidebar.radio("Sort by Rent", ["None", "Low to High", "High to Low"])

        # --- Apply Filters ---
        filtered = df.copy()
        if selected_area != "All":
            filtered = filtered[filtered["village_area"] == selected_area]
        filtered = filtered[(filtered["rent"] >= rent_range[0]) & (filtered["rent"] <= rent_range[1])]
        if selected_rooms:
            filtered = filtered[filtered["rooms"].isin(selected_rooms)]
        if selected_type:
            filtered = filtered[filtered["house_type"].isin(selected_type)]

        if sort_option == "Low to High":
            filtered = filtered.sort_values("rent", ascending=True)
        elif sort_option == "High to Low":
            filtered = filtered.sort_values("rent", ascending=False)

        st.subheader(f"Showing {len(filtered)} house(s)")

        if filtered.empty:
            st.warning("No houses match your filters. Try widening your search.")
        else:
            # --- Display as cards, 2 per row ---
            cols_per_row = 2
            rows = [filtered.iloc[i:i + cols_per_row] for i in range(0, len(filtered), cols_per_row)]

            for row in rows:
                cols = st.columns(cols_per_row)
                for col, (_, house) in zip(cols, row.iterrows()):
                    with col:
                        with st.container(border=True):
                            st.markdown(f"### {house['village_area']}")
                            st.write(f"📍 **Address:** {house['full_address']}")
                            st.write(f"💰 **Rent:** PKR {int(house['rent']):,} / month")
                            st.write(f"🛏️ **Rooms:** {house['rooms']}  |  🚿 **Bathrooms:** {house['bathrooms']}")
                            st.write(f"🏘️ **Type:** {house['house_type']}  |  📐 **Size:** {house['area_size']}")
                            st.write(f"🛋️ **Furnished:** {house['furnished']}")
                            if pd.notna(house.get("description")):
                                st.caption(house["description"])
                            with st.expander("📞 Contact Owner"):
                                st.write(f"**Phone:** {house['owner_contact']}")
                                st.write(f"[Open WhatsApp](https://wa.me/92{str(house['owner_contact']).lstrip('0')})")

# ============================================================
# TAB 2: ADD NEW HOUSE
# ============================================================
with tab_add:
    st.subheader("Add a New House Listing")

    with st.form("add_house_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            village_area = st.text_input("Village / Area *", placeholder="e.g. Hayatabad Phase 3")
            full_address = st.text_input("Full Address *", placeholder="Street, Sector, Landmark")
            rent = st.number_input("Rent (PKR/month) *", min_value=0, step=1000)
            rooms = st.number_input("Rooms (Bedrooms) *", min_value=0, step=1)
            bathrooms = st.number_input("Bathrooms *", min_value=0, step=1)
        with col2:
            house_type = st.selectbox("House Type *", ["House", "Flat", "Portion"])
            area_size = st.text_input("Area Size", placeholder="e.g. 5 Marla")
            furnished = st.selectbox("Furnished", ["No", "Semi", "Yes"])
            owner_contact = st.text_input("Owner Contact Number *", placeholder="03XXXXXXXXX")
            description = st.text_area("Description", placeholder="Any extra details about the house")

        submitted = st.form_submit_button("Add Listing")

        if submitted:
            if not village_area or not full_address or not owner_contact:
                st.error("Please fill all required fields marked with *")
            else:
                new_id = f"H{len(st.session_state.houses_df) + 1:03d}"
                new_row = {
                    "house_id": new_id,
                    "village_area": village_area,
                    "full_address": full_address,
                    "rent": rent,
                    "rooms": rooms,
                    "bathrooms": bathrooms,
                    "house_type": house_type,
                    "area_size": area_size,
                    "furnished": furnished,
                    "owner_contact": owner_contact,
                    "description": description,
                    "date_added": str(date.today()),
                }
                st.session_state.houses_df = pd.concat(
                    [st.session_state.houses_df, pd.DataFrame([new_row])], ignore_index=True
                )
                save_data(st.session_state.houses_df)
                st.success(f"House {new_id} added successfully! Check the 'Browse Houses' tab.")
