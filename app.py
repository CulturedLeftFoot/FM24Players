import streamlit as st
import pandas as pd

# Clear all Streamlit caches
st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(layout="wide")
st.title("Smart Player Role Tool")

uploaded_file = st.file_uploader(
    "Upload your Football Manager data file",
    type=["xlsx", "xls", "csv"]
)

column_map = {
    "Player": "Name",
    "Decisions": "Dec",
    "Long Throws": "L Th",
    "Passing": "Pas",
    "Technique": "Tec",
    "Tackling": "Tck",
    "Penalty Taking": "Pen",
    "Marking": "Mar",
    "Long Shots": "Lon",
    "Heading": "Hea",
    "Crossing": "Cro",
    "First Touch": "Fir",
    "Free Kick Taking": "Fre",
    "Finishing": "Fin",
    "Dribbling": "Dri",
    "Corners": "Cor",
    "Acceleration": "Acc",
    "Work Rate": "Wor",
    "Vision": "Vis",
    "Team Work": "Tea",
    "Teamwork": "Tea",
    "Positioning": "Pos",
    "Off The Ball": "OtB",
    "Off the Ball": "OtB",
    "Leadership": "Ldr",
    "Flair": "Fla",
    "Determination": "Det",
    "Concentration": "Cnt",
    "Composure": "Cmp",
    "Bravery": "Bra",
    "Anticipation": "Ant",
    "Aggression": "Agg",
    "Agility": "Agi",
    "Balance": "Bal",
    "Jumping Reach": "Jum",
    "Jumping": "Jum",
    "Natural Fitness": "Nat",
    "Pace": "Pac",
    "Stamina": "Sta",
    "Strength": "Str"
}

# Role attributes are split into In Possession and Out of Possession.
# Scoring uses 80% Key attributes and 20% Preferred attributes.
# Roles with no Preferred attributes are scored from Key attributes only.
role_attributes = {
    "In Possession": {
        # Centre-Backs
        "Centre-Back": {
            "key": ["Hea", "Mar", "Tck", "Ant", "Pos", "Jum", "Str"],
            "preferred": ["Agg", "Bra", "Cmp", "Cnt", "Dec", "Pac"]
        },
        "Ball-Playing Centre-Back": {
            "key": ["Hea", "Mar", "Pas", "Tck", "Ant", "Cmp", "Pos", "Jum", "Str"],
            "preferred": ["Fir", "Tec", "Agg", "Bra", "Cnt", "Dec", "Vis", "Pac"]
        },
        "No-Nonsense Centre-Back": {
            "key": ["Hea", "Mar", "Tck", "Ant", "Pos", "Jum", "Str"],
            "preferred": ["Agg", "Bra", "Cnt", "Pac"]
        },
        "Wide Centre-Back": {
            "key": ["Hea", "Mar", "Tck", "Ant", "Pos", "Jum", "Str"],
            "preferred": ["Dri", "Agg", "Bra", "Cmp", "Cnt", "Dec", "Wor", "Acc", "Agi", "Pac", "Sta"]
        },
        "Advanced Centre-Back": {
            "key": ["Hea", "Mar", "Pas", "Tck", "Tec", "Ant", "Cmp", "Dec", "Pos", "Tea", "Jum", "Str"],
            "preferred": ["Dri", "Fir", "Agg", "Bra", "Cnt", "Vis", "Pac", "Sta"]
        },
        "Overlapping Centre-Back": {
            "key": ["Cro", "Hea", "Mar", "Tck", "Ant", "Wor", "Jum", "Pac", "Sta", "Str"],
            "preferred": ["Dri", "Tec", "Agg", "Bra", "Cmp", "Cnt", "Dec", "OtB", "Pos", "Acc", "Agi"]
        },

        # Full-Backs and Wing-Backs
        "Full-Back": {
            "key": ["Mar", "Tck", "Ant", "Cnt", "Pos", "Tea", "Acc"],
            "preferred": ["Cro", "Dri", "Pas", "Tec", "Dec", "Wor", "Agi", "Pac", "Sta"]
        },
        "Inside Full-Back": {
            "key": ["Hea", "Mar", "Tck", "Ant", "Pos", "Str"],
            "preferred": ["Dri", "Agg", "Bra", "Cmp", "Cnt", "Dec", "Wor", "Acc", "Agi", "Jum", "Pac", "Sta"]
        },
        "Inside Wing-Back": {
            "key": ["Pas", "Tck", "Ant", "Cmp", "Dec", "Pos", "Tea", "Acc"],
            "preferred": ["Fir", "Mar", "Tec", "Cnt", "Wor", "Agi", "Pac", "Sta"]
        },
        "Playmaking Wing-Back": {
            "key": ["Fir", "Pas", "Tck", "Tec", "Cmp", "Dec", "Pos", "Tea", "Vis", "Acc"],
            "preferred": ["Cro", "Dri", "Mar", "Ant", "Cnt", "OtB", "Pos", "Wor", "Agi", "Pac", "Sta"]
        },
        "Wing-Back": {
            "key": ["Cro", "Mar", "Tck", "Tea", "Wor", "Acc", "Pac", "Sta"],
            "preferred": ["Dri", "Fir", "Pas", "Tec", "Ant", "Cnt", "Dec", "OtB", "Pos", "Agi", "Bal"]
        },
        "Advanced Wing-Back": {
            "key": ["Cro", "Dri", "Tec", "OtB", "Tea", "Wor", "Acc", "Agi", "Pac", "Sta"],
            "preferred": ["Fir", "Mar", "Pas", "Tck", "Ant", "Dec", "Fla", "Pos", "Bal"]
        },

        # Defensive Midfield
        "Defensive Midfielder": {
            "key": ["Tck", "Ant", "Cnt", "Pos", "Tea"],
            "preferred": ["Fir", "Mar", "Pas", "Agg", "Cmp", "Dec", "Wor", "Sta", "Str"]
        },
        "Box-to-Box Midfielder": {
            "key": ["Pas", "Tck", "OtB", "Tea", "Wor", "Sta"],
            "preferred": ["Dri", "Fin", "Fir", "Lon", "Tec", "Agg", "Ant", "Cmp", "Dec", "Pos", "Acc", "Bal", "Pac", "Str"]
        },
        "Box-to-Box Playmaker": {
            "key": ["Fir", "Pas", "Tec", "Cmp", "Dec", "OtB", "Tea", "Vis", "Wor", "Sta"],
            "preferred": ["Dri", "Mar", "Tck", "Ant", "Pos", "Acc", "Agi", "Bal", "Pac"]
        },
        "Deep-Lying Playmaker": {
            "key": ["Fir", "Pas", "Tec", "Cmp", "Dec", "OtB", "Tea", "Vis"],
            "preferred": ["Mar", "Tck", "Ant", "Cnt", "Pos", "Wor", "Bal", "Sta"]
        },
        "Half-Back": {
            "key": ["Hea", "Mar", "Tck", "Ant", "Cnt", "Pos", "Tea", "Jum", "Str"],
            "preferred": ["Fir", "Pas", "Agg", "Bra", "Cmp", "Dec", "Wor", "Sta"]
        },

        # Central Midfield
        "Central Midfielder": {
            "key": ["Fir", "Pas", "Tck", "Dec", "Tea"],
            "preferred": ["Tec", "Ant", "Cmp", "Cnt", "OtB", "Pos", "Vis", "Wor", "Sta"]
        },
        "Advanced Playmaker": {
            "key": ["Fir", "Pas", "Tec", "Cmp", "Dec", "OtB", "Tea", "Vis"],
            "preferred": ["Cro", "Dri", "Ant", "Fla", "Acc", "Agi"]
        },
        "Midfield Playmaker": {
            "key": ["Fir", "Pas", "Tec", "Cmp", "Dec", "OtB", "Tea", "Vis"],
            "preferred": ["Dri", "Tck", "Ant", "Fla", "Pos", "Wor", "Agi", "Sta"]
        },
        "Wide Central Midfielder": {
            "key": ["Fir", "Pas", "Tck", "Dec", "Tea"],
            "preferred": ["Cro", "Dri", "Tec", "Ant", "Cmp", "Cnt", "OtB", "Pos", "Vis", "Wor", "Agi", "Sta"]
        },

        # Wide Midfield and Wingers
        "Wide Midfielder": {
            "key": ["Cro", "Pas", "Tec", "Tea", "Wor", "Pac", "Sta"],
            "preferred": ["Dri", "Fir", "Ant", "Cmp", "OtB", "Vis", "Acc", "Agi"]
        },
        "Inside Winger": {
            "key": ["Dri", "Fir", "Tec", "Cmp", "Tea", "Acc", "Agi"],
            "preferred": ["Cro", "Lon", "Pas", "Ant", "Fla", "OtB", "Vis", "Wor", "Bal", "Pac", "Sta"]
        },
        "Playmaking Winger": {
            "key": ["Cro", "Dri", "Fir", "Pas", "Tec", "Cmp", "Dec", "OtB", "Tea", "Vis", "Acc"],
            "preferred": ["Ant", "Fla", "Wor", "Agi", "Pac", "Sta"]
        },
        "Winger": {
            "key": ["Cro", "Dri", "Tec", "Tea", "Acc", "Agi", "Pac"],
            "preferred": ["Fir", "Pas", "Ant", "Fla", "OtB", "Wor", "Bal", "Sta"]
        },

        # Attacking Midfield
        "Attacking Midfielder": {
            "key": ["Fir", "Lon", "Pas", "Tec", "Cmp", "Fla", "OtB"],
            "preferred": ["Cro", "Dri", "Fin", "Ant", "Dec", "Vis", "Acc", "Agi"]
        },
        "Channel Midfielder": {
            "key": ["Cro", "Fir", "Pas", "Tec", "Cmp", "OtB", "Wor", "Acc"],
            "preferred": ["Dri", "Lon", "Ant", "Dec", "Fla", "Vis", "Agi", "Pac", "Sta"]
        },
        "Free Role": {
            "key": ["Dri", "Fir", "Lon", "Pas", "Tec", "Cmp", "Fla", "OtB", "Vis"],
            "preferred": ["Cro", "Fin", "Ant", "Dec", "Acc", "Agi"]
        },
        "Second Striker": {
            "key": ["Fin", "Fir", "Ant", "Cmp", "OtB", "Acc"],
            "preferred": ["Dri", "Lon", "Pas", "Tec", "Cnt", "Dec", "Wor", "Agi", "Pac", "Sta"]
        },

        # Wide Forwards
        "Wide Forward": {
            "key": ["Dri", "Fir", "Tec", "Ant", "OtB", "Acc", "Agi", "Pac"],
            "preferred": ["Cro", "Fin", "Pas", "Cmp", "Fla", "Wor", "Bal", "Sta"]
        },
        "Inside Forward": {
            "key": ["Dri", "Fir", "Tec", "Ant", "Cmp", "OtB", "Acc", "Agi"],
            "preferred": ["Cro", "Fin", "Lon", "Pas", "Fla", "Vis", "Wor", "Bal", "Pac", "Sta"]
        },

        # Centre Forwards
        "Centre Forward": {
            "key": ["Fin", "Fir", "Hea", "Tec", "Cmp", "OtB", "Acc", "Str"],
            "preferred": ["Dri", "Pas", "Ant", "Dec", "Agi", "Bal", "Jum", "Pac"]
        },
        "Channel Forward": {
            "key": ["Dri", "Fin", "Fir", "Tec", "Cmp", "OtB", "Wor", "Acc"],
            "preferred": ["Cro", "Hea", "Pas", "Ant", "Dec", "Agi", "Bal", "Pac", "Sta"]
        },
        "Deep-Lying Forward": {
            "key": ["Fin", "Fir", "Tec", "Cmp", "OtB", "Str"],
            "preferred": ["Dri", "Pas", "Ant", "Dec", "Tea", "Vis", "Bal"]
        },
        "False Nine": {
            "key": ["Dri", "Fir", "Pas", "Tec", "Cmp", "Dec", "OtB", "Tea", "Vis", "Acc"],
            "preferred": ["Fin", "Ant", "Fla", "Agi", "Bal"]
        },
        "Poacher": {
            "key": ["Fin", "Hea", "Ant", "Cmp", "Cnt", "OtB", "Acc"],
            "preferred": ["Fir", "Tec", "Dec", "Bal"]
        },
        "Target Forward": {
            "key": ["Fin", "Hea", "Agg", "Bra", "Cmp", "OtB", "Bal", "Jum", "Str"],
            "preferred": ["Fir", "Ant", "Dec", "Tea"]
        },
    },
    "Out of Possession": {
        "Covering Centre-Back": {"key": ["Ant", "Pac", "Mar"], "preferred": []},
        "Stopping Centre-Back": {"key": ["Agg", "Tck", "Str"], "preferred": []},
        "Covering Wide Centre-Back": {"key": ["Ant", "Pac", "Mar"], "preferred": []},
        "Stopping Wide Centre-Back": {"key": ["Agg", "Tck", "Str"], "preferred": []},
        "Holding Full-Back": {"key": ["Pos", "Cnt", "Mar"], "preferred": []},
        "Pressing Full-Back": {"key": ["Agg", "Wor", "Ant"], "preferred": []},
        "Holding Wing-Back": {"key": ["Pos", "Cnt", "Mar"], "preferred": []},
        "Pressing Wing-Back": {"key": ["Agg", "Wor", "Ant"], "preferred": []},
        "Dropping Defensive Midfielder": {"key": ["Pos", "Dec", "Ant"], "preferred": []},
        "Pressing Defensive Midfielder": {"key": ["Agg", "Wor", "Ant"], "preferred": []},
        "Screening Defensive Midfielder": {"key": ["Pos", "Cnt", "Mar"], "preferred": []},
        "Wide Covering Defensive Midfielder": {"key": ["Ant", "Pac", "Wor"], "preferred": []},
        "Pressing Central Midfielder": {"key": ["Agg", "Wor", "Ant"], "preferred": []},
        "Screening Central Midfielder": {"key": ["Pos", "Cnt", "Mar"], "preferred": []},
        "Wide Covering Central Midfielder": {"key": ["Ant", "Pac", "Wor"], "preferred": []},
        "Tracking Wide Midfielder": {"key": ["Mar", "Wor", "Sta"], "preferred": []},
        "Wide Outlet Wide Midfielder": {"key": ["OtB", "Pac", "Ant"], "preferred": []},
        "Central Outlet Attacking Midfielder": {"key": ["OtB", "Dec", "Ant"], "preferred": []},
        "Splitting Outlet Attacking Midfielder": {"key": ["OtB", "Pac", "Ant"], "preferred": []},
        "Tracking Attacking Midfielder": {"key": ["Mar", "Wor", "Sta"], "preferred": []},
        "Inside Outlet Winger": {"key": ["OtB", "Dec", "Ant"], "preferred": []},
        "Tracking Winger": {"key": ["Mar", "Wor", "Sta"], "preferred": []},
        "Wide Outlet Winger": {"key": ["OtB", "Pac", "Ant"], "preferred": []},
        "Central Outlet Centre Forward": {"key": ["OtB", "Dec", "Ant"], "preferred": []},
        "Splitting Outlet Centre Forward": {"key": ["OtB", "Pac", "Ant"], "preferred": []},
        "Tracking Centre Forward": {"key": ["Mar", "Wor", "Sta"], "preferred": []},
    }
}

role_groups = {
    role: phase
    for phase, roles in role_attributes.items()
    for role in roles.keys()
}


role_area_groups = {
    # Defensive roles
    "Centre-Back": "Defensive",
    "Ball-Playing Centre-Back": "Defensive",
    "No-Nonsense Centre-Back": "Defensive",
    "Wide Centre-Back": "Defensive",
    "Advanced Centre-Back": "Defensive",
    "Overlapping Centre-Back": "Defensive",
    "Full-Back": "Defensive",
    "Inside Full-Back": "Defensive",
    "Inside Wing-Back": "Defensive",
    "Playmaking Wing-Back": "Defensive",
    "Wing-Back": "Defensive",
    "Advanced Wing-Back": "Defensive",
    "Covering Centre-Back": "Defensive",
    "Stopping Centre-Back": "Defensive",
    "Covering Wide Centre-Back": "Defensive",
    "Stopping Wide Centre-Back": "Defensive",
    "Holding Full-Back": "Defensive",
    "Pressing Full-Back": "Defensive",
    "Holding Wing-Back": "Defensive",
    "Pressing Wing-Back": "Defensive",

    # Midfield roles
    "Defensive Midfielder": "Midfield",
    "Box-to-Box Midfielder": "Midfield",
    "Box-to-Box Playmaker": "Midfield",
    "Deep-Lying Playmaker": "Midfield",
    "Half-Back": "Midfield",
    "Central Midfielder": "Midfield",
    "Advanced Playmaker": "Midfield",
    "Midfield Playmaker": "Midfield",
    "Wide Central Midfielder": "Midfield",
    "Wide Midfielder": "Midfield",
    "Inside Winger": "Midfield",
    "Playmaking Winger": "Midfield",
    "Winger": "Midfield",
    "Dropping Defensive Midfielder": "Midfield",
    "Pressing Defensive Midfielder": "Midfield",
    "Screening Defensive Midfielder": "Midfield",
    "Wide Covering Defensive Midfielder": "Midfield",
    "Pressing Central Midfielder": "Midfield",
    "Screening Central Midfielder": "Midfield",
    "Wide Covering Central Midfielder": "Midfield",
    "Tracking Wide Midfielder": "Midfield",
    "Wide Outlet Wide Midfielder": "Midfield",

    # Attacking roles
    "Attacking Midfielder": "Attacking",
    "Channel Midfielder": "Attacking",
    "Free Role": "Attacking",
    "Second Striker": "Attacking",
    "Wide Forward": "Attacking",
    "Inside Forward": "Attacking",
    "Centre Forward": "Attacking",
    "Channel Forward": "Attacking",
    "Deep-Lying Forward": "Attacking",
    "False Nine": "Attacking",
    "Poacher": "Attacking",
    "Target Forward": "Attacking",
    "Central Outlet Attacking Midfielder": "Attacking",
    "Splitting Outlet Attacking Midfielder": "Attacking",
    "Tracking Attacking Midfielder": "Attacking",
    "Inside Outlet Winger": "Attacking",
    "Tracking Winger": "Attacking",
    "Wide Outlet Winger": "Attacking",
    "Central Outlet Centre Forward": "Attacking",
    "Splitting Outlet Centre Forward": "Attacking",
    "Tracking Centre Forward": "Attacking",
}

area_order = ["Defensive", "Midfield", "Attacking"]


# Broad position groups used for optional role filtering.
# The filter is intentionally broad so players are not over-restricted.
role_position_groups = {
    # Centre-backs
    "Centre-Back": ["CB"],
    "Ball-Playing Centre-Back": ["CB"],
    "No-Nonsense Centre-Back": ["CB"],
    "Wide Centre-Back": ["CB", "FB", "WB"],
    "Advanced Centre-Back": ["CB"],
    "Overlapping Centre-Back": ["CB", "FB", "WB"],
    "Covering Centre-Back": ["CB"],
    "Stopping Centre-Back": ["CB"],
    "Covering Wide Centre-Back": ["CB", "FB", "WB"],
    "Stopping Wide Centre-Back": ["CB", "FB", "WB"],

    # Full-backs / wing-backs
    "Full-Back": ["FB", "WB"],
    "Inside Full-Back": ["FB", "WB", "CB"],
    "Inside Wing-Back": ["FB", "WB", "DM", "CM"],
    "Playmaking Wing-Back": ["FB", "WB", "CM", "WM"],
    "Wing-Back": ["FB", "WB", "WM"],
    "Advanced Wing-Back": ["FB", "WB", "WM", "W"],
    "Holding Full-Back": ["FB", "WB"],
    "Pressing Full-Back": ["FB", "WB"],
    "Holding Wing-Back": ["FB", "WB"],
    "Pressing Wing-Back": ["FB", "WB", "WM", "W"],

    # Defensive midfield / central midfield
    "Defensive Midfielder": ["DM", "CM"],
    "Box-to-Box Midfielder": ["DM", "CM"],
    "Box-to-Box Playmaker": ["DM", "CM"],
    "Deep-Lying Playmaker": ["DM", "CM"],
    "Half-Back": ["DM", "CB"],
    "Dropping Defensive Midfielder": ["DM", "CM", "CB"],
    "Pressing Defensive Midfielder": ["DM", "CM"],
    "Screening Defensive Midfielder": ["DM", "CM"],
    "Wide Covering Defensive Midfielder": ["DM", "CM", "FB", "WB"],

    # Central midfield
    "Central Midfielder": ["CM", "DM", "AM"],
    "Advanced Playmaker": ["CM", "AM", "DM"],
    "Midfield Playmaker": ["CM", "DM", "AM"],
    "Wide Central Midfielder": ["CM", "WM", "W"],
    "Pressing Central Midfielder": ["CM", "DM", "AM"],
    "Screening Central Midfielder": ["CM", "DM"],
    "Wide Covering Central Midfielder": ["CM", "DM", "WM", "W"],

    # Wide midfield / wide attackers
    "Wide Midfielder": ["WM", "W", "FB", "WB"],
    "Inside Winger": ["WM", "W", "AM"],
    "Playmaking Winger": ["WM", "W", "AM"],
    "Winger": ["WM", "W", "AM"],
    "Tracking Wide Midfielder": ["WM", "W", "FB", "WB"],
    "Wide Outlet Wide Midfielder": ["WM", "W", "AM"],
    "Inside Outlet Winger": ["WM", "W", "AM", "ST"],
    "Tracking Winger": ["WM", "W", "AM"],
    "Wide Outlet Winger": ["WM", "W", "AM"],

    # Attacking midfield / forwards
    "Attacking Midfielder": ["AM", "CM", "W", "ST"],
    "Channel Midfielder": ["AM", "CM", "WM", "W"],
    "Free Role": ["AM", "CM", "W", "ST"],
    "Second Striker": ["AM", "ST"],
    "Central Outlet Attacking Midfielder": ["AM", "CM", "ST"],
    "Splitting Outlet Attacking Midfielder": ["AM", "W", "ST"],
    "Tracking Attacking Midfielder": ["AM", "CM", "WM"],

    # Strikers
    "Wide Forward": ["W", "AM", "ST"],
    "Inside Forward": ["W", "AM", "ST"],
    "Centre Forward": ["ST"],
    "Channel Forward": ["ST", "W", "AM"],
    "Deep-Lying Forward": ["ST", "AM"],
    "False Nine": ["ST", "AM"],
    "Poacher": ["ST"],
    "Target Forward": ["ST"],
    "Central Outlet Centre Forward": ["ST"],
    "Splitting Outlet Centre Forward": ["ST", "W", "AM"],
    "Tracking Centre Forward": ["ST", "AM"],
}


def infer_position_groups(position_text):
    """Convert FM position text into broad groups used by this app."""
    text = str(position_text).upper()
    groups = set()

    if any(token in text for token in ["D (C)", "DC", "CB", "CENTRE-BACK", "CENTER-BACK"]):
        groups.add("CB")
    if any(token in text for token in ["D (R)", "D (L)", "DR", "DL", "RB", "LB", "FULL-BACK", "FULL BACK"]):
        groups.add("FB")
    if any(token in text for token in ["WB", "WING-BACK", "WING BACK"]):
        groups.add("WB")
    if any(token in text for token in ["DM", "DEFENSIVE MIDFIELDER"]):
        groups.add("DM")
    if any(token in text for token in ["M (C)", "MC", "CM", "CENTRAL MIDFIELDER", "MIDFIELDER CENTRE"]):
        groups.add("CM")
    if any(token in text for token in ["M (R)", "M (L)", "MR", "ML", "RM", "LM", "WIDE MIDFIELDER"]):
        groups.add("WM")
    if any(token in text for token in ["AM (C)", "AMC", "AM C", "ATTACKING MIDFIELDER"]):
        groups.add("AM")
    if any(token in text for token in ["AM (R)", "AM (L)", "AMR", "AML", "RW", "LW", "WINGER", "INSIDE FORWARD"]):
        groups.add("W")
    if any(token in text for token in ["ST", "STRIKER", "CENTRE FORWARD", "CENTER FORWARD"]):
        groups.add("ST")

    return groups


def role_matches_player_position(role, player_position_groups):
    allowed_groups = set(role_position_groups.get(role, []))
    if not allowed_groups or not player_position_groups:
        return True
    return bool(allowed_groups.intersection(player_position_groups))


def build_best_role_summary(results):
    if results.empty:
        return pd.DataFrame()

    idx = results.groupby(["Player", "Phase"])["Score"].idxmax()
    best = results.loc[idx, ["Player", "Phase", "Role", "Score", "Area"]].copy()

    rows = []
    for player, player_best in best.groupby("Player"):
        row = {"Player": player}
        for phase in ["In Possession", "Out of Possession"]:
            phase_best = player_best[player_best["Phase"] == phase]
            if phase_best.empty:
                row[f"Best {phase} Role"] = ""
                row[f"Best {phase} Score"] = None
                row[f"Best {phase} Area"] = ""
            else:
                item = phase_best.iloc[0]
                row[f"Best {phase} Role"] = item["Role"]
                row[f"Best {phase} Score"] = item["Score"]
                row[f"Best {phase} Area"] = item["Area"]
        rows.append(row)

    return pd.DataFrame(rows)

all_role_names = [
    role
    for phase in ["In Possession", "Out of Possession"]
    for role in role_attributes[phase].keys()
]

all_attributes = sorted({
    attr
    for phase_roles in role_attributes.values()
    for attrs in phase_roles.values()
    for attr_list in [attrs["key"], attrs["preferred"]]
    for attr in attr_list
})


def avg_attrs(df, attrs):
    existing = [attr for attr in attrs if attr in df.columns]
    if not existing:
        return pd.Series(0, index=df.index)
    return df[existing].mean(axis=1)


def calculate_role_scores(df):
    results = []

    for phase, roles in role_attributes.items():
        for role, attrs in roles.items():
            key_score = avg_attrs(df, attrs["key"])

            if attrs["preferred"]:
                preferred_score = avg_attrs(df, attrs["preferred"])
                score_series = (key_score * 0.8) + (preferred_score * 0.2)
            else:
                score_series = key_score

            for player, score in zip(df["Name"], score_series.round(2)):
                results.append({
                    "Player": player,
                    "Phase": phase,
                    "Area": role_area_groups.get(role, "Midfield"),
                    "Role": role,
                    "Score": score
                })

    return pd.DataFrame(results)


def highlight_max(s):
    is_max = s == s.max()
    return ["background-color: #006400; color: white" if v else "" for v in is_max]


if uploaded_file:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            attributes_df = pd.read_csv(uploaded_file)
        else:
            attributes_df = pd.read_excel(uploaded_file)

        attributes_df.columns = attributes_df.columns.str.strip()

    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    attributes_df = attributes_df.rename(columns=column_map)

    if "Name" not in attributes_df.columns:
        st.error("Could not find a player name column. Your file needs a column called 'Player' or 'Name'.")
        st.write("Columns found:", list(attributes_df.columns))
        st.stop()

    missing_attributes = [attr for attr in all_attributes if attr not in attributes_df.columns]

    if missing_attributes:
        st.warning(
            "Some attributes used in the role scores were not found in your upload. "
            "They will be treated as 0: " + ", ".join(missing_attributes)
        )
        for attr in missing_attributes:
            attributes_df[attr] = 0

    for attr in all_attributes:
        attributes_df[attr] = pd.to_numeric(attributes_df[attr], errors="coerce").fillna(0)

    # Remove Goalkeepers
    if "Best Pos" in attributes_df.columns:
        attributes_df = attributes_df[
            ~attributes_df["Best Pos"].astype(str).str.contains("GK", case=False, na=False)
        ]

    if attributes_df.empty:
        st.warning("No outfield players found after filtering out goalkeepers.")
        st.stop()

    results_df = calculate_role_scores(attributes_df)
    results_df["Rank"] = results_df.groupby("Role")["Score"].rank(ascending=False, method="min")

    st.success("Role scores calculated!")

    position_column_options = [col for col in ["Best Pos", "Best Position", "Position", "Positions", "Natural Position"] if col in attributes_df.columns]
    apply_position_filter = False
    position_column = None

    if position_column_options:
        apply_position_filter = st.checkbox(
            "Only show roles that match each player's position",
            value=False,
            help="Uses your position column to hide roles that are not relevant to each player's broad position group."
        )
        position_column = st.selectbox(
            "Position column to use for filtering:",
            position_column_options,
            index=0
        )
    else:
        st.info("Position filtering is unavailable because no position column was found. Add a column like 'Best Pos' or 'Position' to enable it.")

    if apply_position_filter and position_column:
        player_position_groups = {
            row["Name"]: infer_position_groups(row.get(position_column, ""))
            for _, row in attributes_df.iterrows()
        }
        results_df = results_df[
            results_df.apply(
                lambda row: role_matches_player_position(
                    row["Role"],
                    player_position_groups.get(row["Player"], set())
                ),
                axis=1
            )
        ].copy()
        results_df["Rank"] = results_df.groupby("Role")["Score"].rank(ascending=False, method="min")

    phase_filter = st.radio(
        "Choose role phase to view:",
        ["All", "In Possession", "Out of Possession"],
        horizontal=True
    )

    area_filter = st.radio(
        "Choose role area to view:",
        ["All", "Defensive", "Midfield", "Attacking"],
        horizontal=True
    )

    visible_results_df = results_df.copy()

    if phase_filter != "All":
        visible_results_df = visible_results_df[visible_results_df["Phase"] == phase_filter].copy()

    if area_filter != "All":
        visible_results_df = visible_results_df[visible_results_df["Area"] == area_filter].copy()

    if visible_results_df.empty:
        st.warning("No roles match the selected filters.")
        st.stop()

    with st.expander("Best Role Summary", expanded=True):
        summary_df = build_best_role_summary(visible_results_df)
        if summary_df.empty:
            st.warning("No best role summary available for the selected filters.")
        else:
            score_cols = [col for col in summary_df.columns if col.endswith("Score")]
            sort_col = score_cols[0] if score_cols else "Player"
            display_summary_df = summary_df.sort_values(by=sort_col, ascending=False if score_cols else True)
            st.dataframe(
                display_summary_df.style.format({col: "{:.2f}" for col in score_cols}),
                use_container_width=True
            )

    with st.expander("View Top Player Per Role", expanded=False):
        top_players = visible_results_df.loc[
            visible_results_df.groupby("Role")["Score"].idxmax()
        ].reset_index(drop=True)
        st.dataframe(
            top_players.sort_values(by=["Phase", "Area", "Role"]),
            use_container_width=True
        )

    with st.expander("View Ranked Role Scores Per Player", expanded=True):
        player_list = sorted(visible_results_df["Player"].unique().tolist())
        selected_player = st.selectbox("Select a player to view their roles:", player_list)
        player_roles = visible_results_df[visible_results_df["Player"] == selected_player].sort_values(
            by=["Phase", "Area", "Score"],
            ascending=[True, True, False]
        )
        st.dataframe(player_roles, use_container_width=True)

    with st.expander("View All Role Scores Table", expanded=True):
        pivot_df = visible_results_df.pivot(index="Player", columns="Role", values="Score")

        if pivot_df.empty:
            st.warning("No role scores available to display.")
        else:
            min_score = float(pivot_df.min().min())
            max_score = float(pivot_df.max().max())

            if min_score == max_score:
                st.info(f"All scores are the same: {min_score:.2f}")
                score_range = (min_score, max_score)
            else:
                score_range = st.slider(
                    "Select score range to filter players",
                    min_value=round(min_score, 2),
                    max_value=round(max_score, 2),
                    value=(round(min_score, 2), round(max_score, 2)),
                    step=0.01
                )

            mask = pivot_df.apply(lambda row: row.between(score_range[0], score_range[1]).any(), axis=1)
            filtered_df = pivot_df[mask]

            selected_roles = visible_results_df[["Role", "Area", "Phase"]].drop_duplicates()
            selected_roles["AreaOrder"] = selected_roles["Area"].apply(lambda x: area_order.index(x) if x in area_order else 99)
            selected_roles["PhaseOrder"] = selected_roles["Phase"].apply(lambda x: 0 if x == "In Possession" else 1)
            ordered_roles = selected_roles.sort_values(["PhaseOrder", "AreaOrder", "Role"])["Role"].tolist()
            ordered_roles = [role for role in ordered_roles if role in filtered_df.columns]
            filtered_df = filtered_df[ordered_roles]

            styled_filtered_df = (
                filtered_df.style
                .apply(highlight_max, axis=1)
                .format("{:.2f}")
            )

            st.dataframe(styled_filtered_df, use_container_width=True)

    with st.expander("Show Players Outside Top N in Every Role", expanded=False):
        rank_threshold = st.selectbox(
            "Only show players ranked outside top N across all visible roles:",
            [5, 10, 12],
            index=1
        )
        display_option = st.radio("View:", ["Scores", "Ranks"], horizontal=True)

        score_pivot = visible_results_df.pivot(index="Player", columns="Role", values="Score")
        rank_pivot = visible_results_df.pivot(index="Player", columns="Role", values="Rank")

        mask_outside_top_n = rank_pivot.apply(lambda row: row.dropna().min() > rank_threshold, axis=1)
        outside_top_n_players = rank_pivot[mask_outside_top_n]

        if outside_top_n_players.empty:
            st.warning(f"All players have at least one visible role ranked within top {rank_threshold}.")
        else:
            if display_option == "Scores":
                df_to_display = score_pivot.loc[outside_top_n_players.index]
                selected_roles = visible_results_df[["Role", "Area", "Phase"]].drop_duplicates()
                selected_roles["AreaOrder"] = selected_roles["Area"].apply(lambda x: area_order.index(x) if x in area_order else 99)
                selected_roles["PhaseOrder"] = selected_roles["Phase"].apply(lambda x: 0 if x == "In Possession" else 1)
                ordered_roles = selected_roles.sort_values(["PhaseOrder", "AreaOrder", "Role"])["Role"].tolist()
                df_to_display = df_to_display[[role for role in ordered_roles if role in df_to_display.columns]]
                st.dataframe(df_to_display.style.format("{:.2f}"), use_container_width=True)
            else:
                df_to_display = rank_pivot.loc[outside_top_n_players.index]
                selected_roles = visible_results_df[["Role", "Area", "Phase"]].drop_duplicates()
                selected_roles["AreaOrder"] = selected_roles["Area"].apply(lambda x: area_order.index(x) if x in area_order else 99)
                selected_roles["PhaseOrder"] = selected_roles["Phase"].apply(lambda x: 0 if x == "In Possession" else 1)
                ordered_roles = selected_roles.sort_values(["PhaseOrder", "AreaOrder", "Role"])["Role"].tolist()
                df_to_display = df_to_display[[role for role in ordered_roles if role in df_to_display.columns]]
                st.dataframe(df_to_display.style.format("{:.0f}"), use_container_width=True)
else:
    st.info("Please upload a file to begin.")
