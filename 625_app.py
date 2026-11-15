import streamlit as st
import pandas as pd

def normalize_name(name):
    return (
        str(name)
        .lower()
        .replace("-", "")
        .replace(" ", "")
    )

# Load the processed card dataset
df = pd.read_csv("ygo_cards_features.csv")

# Load the processed rarities dataset
rarities_df = pd.read_csv("ygo_card_rarities.csv")

# Gameplay mechanic flags engineered in the notebook.
# Keep only columns actually present in the exported CSV.
ALL_MECHANICS = [
    "special_summon", "can_search", "can_draw", "can_negate",
    "can_destroy", "uses_gy", "can_banish", "quick_effect",
    "from_your_hand", "protection", "atk_def_cards", "piercing",
    "burn", "pay_lp", "lp_gain", "change_control",
    "change_battle_position", "tribute", "discard", "bounce",
    "shuffle_into_deck"
]
mechanics = [name for name in ALL_MECHANICS if name in df.columns]

# Application navigation
page = st.sidebar.radio(
    "Navigation",
    ["Card Explorer", "Archetype Analytics"]
)

if page == "Card Explorer":
    st.title("YGO Insight — Card Explorer")

    # Find the maximum ATK and DEF in the dataset
    max_atk = int(df["atk"].max())
    max_def = int(df["def"].max())

    # --------------------------------------------------
    # 1. SEARCH AND FILTER OPTIONS
    # --------------------------------------------------

    st.subheader("Card Search")

    # Let users search for cards by name
    card_name = st.text_input("Search for a card")

    st.subheader("Card Classification & Filters")

    # Get all available attributes from the dataset
    attributes = sorted(df["attribute"].dropna().unique())

    # Create an Attribute dropdown
    selected_attribute = st.selectbox(
        "Filter by Attribute",
        options=["All"] + attributes
    )

    # Official Yu-Gi-Oh! monster types
    valid_monster_types = [
        "Aqua", "Beast", "Beast-Warrior", "Cyberse",
        "Dinosaur", "Divine-Beast", "Dragon", "Fairy",
        "Fiend", "Fish", "Illusion", "Insect",
        "Machine", "Plant", "Psychic", "Pyro",
        "Reptile", "Rock", "Sea Serpent", "Spellcaster",
        "Thunder", "Warrior", "Winged Beast",
        "Wyrm", "Zombie"
    ]

    # Get Monster Types from Monster Cards only
    monster_types = sorted(
        df["monster_race"].dropna().unique().tolist()
    )

    # Create a Monster Type dropdown
    selected_monster_type = st.selectbox(
        "Filter by Monster Type",
        options=["All"] + monster_types,
        index=0,
        placeholder="Search or select a Monster Type",
        accept_new_options=False
    )

    # Spell Card subtypes
    spell_types = [
        "All", "Normal", "Quick-Play", "Continuous",
        "Field", "Equip", "Ritual"
    ]

    selected_spell_type = st.selectbox(
        "Filter by Spell Type",
        options=spell_types
    )

    # Trap Card subtypes
    trap_types = [
        "All", "Normal", "Continuous", "Counter"
    ]

    selected_trap_type = st.selectbox(
        "Filter by Trap Type",
        options=trap_types
    )

    # Available card classifications
    card_classifications = [
        "All",
        "Monster",
        "Spell",
        "Trap",
        "Skill",
        "Fusion",
        "Synchro",
        "XYZ",
        "Link",
        "Ritual",
        "Pendulum",
        "Tuner",
        "Normal",
        "Effect",
        "Flip",
        "Gemini",
        "Spirit",
        "Toon",
        "Union",
        "Token"
    ]

    # Create a Card Classification dropdown
    selected_classification = st.selectbox(
        "Filter by Card Classification",
        options=card_classifications
    )

    # Get available archetypes from the dataset
    archetypes = sorted(df["archetype"].dropna().unique())

    # Create a searchable Archetype dropdown
    selected_archetype = st.selectbox(
        "Filter by Archetype",
        options=["All"] + archetypes
    )

    # Get available release years
    release_years = sorted(
        df["release_year"].dropna().astype(int).unique().tolist()
    )

    # Create Release Year dropdown
    selected_year = st.selectbox(
        "Filter by Release Year",
        options=["All"] + release_years
    )

    # Get available card rarities
    rarity_options = sorted(
        rarities_df["rarity_clean"].dropna().unique().tolist()
    )

    # Create Card Rarity dropdown
    selected_rarity = st.selectbox(
        "Filter by Card Rarity",
        options=["All"] + rarity_options
    )

    st.subheader("Monster Statistics & Ratings")

    # ATK range inputs
    #st.subheader("ATK / DEF Filters")

    atk_min = st.number_input(
        "Minimum ATK",
        min_value=0,
        value=0,
        step=100
    )

    atk_max = st.number_input(
        "Maximum ATK",
        min_value=0,
        value=max_atk,
        step=100
    )

    # DEF range inputs
    def_min = st.number_input(
        "Minimum DEF",
        min_value=0,
        value=0,
        step=100
    )

    def_max = st.number_input(
        "Maximum DEF",
        min_value=0,
        value=max_def,
        step=100
    )

    # Independent monster Level, Xyz Rank, and Link Rating filters.
    # Engineered columns distinguish the three concepts.
    rating_columns = {
        "Level": "monster_level",
        "Rank": "monster_rank",
        "Link Rating": "monster_link_rating"
    }
    selected_ratings = {}
    for label, column in rating_columns.items():
        if column in df.columns:
            options = ["All"] + sorted(
                df[column].dropna().astype(int).unique().tolist()
            )
            selected_ratings[column] = st.selectbox(
                f"Filter by {label}", options=options
            )
        else:
            st.warning(f"{label} filtering unavailable: missing column '{column}'.")

    st.subheader("Gameplay Mechanics")

    # Use all available engineered mechanic flags.
    gameplay_mechanics = mechanics

    # Create a Gameplay Mechanics multiselect
    selected_mechanics = st.multiselect(
        "Filter by Gameplay Mechanics",
        options=gameplay_mechanics,
        format_func=lambda x: x.replace("_", " ").title()
    )

    # --------------------------------------------------
    # 2. APPLY FILTERS
    # --------------------------------------------------

    # Normalize card names
    normalized_names = (
        df["name"]
        .fillna("")
        .apply(normalize_name)
    )

    # Normalize the user's search
    normalized_search = normalize_name(card_name)

    # Filter cards by normalized name
    filtered_df = df[
        normalized_names.str.contains(
            normalized_search,
            regex=False
        )
    ]

    # Apply Attribute filtering
    if selected_attribute != "All":
        filtered_df = filtered_df[
            filtered_df["attribute"] == selected_attribute
        ]

    # Apply Monster Type filtering
    if selected_monster_type != "All":
        filtered_df = filtered_df[
            filtered_df["monster_race"] == selected_monster_type
        ]

    # Apply Spell and Trap subtype filtering
    if selected_spell_type != "All" or selected_trap_type != "All":

        spell_match = (
            (filtered_df["card_category"] == "Spell")
            & (
                (filtered_df["spell_type"] == selected_spell_type)
                if selected_spell_type != "All"
                else True
            )
        )

        trap_match = (
            (filtered_df["card_category"] == "Trap")
            & (
                (filtered_df["trap_type"] == selected_trap_type)
                if selected_trap_type != "All"
                else True
            )
        )

        filtered_df = filtered_df[spell_match | trap_match]

    # Apply Card Classification filtering
    if selected_classification != "All":

        if selected_classification == "Monster":
            filtered_df = filtered_df[
                filtered_df["type"].str.contains(
                    "Monster|Token",
                    case=False,
                    na=False,
                    regex=True
                )
            ]

        else:
            filtered_df = filtered_df[
                filtered_df["type"].str.contains(
                    selected_classification,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

    # Apply Archetype filtering
    if selected_archetype != "All":
        filtered_df = filtered_df[
            filtered_df["archetype"] == selected_archetype
        ]

    # Apply Release Year filtering
    if selected_year != "All":
        filtered_df = filtered_df[
            filtered_df["release_year"] == selected_year
        ]

    # Apply Card Rarity filtering
    if selected_rarity != "All":

        matching_card_ids = rarities_df.loc[
            rarities_df["rarity_clean"] == selected_rarity,
            "card_id"
        ].unique()

        filtered_df = filtered_df[
            filtered_df["id"].isin(matching_card_ids)
        ]

    # Validate ATK and DEF ranges
    if atk_min > atk_max:
        st.error("Minimum ATK cannot exceed Maximum ATK.")
        st.stop()

    if def_min > def_max:
        st.error("Minimum DEF cannot exceed Maximum DEF.")
        st.stop()

    # Apply ATK filtering
    if atk_min > 0 or atk_max < max_atk:
        filtered_df = filtered_df[
            filtered_df["atk"].between(atk_min, atk_max)
        ]

    # Apply DEF filtering
    if def_min > 0 or def_max < max_def:
        filtered_df = filtered_df[
            filtered_df["def"].between(def_min, def_max)
        ]

    # Apply Level, Rank, and Link Rating independently.
    # A selected rating matches only cards with that engineered value.
    for column, selected_value in selected_ratings.items():
        if selected_value != "All":
            filtered_df = filtered_df[
                filtered_df[column] == selected_value
            ]

    # Apply Gameplay Mechanics filtering
    for mechanic in selected_mechanics:
        filtered_df = filtered_df[
            filtered_df[mechanic].eq(1)
        ]

    st.subheader("Search Results")

    # Show the number of matching cards
    st.write(f"Found {len(filtered_df)} cards")


    # --------------------------------------------------
    # 3. COLUMN SELECTION
    # --------------------------------------------------

    # Default columns displayed when the website loads
    default_columns = [
        "id",
        "name",
        "type",
        "desc",
        "monster_race",
        "spell_type",
        "trap_type",
        "attribute",
        "atk",
        "def"
    ]

    # Only include columns that exist in the dataset
    default_columns = [
        col for col in default_columns if col in df.columns
    ]

    st.subheader("Results Table & Display Columns")

    # Let users choose which columns to display
    selected_columns = st.multiselect(
        "Choose columns to display",
        options=df.columns.tolist(),
        default=default_columns
    )


    # --------------------------------------------------
    # 4. INTERACTIVE CARD TABLE
    # --------------------------------------------------

    if selected_columns:

        # Display selected columns and allow row selection
        event = st.dataframe(
            filtered_df[selected_columns],
            width="stretch",
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn(
                    "Card Name",
                    width="large"
                ),
                "desc": st.column_config.TextColumn(
                    "Card Effect",
                    width="large"
                ),
            },
            on_select="rerun",
            selection_mode="single-row"
        )

        # Get selected row
        selected_rows = event.selection.rows

        # --------------------------------------------------
        # 5. CARD DETAILS VIEWER
        # --------------------------------------------------

        if selected_rows:

            # Get the position of the selected card
            selected_position = selected_rows[0]

            # Retrieve the full card information
            selected_card = filtered_df.iloc[selected_position]

            st.subheader("Card Details")

            # Display the selected card's name
            st.subheader(selected_card["name"])

            # Get the selected card's image URL
            card_image = selected_card.get("image_url")

            # Display the image if a URL exists
            if pd.notna(card_image) and str(card_image).strip():
                st.image(card_image, width=250) 
        
            # Display basic card information
            st.write("Card Type:", selected_card["type"])

            card_category = selected_card["card_category"]

            # Monster Cards
            if card_category in ["Main Deck Monster", "Extra Deck Monster", "Token"]:

                st.write("Monster Race:", selected_card["monster_race"])

                attribute = selected_card.get("attribute")
                if pd.notna(attribute):
                    st.write("Attribute:", attribute)

                # Display Level, Rank, or Link Rating
                for label, column in rating_columns.items():
                    rating = selected_card.get(column)

                    if pd.notna(rating):
                        st.write(f"{label}:", int(rating))

                # Display Link Markers if available
                link_markers = selected_card.get("linkmarkers")

                if pd.notna(link_markers):
                    st.write("Link Markers:", link_markers)

                # Display Pendulum Scale if available
                pendulum_scale = selected_card.get("scale")

                if pd.notna(pendulum_scale):
                    st.write("Pendulum Scale:", pendulum_scale)

                # Display ATK and DEF if available
                atk = selected_card.get("atk")
                defense = selected_card.get("def")

                if pd.notna(atk):
                    st.write("ATK:", int(atk))

                if pd.notna(defense):
                    st.write("DEF:", int(defense))
            # Spell Cards
            elif card_category == "Spell":

                spell_type = selected_card.get("spell_type")

                if pd.notna(spell_type):
                    st.write("Spell Type:", spell_type)

            # Trap Cards
            elif card_category == "Trap":

                trap_type = selected_card.get("trap_type")

                if pd.notna(trap_type):
                    st.write("Trap Type:", trap_type)

            # Display the complete card description
            st.markdown("### Card Description")
            st.write(
                selected_card.get(
                    "desc",
                    "No description available."
                )
            )

    else:
        st.info("Select at least one column to display.")
elif page == "Archetype Analytics":
    st.title("YGO Insight — Archetype Analytics")

    # Get available archetypes
    archetype_options = sorted(
        df["archetype"].dropna().unique().tolist()
    )

    # Let users select an archetype
    selected_archetype = st.selectbox(
        "Select an Archetype",
        options=archetype_options,
        index=archetype_options.index("Blackwing")
        if "Blackwing" in archetype_options else 0
    )

    # Filter the dataset
    archetype_df = df[
        df["archetype"] == selected_archetype
    ]

    # Count cards by category
    category_counts = archetype_df[
        "card_category"
    ].value_counts()

    # Calculate overview metrics
    total_cards = len(archetype_df)

    main_deck = category_counts.get(
        "Main Deck Monster", 0
    )

    extra_deck = category_counts.get(
        "Extra Deck Monster", 0
    )

    spells_traps = (
        category_counts.get("Spell", 0)
        + category_counts.get("Trap", 0)
    )

    # Display overview metrics
    st.subheader(selected_archetype)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cards", total_cards)
    col2.metric("Main Deck Monsters", main_deck)
    col3.metric("Extra Deck Monsters", extra_deck)
    col4.metric("Spells & Traps", spells_traps)

    # --------------------------------------------------
    # ARCHETYPE COMPOSITION CHART
    # --------------------------------------------------

    st.subheader("Card Composition")

    # Define the order of card categories
    category_order = [
        "Main Deck Monster",
        "Extra Deck Monster",
        "Spell",
        "Trap",
        "Token"
    ]

    # Create a DataFrame for the chart
    composition_df = pd.DataFrame({
        "Category": category_order,
        "Cards": [
            category_counts.get(category, 0)
            for category in category_order
        ]
    })

    # Display the chart
    st.bar_chart(
        composition_df,
        x="Category",
        y="Cards"
    )

    # --------------------------------------------------
    # ARCHETYPE MONSTER STATISTICS
    # --------------------------------------------------

    st.subheader("Monster Statistics")

    # Filter Main Deck and Extra Deck Monsters
    monster_df = archetype_df[
        archetype_df["card_category"].isin([
            "Main Deck Monster",
            "Extra Deck Monster"
        ])
    ]

    # Calculate monster statistics
    monster_count = len(monster_df)
    avg_atk = monster_df["atk"].mean()
    avg_def = monster_df["def"].mean()
    max_atk = monster_df["atk"].max()
    max_def = monster_df["def"].max()

    # Display statistics
    col1, col2, col3 = st.columns(3)

    col1.metric("Monster Count", monster_count)
    col2.metric("Average ATK", f"{avg_atk:,.2f}")
    col3.metric("Average DEF", f"{avg_def:,.2f}")

    col4, col5 = st.columns(2)

    col4.metric("Maximum ATK", f"{max_atk:,.0f}")
    col5.metric("Maximum DEF", f"{max_def:,.0f}")

    # --------------------------------------------------
    # ARCHETYPE RELEASE HISTORY
    # --------------------------------------------------

    st.subheader("Archetype Release History")

    # Only include cards with a known release year
    release_df = archetype_df.dropna(
        subset=["release_year"]
    ).copy()

    # Count new cards by year
    release_history = (
        release_df.groupby("release_year")
        .size()
        .reset_index(name="New Cards")
        .sort_values("release_year")
    )

    if not release_history.empty:

        # Calculate release statistics
        first_year = int(release_history["release_year"].min())
        latest_year = int(release_history["release_year"].max())

        peak_row = release_history.loc[
            release_history["New Cards"].idxmax()
        ]

        peak_year = int(peak_row["release_year"])
        peak_cards = int(peak_row["New Cards"])

        # Calculate number of cards with known release dates
        dated_cards = len(release_df)

        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("First Release", first_year)
        col2.metric("Latest Release", latest_year)
        col3.metric("Peak Year", peak_year)
        col4.metric("Cards in Peak Year", peak_cards)
        col5.metric("Cards with Dates", dated_cards)

        # Display release chart
        release_history["release_year"] = (
            release_history["release_year"].astype(int).astype(str)
        )

        st.bar_chart(
            release_history,
            x="release_year",
            y="New Cards"
        )

    else:
        st.info("No release history available for this archetype.")

    
    # --------------------------------------------------
    # ARCHETYPE GAMEPLAY MECHANICS
    # --------------------------------------------------

    st.subheader("Gameplay Mechanics Analysis")

    # Use the full available mechanic list, shared with Card Explorer.
    # Each flag represents a keyword-based feature, not gameplay power.

    # Calculate the number and percentage of cards
    # containing each mechanic
    mechanic_results = []

    for mechanic in mechanics:
        card_count = int(pd.to_numeric(archetype_df[mechanic], errors="coerce").fillna(0).sum())

        percentage = (
            card_count / len(archetype_df) * 100
            if len(archetype_df) > 0 else 0
        )

        mechanic_results.append({
            "Mechanic": mechanic.replace("_", " ").title(),
            "Card Count": card_count,
            "Percentage": round(percentage, 2)
        })

    # Convert results into a DataFrame
    mechanics_df = pd.DataFrame(mechanic_results)

    # Sort by percentage
    mechanics_df = mechanics_df.sort_values(
        "Percentage",
        ascending=False
    )

    # Display mechanics chart
    st.bar_chart(
        mechanics_df,
        x="Mechanic",
        y="Percentage",
        horizontal=True,
        x_label="Percentage (%)"
    )

    # Display the detailed table
    st.dataframe(
        mechanics_df,
        hide_index=True,
        width="stretch",
        column_config={
            "Percentage": st.column_config.NumberColumn(
                "Percentage",
                format="%.2f%%"
            )
        }
    )

    st.caption(
        "Percentages represent keyword-based mechanic flags "
        "in card descriptions, not competitive strength."
    )


    # --------------------------------------------------
    # ARCHETYPE COMPARISONS
    # --------------------------------------------------

    st.divider()
    st.header("Archetype Comparisons")

    # Select archetypes to compare
    comparison_archetypes = st.multiselect(
        "Select Archetypes to Compare",
        options=archetype_options,
        default=[
            name for name in [
                "Blackwing",
                "Elemental HERO",
                "Gimmick Puppet"
            ]
            if name in archetype_options
        ]
    )

    if len(comparison_archetypes) >= 2:

        comparison_df = df[
            df["archetype"].isin(comparison_archetypes)
        ].copy()

        # ----------------------------------------------
        # 1. CARD COMPOSITION COMPARISON
        # ----------------------------------------------

        st.subheader("Card Composition Comparison")

        composition_comparison = pd.crosstab(
            comparison_df["archetype"],
            comparison_df["card_category"]
        )

        composition_comparison = composition_comparison.reindex(
            index=comparison_archetypes,
            columns=category_order,
            fill_value=0
        )

        st.bar_chart(composition_comparison)

        st.dataframe(
            composition_comparison,
            width="stretch"
        )

        # ----------------------------------------------
        # 2. MONSTER STATISTICS COMPARISON
        # ----------------------------------------------

        st.subheader("Monster Statistics Comparison")

        comparison_monsters = comparison_df[
            comparison_df["card_category"].isin([
                "Main Deck Monster",
                "Extra Deck Monster"
            ])
        ]

        monster_comparison = (
            comparison_monsters
            .groupby("archetype")
            .agg(
                Monster_Count=("id", "count"),
                Average_ATK=("atk", "mean"),
                Average_DEF=("def", "mean"),
                Maximum_ATK=("atk", "max"),
                Maximum_DEF=("def", "max")
            )
            .reindex(comparison_archetypes)
            .round(2)
        )

        st.dataframe(
            monster_comparison,
            width="stretch"
        )

        # ----------------------------------------------
        # 3. RELEASE HISTORY COMPARISON
        # ----------------------------------------------

        st.subheader("Release History Comparison")

        comparison_releases = comparison_df.dropna(
            subset=["release_year"]
        )

        release_comparison = pd.crosstab(
            comparison_releases["release_year"],
            comparison_releases["archetype"]
        )

        release_comparison = release_comparison.reindex(
            columns=comparison_archetypes,
            fill_value=0
        )

        st.line_chart(release_comparison)

        # ----------------------------------------------
        # 4. GAMEPLAY MECHANICS COMPARISON
        # ----------------------------------------------

        st.subheader("Gameplay Mechanics Comparison")

        # Convert flags to numeric before calculating prevalence.
        comparison_df[mechanics] = comparison_df[mechanics].apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0)

        mechanics_comparison = (
            comparison_df
            .groupby("archetype")[mechanics]
            .mean()
            .mul(100)
            .reindex(comparison_archetypes)
            .round(2)
        )

        mechanics_comparison.columns = [
            col.replace("_", " ").title()
            for col in mechanics_comparison.columns
        ]

        st.bar_chart(
            mechanics_comparison.T,
            horizontal=True,
            x_label="Percentage (%)"
        )

        st.dataframe(
            mechanics_comparison,
            width="stretch",
            column_config={
                column: st.column_config.NumberColumn(
                    column,
                    format="%.2f%%"
                )
                for column in mechanics_comparison.columns
            }
        )

    else:
        st.info(
            "Select at least two archetypes to compare."
        )
